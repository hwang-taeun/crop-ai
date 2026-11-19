package com.taeun.crop.disease;

import com.taeun.crop.common.Crop;

/** 병 상세 (설명·방제법 + 출처 표시) */
public record DiseaseDetail(
        Long id,
        String label,
        String nameKo,
        Crop crop,
        boolean healthy,
        String description,
        String treatment,
        String source,
        String notice
) {
    static final String SOURCE = "농촌진흥청 국가농작물병해충관리시스템(NCPMS)";
    static final String NOTICE = "약제는 사용 전 제품 라벨과 지역 농업기술센터에 확인하세요.";

    public static DiseaseDetail from(Disease d) {
        return new DiseaseDetail(d.getId(), d.getLabel(), d.getNameKo(), d.getCrop(), d.isHealthy(),
                d.getDescription(), d.getTreatment(), SOURCE, NOTICE);
    }
}
