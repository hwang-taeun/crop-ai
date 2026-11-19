package com.taeun.crop.auth;

import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.ErrorCode;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Component;

/** 지금 요청한 회원의 id — JWT 의 sub(회원 id)에서 꺼냄 */
@Component
public class CurrentMember {

    public Long id() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth instanceof JwtAuthenticationToken jwt) {
            try {
                return Long.valueOf(jwt.getToken().getSubject());
            } catch (NumberFormatException e) {
                throw new ApiException(ErrorCode.UNAUTHORIZED);
            }
        }
        throw new ApiException(ErrorCode.UNAUTHORIZED);
    }
}
