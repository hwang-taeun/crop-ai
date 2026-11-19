"""라벨 3곳이 같은지 대조한다: ① app/labels.py(모델·서버) ② MySQL disease.label ③ 학습 데이터 폴더명.

  python -m db.check_labels                          # ①↔② (DB 접속 환경변수 필요)
  python -m db.check_labels --data-dir data/train    # ①↔③ 도 함께
  python -m db.check_labels --labels-file labels.txt # DB 대신 한 줄에 라벨 1개인 파일과 비교 (팀 data.sql 에서 뽑은 것 등)

글자 하나(밑줄 개수, 공백, 대소문자)만 달라도 진단 결과가 병명에 안 붙으므로, 학습 전에 먼저 돌려 보세요.
"""
import argparse
import os
from pathlib import Path

from app.labels import CLASS_NAMES


def diff(expected, actual, name_a, name_b) -> list[str]:
    ea, ac = set(expected), set(actual)
    out = [f"  {name_a} 에만 있음: {x!r}" for x in sorted(ea - ac)]
    out += [f"  {name_b} 에만 있음: {x!r}" for x in sorted(ac - ea)]
    return out


def labels_from_db() -> list[str]:
    import pymysql

    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"], charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT label FROM disease")
            return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir")
    ap.add_argument("--labels-file")
    a = ap.parse_args()

    problems = 0
    if a.labels_file:
        other = [l.strip() for l in Path(a.labels_file).read_text(encoding="utf-8").splitlines() if l.strip()]
        name = f"파일({a.labels_file})"
    else:
        other, name = labels_from_db(), "MySQL disease"
    d = diff(CLASS_NAMES, other, "app/labels.py", name)
    print(f"[app/labels.py {len(CLASS_NAMES)}개 ↔ {name} {len(other)}개] " + ("일치" if not d else "불일치"))
    print("\n".join(d)); problems += bool(d)

    if a.data_dir:
        folders = [p.name for p in Path(a.data_dir).iterdir() if p.is_dir()]
        missing = [x for x in CLASS_NAMES if x not in folders]   # 다른 폴더(사과 등)는 학습에서 무시되므로 '없는 것'만 문제
        print(f"[app/labels.py ↔ 학습 폴더 {a.data_dir}] " + ("일치" if not missing else "불일치"))
        print("\n".join(f"  학습 폴더에 없음: {x!r}" for x in missing)); problems += bool(missing)

    if problems:
        print("\n→ 기준을 하나 정해 맞추세요. 보통 DB(팀 data.sql)가 기준이고, app/labels.py 의 CLASS_NAMES 와 db/labels_ko.py 를 거기에 맞춥니다.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
