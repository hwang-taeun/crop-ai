package com.taeun.crop.diagnosis;

/** 결과 판정 (DB에 저장하지 않고 조회할 때마다 계산) — docs/api-spec.md 3장 */
public enum DiagnosisStatus {
    HEALTHY, LIKELY, POSSIBLE, UNCERTAIN
}
