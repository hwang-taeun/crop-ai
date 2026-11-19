package com.taeun.crop.storage;

import java.util.Optional;
import org.springframework.http.MediaType;

/** 허용하는 사진 형식. 확장자나 Content-Type 이 아니라 파일 앞부분(매직 바이트)으로 판단 */
public enum ImageType {
    JPEG("jpg", MediaType.IMAGE_JPEG),
    PNG("png", MediaType.IMAGE_PNG);

    private final String ext;
    private final MediaType mediaType;

    ImageType(String ext, MediaType mediaType) {
        this.ext = ext;
        this.mediaType = mediaType;
    }

    public String ext() { return ext; }
    public MediaType mediaType() { return mediaType; }

    public static Optional<ImageType> detect(byte[] b) {
        if (b.length >= 3 && (b[0] & 0xFF) == 0xFF && (b[1] & 0xFF) == 0xD8 && (b[2] & 0xFF) == 0xFF) {
            return Optional.of(JPEG);
        }
        if (b.length >= 8 && (b[0] & 0xFF) == 0x89 && b[1] == 'P' && b[2] == 'N' && b[3] == 'G') {
            return Optional.of(PNG);
        }
        return Optional.empty();
    }

    /** 저장 키의 확장자로 응답 Content-Type 결정 */
    public static MediaType mediaTypeOfKey(String key) {
        return key.endsWith(".png") ? MediaType.IMAGE_PNG : MediaType.IMAGE_JPEG;
    }
}
