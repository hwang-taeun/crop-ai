import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.labels import CLASS_NAMES
from app.main import create_app
from app.predictor import Predictor


class FakeModel:
    def __call__(self, x, training=False):
        logits = np.zeros((1, 17), dtype=np.float32)
        logits[0, CLASS_NAMES.index("Tomato___Late_blight")] = 5
        logits[0, CLASS_NAMES.index("Potato___Late_blight")] = 4
        return logits


def _img(fmt="JPEG", size=(300, 200)):
    buf = io.BytesIO()
    Image.new("RGB", size, (30, 120, 40)).save(buf, fmt)
    return buf.getvalue()


def _client():
    return TestClient(create_app(Predictor(FakeModel(), CLASS_NAMES, 1.0, "test-1", 64)))


def test_predict_ok():
    with _client() as c:
        r = c.post("/predict", files={"image": ("a.jpg", _img(), "image/jpeg")}, data={"crop": "TOMATO"})
        assert r.status_code == 200
        body = r.json()
        assert body["model_version"] == "test-1" and body["crop"] == "TOMATO"
        assert body["predictions"][0]["label"] == "Tomato___Late_blight"
        assert len(body["predictions"]) == 3


def test_crop_changes_result():
    with _client() as c:
        r = c.post("/predict", files={"image": ("a.png", _img("PNG"), "image/png")}, data={"crop": "POTATO"})
        assert r.json()["predictions"][0]["label"] == "Potato___Late_blight"


def test_bad_image_400():
    with _client() as c:
        r = c.post("/predict", files={"image": ("a.jpg", b"not an image", "image/jpeg")}, data={"crop": "TOMATO"})
        assert r.status_code == 400 and "detail" in r.json()


def test_gif_rejected_400():
    with _client() as c:
        r = c.post("/predict", files={"image": ("a.gif", _img("GIF"), "image/gif")}, data={"crop": "TOMATO"})
        assert r.status_code == 400


def test_invalid_crop_400():
    with _client() as c:
        r = c.post("/predict", files={"image": ("a.jpg", _img(), "image/jpeg")}, data={"crop": "RICE"})
        assert r.status_code == 400


def test_health():
    with _client() as c:
        assert c.get("/health").json() == {"status": "ok", "model_version": "test-1", "classes": 17}


def test_internal_token(monkeypatch):
    monkeypatch.setenv("INTERNAL_TOKEN", "secret")
    with _client() as c:
        f = {"image": ("a.jpg", _img(), "image/jpeg")}
        assert c.post("/predict", files=f, data={"crop": "TOMATO"}).status_code == 401
        assert c.post("/predict", files=f, data={"crop": "TOMATO"}, headers={"X-Internal-Token": "secret"}).status_code == 200
