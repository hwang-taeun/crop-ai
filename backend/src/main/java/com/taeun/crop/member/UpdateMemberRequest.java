package com.taeun.crop.member;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

/** 바꿀 항목만 보냄. region·email 은 빈 문자열("")을 보내면 지움 */
public record UpdateMemberRequest(
        @Size(min = 2, max = 20, message = "닉네임은 2~20자입니다.") String nickname,
        @Size(max = 20, message = "지역은 20자 이하입니다.") String region,
        @Email(message = "이메일 형식이 올바르지 않습니다.") @Size(max = 255) String email
) {
}
