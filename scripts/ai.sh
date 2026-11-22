#!/bin/bash
# ① AI 서버 (포트 8000) — 창 하나를 차지함, 끄기: Ctrl+C 또는 scripts/stop.sh
printf '\033]0;① AI 서버 :8000\007'
source "$(dirname "$0")/env.sh"
source "$VENV/bin/activate"
cd "$CROP"
export INTERNAL_TOKEN=$(cat "$SECRETS/crop_internal_token")
echo "===== ① AI 서버 시작 (포트 8000) ====="
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
