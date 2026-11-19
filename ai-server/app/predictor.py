"""모델 로딩 + 추론. 순수 numpy 로직(rank_candidates)은 TensorFlow 없이 테스트 가능."""
import json
import threading
from pathlib import Path

import numpy as np

from .labels import CLASS_NAMES, CROP_PREFIX


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def rank_candidates(logits, class_names, crop: str, temperature: float = 1.0, top_k: int = 3):
    """선택한 작물의 클래스만 남기고 확률을 다시 계산한 뒤 상위 top_k를 돌려준다."""
    prefix = CROP_PREFIX[crop]
    idx = [i for i, name in enumerate(class_names) if name.startswith(prefix)]
    probs = softmax(np.asarray(logits, dtype=np.float64)[idx] / temperature)
    order = np.argsort(-probs)[:top_k]
    return [
        {"rank": r + 1, "label": class_names[idx[j]], "confidence": round(float(probs[j]), 4)}
        for r, j in enumerate(order)
    ]


class Predictor:
    def __init__(self, model, class_names, temperature=1.0, version="dev", img_size=224):
        if set(class_names) != set(CLASS_NAMES):
            raise ValueError("class_names.json 이 app/labels.py 의 17개 라벨과 다릅니다.")
        self.model = model
        self.class_names = list(class_names)
        self.temperature = float(temperature)
        self.version = version
        self.img_size = int(img_size)
        self._lock = threading.Lock()

    @classmethod
    def load(cls, settings) -> "Predictor":
        import tensorflow as tf  # 서버 시작 때만 import

        d = Path(settings.model_dir)
        model = tf.keras.models.load_model(d / "crop_model.keras", compile=False)
        names = json.loads((d / "class_names.json").read_text(encoding="utf-8"))
        meta = json.loads((d / "model_meta.json").read_text(encoding="utf-8"))
        p = cls(model, names, meta.get("temperature", 1.0), meta.get("version", "unknown"), meta.get("img_size", 224))
        p.predict(np.zeros((p.img_size, p.img_size, 3), dtype=np.float32), "TOMATO")  # 워밍업
        return p

    def predict(self, image: np.ndarray, crop: str):
        with self._lock:
            logits = np.asarray(self.model(image[None], training=False))[0]
        return rank_candidates(logits, self.class_names, crop, self.temperature)
