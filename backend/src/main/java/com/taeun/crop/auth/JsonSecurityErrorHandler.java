package com.taeun.crop.auth;

import com.taeun.crop.common.ErrorCode;
import com.taeun.crop.common.ErrorResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

/** Spring Security 단계의 401/403도 공통 오류 형식 { code, message, timestamp } 으로 응답 */
@Component
public class JsonSecurityErrorHandler implements AuthenticationEntryPoint, AccessDeniedHandler {

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                         AuthenticationException e) throws IOException {
        String header = request.getHeader("Authorization");
        String message = (header != null && header.startsWith("Bearer "))
                ? "로그인이 만료되었거나 올바르지 않습니다. 다시 로그인하세요."
                : ErrorCode.UNAUTHORIZED.defaultMessage();
        response.setHeader("WWW-Authenticate", "Bearer");
        write(response, ErrorCode.UNAUTHORIZED, message);
    }

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response,
                       AccessDeniedException e) throws IOException {
        write(response, ErrorCode.FORBIDDEN, ErrorCode.FORBIDDEN.defaultMessage());
    }

    private static void write(HttpServletResponse response, ErrorCode code, String message) throws IOException {
        ErrorResponse body = ErrorResponse.of(code, message);
        response.setStatus(code.status().value());
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"code\":\"" + body.code()
                + "\",\"message\":\"" + escape(body.message())
                + "\",\"timestamp\":\"" + body.timestamp() + "\"}");
    }

    private static String escape(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
