package com.taeun.crop.diagnosis;

import java.math.BigDecimal;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 1순위 확률로 결과 판정 (docs/api-spec.md 3장).
 * 기준값은 application.properties 의 app.diagnosis.* 로 조정.
 */
@Component
public class DiagnosisPolicy {

    private final BigDecimal likely;
    private final BigDecimal uncertain;

    public DiagnosisPolicy(@Value("${app.diagnosis.likely-threshold}") BigDecimal likely,
                           @Value("${app.diagnosis.uncertain-threshold}") BigDecimal uncertain) {
        this.likely = likely;
        this.uncertain = uncertain;
    }

    public DiagnosisStatus decide(List<DiagnosisCandidate> candidates) {
        if (candidates.isEmpty()) {
            return DiagnosisStatus.UNCERTAIN;
        }
        DiagnosisCandidate top = candidates.get(0);
        BigDecimal c = top.getConfidence();
        if (c.compareTo(likely) >= 0) {
            return top.getDisease().isHealthy() ? DiagnosisStatus.HEALTHY : DiagnosisStatus.LIKELY;
        }
        if (c.compareTo(uncertain) >= 0) {
            return DiagnosisStatus.POSSIBLE;
        }
        return DiagnosisStatus.UNCERTAIN;
    }
}
