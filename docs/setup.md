# 설치 · 데이터 다시 만들기

이 저장소에는 **용량이 크거나, 민감하거나, 재배포하면 안 되는 파일**이 빠져 있습니다.
아래 순서대로 하면 처음부터 같은 환경을 만들 수 있습니다. 명령은 Linux(WSL 포함) 기준입니다.

## 0. 저장소에 없는 것

| 빠진 것 | 이유 | 다시 만드는 곳 |
|---|---|---|
| AI 모델 (`ai-server/models/`) | 용량 큼, 원본은 암호화본(`models.tgz.gpg`)만 포함 | 4장 |
| 학습 사진 (`ai-server/data/`) | 용량 큼, 외부 데이터셋 | 4장 |
| 시험용 실제 사진 (`ai-server/samples_real_photos/`) | 인터넷에서 모은 사진이라 재배포 불가 | 7장 |
| 비밀값 (DB 비밀번호, 토큰, 서명 키, NCPMS API 키) | 보안 | 2·3장 |
| 회원·진단 기록, 업로드 사진 | 개인정보 | 실행하면 새로 생김 |
| `node_modules/`, `build/` 등 | 설치·빌드 결과물 | 5장 |

## 1. 준비물

| 프로그램 | 버전 (확인한 버전) | 설치 예 (AlmaLinux/Rocky 10) |
|---|---|---|
| Python | 3.12 | 기본 포함 |
| Java | 21 | `sudo dnf install -y java-21-openjdk-devel` |
| Node.js | 22.12 이상 | `sudo dnf install -y nodejs npm` |
| MySQL | 8.4 | `sudo dnf install -y mysql-server && sudo systemctl enable --now mysqld` |

```bash
git clone https://github.com/<계정>/crop-ai.git
cd crop-ai
ROOT=$(pwd)
```

## 2. DB 만들기

관리자 계정(root 등)으로 DB와 앱 전용 계정을 만듭니다. 비밀번호는 직접 정하세요.

```bash
mysql -u root -p <<'EOF'
CREATE DATABASE IF NOT EXISTS my_ncpms CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 백엔드(Spring)용: 데이터 읽기·쓰기만
CREATE USER IF NOT EXISTS 'crop_backend'@'localhost' IDENTIFIED BY '여기에_비밀번호';
GRANT SELECT, INSERT, UPDATE, DELETE ON my_ncpms.* TO 'crop_backend'@'localhost';

-- 병 정보 도구·백업용 (선택)
CREATE USER IF NOT EXISTS 'ncpms'@'localhost' IDENTIFIED BY '여기에_다른_비밀번호';
GRANT SELECT, INSERT, UPDATE, DELETE, LOCK TABLES, SHOW VIEW ON my_ncpms.* TO 'ncpms'@'localhost';
FLUSH PRIVILEGES;
EOF
```

테이블 구조와 **병 정보 17종**(NCPMS 데이터)은 백업 파일 하나로 들어갑니다. 회원 데이터는 포함돼 있지 않습니다.

```bash
cd "$ROOT/ai-server"
DB_USER=root DB_NAME=my_ncpms bash scripts/restore_db.sh db/backup/my_ncpms.sql
mysql -u crop_backend -p -e "SELECT COUNT(*) FROM my_ncpms.disease;"   # 17
```

> 테이블만 비어 있는 상태로 만들려면 `db/schema.sql` → `db/data.sql` 순서로 실행한 뒤, 6장 방법으로 병 설명을 채웁니다.

## 3. 비밀값 만들기

무작위 값을 만들어 **저장소 밖**(예: `~/.secrets/`)에 보관합니다.

```bash
mkdir -p ~/.secrets && chmod 700 ~/.secrets
python3 -c "import secrets; print(secrets.token_hex(32))"     > ~/.secrets/crop_internal_token   # Spring ↔ AI 서버 공유 토큰
python3 -c "import secrets; print(secrets.token_urlsafe(48))" > ~/.secrets/crop_jwt_secret       # JWT 서명 키 (32자 이상)
chmod 600 ~/.secrets/*
```

| 환경변수 | 쓰는 곳 | 값 |
|---|---|---|
| `INTERNAL_TOKEN` | ai-server, backend | `~/.secrets/crop_internal_token` (두 곳이 같아야 함) |
| `JWT_SECRET` | backend | `~/.secrets/crop_jwt_secret` |
| `DB_PASSWORD` | backend | 2장의 `crop_backend` 비밀번호 |
| `NCPMS_API_KEY` | ai-server/db 도구 | 6장 (병 정보를 다시 받을 때만) |

전체 목록은 `backend/.env.example`, `ai-server/.env.example` 을 참고하세요.

## 4. AI 모델 준비

모델 파일 3개가 `ai-server/models/` 에 있어야 AI 서버가 시작됩니다.
(`crop_model.keras`, `class_names.json`, `model_meta.json`)

### A. 암호 키가 있는 경우 (프로젝트 소유자)

```bash
cd "$ROOT/ai-server"
gpg -d --pinentry-mode loopback -o models.tgz models.tgz.gpg
sha256sum -c models.tgz.sha256          # OK 확인
tar xzf models.tgz && ls models
```

### B. 직접 학습하는 경우

GPU 가 없으면 Google Colab(무료 T4 GPU)을 권장합니다. 학습은 GPU 기준 수십 분이 걸립니다.

1. 코드 묶기 (내 PC)
   ```bash
   cd "$ROOT/ai-server"
   tar czf ~/crop-ai-code.tgz app training db requirements*.txt
   ```
2. Colab: **런타임 → 런타임 유형 변경 → T4 GPU** 후, 파일 패널에 `crop-ai-code.tgz` 업로드
3. Colab 셀 실행
   ```python
   import tensorflow as tf, keras
   print("TF", tf.__version__, "| Keras", keras.__version__)   # 이 버전을 기록 (5장에서 같은 버전 설치)

   !tar xzf crop-ai-code.tgz
   # PlantVillage 중 토마토·감자·옥수수 컬러 사진만 받기 (약 360MB)
   !git clone -q --depth 1 --filter=blob:none --sparse https://github.com/spMohanty/PlantVillage-Dataset.git pv
   !cd pv && git sparse-checkout set --no-cone "raw/color/Tomato___*" "raw/color/Potato___*" "raw/color/Corn_(maize)___*"

   !python -m training.split_plantvillage --src pv/raw/color --out data
   !python -m training.train --train-dir data/train --val-dir data/valid
   !python -m training.evaluate --data-dir data/valid --fit-temperature
   !tar czf models.tgz models
   ```
4. `models.tgz` 를 내려받아 `ai-server/` 에서 `tar xzf models.tgz`

로컬 GPU 가 있으면 같은 명령을 `ai-server/` 에서 그대로 실행하면 됩니다 (`pip install -r requirements-train.txt`).

> **라벨 일치 확인**: 모델 클래스명, DB `disease.label`, 학습 폴더명이 글자까지 같아야 진단 결과가 병 정보와 연결됩니다.
> `python -m db.check_labels --labels-file <파일> --data-dir data/train`

## 5. 실행

터미널 3개를 씁니다.

**① AI 서버 (포트 8000)**
```bash
cd "$ROOT/ai-server"
python3 -m venv ~/venvs/crop-ai && source ~/venvs/crop-ai/bin/activate
pip install -U pip
pip install "tensorflow==<4장에서 기록한 버전>" "keras==<4장에서 기록한 버전>"
pip install -r requirements-dev.txt
pytest -q                                              # 34 passed
export INTERNAL_TOKEN=$(cat ~/.secrets/crop_internal_token)
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
> 모델을 학습한 TensorFlow·Keras 버전과 같은 버전을 설치해야 모델 파일이 열립니다.
> WSL 에서는 venv 를 `/mnt/c` 가 아닌 리눅스 홈 폴더에 두어야 설치가 빠릅니다.

**② 백엔드 (포트 8080)**
```bash
cd "$ROOT/backend"
export INTERNAL_TOKEN=$(cat ~/.secrets/crop_internal_token)
export JWT_SECRET=$(cat ~/.secrets/crop_jwt_secret)
read -rsp "crop_backend DB 비밀번호: " DB_PASSWORD; echo; export DB_PASSWORD
./gradlew bootRun                                      # 'Started CropBackendApplication' 나오면 완료
```

**③ 화면 (포트 5173)**
```bash
cd "$ROOT/frontend"
npm install
npm run dev                                            # 브라우저에서 http://localhost:5173
```
개발 서버가 `/api` 요청을 백엔드(8080)로 넘겨주므로 따로 CORS 설정이 필요 없습니다.

## 6. 병 정보를 NCPMS 에서 다시 받기 (선택)

백업 파일(2장)에 이미 들어 있으므로 보통은 필요 없습니다. 최신 내용으로 다시 받고 싶을 때만 합니다.

1. [NCPMS](https://ncpms.rda.go.kr) 회원가입 → 마이페이지 → **openAPI 신청** → 제공서비스 **병해충검색**, 사용도메인에 실제 호출할 서버 주소 입력 → 인증키 즉시 발급
2. 실행
   ```bash
   cd "$ROOT/ai-server"
   export NCPMS_API_KEY='발급받은 키'
   export DB_USER=ncpms DB_NAME=my_ncpms; read -rsp "DB 비밀번호: " DB_PASSWORD; echo; export DB_PASSWORD
   python -m db.seed_disease_texts fetch           # db/out/disease_texts.json 으로 먼저 받아서 확인
   python -m db.seed_disease_texts fetch --apply   # 확인 후 DB 반영
   ```
- 등록하지 않은 도메인에서 호출하면 `ERR_105` 가 납니다.
- NCPMS 에 없는 4건은 `db/manual_texts.json` 의 문구가 들어갑니다 (검토 필요 표시).
- 병 정보는 **공공누리 제2유형**입니다. 출처를 표시하고 상업적으로 이용하지 마세요.

## 7. 실제 사진으로 평가 (선택)

검증 점수는 단색 배경 사진 기준이라 실제 성능보다 높게 나옵니다. 직접 찍은 잎 사진으로 따로 평가하세요.

```
ai-server/data/real_photos/
├── Tomato___Late_blight/      ← 폴더 이름은 app/labels.py 의 클래스명과 같게
│   ├── 001.jpg
│   └── ...
└── Potato___healthy/
```
```bash
cd "$ROOT/ai-server"
python -m training.evaluate --data-dir data/real_photos --tag real
```

화면에서 바로 시험할 때는 진단 화면에서 사진을 올리면 됩니다. 인터넷에서 받은 사진은 저장소에 올리지 마세요.

## 8. 모델 파일 암호화 (소유자용)

새로 학습한 모델을 저장소에 올릴 때만 합니다.
```bash
cd "$ROOT/ai-server"
tar czf models.tgz models
sha256sum models.tgz > models.tgz.sha256
gpg --symmetric --cipher-algo AES256 --pinentry-mode loopback -o models.tgz.gpg models.tgz
rm models.tgz
```
