#!/bin/bash
# 화면 배포 — React를 빌드해서 nginx가 읽는 폴더(WEB_ROOT)로 복사
#   scripts/deploy-front.sh       (화면 코드를 고쳤을 때마다)
set -e
source "$(dirname "$0")/env.sh"
cd "$FRONT"
[ -d node_modules ] || npm install
npm run build
sudo mkdir -p "$WEB_ROOT"
sudo rsync -a --delete dist/ "$WEB_ROOT"/
echo "배포 완료: $WEB_ROOT → http://$SITE_DOMAIN"
ls "$WEB_ROOT"
