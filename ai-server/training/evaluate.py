"""평가 + 온도 보정.

  python -m training.evaluate --data-dir data/valid --fit-temperature   # 검증셋으로 온도 보정
  python -m training.evaluate --data-dir data/real_photos --tag real     # 실제 휴대폰 사진 테스트셋

서버와 같은 방식(정답 작물의 클래스만 남기고 softmax)으로 계산한 수치도 함께 보여준다.
일부 클래스만 있는 폴더(실사진 테스트셋)도 쓸 수 있다.
온도는 학습/검증 데이터로만 맞추고, 최종 성능은 따로 떼어 둔 테스트셋으로 본다.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from app.labels import CLASS_NAMES, allowed_matrix

NEG = -1e9


def masked(logits, y_true):
    return np.where(allowed_matrix()[y_true], logits, NEG)


def topk_acc(logits, y, k):
    top = np.argsort(-logits, axis=1)[:, :k]
    return float(np.mean([y[i] in top[i] for i in range(len(y))]))


def nll(logits, y, t):
    z = logits / t
    z = z - z.max(axis=1, keepdims=True)
    log_p = z - np.log(np.exp(z).sum(axis=1, keepdims=True))
    return float(-log_p[np.arange(len(y)), y].mean())


def fit_temperature(logits_masked, y):
    grid = np.linspace(0.5, 5.0, 91)
    return float(grid[int(np.argmin([nll(logits_masked, y, t) for t in grid]))])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--model-dir", default="models")
    ap.add_argument("--tag", default="val")
    ap.add_argument("--fit-temperature", action="store_true")
    a = ap.parse_args()

    from sklearn.metrics import classification_report, confusion_matrix
    from tensorflow import keras

    d = Path(a.model_dir)
    meta = json.loads((d / "model_meta.json").read_text(encoding="utf-8"))
    model = keras.models.load_model(d / "crop_model.keras", compile=False)
    size = meta.get("img_size", 224)

    root = Path(a.data_dir)
    present = [c for c in CLASS_NAMES if (root / c).is_dir()]
    if not present:
        raise SystemExit(f"{root} 에서 라벨 폴더를 찾지 못했습니다.")
    ds = keras.utils.image_dataset_from_directory(
        root, class_names=present, label_mode="int", image_size=(size, size), batch_size=32, shuffle=False
    )
    to_global = np.array([CLASS_NAMES.index(c) for c in present])
    logits, y = [], []
    for xb, yb in ds:
        logits.append(np.asarray(model(xb, training=False)))
        y.append(to_global[yb.numpy()])
    logits, y = np.concatenate(logits), np.concatenate(y)
    lm = masked(logits, y)

    print(f"\n샘플 {len(y)}장, 클래스 {len(present)}개  (tag={a.tag})")
    print(f"전체 17클래스 기준  top1 {topk_acc(logits, y, 1):.4f}  top3 {topk_acc(logits, y, 3):.4f}")
    print(f"작물 마스킹(서버 방식) top1 {topk_acc(lm, y, 1):.4f}  top3 {topk_acc(lm, y, 3):.4f}")
    pred = lm.argmax(axis=1)
    labels = sorted(set(y) | set(pred))
    print(classification_report(y, pred, labels=labels, target_names=[CLASS_NAMES[i] for i in labels], zero_division=0))
    cm = confusion_matrix(y, pred, labels=labels)
    csv = d / f"confusion_{a.tag}.csv"
    header = "," + ",".join(CLASS_NAMES[i] for i in labels)
    rows = [CLASS_NAMES[i] + "," + ",".join(map(str, r)) for i, r in zip(labels, cm)]
    csv.write_text("\n".join([header] + rows), encoding="utf-8")
    print("혼동행렬 저장:", csv)

    if a.fit_temperature:
        t = fit_temperature(lm, y)
        print(f"온도 보정: T={t:.2f}  (NLL {nll(lm, y, 1.0):.4f} → {nll(lm, y, t):.4f})")
        if t in (0.5, 5.0):
            print("[경고] 탐색 범위 끝값입니다. 모델이 덜 학습됐거나 검증셋이 너무 작을 수 있어요. 학습 후 다시 보정하세요.")
        meta["temperature"] = t
        (d / "model_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print("model_meta.json 에 temperature 저장")


if __name__ == "__main__":
    main()
