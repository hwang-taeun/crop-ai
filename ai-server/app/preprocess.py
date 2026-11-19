"""업로드 이미지 → 모델 입력. 학습 때(224x224 리사이즈, 0~255 값)와 같은 규칙이어야 한다.
값 스케일링(-1~1)은 모델 안의 Rescaling 층이 하므로 여기서는 0~255 그대로 둔다."""
import io

import numpy as np
from PIL import Image, ImageOps

ALLOWED_FORMATS = {"JPEG", "PNG"}


class InvalidImage(ValueError):
    pass


def load_image(data: bytes, size: int) -> np.ndarray:
    try:
        Image.open(io.BytesIO(data)).verify()  # 깨진 파일 검사
        img = Image.open(io.BytesIO(data))     # verify 후에는 다시 열어야 함
        fmt = img.format
        if fmt not in ALLOWED_FORMATS:
            raise InvalidImage("jpg/png 사진만 올릴 수 있습니다.")
        img = ImageOps.exif_transpose(img)     # 휴대폰 사진 회전 보정
        img = img.convert("RGB").resize((size, size), Image.BILINEAR)
    except InvalidImage:
        raise
    except Exception as e:  # PIL 예외 종류가 많아 한꺼번에 처리
        raise InvalidImage("열 수 없는 이미지 파일입니다.") from e
    return np.asarray(img, dtype=np.float32)  # (size, size, 3), 0~255
