-- crop-ai DB 스키마 (docs/api-spec.md v1.1 기준). 2026-11-18: member 를 자체 로그인 구조로 변경.
CREATE TABLE IF NOT EXISTS member (
  id                 BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  login_id           VARCHAR(30)  NULL UNIQUE,
  password_hash      VARCHAR(100) NULL,           -- BCrypt 해시
  failed_login_count INT          NOT NULL DEFAULT 0,
  locked_until       DATETIME(6)  NULL,           -- 로그인 연속 실패 시 잠금 해제 시각
  google_sub         VARCHAR(255) NULL UNIQUE,     -- (사용 안 함) Google 로그인용으로 남겨 둔 컬럼
  email              VARCHAR(255) NULL,
  nickname           VARCHAR(50)  NOT NULL,
  region             VARCHAR(20)  NULL,
  role               ENUM('USER','ADMIN') NOT NULL DEFAULT 'USER',
  created_at         DATETIME(6)  NOT NULL,
  updated_at         DATETIME(6)  NOT NULL,
  UNIQUE KEY uq_member_nickname (nickname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS disease (
  id          BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  label       VARCHAR(100) NOT NULL UNIQUE,
  crop        ENUM('TOMATO','POTATO','CORN') NOT NULL,
  name_ko     VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  treatment   TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS diagnosis (
  id            BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  member_id     BIGINT NOT NULL,
  crop          ENUM('TOMATO','POTATO','CORN') NOT NULL,
  image_key     VARCHAR(255) NOT NULL,
  thumbnail_key VARCHAR(255) NOT NULL,
  feedback      ENUM('CORRECT','INCORRECT') NULL,
  feedback_at   DATETIME(6) NULL,
  created_at    DATETIME(6) NOT NULL,
  CONSTRAINT fk_diagnosis_member FOREIGN KEY (member_id) REFERENCES member(id),
  INDEX idx_member_created (member_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS diagnosis_candidate (
  id           BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  diagnosis_id BIGINT NOT NULL,
  disease_id   BIGINT NOT NULL,
  ranking      INT NOT NULL,
  confidence   DECIMAL(5,4) NOT NULL,
  CONSTRAINT fk_candidate_diagnosis FOREIGN KEY (diagnosis_id) REFERENCES diagnosis(id),
  CONSTRAINT fk_candidate_disease   FOREIGN KEY (disease_id)   REFERENCES disease(id),
  UNIQUE KEY uq_diagnosis_ranking (diagnosis_id, ranking)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
