# 공통 경로 — 다른 스크립트가 source 해서 씀 (직접 실행하지 않음)
# 저장소 위치는 이 파일 위치로 자동 계산. venv·비밀값 위치만 필요하면 환경변수로 바꿈.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CROP="$ROOT/ai-server"
BACK="$ROOT/backend"
FRONT="$ROOT/frontend"
VENV="${VENV:-$HOME/venvs/crop-ai}"
SECRETS="${SECRETS:-$HOME/.secrets}"
SITE_DOMAIN="${SITE_DOMAIN:-crop-ai.taeun.org}"   # nginx로 서비스할 때 도메인
WEB_ROOT="${WEB_ROOT:-/var/www/crop-ai}"          # nginx가 화면 파일을 읽는 곳
