package com.taeun.crop.member;

import com.taeun.crop.common.Times;

/** 회원 정보 응답 — 비밀번호 해시·잠금 정보는 내보내지 않음 */
public record MemberResponse(Long id, String loginId, String nickname, String email, String region,
                             Role role, String createdAt) {

    public static MemberResponse from(Member m) {
        return new MemberResponse(m.getId(), m.getLoginId(), m.getNickname(), m.getEmail(), m.getRegion(),
                m.getRole(), Times.format(m.getCreatedAt()));
    }
}
