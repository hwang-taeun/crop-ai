package com.taeun.crop.common;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.multipart.support.MissingServletRequestPartException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(ApiException.class)
    public ResponseEntity<ErrorResponse> handleApi(ApiException e) {
        return respond(e.code(), e.getMessage());
    }

    /** ?crop=RICE 처럼 값의 형식이 틀린 경우 */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ErrorResponse> handleTypeMismatch(MethodArgumentTypeMismatchException e) {
        if (e.getRequiredType() == Crop.class) {
            return respond(ErrorCode.INVALID_CROP, ErrorCode.INVALID_CROP.defaultMessage());
        }
        return respond(ErrorCode.INVALID_REQUEST, "'" + e.getName() + "' 값의 형식이 올바르지 않습니다.");
    }

    @ExceptionHandler({
            MissingServletRequestParameterException.class,
            MissingServletRequestPartException.class,
            HttpMessageNotReadableException.class
    })
    public ResponseEntity<ErrorResponse> handleBadRequest(Exception e) {
        return respond(ErrorCode.INVALID_REQUEST, ErrorCode.INVALID_REQUEST.defaultMessage());
    }

    /** @Valid 검사 실패 — 첫 번째 항목의 안내 문구를 그대로 돌려줌 */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
        FieldError first = e.getBindingResult().getFieldError();
        String message = (first != null && first.getDefaultMessage() != null)
                ? first.getDefaultMessage()
                : ErrorCode.INVALID_REQUEST.defaultMessage();
        return respond(ErrorCode.INVALID_REQUEST, message);
    }

    /** UNIQUE 제약 위반 (동시에 같은 아이디·닉네임으로 가입하는 경우 등) */
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<ErrorResponse> handleConflict(DataIntegrityViolationException e) {
        return ResponseEntity.status(409)
                .body(ErrorResponse.of(ErrorCode.DUPLICATE_LOGIN_ID, "이미 사용 중인 아이디 또는 닉네임입니다."));
    }

    /** 10MB 초과 업로드 (Spring 단계에서 걸러짐) */
    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<ErrorResponse> handleTooLarge(MaxUploadSizeExceededException e) {
        return respond(ErrorCode.IMAGE_TOO_LARGE, ErrorCode.IMAGE_TOO_LARGE.defaultMessage());
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<ErrorResponse> handleNoResource(NoResourceFoundException e) {
        return respond(ErrorCode.NOT_FOUND, ErrorCode.NOT_FOUND.defaultMessage());
    }

    /** 예상하지 못한 오류 — 내부 내용은 로그에만 남기고 사용자에게는 일반 문구만 */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleUnknown(Exception e) {
        log.error("처리하지 못한 오류", e);
        return respond(ErrorCode.INTERNAL_ERROR, ErrorCode.INTERNAL_ERROR.defaultMessage());
    }

    private ResponseEntity<ErrorResponse> respond(ErrorCode code, String message) {
        return ResponseEntity.status(code.status()).body(ErrorResponse.of(code, message));
    }
}
