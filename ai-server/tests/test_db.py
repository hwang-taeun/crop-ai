import re
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_manual(tmp_path, monkeypatch):
    from db import seed_disease_texts as seed

    monkeypatch.setattr(seed, "MANUAL_PATH", tmp_path / "no_manual.json")

from app.labels import CLASS_NAMES
from db.labels_ko import LABELS_KO, STATIC_TEXT
from db.ncpms_client import NcpmsError, NcpmsResponse, compose_texts

XML_DETAIL = """<?xml version="1.0" encoding="UTF-8"?>
<service><cropName>토마토</cropName><sickNameKor>역병</sickNameKor>
<developmentCondition><![CDATA[저온다습할 때 발생<br/>비 온 뒤 확산]]></developmentCondition>
<symptoms>잎에 &lt;b&gt;암갈색&lt;/b&gt; 병반</symptoms>
<preventionMethod>이병 잎 제거</preventionMethod>
<chemicalPrvnbeMth>등록 약제 적용</chemicalPrvnbeMth></service>"""

JSON_DETAIL = '{"service": {"symptoms": "잎에 병반", "preventionMethod": "이병 잎 제거", "developmentCondition": ""}}'

XML_SEARCH = """<service><list><item><sickKey>101</sickKey><cropName>토마토</cropName><sickNameKor>역병</sickNameKor></item>
<item><sickKey>102</sickKey><cropName>토마토</cropName><sickNameKor>잎곰팡이병</sickNameKor></item></list></service>"""


def test_label_tables_consistent():
    assert set(LABELS_KO) == set(CLASS_NAMES) == set(STATIC_TEXT) | {l for l, m in LABELS_KO.items() if m["kind"] == "disease"}


def test_data_sql_matches_labels():
    sql = (Path(__file__).parent.parent / "db" / "data.sql").read_text(encoding="utf-8")
    assert set(re.findall(r"^\s*\('([^']+)'", sql, re.M)) == set(CLASS_NAMES)


def test_compose_xml_cleans_html():
    d, t = compose_texts(NcpmsResponse(XML_DETAIL))
    assert "[증상]" in d and "암갈색" in d and "<b>" not in d
    assert "저온다습할 때 발생\n비 온 뒤 확산" in d
    assert t.startswith("[방제 방법]") and "[화학적 방제]" in t and "[생물학적 방제]" not in t


def test_compose_json():
    d, t = compose_texts(NcpmsResponse(JSON_DETAIL))
    assert d == "[증상]\n잎에 병반" and t == "[방제 방법]\n이병 잎 제거"


def test_records_xml():
    recs = NcpmsResponse(XML_SEARCH).records()
    assert [r["sickKey"] for r in recs] == ["101", "102"] and recs[0]["sickNameKor"] == "역병"


def test_error_code_raises():
    with pytest.raises(NcpmsError):
        NcpmsResponse("<error>ERR_105</error>")


def test_fetch_dry_run_with_fake_client(tmp_path, monkeypatch, capsys):
    import json

    from db import seed_disease_texts as seed

    monkeypatch.setattr(seed, "OUT", tmp_path)
    monkeypatch.setattr(seed, "MAP_PATH", tmp_path / "map.json")
    (tmp_path / "map.json").write_text(json.dumps({"Tomato___Late_blight": 11, "Potato___Late_blight": None}))

    class FakeClient:
        def sick_detail(self, key):
            return NcpmsResponse(XML_DETAIL)

    monkeypatch.setattr(seed, "NcpmsClient", FakeClient)

    class Args:
        apply = False
        force = False

    seed.cmd_fetch(Args)
    out = json.loads((tmp_path / "disease_texts.json").read_text(encoding="utf-8"))
    assert out["Tomato___Late_blight"]["source"] == "ncpms:11"
    assert "Potato___Late_blight" not in out            # sickKey 없는 항목은 건너뜀
    assert out["Tomato___healthy"]["source"] == "static"  # 정상 잎은 고정 문구
    assert "건너뜀" in capsys.readouterr().out


# ---- 실제 NCPMS 응답(2026-11-12 curl 결과, 이미지 URL만 줄임) ----
REAL_SEARCH_JSON = '''{"service":{"buildTime":"21:33:51[785]","displayCount":"10","startPoint":1,"totalCount":2,"list":[
{"sortOrder2":674,"cropName":"토마토","thumbImg":"http://x/1","sickNameChn":"疫病","sickNameKor":"뿌리역병","cropCode":"VC010803","oriImg":"http://x/2","sickNameEng":"Phytophthora root rot","sickKey":"D00001535"},
{"sortOrder2":5445,"cropName":"토마토","thumbImg":"http://x/3","sickNameChn":"疫病","sickNameKor":"잎마름역병","cropCode":"VC010803","oriImg":"http://x/4","sickNameEng":"Late blight","sickKey":"D00001550"}]}}'''


def test_real_search_response_parsed():
    resp = NcpmsResponse(REAL_SEARCH_JSON)
    recs = resp.records()
    assert resp.total_count() == 2
    assert [r["sickKey"] for r in recs] == ["D00001535", "D00001550"]   # 문자열 키
    assert recs[1]["sickNameEng"] == "Late blight"


def test_match_by_english_name_picks_leaf_late_blight_not_root_rot():
    from db.labels_ko import LABELS_KO
    from db.seed_disease_texts import match_candidates

    hits = match_candidates(NcpmsResponse(REAL_SEARCH_JSON).records(), LABELS_KO["Tomato___Late_blight"])
    assert [h["sickKey"] for h in hits] == ["D00001550"]                # 뿌리역병(D00001535)이 아니라 잎마름역병


def test_search_sick_pages_until_total(monkeypatch):
    from db.ncpms_client import NcpmsClient

    def page(keys, total):
        items = ",".join('{"sickKey":"%s","cropName":"토마토","sickNameKor":"병%s","sickNameEng":"e"}' % (k, k) for k in keys)
        return '{"service":{"totalCount":%d,"list":[%s]}}' % (total, items)

    pages = {1: page(["A", "B"], 3), 2: page(["C"], 3), 3: page([], 3)}
    calls = []
    c = NcpmsClient(api_key="k", delay=0)
    monkeypatch.setattr(c, "_call", lambda **p: (calls.append(p["startPoint"]), NcpmsResponse(pages[p["startPoint"]]))[1])
    assert [r["sickKey"] for r in c.search_sick("토마토")] == ["A", "B", "C"]
    assert calls == [1, 2]                                              # totalCount(3)만큼 모이면 더 부르지 않음


def test_non_json_response_gives_clear_error():
    with pytest.raises(NcpmsError, match="XML/JSON"):
        NcpmsResponse("Bad Gateway")


def test_check_labels_diff():
    from db.check_labels import diff

    assert diff(["a", "b"], ["a", "b"], "X", "Y") == []
    out = diff(["Tomato___Late_blight"], ["Tomato__Late_blight"], "X", "Y")   # 밑줄 하나 차이
    assert len(out) == 2 and "Tomato___Late_blight" in out[0] and "Tomato__Late_blight" in out[1]


# ---- 2026-11-12 실제 search 결과 기반 (사용자 실행 출력) ----
def _rec(key, crop, kor, eng=""):
    return {"sickKey": key, "cropName": crop, "sickNameKor": kor, "sickNameEng": eng}


TOMATO_RECS = [
    _rec("D00004333", "토마토", "세균점무늬병"),                      # 영문명이 비어 있음
    _rec("D00004100", "토마토", "검은점뿌리썩음병", "Black dot root rot"),
    _rec("D00004252", "토마토", "황화잎말림바이러스"),
    _rec("D00001529", "토마토", "모자이크병", "Mosaic"),
    _rec("D00001532", "토마토", "겹무늬병", "Early blight"),
]


def test_pick_by_exact_korean_name_even_when_english_empty():
    from db.labels_ko import LABELS_KO
    from db.seed_disease_texts import pick_matches

    for label, key in [("Tomato___Bacterial_spot", "D00004333"),
                       ("Tomato___Tomato_Yellow_Leaf_Curl_Virus", "D00004252"),
                       ("Tomato___Tomato_mosaic_virus", "D00001529")]:
        assert [r["sickKey"] for r in pick_matches(TOMATO_RECS, LABELS_KO[label])] == [key], label


def test_corn_rust_exact_korean_match():
    from db.labels_ko import LABELS_KO
    from db.seed_disease_texts import pick_matches

    corn = [_rec("D00001197", "옥수수", "녹병", "Rust"), _rec("D00001177", "옥수수", "깜부기병", "Smut")]
    assert [r["sickKey"] for r in pick_matches(corn, LABELS_KO["Corn_(maize)___Common_rust_"])] == ["D00001197"]


def test_tomato_early_blight_falls_back_to_english():
    from db.labels_ko import LABELS_KO
    from db.seed_disease_texts import pick_matches

    # 우리 검색어(겹둥근무늬병)는 NCPMS 이름(겹무늬병)과 달라도 영문명으로 잡힘
    assert [r["sickKey"] for r in pick_matches(TOMATO_RECS, LABELS_KO["Tomato___Early_blight"])] == ["D00001532"]


def test_other_crop_not_matched():
    from db.labels_ko import LABELS_KO
    from db.seed_disease_texts import pick_matches

    recs = [_rec("D1", "감자", "세균점무늬병")]
    assert pick_matches(recs, LABELS_KO["Tomato___Bacterial_spot"]) == []


def test_set_and_list(tmp_path, monkeypatch, capsys):
    import json

    from db import seed_disease_texts as seed

    monkeypatch.setattr(seed, "OUT", tmp_path)
    monkeypatch.setattr(seed, "MAP_PATH", tmp_path / "map.json")
    (tmp_path / "map.json").write_text("{}")
    seed.cmd_set(type("A", (), {"label": "Tomato___Target_Spot", "sickkey": "D00001234"}))
    assert json.loads((tmp_path / "map.json").read_text())["Tomato___Target_Spot"] == "D00001234"
    with pytest.raises(SystemExit):                       # 형식 오류
        seed.cmd_set(type("A", (), {"label": "Tomato___Target_Spot", "sickkey": "1234"}))
    with pytest.raises(SystemExit):                       # 병 API 대상이 아닌 라벨(정상 잎)
        seed.cmd_set(type("A", (), {"label": "Tomato___healthy", "sickkey": "D00001234"}))

    (tmp_path / "candidates.json").write_text(json.dumps({"a": TOMATO_RECS[:2], "b": TOMATO_RECS[1:3]}, ensure_ascii=False))
    seed.cmd_list(type("A", (), {"crop": "토마토"}))
    out = capsys.readouterr().out
    assert out.count("D00004100") == 1 and "(3개)" in out    # 중복 제거


def test_show_prints_pathogen(monkeypatch, capsys):
    from db import seed_disease_texts as seed

    xml = ("<service><cropName>토마토</cropName><sickNameKor>점무늬병</sickNameKor><sickNameEng>Gray leaf spot</sickNameEng>"
           "<virusName>Stemphylium solani</virusName><symptoms>잎에 작은 갈색 반점</symptoms></service>")

    class FakeClient:
        def sick_detail(self, key):
            return NcpmsResponse(xml)

    monkeypatch.setattr(seed, "NcpmsClient", FakeClient)
    seed.cmd_show(type("A", (), {"sickkey": "D00001538"}))
    out = capsys.readouterr().out
    assert "Stemphylium solani" in out and "점무늬병" in out and "작은 갈색 반점" in out


def test_fetch_fills_missing_fields_with_notice(tmp_path, monkeypatch, capsys):
    import json

    from db import seed_disease_texts as seed

    monkeypatch.setattr(seed, "OUT", tmp_path)
    monkeypatch.setattr(seed, "MAP_PATH", tmp_path / "map.json")
    (tmp_path / "map.json").write_text(json.dumps({"Corn_(maize)___Common_rust_": "D00001197"}))
    xml = "<service><sickNameKor>녹병</sickNameKor><symptoms>잎 뒷면에 녹포자퇴</symptoms></service>"   # 치료법 없음

    class FakeClient:
        def sick_detail(self, key):
            return NcpmsResponse(xml)

    monkeypatch.setattr(seed, "NcpmsClient", FakeClient)
    seed.cmd_fetch(type("A", (), {"apply": False, "force": False}))
    out = json.loads((tmp_path / "disease_texts.json").read_text(encoding="utf-8"))["Corn_(maize)___Common_rust_"]
    assert out["treatment"] == seed.MISSING_TREAT and out["missing"] == ["treatment"]
    assert "녹포자퇴" in out["description"]
    assert "[주의]" in capsys.readouterr().out


def test_compose_includes_infection_route():
    d, _ = compose_texts(NcpmsResponse("<s><infectionRoute>가루이가 매개</infectionRoute></s>"))
    assert d == "[전염 경로]\n가루이가 매개"


def test_manual_texts_override_and_cover_unmapped(tmp_path, monkeypatch, capsys):
    import json

    from db import seed_disease_texts as seed

    monkeypatch.setattr(seed, "OUT", tmp_path)
    monkeypatch.setattr(seed, "MAP_PATH", tmp_path / "map.json")
    monkeypatch.setattr(seed, "MANUAL_PATH", tmp_path / "manual.json")
    (tmp_path / "map.json").write_text(json.dumps({"Corn_(maize)___Common_rust_": "D00001197"}))
    (tmp_path / "manual.json").write_text(json.dumps({
        "_안내": "무시됨",
        "Corn_(maize)___Common_rust_": {"treatment": "사람이 쓴 방제"},                       # NCPMS 치료법이 비었을 때 채움
        "Corn_(maize)___Northern_Leaf_Blight": {"description": "증상", "treatment": "방제"},  # sickKey 없는 병
        "Potato___Late_blight": {"description": "설명만 있음"},                                # 불완전 → 쓰지 않음
    }, ensure_ascii=False))
    xml = "<service><sickNameKor>녹병</sickNameKor><symptoms>NCPMS 증상</symptoms></service>"

    class FakeClient:
        def sick_detail(self, key):
            return NcpmsResponse(xml)

    monkeypatch.setattr(seed, "NcpmsClient", FakeClient)
    seed.cmd_fetch(type("A", (), {"apply": False, "force": False}))
    out = json.loads((tmp_path / "disease_texts.json").read_text(encoding="utf-8"))
    rust = out["Corn_(maize)___Common_rust_"]
    assert rust["treatment"] == "사람이 쓴 방제" and "NCPMS 증상" in rust["description"]
    assert rust["missing"] == [] and rust["source"].endswith("+manual")
    assert out["Corn_(maize)___Northern_Leaf_Blight"]["source"] == "manual"
    assert "Potato___Late_blight" not in out


def test_shipped_manual_file_is_valid():
    import json

    from app.labels import CLASS_NAMES

    real = json.loads((Path(__file__).parent.parent / "db" / "manual_texts.json").read_text(encoding="utf-8"))
    for k, v in real.items():
        if k.startswith("_"):
            continue
        assert k in CLASS_NAMES, k
        assert v.get("description") or v.get("treatment"), k
