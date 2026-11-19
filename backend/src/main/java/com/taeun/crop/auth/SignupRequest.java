package com.taeun.crop.auth;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record SignupRequest(
        @NotBlank(message = "아이디를 입력하세요.")
        @Pattern(regexp = "^[a-z0-9_]{4,20}$", message = "아이디는 영문 소문자·숫자·밑줄(_) 4~20자입니다.")
        String loginId,

        @NotBlank(message = "비밀번호를 입력하세요.")
        @Size(min = 8, max = 64, message = "비밀번호는 8~64자입니다.")
        String password,

        @NotBlank(message = "닉네임을 입력하세요.")
        @Size(min = 2, max = 20, message = "닉네임은 2~20자입니다.")
        String nickname,

        @Size(max = 20, message = "지역은 20자 이하입니다.")
        String region,

        @Email(message = "이메일 형식이 올바르지 않습니다.")
        @Size(max = 255)
        String email
) {
}
