package com.taeun.crop.diagnosis;

import com.taeun.crop.common.Crop;
import com.taeun.crop.disease.Disease;
import com.taeun.crop.member.Member;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OrderBy;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/** my_ncpms.diagnosis — 진단 1건 (사진 + 작물 + 후보 3개 + 피드백) */
@Entity
@Table(name = "diagnosis")
public class Diagnosis {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Crop crop;

    @Column(name = "image_key", nullable = false)
    private String imageKey;

    @Column(name = "thumbnail_key", nullable = false)
    private String thumbnailKey;

    @Enumerated(EnumType.STRING)
    private Feedback feedback;

    @Column(name = "feedback_at")
    private LocalDateTime feedbackAt;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "diagnosis", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("ranking ASC")
    private List<DiagnosisCandidate> candidates = new ArrayList<>();

    protected Diagnosis() {
    }

    public Diagnosis(Member member, Crop crop, String imageKey, String thumbnailKey, LocalDateTime createdAt) {
        this.member = member;
        this.crop = crop;
        this.imageKey = imageKey;
        this.thumbnailKey = thumbnailKey;
        this.createdAt = createdAt;
    }

    public void addCandidate(Disease disease, int ranking, BigDecimal confidence) {
        candidates.add(new DiagnosisCandidate(this, disease, ranking, confidence));
    }

    public void giveFeedback(Feedback feedback, LocalDateTime at) {
        this.feedback = feedback;
        this.feedbackAt = at;
    }

    public boolean isOwnedBy(Long memberId) {
        return member.getId().equals(memberId);
    }

    public Long getId() { return id; }
    public Member getMember() { return member; }
    public Crop getCrop() { return crop; }
    public String getImageKey() { return imageKey; }
    public String getThumbnailKey() { return thumbnailKey; }
    public Feedback getFeedback() { return feedback; }
    public LocalDateTime getFeedbackAt() { return feedbackAt; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public List<DiagnosisCandidate> getCandidates() { return candidates; }
}
