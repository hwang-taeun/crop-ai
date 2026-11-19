package com.taeun.crop.member;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ChangePasswordRequest(
        @NotBlank(message = "현재 비밀번호를 입력하세요.") String currentPassword,
        @NotBlank(message = "새 비밀번호를 입력하세요.")
        @Size(min = 8, max = 64, message = "비밀번호는 8~64자입니다.") String newPassword
) {
}
