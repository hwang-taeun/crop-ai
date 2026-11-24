#!/bin/bash
# ① AI 서버 (포트 8000) — 창 하나를 차지함, 끄기: Ctrl+C 또는 scripts/stop.sh
#   AI 서버를 다른 장비에 둘 때: AI_HOST=내부IP scripts/ai.sh  (방화벽은 Spring IP만 허용)
printf '\033]0;① AI 서버 :8000\007'
source "$(dirname "$0")/env.sh"
source "$VENV/bin/activate"
cd "$CROP"
export INTERNAL_TOKEN=$(cat "$SECRETS/crop_internal_token")
echo "===== ① AI 서버 시작 (${AI_HOST:-127.0.0.1}:8000) ====="
exec uvicorn app.main:app --host "${AI_HOST:-127.0.0.1}" --port 8000
