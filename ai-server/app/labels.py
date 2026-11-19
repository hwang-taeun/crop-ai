"""라벨 단일 출처.

DB disease.label · FastAPI 응답 label · 학습 클래스명이 이 17개와 글자 하나까지 같아야 한다.
(PlantVillage 폴더명 기준. 데이터셋 버전에 따라 폴더명이 다르면 여기만 고치면 된다.)
"""

CROP_PREFIX = {
    "TOMATO": "Tomato___",
    "POTATO": "Potato___",
    "CORN": "Corn_(maize)___",
}

CLASS_NAMES = sorted([
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
])


def crop_of(label: str) -> str:
    for crop, prefix in CROP_PREFIX.items():
        if label.startswith(prefix):
            return crop
    raise ValueError(f"알 수 없는 라벨: {label}")


def allowed_matrix(class_names=CLASS_NAMES):
    """[i, j] = i번 클래스와 j번 클래스가 같은 작물이면 True (작물 마스킹용)."""
    import numpy as np  # 서버/학습에서만 필요. DB 작업 환경에는 numpy 가 없어도 이 모듈을 불러올 수 있게 여기서 import
    crops = [crop_of(c) for c in class_names]
    return np.array([[a == b for b in crops] for a in crops])
