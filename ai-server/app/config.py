import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model_dir: str
    max_upload_mb: int
    internal_token: str  # 비어 있으면 토큰 검사 안 함

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model_dir=os.getenv("MODEL_DIR", "models"),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "10")),
            internal_token=os.getenv("INTERNAL_TOKEN", ""),
        )
