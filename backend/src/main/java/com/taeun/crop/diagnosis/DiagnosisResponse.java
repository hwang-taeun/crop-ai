package com.taeun.crop.diagnosis;

import com.taeun.crop.common.Crop;
import java.util.List;

/** 진단 요청·상세 응답 (docs/api-spec.md 5.1) */
public record DiagnosisResponse(
        Long id,
        Crop crop,
        DiagnosisStatus status,
        String modelVersion,
        String createdAt,
        String imageUrl,
        String thumbnailUrl,
        List<CandidateResponse> candidates,
        Feedback feedback,
        String notice
) {
    public static final String NOTICE = "AI 진단은 참고용입니다. 정확한 진단은 지역 농업기술센터에 문의하세요.";
}
