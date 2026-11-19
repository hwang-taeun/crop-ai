package com.taeun.crop.disease;

import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.Crop;
import com.taeun.crop.common.ErrorCode;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class DiseaseService {

    private final DiseaseRepository repository;

    public DiseaseService(DiseaseRepository repository) {
        this.repository = repository;
    }

    public List<DiseaseSummary> list(Crop crop) {
        List<Disease> diseases = (crop == null)
                ? repository.findAllByOrderByIdAsc()
                : repository.findAllByCropOrderByIdAsc(crop);
        return diseases.stream().map(DiseaseSummary::from).toList();
    }

    public DiseaseDetail get(Long id) {
        return repository.findById(id)
                .map(DiseaseDetail::from)
                .orElseThrow(() -> new ApiException(ErrorCode.NOT_FOUND, "병 정보를 찾을 수 없습니다: " + id));
    }
}
