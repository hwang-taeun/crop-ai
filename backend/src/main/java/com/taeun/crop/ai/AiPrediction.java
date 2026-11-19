package com.taeun.crop.ai;

/** AI 서버 응답의 후보 1개 */
public record AiPrediction(int rank, String label, double confidence) {
}
