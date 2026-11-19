#!/usr/bin/env bash
# my_ncpms 백업 → db/backup/my_ncpms.sql
# 사용: DB_USER=ncpms DB_NAME=my_ncpms bash scripts/backup_db.sh          (공유용: disease 데이터만)
#       DB_USER=ncpms DB_NAME=my_ncpms bash scripts/backup_db.sh --full   (전체 데이터, 개인 백업용 - 커밋 금지)
set -euo pipefail
cd "$(dirname "$0")/.."

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_NAME="${DB_NAME:-my_ncpms}"
DB_USER="${DB_USER:?DB_USER 환경변수가 필요합니다}"
OUT="db/backup/${DB_NAME}.sql"
FULL=0
[ "${1:-}" = "--full" ] && { FULL=1; OUT="db/backup/${DB_NAME}_full.sql"; }

command -v mysqldump >/dev/null || { echo "mysqldump 가 없습니다 (sudo apt install mysql-client)"; exit 1; }
mkdir -p db/backup

# 비밀번호: DB_PASSWORD 환경변수가 없으면 mysqldump 가 직접 물어봄
PW_OPT=(-p)
[ -n "${DB_PASSWORD:-}" ] && { export MYSQL_PWD="$DB_PASSWORD"; PW_OPT=(); }

COMMON=(-h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" "${PW_OPT[@]}"
        --single-transaction --no-tablespaces --default-character-set=utf8mb4
        --skip-comments --skip-dump-date)

if [ "$FULL" = 1 ]; then
  mysqldump "${COMMON[@]}" "$DB_NAME" > "$OUT"
else
  # 공유용: 모든 테이블 구조 + disease 테이블 데이터만 (member 등 개인정보 제외)
  { mysqldump "${COMMON[@]}" --no-data "$DB_NAME"
    mysqldump "${COMMON[@]}" --no-create-info "$DB_NAME" disease
  } > "$OUT"
fi
echo "백업 완료: $OUT ($(wc -c < "$OUT") bytes)"
echo "disease INSERT 구문 수: $(grep -c '^INSERT INTO `disease`' "$OUT" || true) (1이면 정상, 한 문장에 17행이 묶임)"
