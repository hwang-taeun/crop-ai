package com.taeun.crop.diagnosis;

import com.taeun.crop.common.Crop;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DiagnosisRepository extends JpaRepository<Diagnosis, Long> {

    Page<Diagnosis> findByMember_Id(Long memberId, Pageable pageable);

    Page<Diagnosis> findByMember_IdAndCrop(Long memberId, Crop crop, Pageable pageable);

    /** 회원 탈퇴 시 전체 삭제용 */
    List<Diagnosis> findAllByMember_Id(Long memberId);
}
