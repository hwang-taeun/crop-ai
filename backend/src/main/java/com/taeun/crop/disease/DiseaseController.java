package com.taeun.crop.disease;

import com.taeun.crop.common.Crop;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** docs/api-spec.md 6장 — 로그인 없이 호출 가능 */
@RestController
@RequestMapping("/api/v1/diseases")
public class DiseaseController {

    private final DiseaseService service;

    public DiseaseController(DiseaseService service) {
        this.service = service;
    }

    /** GET /api/v1/diseases?crop=TOMATO (crop 생략 시 전체 17개) */
    @GetMapping
    public List<DiseaseSummary> list(@RequestParam(required = false) Crop crop) {
        return service.list(crop);
    }

    /** GET /api/v1/diseases/{id} */
    @GetMapping("/{id}")
    public DiseaseDetail get(@PathVariable Long id) {
        return service.get(id);
    }
}
