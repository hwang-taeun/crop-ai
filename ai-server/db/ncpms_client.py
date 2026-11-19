"""NCPMS Open API 클라이언트.

확인된 명세: SVC05(병 상세정보) — apiKey, serviceCode=SVC05, sickKey.
확인됨(curl 실측): SVC01 — cropName, sickNameKor 로 검색, 응답은 기본 JSON
              {"service": {"totalCount":.., "list":[{sickKey, cropName, sickNameKor, sickNameEng, ...}]}}
              sickKey 는 정수가 아니라 "D00001550" 같은 문자열이다.
미확인: displayCount/startPoint 의 정확한 의미(startPoint 가 페이지인지 위치인지)와 최대값.
응답은 XML/JSON 어느 쪽이든 읽도록 만들었다 (글자 내용으로 판별).
"""
import html
import json
import os
import re
import time

import requests

BASE_URL = "http://ncpms.rda.go.kr/npmsAPI/service"
ERR_RE = re.compile(r"ERR_\d{3}")
CDATA_RE = re.compile(r"^<!\[CDATA\[(.*)\]\]>$", re.S)


class NcpmsError(RuntimeError):
    pass


def clean_text(s: str) -> str:
    s = html.unescape(CDATA_RE.sub(r"\1", s.strip()))  # 이스케이프된 태그(&lt;b&gt;)도 풀어서 같이 제거
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def _walk_json(obj, key):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key and isinstance(v, (str, int, float)):
                yield str(v)
            else:
                yield from _walk_json(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_json(v, key)


def _dicts_with_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            yield obj
        for v in obj.values():
            yield from _dicts_with_key(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from _dicts_with_key(v, key)


class NcpmsResponse:
    def __init__(self, text: str):
        self.text = text.strip()
        m = ERR_RE.search(self.text)
        if m:
            raise NcpmsError(f"NCPMS 오류 {m.group()} (ERR_101 키없음, 103 서비스코드, 105 미등록 도메인, 201 파라미터)")
        self.is_xml = self.text.startswith("<")
        self.json = None
        if not self.is_xml:
            try:
                self.json = json.loads(self.text)
            except ValueError:
                raise NcpmsError(f"XML/JSON 이 아닌 응답입니다: {self.text[:200]!r}") from None

    def values(self, key: str) -> list[str]:
        if self.is_xml:
            return [clean_text(v) for v in re.findall(rf"<{key}>(.*?)</{key}>", self.text, re.S)]
        return [clean_text(v) for v in _walk_json(self.json, key)]

    def total_count(self):
        v = self.first("totalCount")
        return int(v) if v.isdigit() else None

    def first(self, key: str) -> str:
        v = self.values(key)
        return v[0] if v else ""

    def records(self, keys=("sickKey", "cropName", "sickNameKor", "sickNameEng")) -> list[dict]:
        """검색 결과 목록. sickKey 를 가진 덩어리를 찾아 keys 값만 뽑는다."""
        out = []
        if self.is_xml:
            for block in re.findall(r"<item>(.*?)</item>", self.text, re.S):
                rec = {}
                for k in keys:
                    m = re.search(rf"<{k}>(.*?)</{k}>", block, re.S)
                    rec[k] = clean_text(m.group(1)) if m else ""
                if rec.get("sickKey"):
                    out.append(rec)
        else:
            for d in _dicts_with_key(self.json, "sickKey"):
                out.append({k: clean_text(str(d.get(k, ""))) for k in keys})
        return out


class NcpmsClient:
    def __init__(self, api_key: str | None = None, timeout: int = 15, delay: float = 0.3):
        self.api_key = api_key or os.getenv("NCPMS_API_KEY", "")
        if not self.api_key:
            raise SystemExit("환경변수 NCPMS_API_KEY 가 필요합니다.")
        self.timeout, self.delay = timeout, delay

    def _call(self, **params) -> NcpmsResponse:
        time.sleep(self.delay)  # 호출 제한 대비
        try:
            r = requests.get(BASE_URL, params={"apiKey": self.api_key, **params}, timeout=self.timeout)
            r.raise_for_status()
        except requests.RequestException as e:
            # 예외 메시지에 URL(=apiKey)이 들어 있어서 가린다
            raise NcpmsError(str(e).replace(self.api_key, "***")) from None
        return NcpmsResponse(r.content.decode("utf-8", errors="replace"))  # 헤더에 charset 이 없어도 한글이 깨지지 않게

    def search_sick(self, crop_name: str, sick_name: str = "", page_size: int = 100, max_pages: int = 10) -> list[dict]:
        """검색 결과 전체(최대 page_size*max_pages개). startPoint 를 1,2,3... 로 올리며 가져오고,
        새 결과가 없거나 totalCount 만큼 모이면 멈춘다. sick_name 이 비면 작물 전체를 검색한다.
        (startPoint 가 페이지가 아니라 위치라면 중복만 걸러지고 일부가 빠질 수 있다 — README 의 확인 방법 참고)"""
        out, seen = [], set()
        for page in range(1, max_pages + 1):
            params = dict(serviceCode="SVC01", cropName=crop_name, displayCount=page_size, startPoint=page)
            if sick_name:
                params["sickNameKor"] = sick_name
            resp = self._call(**params)
            new = [r for r in resp.records() if r["sickKey"] not in seen]
            if not new:
                break
            seen.update(r["sickKey"] for r in new)
            out.extend(new)
            total = resp.total_count()
            if total is not None and len(out) >= total:
                break
        return out

    def sick_detail(self, sick_key: str) -> NcpmsResponse:
        return self._call(serviceCode="SVC05", sickKey=sick_key)


def compose_texts(resp: NcpmsResponse) -> tuple[str, str]:
    """SVC05 응답 → (disease.description, disease.treatment)."""
    def sec(title, key):
        v = resp.first(key)
        return f"[{title}]\n{v}" if v else ""

    description = "\n\n".join(
        x for x in (sec("증상", "symptoms"), sec("발생 환경", "developmentCondition"), sec("전염 경로", "infectionRoute")) if x
    )
    treatment = "\n\n".join(
        x for x in (sec("방제 방법", "preventionMethod"), sec("생물학적 방제", "biologyPrvnbeMth"),
                    sec("화학적 방제", "chemicalPrvnbeMth")) if x
    )
    return description, treatment
