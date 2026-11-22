#!/bin/bash
# 켜져 있는 AI 서버·Spring 서버·React 화면 모두 끄기
source "$(dirname "$0")/env.sh"
pkill -f 'uvicorn app.main:app'
pkill -f CropBackendApplication
pkill -f vite
(cd "$BACK" && ./gradlew --stop -q)
sleep 2
ss -ltnp | grep -E ':8000|:8080|:5173' || echo "모두 꺼짐 (8000, 8080, 5173 비어 있음)"
