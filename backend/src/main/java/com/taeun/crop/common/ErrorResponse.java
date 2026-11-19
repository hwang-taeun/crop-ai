package com.taeun.crop.common;

import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;

/** 모든 오류의 공통 응답 형식 { code, message, timestamp } */
public record ErrorResponse(String code, String message, String timestamp) {

    private static final ZoneId SEOUL = ZoneId.of("Asia/Seoul");

    public static ErrorResponse of(ErrorCode code, String message) {
        String now = OffsetDateTime.now(SEOUL).truncatedTo(ChronoUnit.SECONDS).toString();
        return new ErrorResponse(code.name(), message, now);
    }
}
