"""
PlantVillage(color) 원본에서 이 프로젝트의 17개 클래스만 골라 학습용·검증용으로 나눕니다.

사용 예 (ai-server 폴더에서):
    python -m training.split_plantvillage --src ~/pv/raw/color --out data --val-ratio 0.2

결과:
    data/train/<클래스명>/*.jpg
    data/valid/<클래스명>/*.jpg

주의: PlantVillage는 같은 잎을 여러 장 찍은 사진이 섞여 있어, 무작위로 나누면 검증 점수가
실제보다 높게 나올 수 있습니다. 실제 성능은 직접 찍은 사진(data/real_photos)으로 따로 평가하세요.
"""
import argparse
import random
import shutil
from pathlib import Path

from app.labels import CLASS_NAMES


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="PlantVillage-Dataset/raw/color 경로")
    ap.add_argument("--out", default="data", help="결과 폴더 (train/, valid/ 가 생김)")
    ap.add_argument("--val-ratio", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    src, out = Path(a.src).expanduser(), Path(a.out)
    missing = [c for c in CLASS_NAMES if not (src / c).is_dir()]
    if missing:
        print("원본에 없는 클래스 폴더:", *missing, sep="\n  ")
        return 1

    rng = random.Random(a.seed)
    total_train = total_valid = 0
    for c in CLASS_NAMES:
        files = sorted(p for p in (src / c).iterdir() if p.is_file())
        rng.shuffle(files)
        n_valid = int(len(files) * a.val_ratio)
        for i, f in enumerate(files):
            dst = out / ("valid" if i < n_valid else "train") / c
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst / f.name)
        print(f"{c}: train {len(files) - n_valid} / valid {n_valid}")
        total_train += len(files) - n_valid
        total_valid += n_valid
    print(f"합계: train {total_train} / valid {total_valid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
