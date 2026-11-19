package com.taeun.crop.common;

/** 서비스 코드에서 던지면 GlobalExceptionHandler 가 오류 응답으로 바꿔 줌 */
public class ApiException extends RuntimeException {
    private final ErrorCode code;

    public ApiException(ErrorCode code) {
        this(code, code.defaultMessage());
    }

    public ApiException(ErrorCode code, String message) {
        super(message);
        this.code = code;
    }

    public ErrorCode code() { return code; }
}
