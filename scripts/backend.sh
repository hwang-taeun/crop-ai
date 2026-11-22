#!/bin/bash
# ② Spring 서버 (포트 8080) — DB 비밀번호를 물어봄
printf '\033]0;② Spring 서버 :8080\007'
source "$(dirname "$0")/env.sh"
cd "$BACK"
export INTERNAL_TOKEN=$(cat "$SECRETS/crop_internal_token")
export JWT_SECRET=$(cat "$SECRETS/crop_jwt_secret")
read -rsp "DB 비밀번호(crop_backend): " DB_PASSWORD; echo; export DB_PASSWORD
echo "===== ② Spring 서버 시작 (포트 8080) — 'Started CropBackendApplication' 이 나오면 준비 완료 ====="
exec ./gradlew bootRun
