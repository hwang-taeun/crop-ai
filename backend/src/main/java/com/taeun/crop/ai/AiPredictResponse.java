package com.taeun.crop.ai;

import java.util.List;

/** AI 서버 POST /predict 응답 (필드 이름을 AI 서버의 snake_case 그대로 맞춤) */
public record AiPredictResponse(String model_version, String crop, List<AiPrediction> predictions) {
}
