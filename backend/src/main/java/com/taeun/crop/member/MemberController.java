package com.taeun.crop.member;

import com.taeun.crop.auth.CurrentMember;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** docs/api-spec.md 4장 — 내 정보 (로그인 필요) */
@RestController
@RequestMapping("/api/v1/members/me")
public class MemberController {

    private final MemberService service;
    private final CurrentMember currentMember;

    public MemberController(MemberService service, CurrentMember currentMember) {
        this.service = service;
        this.currentMember = currentMember;
    }

    @GetMapping
    public MemberResponse me() {
        return service.me(currentMember.id());
    }

    @PatchMapping
    public MemberResponse update(@Valid @RequestBody UpdateMemberRequest request) {
        return service.update(currentMember.id(), request);
    }

    @PutMapping("/password")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void changePassword(@Valid @RequestBody ChangePasswordRequest request) {
        service.changePassword(currentMember.id(), request);
    }

    @DeleteMapping
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete() {
        service.delete(currentMember.id());
    }
}
