package com.taeun.crop.disease;

import com.taeun.crop.common.Crop;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DiseaseRepository extends JpaRepository<Disease, Long> {

    List<Disease> findAllByOrderByIdAsc();

    List<Disease> findAllByCropOrderByIdAsc(Crop crop);

    /** 진단 결과(AI 라벨) → 병 정보 조회에 사용 */
    Optional<Disease> findByLabel(String label);
}
