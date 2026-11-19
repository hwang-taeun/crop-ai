package com.taeun.crop.diagnosis;

import com.taeun.crop.ai.AiClient;
import com.taeun.crop.ai.AiPrediction;
import com.taeun.crop.ai.AiPredictResponse;
import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.Crop;
import com.taeun.crop.common.ErrorCode;
import com.taeun.crop.common.PageResponse;
import com.taeun.crop.common.Times;
import com.taeun.crop.disease.Disease;
import com.taeun.crop.disease.DiseaseRepository;
import com.taeun.crop.member.MemberRepository;
import com.taeun.crop.storage.ImageStorage;
import com.taeun.crop.storage.ImageType;
import com.taeun.crop.storage.StoredImage;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import javax.imageio.ImageIO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.web.multipart.MultipartFile;

@Service
public class DiagnosisService {

    private static final Logger log = LoggerFactory.getLogger(DiagnosisService.class);
    private static final int MAX_PAGE_SIZE = 50;

    private final DiagnosisRepository diagnoses;
    private final DiseaseRepository diseases;
    private final MemberRepository members;
    private final ImageStorage storage;
    private final AiClient ai;
    private final DiagnosisPolicy policy;
    private final TransactionTemplate tx;
    private final long maxUploadBytes;

    public DiagnosisService(DiagnosisRepository diagnoses, DiseaseRepository diseases, MemberRepository members,
                            ImageStorage storage, AiClient ai, DiagnosisPolicy policy, TransactionTemplate tx,
                            @Value("${app.diagnosis.max-upload-mb}") long maxUploadMb) {
        this.diagnoses = diagnoses;
        this.diseases = diseases;
        this.members = members;
        this.storage = storage;
        this.ai = ai;
        this.policy = policy;
        this.tx = tx;
        this.maxUploadBytes = maxUploadMb * 1024 * 1024;
    }

    /**
     * 진단 요청 (docs/api-spec.md 5.1 처리 순서)
     * 파일 검사 → 사진 저장 → AI 호출(트랜잭션 밖) → DB 저장(트랜잭션) → 응답.
     * 중간에 실패하면 저장한 사진을 지움.
     */
    public DiagnosisResponse create(Long memberId, MultipartFile file, Crop crop) {
        byte[] bytes = readFile(file);
        ImageType type = ImageType.detect(bytes)
                .orElseThrow(() -> new ApiException(ErrorCode.INVALID_IMAGE));
        BufferedImage image = decode(bytes);

        StoredImage stored = storage.store(bytes, type, image);
        try {
            AiPredictResponse result = ai.predict(bytes, type, crop);
            return tx.execute(status -> {
                Diagnosis d = new Diagnosis(members.getReferenceById(memberId), crop,
                        stored.originalKey(), stored.thumbnailKey(), Times.now());
                for (AiPrediction p : result.predictions()) {
                    Disease disease = diseases.findByLabel(p.label()).orElseThrow(() -> {
                        log.error("AI 라벨이 DB에 없음 (라벨 불일치): {}", p.label());
                        return new ApiException(ErrorCode.INTERNAL_ERROR);
                    });
                    d.addCandidate(disease, p.rank(), toConfidence(p.confidence()));
                }
                diagnoses.save(d);
                return toResponse(d, result.model_version());
            });
        } catch (RuntimeException e) {
            storage.deleteQuietly(stored.originalKey(), stored.thumbnailKey());
            throw e;
        }
    }

    @Transactional(readOnly = true)
    public PageResponse<DiagnosisListItem> list(Long memberId, Crop crop, int page, int size) {
        if (page < 0 || size < 1 || size > MAX_PAGE_SIZE) {
            throw new ApiException(ErrorCode.INVALID_REQUEST, "page는 0 이상, size는 1~" + MAX_PAGE_SIZE + " 사이여야 합니다.");
        }
        PageRequest pageable = PageRequest.of(page, size,
                Sort.by(Sort.Order.desc("createdAt"), Sort.Order.desc("id")));
        Page<Diagnosis> result = (crop == null)
                ? diagnoses.findByMember_Id(memberId, pageable)
                : diagnoses.findByMember_IdAndCrop(memberId, crop, pageable);
        List<DiagnosisListItem> items = result.getContent().stream().map(this::toListItem).toList();
        return PageResponse.of(result, items);
    }

    @Transactional(readOnly = true)
    public DiagnosisResponse get(Long memberId, Long id) {
        return toResponse(findOwned(memberId, id), null);
    }

    @Transactional(readOnly = true)
    public ImageFile image(Long memberId, Long id, boolean thumbnail) {
        Diagnosis d = findOwned(memberId, id);
        String key = thumbnail ? d.getThumbnailKey() : d.getImageKey();
        return new ImageFile(storage.load(key), ImageType.mediaTypeOfKey(key));
    }

    @Transactional
    public FeedbackResponse feedback(Long memberId, Long id, Feedback feedback) {
        Diagnosis d = findOwned(memberId, id);
        d.giveFeedback(feedback, Times.now());
        return new FeedbackResponse(d.getId(), d.getFeedback(), Times.format(d.getFeedbackAt()));
    }

    /** DB에서 지운 뒤(커밋 후) 사진 파일 삭제 */
    public void delete(Long memberId, Long id) {
        StoredImage keys = tx.execute(status -> {
            Diagnosis d = findOwned(memberId, id);
            StoredImage k = new StoredImage(d.getImageKey(), d.getThumbnailKey());
            diagnoses.delete(d);
            return k;
        });
        storage.deleteQuietly(keys.originalKey(), keys.thumbnailKey());
    }

    // ── 내부 ──

    private Diagnosis findOwned(Long memberId, Long id) {
        Diagnosis d = diagnoses.findById(id)
                .orElseThrow(() -> new ApiException(ErrorCode.NOT_FOUND, "진단 기록을 찾을 수 없습니다: " + id));
        if (!d.isOwnedBy(memberId)) {
            throw new ApiException(ErrorCode.FORBIDDEN);
        }
        return d;
    }

    private byte[] readFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new ApiException(ErrorCode.INVALID_IMAGE, "사진 파일이 비어 있습니다.");
        }
        if (file.getSize() > maxUploadBytes) {
            throw new ApiException(ErrorCode.IMAGE_TOO_LARGE);
        }
        try {
            return file.getBytes();
        } catch (IOException e) {
            throw new ApiException(ErrorCode.INVALID_IMAGE);
        }
    }

    private static BufferedImage decode(byte[] bytes) {
        try {
            BufferedImage img = ImageIO.read(new ByteArrayInputStream(bytes));
            if (img == null) {
                throw new ApiException(ErrorCode.INVALID_IMAGE, "사진을 읽을 수 없습니다.");
            }
            return img;
        } catch (IOException e) {
            throw new ApiException(ErrorCode.INVALID_IMAGE, "사진을 읽을 수 없습니다.");
        }
    }

    private static BigDecimal toConfidence(double v) {
        return BigDecimal.valueOf(v).setScale(4, RoundingMode.HALF_UP);
    }

    private DiagnosisResponse toResponse(Diagnosis d, String modelVersion) {
        List<CandidateResponse> candidates = d.getCandidates().stream().map(CandidateResponse::from).toList();
        return new DiagnosisResponse(
                d.getId(), d.getCrop(), policy.decide(d.getCandidates()), modelVersion,
                Times.format(d.getCreatedAt()),
                imageUrl(d.getId()), thumbnailUrl(d.getId()),
                candidates, d.getFeedback(), DiagnosisResponse.NOTICE);
    }

    private DiagnosisListItem toListItem(Diagnosis d) {
        CandidateResponse top = d.getCandidates().isEmpty() ? null : CandidateResponse.from(d.getCandidates().get(0));
        return new DiagnosisListItem(d.getId(), d.getCrop(), policy.decide(d.getCandidates()), top,
                thumbnailUrl(d.getId()), d.getFeedback(), Times.format(d.getCreatedAt()));
    }

    private static String imageUrl(Long id) {
        return "/api/v1/diagnoses/" + id + "/image";
    }

    private static String thumbnailUrl(Long id) {
        return "/api/v1/diagnoses/" + id + "/thumbnail";
    }
}
