package com.taeun.crop.diagnosis;

import com.taeun.crop.disease.Disease;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.math.BigDecimal;

/** my_ncpms.diagnosis_candidate — 진단 1건의 후보 3개 */
@Entity
@Table(name = "diagnosis_candidate")
public class DiagnosisCandidate {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "diagnosis_id", nullable = false)
    private Diagnosis diagnosis;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "disease_id", nullable = false)
    private Disease disease;

    @Column(nullable = false)
    private int ranking;

    @Column(nullable = false, precision = 5, scale = 4)
    private BigDecimal confidence;

    protected DiagnosisCandidate() {
    }

    DiagnosisCandidate(Diagnosis diagnosis, Disease disease, int ranking, BigDecimal confidence) {
        this.diagnosis = diagnosis;
        this.disease = disease;
        this.ranking = ranking;
        this.confidence = confidence;
    }

    public Long getId() { return id; }
    public Diagnosis getDiagnosis() { return diagnosis; }
    public Disease getDisease() { return disease; }
    public int getRanking() { return ranking; }
    public BigDecimal getConfidence() { return confidence; }
}
