"""전이학습(MobileNetV2) 학습 스크립트.

  python -m training.train --train-dir data/train --val-dir data/valid

- 폴더 구조: <dir>/<라벨폴더>/*.jpg  (app/labels.py 의 17개 폴더만 사용, 나머지 폴더는 무시)
- --val-dir 을 생략하면 train-dir 에서 20%를 떼어 검증용으로 쓴다.
  PlantVillage는 같은 잎 사진이 여러 장이라 이 경우 검증 정확도가 부풀려진다(데이터 누수).
- 증강·값 스케일링 층이 모델 안에 들어 있어서, 서버는 0~255 이미지를 그대로 넣으면 된다.
- 출력층은 softmax 없는 logits (온도 보정 때문).
"""
import argparse
import json
import time
from pathlib import Path

from app.labels import CLASS_NAMES

IMG_EXT = {".jpg", ".jpeg", ".png"}


def check_dirs(root: Path):
    missing = [c for c in CLASS_NAMES if not (root / c).is_dir()]
    if missing:
        found = sorted(p.name for p in root.iterdir() if p.is_dir())
        raise SystemExit(
            f"[오류] {root} 에 없는 라벨 폴더 {len(missing)}개:\n  " + "\n  ".join(missing)
            + f"\n실제 폴더({len(found)}개): {found[:10]}...\n"
            "폴더명이 다르면 app/labels.py 의 CLASS_NAMES 를 데이터셋에 맞게 고치세요."
        )


def class_weights(root: Path):
    counts = [sum(1 for p in (root / c).iterdir() if p.suffix.lower() in IMG_EXT) for c in CLASS_NAMES]
    total = sum(counts)
    return {i: total / (len(counts) * max(n, 1)) for i, n in enumerate(counts)}


def build_model(img_size: int, weights):
    from tensorflow import keras

    L = keras.layers
    inputs = keras.Input((img_size, img_size, 3))
    x = keras.Sequential(
        [
            L.RandomFlip("horizontal_and_vertical"),
            L.RandomRotation(0.1),
            L.RandomZoom(0.15),
            L.RandomContrast(0.2),
            L.RandomBrightness(0.2, value_range=(0, 255)),
        ],
        name="augment",  # 학습 때만 동작, 추론 때는 자동으로 꺼짐
    )(inputs)
    x = L.Rescaling(1 / 127.5, offset=-1, name="rescale")(x)  # 0~255 → -1~1 (MobileNetV2 규격)
    base = keras.applications.MobileNetV2(input_shape=(img_size, img_size, 3), include_top=False, weights=weights)
    base.trainable = False
    x = base(x, training=False)
    x = L.GlobalAveragePooling2D()(x)
    x = L.Dropout(0.3)(x)
    outputs = L.Dense(len(CLASS_NAMES), name="logits")(x)
    return keras.Model(inputs, outputs), base


def compile_model(model, lr):
    from tensorflow import keras

    model.compile(
        optimizer=keras.optimizers.Adam(lr),
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[
            keras.metrics.SparseCategoricalAccuracy(name="acc"),
            keras.metrics.SparseTopKCategoricalAccuracy(k=3, name="top3"),
        ],
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-dir", required=True)
    ap.add_argument("--val-dir")
    ap.add_argument("--out", default="models")
    ap.add_argument("--img-size", type=int, default=224)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--epochs-head", type=int, default=5)
    ap.add_argument("--epochs-ft", type=int, default=10)
    ap.add_argument("--weights", choices=["imagenet", "none"], default="imagenet")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    from tensorflow import keras
    import tensorflow as tf

    train_root = Path(a.train_dir)
    check_dirs(train_root)
    common = dict(class_names=CLASS_NAMES, label_mode="int", image_size=(a.img_size,) * 2, batch_size=a.batch)
    if a.val_dir:
        check_dirs(Path(a.val_dir))
        train_ds = keras.utils.image_dataset_from_directory(train_root, shuffle=True, seed=a.seed, **common)
        val_ds = keras.utils.image_dataset_from_directory(a.val_dir, shuffle=False, **common)
    else:
        print("[경고] --val-dir 없음: 무작위 분할이라 검증 정확도가 실제보다 높게 나올 수 있습니다.")
        kw = dict(validation_split=0.2, seed=a.seed, **common)
        train_ds = keras.utils.image_dataset_from_directory(train_root, subset="training", **kw)
        val_ds = keras.utils.image_dataset_from_directory(train_root, subset="validation", **kw)
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

    cw = class_weights(train_root)
    model, base = build_model(a.img_size, None if a.weights == "none" else "imagenet")
    stop = keras.callbacks.EarlyStopping(monitor="val_acc", patience=3, restore_best_weights=True)

    print("== 1단계: 분류층만 학습 ==")
    compile_model(model, 1e-3)
    model.fit(train_ds, validation_data=val_ds, epochs=a.epochs_head, class_weight=cw, callbacks=[stop], verbose=2)

    print("== 2단계: 상위 층 미세조정 ==")
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False
    for layer in base.layers:  # BatchNorm은 계속 고정
        if isinstance(layer, keras.layers.BatchNormalization):
            layer.trainable = False
    compile_model(model, 1e-5)
    model.fit(train_ds, validation_data=val_ds, epochs=a.epochs_ft, class_weight=cw, callbacks=[stop], verbose=2)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    model.save(out / "crop_model.keras")
    (out / "class_names.json").write_text(json.dumps(CLASS_NAMES, ensure_ascii=False, indent=2), encoding="utf-8")
    meta = {"version": time.strftime("%Y%m%d-%H%M"), "temperature": 1.0, "img_size": a.img_size}
    (out / "model_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("저장 완료:", out.resolve(), meta)


if __name__ == "__main__":
    main()
