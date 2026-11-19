"""FastAPI 추론 서버. Spring Boot가 호출한다 (외부에 포트를 열지 않는다).

POST /predict  multipart: image(파일), crop(TOMATO|POTATO|CORN)
GET  /health
"""
import hmac
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import Settings
from .predictor import Predictor
from .preprocess import InvalidImage, load_image
from .schemas import Crop, HealthResponse, PredictResponse

log = logging.getLogger("crop-ai")


def create_app(predictor: Predictor | None = None) -> FastAPI:
    settings = Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.predictor = predictor or Predictor.load(settings)
        yield

    app = FastAPI(title="Crop Disease Inference", lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def _bad_request(_, exc):
        return JSONResponse(
            status_code=400,
            content={"detail": "요청 형식이 올바르지 않습니다. image(파일)와 crop(TOMATO|POTATO|CORN)이 필요합니다."},
        )

    def _check_token(token: str | None):
        if settings.internal_token and not hmac.compare_digest(
            (token or "").encode(), settings.internal_token.encode()
        ):
            raise HTTPException(status_code=401, detail="인증 실패")

    @app.get("/health", response_model=HealthResponse)
    def health():
        p = app.state.predictor
        return HealthResponse(status="ok", model_version=p.version, classes=len(p.class_names))

    @app.post("/predict", response_model=PredictResponse)
    def predict(
        image: UploadFile = File(...),
        crop: Crop = Form(...),
        x_internal_token: str | None = Header(default=None),
    ):
        _check_token(x_internal_token)
        p = app.state.predictor
        limit = settings.max_upload_mb * 1024 * 1024
        data = image.file.read(limit + 1)
        if len(data) > limit:
            raise HTTPException(status_code=413, detail=f"사진은 {settings.max_upload_mb}MB 이하만 가능합니다.")
        try:
            arr = load_image(data, p.img_size)
        except InvalidImage as e:
            raise HTTPException(status_code=400, detail=str(e))
        try:
            preds = p.predict(arr, crop.value)
        except Exception:
            log.exception("추론 실패")
            raise HTTPException(status_code=500, detail="추론 중 오류가 발생했습니다.")
        return PredictResponse(model_version=p.version, crop=crop, predictions=preds)

    return app


app = create_app()
