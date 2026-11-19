package com.taeun.crop.auth;

import com.taeun.crop.member.MemberResponse;

/** 가입·로그인 응답 — React 는 accessToken 을 Authorization: Bearer 헤더로 사용 */
public record AuthResponse(String accessToken, String tokenType, long expiresIn, MemberResponse member) {
}
