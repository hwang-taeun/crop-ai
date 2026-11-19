#!/usr/bin/env bash
# 백업 복원: DB 와 계정은 미리 만들어 두어야 합니다 (README 6번 참고)
# 사용: DB_USER=ncpms DB_NAME=my_ncpms bash scripts/restore_db.sh [db/backup/my_ncpms.sql]
set -euo pipefail
cd "$(dirname "$0")/.."
DB_HOST="${DB_HOST:-127.0.0.1}"; DB_PORT="${DB_PORT:-3306}"; DB_NAME="${DB_NAME:-my_ncpms}"
DB_USER="${DB_USER:?DB_USER 환경변수가 필요합니다}"
SRC="${1:-db/backup/${DB_NAME}.sql}"
[ -f "$SRC" ] || { echo "파일이 없습니다: $SRC"; exit 1; }
PW_OPT=(-p); [ -n "${DB_PASSWORD:-}" ] && { export MYSQL_PWD="$DB_PASSWORD"; PW_OPT=(); }
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" "${PW_OPT[@]}" --default-character-set=utf8mb4 "$DB_NAME" < "$SRC"
echo "복원 완료: $SRC → $DB_NAME"
