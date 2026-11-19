"""NCPMS → MySQL disease.description / treatment 채우기.

  export NCPMS_API_KEY=...                       # 발급받은 키
  python -m db.seed_disease_texts search         # 1) 병 검색(SVC01)으로 sickKey 찾기 (한글명 일치 → 영문명 일치 순)
  python -m db.seed_disease_texts list --crop 옥수수            # 수동 항목: 후보 전체 보기
  python -m db.seed_disease_texts show D00001176                # 후보가 우리 병과 같은지 병원체·증상 확인
  python -m db.seed_disease_texts set Tomato___Target_Spot D00001234   # 수동 항목: sickKey 지정
  python -m db.seed_disease_texts fetch          # 2) 병 상세(SVC05) 조회, db/out/ 에 JSON 저장 (DB 안 건드림)
  python -m db.seed_disease_texts fetch --apply  # 3) 확인 후 DB 반영 (기본: '(작성 필요)'인 행만)

DB 접속: DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD 환경변수.
"""
import argparse
import json
import os
import re
from pathlib import Path

from .labels_ko import LABELS_KO, STATIC_TEXT
from .ncpms_client import NcpmsClient, NcpmsError, compose_texts

HERE = Path(__file__).parent
MAP_PATH = HERE / "sickkey_map.json"
MANUAL_PATH = HERE / "manual_texts.json"
OUT = HERE / "out"
PLACEHOLDER = "(작성 필요)"
# NCPMS 응답에 해당 칸이 비어 있을 때 DB(NOT NULL)에 들어갈 안내 문구
MISSING_DESC = "NCPMS에 등록된 증상 설명이 없습니다. 가까운 농업기술센터나 NCPMS 병해충 상담에서 확인하세요."
MISSING_TREAT = "NCPMS에 등록된 방제 방법이 없습니다. 가까운 농업기술센터나 NCPMS 병해충 상담에서 확인하세요."


def load_map() -> dict:
    return json.loads(MAP_PATH.read_text(encoding="utf-8")) if MAP_PATH.exists() else {}


def match_candidates(recs: list[dict], meta: dict) -> list[dict]:
    """같은 작물이고 영문 병명에 meta['eng'] 가 들어 있는 후보 (대소문자 무시)."""
    eng = meta.get("eng", "").lower()
    return [r for r in recs if r["cropName"] == meta["crop_kor"] and eng and eng in r["sickNameEng"].lower()]


def pick_matches(recs: list[dict], meta: dict) -> list[dict]:
    """1순위: 작물 + 한글 병명이 정확히 같은 후보가 1개 (영문명이 비어 있는 병도 잡힘).
    2순위: 영문 병명 일치."""
    kor = {r["sickKey"]: r for r in recs if r["cropName"] == meta["crop_kor"] and r["sickNameKor"] == meta["search"]}
    if len(kor) == 1:
        return list(kor.values())
    return match_candidates(recs, meta)


def dedupe(recs: list[dict]) -> list[dict]:
    seen, out = set(), []
    for r in recs:
        if r["sickKey"] not in seen:
            seen.add(r["sickKey"])
            out.append(r)
    return out


def cmd_search(_):
    client, mapping, cands = NcpmsClient(), load_map(), {}
    for label, m in LABELS_KO.items():
        if m["kind"] != "disease" or mapping.get(label):
            continue
        recs = client.search_sick(m["crop_kor"], m["search"])     # 1) 한글 검색어로 좁혀서
        hits = pick_matches(recs, m)
        if not hits:                                              # 2) 못 찾으면 작물 전체에서
            recs = dedupe(recs + client.search_sick(m["crop_kor"]))
            hits = pick_matches(recs, m)
        cands[label] = recs
        if len({r["sickKey"] for r in hits}) == 1:
            mapping[label] = hits[0]["sickKey"]
            print(f"[확정] {label} → {mapping[label]} ({hits[0]['sickNameKor']} / {hits[0]['sickNameEng'] or '-'})")
        else:
            print(f"[수동] {label}  ({m['crop_kor']} '{m['search']}' / '{m['eng']}') 일치 {len({r['sickKey'] for r in hits})}개, 후보 {len(recs)}개")
            for r in hits[:8]:
                print(f"       {r['sickKey']}  {r['cropName']} {r['sickNameKor']} / {r['sickNameEng'] or '-'}")
    OUT.mkdir(exist_ok=True)
    (OUT / "candidates.json").write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")
    MAP_PATH.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    left = [l for l, m in LABELS_KO.items() if m["kind"] == "disease" and not mapping.get(l)]
    print(f"\n확정 {len(mapping) - len(left)}개 / 수동 필요 {len(left)}개 (db/sickkey_map.json)")
    if left:
        print("수동 항목은 `python -m db.seed_disease_texts list` 로 후보 전체를 보고,\n`python -m db.seed_disease_texts set <라벨> <sickKey>` 로 지정하세요.")


def cmd_list(args):
    """candidates.json 의 후보를 작물·한글명 순으로 한 번씩만 출력."""
    path = OUT / "candidates.json"
    if not path.exists():
        raise SystemExit("db/out/candidates.json 이 없습니다. 먼저 search 를 실행하세요.")
    seen = {}
    for recs in json.loads(path.read_text(encoding="utf-8")).values():
        for r in recs:
            seen[r["sickKey"]] = r
    rows = sorted(seen.values(), key=lambda r: (r["cropName"], r["sickNameKor"]))
    if args.crop:
        rows = [r for r in rows if r["cropName"] == args.crop]
    for r in rows:
        print(f"{r['sickKey']}  {r['cropName']} {r['sickNameKor']} / {r['sickNameEng'] or '-'}")
    print(f"({len(rows)}개)")


def cmd_show(args):
    """sickKey 하나의 이름·병원체·증상 앞부분을 보여준다 (우리 라벨과 같은 병인지 눈으로 확인용)."""
    resp = NcpmsClient().sick_detail(args.sickkey)
    print(f"{args.sickkey}  {resp.first('cropName')} {resp.first('sickNameKor')} / {resp.first('sickNameEng') or '-'}")
    names, feats = resp.values("virusName"), resp.values("sfeNm")
    print("병원체:", ", ".join(dict.fromkeys(n for n in names if n)) or "(응답에 없음)")
    if any(feats):
        print("병원체 특징:", " | ".join(f[:80] for f in feats if f)[:300])
    print("증상:", (resp.first("symptoms") or "(없음)")[:300].replace("\n", " "))


SICKKEY_RE = re.compile(r"^D\d{6,}$")


def cmd_set(args):
    meta = LABELS_KO.get(args.label)
    if not meta or meta["kind"] != "disease":
        raise SystemExit(f"{args.label!r} 는 NCPMS 병 API 대상 라벨이 아닙니다. 대상: " + ", ".join(l for l, m in LABELS_KO.items() if m["kind"] == "disease"))
    if not SICKKEY_RE.match(args.sickkey):
        raise SystemExit("sickKey 형식이 이상합니다. 예: D00001550")
    mapping = load_map()
    mapping[args.label] = args.sickkey
    MAP_PATH.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {args.label} → {args.sickkey}")


def load_manual() -> dict:
    """사람이 쓴 문구(db/manual_texts.json). '_'로 시작하는 키는 안내문이라 무시."""
    if not MANUAL_PATH.exists():
        return {}
    return {k: v for k, v in json.loads(MANUAL_PATH.read_text(encoding="utf-8")).items() if not k.startswith("_")}


def cmd_fetch(args):
    mapping, texts, manual = load_map(), {}, load_manual()
    client = NcpmsClient() if any(LABELS_KO[l]["kind"] == "disease" for l in LABELS_KO) else None
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    for label, m in LABELS_KO.items():
        if label in STATIC_TEXT:
            d, t = STATIC_TEXT[label]
            texts[label] = {"description": d, "treatment": t, "source": "static"}
            continue
        man = manual.get(label, {})
        key = mapping.get(label)
        if not key:
            if man.get("description") and man.get("treatment"):
                texts[label] = {"description": man["description"], "treatment": man["treatment"], "source": "manual", "missing": []}
                print(f"[수동문구] {label} ← db/manual_texts.json ({man.get('상태', '')})")
            else:
                print(f"[건너뜀] {label}: sickKey 도, manual_texts.json 의 완전한 문구도 없습니다.")
            continue
        try:
            resp = client.sick_detail(key)
        except NcpmsError as e:
            print(f"[실패] {label}: {e}")
            continue
        (OUT / "raw" / f"{m['crop']}_{key}.txt").write_text(resp.text, encoding="utf-8")
        d, t = compose_texts(resp)
        used_manual = [f for f in ("description", "treatment") if man.get(f)]
        d, t = man.get("description") or d, man.get("treatment") or t   # 사람이 쓴 문구가 우선
        if not d and not t:
            print(f"[빈 응답] {label} (sickKey={key}) — db/out/raw 확인")
            continue
        missing = []
        if not d:
            d, missing = MISSING_DESC, missing + ["description"]
        if not t:
            t, missing = MISSING_TREAT, missing + ["treatment"]
        texts[label] = {"description": d, "treatment": t, "source": f"ncpms:{key}" + ("+manual" if used_manual else ""),
                        "ncpms_name": resp.first("sickNameKor"), "missing": missing}
        print(f"[OK] {label} ← NCPMS '{texts[label]['ncpms_name']}' (우리 이름: {m['name_ko']})")
        if used_manual:
            print(f"     [수동문구 적용] {', '.join(used_manual)} ← db/manual_texts.json ({man.get('상태', '')})")
        if missing:
            print(f"     [주의] NCPMS 응답에 {', '.join(missing)} 가 비어 있어 안내 문구로 채웠습니다 — 팀에서 직접 쓰는 것을 권장")
    (OUT / "disease_texts.json").write_text(json.dumps(texts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(texts)}/{len(LABELS_KO)}개 저장: db/out/disease_texts.json")
    if args.apply:
        apply_to_db(texts, args.force)
    else:
        print("DB에는 반영하지 않았습니다. 확인 후 --apply 를 붙여 다시 실행하세요.")


def apply_to_db(texts: dict, force: bool):
    import pymysql

    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"], charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            for label, t in texts.items():
                if force:
                    cur.execute("UPDATE disease SET description=%s, treatment=%s WHERE label=%s",
                                (t["description"], t["treatment"], label))
                else:
                    cur.execute("UPDATE disease SET description=%s, treatment=%s WHERE label=%s AND description=%s",
                                (t["description"], t["treatment"], label, PLACEHOLDER))
                print(f"  {label}: {'갱신' if cur.rowcount else '변경 없음(이미 채워졌거나 행 없음)'}")
        conn.commit()
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("search").set_defaults(fn=cmd_search)
    ls = sub.add_parser("list", help="search 가 모은 후보 전체 보기")
    ls.add_argument("--crop", help="예: 옥수수, 토마토")
    ls.set_defaults(fn=cmd_list)
    sh = sub.add_parser("show", help="sickKey 하나의 병원체·증상 확인")
    sh.add_argument("sickkey")
    sh.set_defaults(fn=cmd_show)
    st = sub.add_parser("set", help="수동으로 sickKey 지정")
    st.add_argument("label")
    st.add_argument("sickkey")
    st.set_defaults(fn=cmd_set)
    f = sub.add_parser("fetch")
    f.add_argument("--apply", action="store_true", help="MySQL에 반영")
    f.add_argument("--force", action="store_true", help="이미 채워진 행도 덮어쓰기")
    f.set_defaults(fn=cmd_fetch)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
