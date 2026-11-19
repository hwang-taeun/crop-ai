package com.taeun.crop.diagnosis;

import com.taeun.crop.common.Crop;

/** 진단 기록 목록의 한 줄 (docs/api-spec.md 5.2) */
public record DiagnosisListItem(
        Long id,
        Crop crop,
        DiagnosisStatus status,
        CandidateResponse topCandidate,
        String thumbnailUrl,
        Feedback feedback,
        String createdAt
) {
}
