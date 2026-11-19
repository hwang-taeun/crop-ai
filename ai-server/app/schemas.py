from enum import Enum

from pydantic import BaseModel


class Crop(str, Enum):
    TOMATO = "TOMATO"
    POTATO = "POTATO"
    CORN = "CORN"


class Prediction(BaseModel):
    rank: int
    label: str
    confidence: float  # 0~1


class PredictResponse(BaseModel):
    model_version: str
    crop: Crop
    predictions: list[Prediction]  # 신뢰도 내림차순, 최대 3개


class HealthResponse(BaseModel):
    status: str
    model_version: str
    classes: int
