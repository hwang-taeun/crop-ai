package com.taeun.crop.disease;

import com.taeun.crop.common.Crop;

/** 병 목록·진단 후보에 들어가는 짧은 형태 */
public record DiseaseSummary(Long id, String label, String nameKo, Crop crop, boolean healthy) {

    public static DiseaseSummary from(Disease d) {
        return new DiseaseSummary(d.getId(), d.getLabel(), d.getNameKo(), d.getCrop(), d.isHealthy());
    }
}
