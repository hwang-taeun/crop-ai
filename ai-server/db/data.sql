-- 17개 병명 행. db/labels_ko.py 에서 만든 값이다. 이미 있는 행은 덮어쓰지 않는다(INSERT IGNORE).
-- description/treatment 는 `python -m db.seed_disease_texts fetch --apply` 로 NCPMS 내용으로 채운다.
INSERT IGNORE INTO disease (label, crop, name_ko, description, treatment) VALUES
  ('Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'CORN', '옥수수 잿빛무늬병', '(작성 필요)', '(작성 필요)'),
  ('Corn_(maize)___Common_rust_', 'CORN', '옥수수 녹병', '(작성 필요)', '(작성 필요)'),
  ('Corn_(maize)___Northern_Leaf_Blight', 'CORN', '옥수수 그을음무늬병', '(작성 필요)', '(작성 필요)'),
  ('Corn_(maize)___healthy', 'CORN', '옥수수 정상', '(작성 필요)', '(작성 필요)'),
  ('Potato___Early_blight', 'POTATO', '감자 겹둥근무늬병', '(작성 필요)', '(작성 필요)'),
  ('Potato___Late_blight', 'POTATO', '감자 역병', '(작성 필요)', '(작성 필요)'),
  ('Potato___healthy', 'POTATO', '감자 정상', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Bacterial_spot', 'TOMATO', '토마토 세균점무늬병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Early_blight', 'TOMATO', '토마토 겹둥근무늬병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Late_blight', 'TOMATO', '토마토 역병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Leaf_Mold', 'TOMATO', '토마토 잎곰팡이병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Septoria_leaf_spot', 'TOMATO', '토마토 흰무늬병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Spider_mites Two-spotted_spider_mite', 'TOMATO', '토마토 점박이응애', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Target_Spot', 'TOMATO', '토마토 갈색무늬병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'TOMATO', '토마토 황화잎말림바이러스병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___Tomato_mosaic_virus', 'TOMATO', '토마토 모자이크바이러스병', '(작성 필요)', '(작성 필요)'),
  ('Tomato___healthy', 'TOMATO', '토마토 정상', '(작성 필요)', '(작성 필요)');
