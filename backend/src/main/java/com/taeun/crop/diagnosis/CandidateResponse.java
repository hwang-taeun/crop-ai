package com.taeun.crop.diagnosis;

import com.taeun.crop.disease.DiseaseSummary;
import java.math.BigDecimal;

public record CandidateResponse(int rank, BigDecimal confidence, DiseaseSummary disease) {

    public static CandidateResponse from(DiagnosisCandidate c) {
        return new CandidateResponse(c.getRanking(), c.getConfidence(), DiseaseSummary.from(c.getDisease()));
    }
}
