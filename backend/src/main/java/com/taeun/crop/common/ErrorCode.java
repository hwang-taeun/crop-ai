package com.taeun.crop.common;

import org.springframework.http.HttpStatus;

/** docs/api-spec.md 2.3 오류 코드 */
public enum ErrorCode {
    INVALID_REQUEST(HttpStatus.BAD_REQUEST, "요청 형식이 올바르지 않습니다."),
    INVALID_CROP(HttpStatus.BAD_REQUEST, "작물은 TOMATO, POTATO, CORN 중 하나여야 합니다."),
    INVALID_IMAGE(HttpStatus.BAD_REQUEST, "jpg 또는 png 사진만 올릴 수 있습니다."),
    INVALID_PASSWORD(HttpStatus.BAD_REQUEST, "비밀번호는 영문과 숫자를 모두 포함해야 하고, 아이디를 포함할 수 없습니다."),
    UNAUTHORIZED(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다."),
    LOGIN_FAILED(HttpStatus.UNAUTHORIZED, "아이디 또는 비밀번호가 올바르지 않습니다."),
    FORBIDDEN(HttpStatus.FORBIDDEN, "접근 권한이 없습니다."),
    NOT_FOUND(HttpStatus.NOT_FOUND, "대상을 찾을 수 없습니다."),
    DUPLICATE_LOGIN_ID(HttpStatus.CONFLICT, "이미 사용 중인 아이디입니다."),
    DUPLICATE_NICKNAME(HttpStatus.CONFLICT, "이미 사용 중인 닉네임입니다."),
    IMAGE_TOO_LARGE(HttpStatus.CONTENT_TOO_LARGE, "사진은 10MB 이하만 올릴 수 있습니다."),
    ACCOUNT_LOCKED(HttpStatus.LOCKED, "로그인에 여러 번 실패해 잠시 잠겼습니다. 잠시 후 다시 시도하세요."),
    TOO_MANY_REQUESTS(HttpStatus.TOO_MANY_REQUESTS, "요청이 너무 많습니다. 잠시 후 다시 시도하세요."),
    AI_UNAVAILABLE(HttpStatus.SERVICE_UNAVAILABLE, "AI 진단 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요."),
    INTERNAL_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "서버 오류가 발생했습니다.");

    private final HttpStatus status;
    private final String defaultMessage;

    ErrorCode(HttpStatus status, String defaultMessage) {
        this.status = status;
        this.defaultMessage = defaultMessage;
    }

    public HttpStatus status() { return status; }
    public String defaultMessage() { return defaultMessage; }
}
