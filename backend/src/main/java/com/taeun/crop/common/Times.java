package com.taeun.crop.common;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;

/** DB는 한국 시간(LocalDateTime)으로 저장하고, 응답은 +09:00 이 붙은 ISO-8601 문자열로 내보냄 */
public final class Times {

    public static final ZoneId SEOUL = ZoneId.of("Asia/Seoul");

    private Times() {
    }

    public static LocalDateTime now() {
        return LocalDateTime.now(SEOUL).truncatedTo(ChronoUnit.MICROS);
    }

    public static String format(LocalDateTime time) {
        if (time == null) {
            return null;
        }
        return time.atZone(SEOUL).toOffsetDateTime().truncatedTo(ChronoUnit.SECONDS).toString();
    }
}
