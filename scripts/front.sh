#!/bin/bash
# ③ React 개발 서버 (포트 5173)
printf '\033]0;③ React 화면 :5173\007'
source "$(dirname "$0")/env.sh"
cd "$FRONT"
[ -d node_modules ] || npm install
echo "===== ③ React 화면 — 브라우저에서 http://localhost:5173 ====="
exec npm run dev
