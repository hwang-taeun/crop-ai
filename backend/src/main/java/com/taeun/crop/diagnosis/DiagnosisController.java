package com.taeun.crop.diagnosis;

import com.taeun.crop.auth.CurrentMember;
import com.taeun.crop.common.Crop;
import com.taeun.crop.common.PageResponse;
import jakarta.validation.Valid;
import org.springframework.core.io.Resource;
import org.springframework.http.CacheControl;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.time.Duration;

/** docs/api-spec.md 5장 — 진단 API */
@RestController
@RequestMapping("/api/v1/diagnoses")
public class DiagnosisController {

    private final DiagnosisService service;
    private final CurrentMember currentMember;

    public DiagnosisController(DiagnosisService service, CurrentMember currentMember) {
        this.service = service;
        this.currentMember = currentMember;
    }

    /** 5.1 진단 요청 (multipart: image, crop) */
    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    public DiagnosisResponse create(@RequestParam("image") MultipartFile image,
                                    @RequestParam("crop") Crop crop) {
        return service.create(currentMember.id(), image, crop);
    }

    /** 5.2 내 진단 기록 목록 */
    @GetMapping
    public PageResponse<DiagnosisListItem> list(@RequestParam(defaultValue = "0") int page,
                                                @RequestParam(defaultValue = "20") int size,
                                                @RequestParam(required = false) Crop crop) {
        return service.list(currentMember.id(), crop, page, size);
    }

    /** 5.3 진단 상세 */
    @GetMapping("/{id}")
    public DiagnosisResponse get(@PathVariable Long id) {
        return service.get(currentMember.id(), id);
    }

    /** 5.4 원본 사진 */
    @GetMapping("/{id}/image")
    public ResponseEntity<Resource> image(@PathVariable Long id) {
        return imageResponse(service.image(currentMember.id(), id, false));
    }

    /** 5.4 썸네일 */
    @GetMapping("/{id}/thumbnail")
    public ResponseEntity<Resource> thumbnail(@PathVariable Long id) {
        return imageResponse(service.image(currentMember.id(), id, true));
    }

    /** 5.5 결과 피드백 */
    @PutMapping("/{id}/feedback")
    public FeedbackResponse feedback(@PathVariable Long id, @Valid @RequestBody FeedbackRequest request) {
        return service.feedback(currentMember.id(), id, request.feedback());
    }

    /** 5.6 진단 기록 삭제 */
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        service.delete(currentMember.id(), id);
    }

    private static ResponseEntity<Resource> imageResponse(ImageFile f) {
        return ResponseEntity.ok()
                .contentType(f.mediaType())
                .cacheControl(CacheControl.maxAge(Duration.ofHours(1)).cachePrivate())
                .body(f.resource());
    }
}
