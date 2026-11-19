package com.taeun.crop.disease;

import com.taeun.crop.common.Crop;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/** my_ncpms.disease — 병 17종의 이름·설명·방제법 (앱에서는 읽기만 함) */
@Entity
@Table(name = "disease")
public class Disease {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 모델 클래스명과 글자까지 같아야 함 (예: Tomato___Late_blight) */
    @Column(nullable = false, unique = true, length = 100)
    private String label;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Crop crop;

    @Column(name = "name_ko", nullable = false, length = 100)
    private String nameKo;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String treatment;

    protected Disease() {
    }

    public Long getId() { return id; }
    public String getLabel() { return label; }
    public Crop getCrop() { return crop; }
    public String getNameKo() { return nameKo; }
    public String getDescription() { return description; }
    public String getTreatment() { return treatment; }

    /** 정상 잎 클래스인지 (DB 컬럼이 아니라 라벨로 판단) */
    public boolean isHealthy() {
        return label.endsWith("___healthy");
    }
}
