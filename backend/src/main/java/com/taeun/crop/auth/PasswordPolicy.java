package com.taeun.crop.auth;

import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.ErrorCode;
import org.springframework.stereotype.Component;

/** 비밀번호 규칙: 8~64자(요청 검증), 영문+숫자 포함, 아이디 포함 금지 */
@Component
public class PasswordPolicy {

    public void check(String loginId, String password) {
        boolean hasLetter = password.chars().anyMatch(Character::isLetter);
        boolean hasDigit = password.chars().anyMatch(Character::isDigit);
        boolean containsId = loginId != null && password.toLowerCase().contains(loginId.toLowerCase());
        if (!hasLetter || !hasDigit || containsId) {
            throw new ApiException(ErrorCode.INVALID_PASSWORD);
        }
    }
}
