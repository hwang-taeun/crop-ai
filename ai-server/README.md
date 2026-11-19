# crop-ai — 작물 병해충 진단 앱의 AI·DB 파트

토마토·감자·옥수수 잎 사진을 올리면 **어떤 병인지 추측해서 알려주는 앱**을 만드는 프로젝트 중,
**AI 파트**와 **병 정보 DB 파트**를 담은 폴더입니다.

> ⚠️ 이 폴더에는 **API 키·비밀번호가 들어 있지 않습니다.** 필요한 값은 각자 발급받거나 만들어서 쓰세요.
> 절대 GitHub 등에 올리지 마세요. (`.env` 파일에만 적고, 이 파일은 공유 제외)

---

## 1. 이 프로젝트가 하는 일 (그림으로 보기)

```
 사용자(앱 화면, React)
        │ 사진 + 작물 선택(토마토/감자/옥수수)
        ▼
 백엔드 서버 (Spring Boot)  ───────────►  MySQL DB  (병 이름·설명·치료법 저장)
        │ 사진을 넘겨서 "무슨 병이야?" 질문
        ▼
 ★ AI 서버 (FastAPI) ← 이 폴더(crop-ai)가 만든 부분
        │ 사진을 분석해서 "가능성 높은 병 3개 + 확률" 답변
        ▼
 백엔드가 확률을 보고 결과 결정 → 병 설명·치료법을 DB에서 찾아 화면에 표시
```

이 폴더가 맡은 것은 별표(★) 부분과 DB에 들어갈 **병 설명·치료법 내용**입니다.

용어 풀이
- **FastAPI**: 파이썬으로 만든 작은 서버. 사진을 받아서 AI 분석 결과를 돌려줍니다.
- **CNN / MobileNetV2**: 사진을 보고 분류하는 AI 모델 종류. 이미 잘 학습된 모델을 가져와 우리 작물에 맞게 다시 훈련합니다(전이학습).
- **NCPMS**: 농촌진흥청 "국가농작물병해충관리시스템". 병 설명·방제법을 공개 API로 제공합니다.
- **API 키**: NCPMS에서 데이터를 받을 때 필요한 "출입증". 본인 이름으로 직접 신청해서 받습니다.

---

## 2. 현재 상황 (2026-11-13 기준)

| 항목 | 상태 | 쉬운 설명 |
| --- | --- | --- |
| AI 서버 코드 (`/predict`) | ✅ 완성 | 사진을 보내면 답을 주는 서버. 가짜 모델로는 끝까지 동작 확인 |
| 학습·평가 코드 | ✅ 완성 | 모델을 훈련시키고 성적을 재는 프로그램 |
| **실제 학습된 AI 모델** | ❌ 아직 없음 | 훈련용 사진 데이터를 아직 못 구함 → **가장 큰 남은 일** |
| NCPMS 연동 | ✅ 완료 | 실제로 호출해서 병 설명을 받아옴 (12개 병) |
| MySQL 데이터베이스 `my_ncpms` | ✅ 완성 | 병 17종의 이름·설명·치료법이 들어 있음 |
| DB 백업 파일 | ✅ `db/backup/my_ncpms.sql` | 이 파일로 다른 PC에 똑같이 복원 가능 |
| 자동 테스트 34개 | ✅ 모두 통과 | 코드가 망가지지 않았는지 검사하는 프로그램 |
| 팀 DB와 병 이름(라벨) 대조 | ⏳ 아직 | 팀 DB의 병 이름 17개와 우리 것이 한 글자도 안 다른지 확인 필요 |
| 사람이 쓴 설명 초안 4건 | ⚠️ 검토 필요 | NCPMS에 없는 내용을 임시로 써둠 (아래 참고) |
| 백엔드(Spring)와 연결 | ⏳ 아직 | 서로 주고받는 형식(4번 항목)을 합의해야 함 |

**DB 안의 병 설명 출처**
- 병 17종 중 12종: NCPMS 원문 (실제 공공데이터)
- 정상 잎 3종 + 점박이응애 1종: 우리가 정한 고정 문구 (`db/labels_ko.py`)
- 나머지 4건은 **NCPMS에 내용이 없거나 부족해서 사람이 쓴 초안**입니다 (`db/manual_texts.json`). 전문가 검토 전이므로 **그대로 서비스에 쓰면 안 됩니다.**
  - 옥수수 북방잎마름병 (설명·치료법), 옥수수 회색잎마름병·붉은녹병 (치료법), 토마토 황화잎말림바이러스 (설명)

---

## 3. 앞으로 해야 할 일

### 1순위 — 이게 되어야 앱이 돌아갑니다
1. **병 이름 대조**: 팀 DB(`data.sql`)의 병 이름(label) 17개를 우리 것과 비교 → 7번 "라벨 대조" 참고. 한 글자라도 다르면 진단 결과가 병 정보와 연결되지 않습니다.
2. **훈련용 사진 확보**: 병든 잎 사진 데이터셋(예: PlantVillage)을 받아 `data/train`, `data/valid` 폴더에 병 이름별로 정리.
3. **모델 학습**: 8번 "AI 모델 학습" 순서대로 실행. (GPU가 없으면 오래 걸립니다)
4. **실제 휴대폰으로 찍은 잎 사진 모으기**(`data/real_photos/`): 훈련 사진은 깨끗한 실험실 배경이라 실제 밭 사진에서는 정확도가 떨어질 수 있어, 별도로 성적을 확인해야 합니다.
5. **백엔드와 연결 테스트**: 4번 항목의 형식대로 Spring 서버가 AI 서버를 호출해 보기.

### 2순위 — 품질 높이기
6. 사람이 쓴 초안 4건을 전문가/팀이 검토하고 확정.
7. 화면에 표시할 한글 병명 3개 확정: "겹무늬병", "잎마름병", "점무늬병" (`db/labels_ko.py`의 `name_ko`).
8. 팀이 쓰는 DB에 병 설명 내용 반영 (팀 DB가 따로 있을 때).

### 3순위 — 나중에
9. 사용자가 "진단이 틀렸다"고 표시한 사진으로 모델 재학습.
10. NCPMS의 지역별 병해충 예보 API 연동.
11. 해충(점박이응애) 상세 API 명세를 받으면 고정 문구 교체.

### 화면(앱) 만들 때 꼭 지킬 것
- **출처 표시**: "농촌진흥청 국가농작물병해충관리시스템(NCPMS)" (공공누리 제2유형: 출처 표시 필수, **상업적 이용 금지**. 사용 전 이용 조건을 다시 확인하세요.)
- 약제(농약) 안내에는 "사용 전 제품 라벨과 지역 농업기술센터에 확인" 문구를 넣으세요.
- 병 설명은 줄바꿈이 있는 긴 글입니다. 줄바꿈이 보이게 표시하고, 긴 글은 접기/펼치기를 권장합니다.

---

## 4. 파일·폴더별 용도

```
crop-ai/
├─ README.md               ← 지금 보는 설명서
├─ .env.example            ← 설정값 샘플 (복사해서 .env 로 만들어 사용)
├─ .gitignore              ← GitHub에 올리지 않을 파일 목록
├─ .gitattributes          ← 줄바꿈 형식을 통일하는 설정
├─ requirements*.txt       ← 설치해야 할 파이썬 프로그램 목록 (아래 표)
├─ app/        AI 서버
├─ training/   AI 학습
├─ db/         DB·NCPMS 관련
├─ scripts/    DB 백업·복원 도구
├─ tests/      자동 테스트
└─ models/     학습이 끝난 AI 모델이 저장될 곳 (지금은 비어 있음)
```

### app/ — AI 서버 (백엔드가 호출하는 부분)
| 파일 | 하는 일 |
| --- | --- |
| `main.py` | 서버의 입구. `POST /predict`(진단), `GET /health`(살아있는지 확인) |
| `predictor.py` | 모델을 읽어서 예측. 사용자가 고른 작물의 병만 후보로 남기고 확률 계산, 상위 3개 반환 |
| `preprocess.py` | 사진을 AI가 읽기 좋게 변환(회전 보정, 색상, 크기). 학습할 때와 똑같은 규칙 사용 |
| `labels.py` | **17개 병 이름의 기준표**. DB·학습·결과가 모두 이 이름을 씀 |
| `schemas.py` | 서버가 주고받는 데이터의 형식 정의 |
| `config.py` | 설정값(모델 위치, 최대 사진 크기, 보안 토큰) 읽기 |

### training/ — AI 학습
| 파일 | 하는 일 |
| --- | --- |
| `train.py` | 모델 훈련 (2단계 전이학습). 결과는 `models/` 에 저장 |
| `evaluate.py` | 성적표 만들기: 정확도, 어떤 병을 헷갈리는지(혼동행렬), 확률 보정 |

### db/ — 병 정보 DB
| 파일 | 하는 일 |
| --- | --- |
| `schema.sql` | DB 표(테이블) 설계도: member, disease, diagnosis, diagnosis_candidate |
| `data.sql` | 병 17종의 기본 행을 넣는 SQL (설명은 "(작성 필요)"로 시작) |
| `labels_ko.py` | 병별 한글 이름, NCPMS 검색어, 정상 잎·해충용 고정 문구 |
| `ncpms_client.py` | NCPMS에 접속해서 병 검색·상세 정보를 받아오는 프로그램 |
| `seed_disease_texts.py` | 위 정보를 받아 DB의 설명·치료법 칸을 채우는 도구 (`search` / `fetch`) |
| `sickkey_map.json` | 병 이름 → NCPMS 병 번호(sickKey) 연결표. **사람이 확인해서 확정한 값** |
| `manual_texts.json` | NCPMS에 없어서 사람이 쓴 설명 초안 (검토 필요) |
| `check_labels.py` | 병 이름이 서로 일치하는지 대조하는 도구 |
| `backup/my_ncpms.sql` | 완성된 DB의 백업본 |

### scripts/ 와 tests/
| 파일 | 하는 일 |
| --- | --- |
| `scripts/backup_db.sh` | DB를 `.sql` 파일로 백업 |
| `scripts/restore_db.sh` | `.sql` 백업 파일을 DB로 복원 |
| `tests/` | 자동 테스트 (서버·모델·DB 도구가 정상인지 검사) |

### requirements 파일 (설치 목록)
| 파일 | 언제 필요한가 |
| --- | --- |
| `requirements.txt` | AI 서버를 실행할 때 (필수) |
| `requirements-train.txt` | 모델을 학습할 때 |
| `requirements-db.txt` | NCPMS 데이터를 받아 DB에 넣을 때 |
| `requirements-dev.txt` | 테스트까지 전부 돌릴 때 (위 3개 포함) |

---

## 5. 처음 시작하기 (받은 사람용)

준비물: Linux 또는 Windows의 WSL(Ubuntu), Python 3.12, MySQL 8.x

```bash
# ① 압축 풀고 폴더로 이동
tar xzf crop-ai-날짜.tar.gz
cd crop-ai

# ② 파이썬 가상환경 만들기 (이 프로젝트 전용 설치 공간)
python3 -m venv .venv
source .venv/bin/activate          # 켜지면 줄 앞에 (.venv) 가 보입니다

# ③ 필요한 프로그램 설치 (시간이 좀 걸립니다)
pip install -r requirements-dev.txt

# ④ 자동 테스트로 정상 설치 확인
pytest -q                          # "34 passed" 가 나오면 성공
```

가상환경은 터미널을 새로 열 때마다 `source .venv/bin/activate` 로 다시 켜야 합니다.

### 설정값 넣기
```bash
cp .env.example .env               # 샘플을 복사
nano .env                          # 본인 값 입력 후 저장 (Ctrl+O, Enter, Ctrl+X)
set -a; source .env; set +a        # 입력한 값을 현재 터미널에 적용
```
- `NCPMS_API_KEY`: NCPMS Open API 사이트에서 직접 신청해 발급 (이미 있는 DB를 복원만 한다면 필요 없음)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: 6번에서 만드는 값과 같게 입력

---

## 6. DB 복원하기 (병 정보가 담긴 my_ncpms 가져오기)

**① DB와 계정 만들기** (비밀번호는 원하는 값으로 바꾸세요)
```bash
sudo mysql -e "CREATE DATABASE my_ncpms CHARACTER SET utf8mb4;
CREATE USER 'ncpms'@'localhost' IDENTIFIED BY '여기에_비밀번호';
GRANT ALL ON my_ncpms.* TO 'ncpms'@'localhost'; FLUSH PRIVILEGES;"
```

**② 백업 파일 넣기**
```bash
export DB_USER=ncpms DB_NAME=my_ncpms
bash scripts/restore_db.sh          # 비밀번호를 물어봅니다
```

**③ 잘 들어갔는지 확인** — 아래 결과가 17이면 성공
```bash
mysql -u ncpms -p my_ncpms -e "SELECT COUNT(*) FROM disease;"
mysql -u ncpms -p my_ncpms -e "SELECT label, LEFT(description,30) FROM disease;"
```

**내 DB를 다시 백업하고 싶을 때**
```bash
DB_USER=ncpms DB_NAME=my_ncpms bash scripts/backup_db.sh          # 공유용 (회원 정보 제외)
DB_USER=ncpms DB_NAME=my_ncpms bash scripts/backup_db.sh --full   # 내 보관용 전체 (남에게 전달 금지)
```

### NCPMS에서 병 설명을 직접 다시 받아 채우기 (선택)
```bash
python -m db.seed_disease_texts fetch            # 받아서 db/out/disease_texts.json 에만 저장 (DB는 안 바뀜)
python -m db.seed_disease_texts fetch --apply    # 확인 후 DB에 반영 ("(작성 필요)" 인 행만)
python -m db.seed_disease_texts fetch --apply --force   # 이미 채운 행도 덮어쓰기
```
병 번호(sickKey)는 `db/sickkey_map.json` 에 이미 확정되어 있어 `search` 단계는 다시 안 해도 됩니다.

---

## 7. 라벨(병 이름) 대조 — 학습·연동 전에 꼭 하세요

팀 DB의 병 이름과 우리 이름이 한 글자라도 다르면 결과가 연결되지 않습니다.
(명세서에 병 이름 목록이 없어서, 우리 값은 PlantVillage 폴더명 기준으로 만든 것입니다.)

```bash
# 팀 data.sql 의 label 17개를 한 줄에 하나씩 적은 파일(l.txt)을 만들어 비교
python -m db.check_labels --labels-file l.txt

# 현재 MySQL 의 disease 표와 비교 (DB 환경변수 필요)
python -m db.check_labels

# 학습 데이터 폴더 이름과 비교
python -m db.check_labels --data-dir data/train
```
"일치"가 나오면 OK. 다르면 **팀 DB를 기준으로** `app/labels.py` 의 `CLASS_NAMES` 와 `db/labels_ko.py` 의 이름을 고칩니다.

---

## 8. AI 모델 학습 (훈련 사진을 구한 뒤)

```bash
# 사진 폴더 구조: data/train/병이름/사진.jpg, data/valid/병이름/사진.jpg
python -m training.train --train-dir data/train --val-dir data/valid     # 훈련 (오래 걸림)
python -m training.evaluate --data-dir data/valid --fit-temperature      # 확률 보정 + 성적표
python -m training.evaluate --data-dir data/real_photos --tag real       # 실제 사진 성적표
```
- 폴더 이름이 `labels.py` 와 다르면 `train.py` 가 어떤 폴더가 없는지 알려줍니다.
- `--val-dir` 을 빼면 같은 잎 사진이 훈련용·검증용에 섞여 **점수가 부풀려집니다.** 꼭 지정하세요.
- 훈련이 끝나면 `models/` 에 `crop_model.keras`, `class_names.json`, `model_meta.json` 이 생깁니다.

---

## 9. AI 서버 실행과 호출

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000     # models/ 에 학습 결과가 있어야 실행됨
```
외부에 포트를 열지 마세요. 백엔드(Spring)만 호출하도록 같은 컴퓨터/내부망에서만 사용합니다.

**서버 살아있는지 확인**
```bash
curl http://127.0.0.1:8000/health
```

**진단 요청 예시**
```bash
curl -X POST http://127.0.0.1:8000/predict -F "image=@잎사진.jpg" -F "crop=TOMATO"
```

**백엔드와 주고받는 형식** (백엔드 담당과 합의 필요)
```
요청:  POST /predict   (파일 전송 형식)
        image = 사진(jpg/png),  crop = TOMATO | POTATO | CORN
        헤더(선택) X-Internal-Token: .env 의 INTERNAL_TOKEN 과 같은 값
응답 200:
  { "model_version": "20261112-1224", "crop": "TOMATO",
    "predictions": [ {"rank":1, "label":"Tomato___Late_blight", "confidence":0.9123}, ... ] }   # 최대 3개
오류:  400 사진/요청 문제(한글 사유 포함)   401 토큰 불일치   413 사진 용량 초과   500 내부 오류
```
- 사용자가 고른 작물의 병만 후보로 남기고 확률을 다시 계산합니다.
- "확률 0.8 이상이면 1개만 보여주기 / 0.5 미만이면 진단 불확실" 같은 판단은 **백엔드가** 합니다. AI 서버는 항상 상위 3개를 돌려줍니다.

---

## 10. 알려진 한계·주의

- 아직 **실제 학습 모델이 없어서** 진단 정확도를 말할 수 없습니다.
- 훈련 데이터(PlantVillage)는 실험실 배경이라 **실제 밭 사진에서는 정확도가 낮을 수 있습니다.**
- NCPMS 검색 `startPoint` 옵션이 "페이지 번호"인지 "위치"인지 확인하지 못했습니다. (지금 결과 수가 적어 영향 없음)
- NCPMS에 호출 허용 도메인 제한(`ERR_105`)이 있습니다. 로컬에서는 통과했지만 **운영 서버에서는 다시 확인**하세요.
- DB 표 구조(`schema.sql`)는 명세서를 보고 재구성한 것입니다. 팀 Spring 프로젝트의 `schema.sql` 이 있으면 **그쪽이 기준**입니다.
- 병 설명은 공공데이터를 가공한 것이며 **참고용**입니다. 실제 방제 결정은 전문가·농업기술센터와 상의하세요.

## 자주 겪는 문제

| 증상 | 해결 |
| --- | --- |
| `Access denied for user 'ncpms'` | 비밀번호/계정 확인, 6번 ①을 다시 실행 |
| `ModuleNotFoundError` | `source .venv/bin/activate` 로 가상환경을 켰는지, `pip install -r requirements-dev.txt` 를 했는지 확인 |
| `mysqldump: command not found` | `sudo apt install mysql-client` |
| `ERR_xxx` (NCPMS 오류) | API 키 확인(`NCPMS_API_KEY`), 도메인/IP 허용 설정 확인 |
| 한글이 깨져 보임 | 복원 시 `--default-character-set=utf8mb4` 사용 (`restore_db.sh` 는 이미 적용됨) |
| uvicorn 실행 시 모델 오류 | `models/` 에 학습 결과가 있는지 확인 (아직 학습 전이면 정상) |
