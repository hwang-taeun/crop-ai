import numpy as np

from app.labels import CLASS_NAMES, CROP_PREFIX, allowed_matrix, crop_of
from app.predictor import rank_candidates


def test_labels_17_and_crops():
    assert len(CLASS_NAMES) == 17 and len(set(CLASS_NAMES)) == 17
    assert {crop_of(c) for c in CLASS_NAMES} == set(CROP_PREFIX)


def test_crop_mask_only_returns_selected_crop():
    rng = np.random.default_rng(0)
    logits = rng.normal(size=17)
    # 토마토 클래스에 큰 점수를 줘도 감자를 고르면 감자 라벨만 나와야 한다
    logits[[i for i, c in enumerate(CLASS_NAMES) if c.startswith("Tomato")]] += 10
    out = rank_candidates(logits, CLASS_NAMES, "POTATO")
    assert len(out) == 3 and all(o["label"].startswith("Potato___") for o in out)
    assert abs(sum(o["confidence"] for o in out) - 1.0) < 1e-3  # 감자 클래스는 3개뿐
    assert [o["rank"] for o in out] == [1, 2, 3]


def test_corn_has_four_classes_top3():
    out = rank_candidates(np.zeros(17), CLASS_NAMES, "CORN")
    assert len(out) == 3 and all(o["label"].startswith("Corn_") for o in out)


def test_temperature_flattens_confidence():
    logits = np.zeros(17)
    idx = CLASS_NAMES.index("Tomato___Late_blight")
    logits[idx] = 8
    hot = rank_candidates(logits, CLASS_NAMES, "TOMATO", temperature=1.0)[0]["confidence"]
    cool = rank_candidates(logits, CLASS_NAMES, "TOMATO", temperature=3.0)[0]["confidence"]
    assert rank_candidates(logits, CLASS_NAMES, "TOMATO")[0]["label"] == "Tomato___Late_blight"
    assert cool < hot


def test_allowed_matrix_shape():
    m = allowed_matrix()
    assert m.shape == (17, 17) and m.diagonal().all()
