package com.taeun.crop.member;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Duration;
import java.time.LocalDateTime;

/** my_ncpms.member — 아이디·비밀번호(BCrypt) 로그인 */
@Entity
@Table(name = "member")
public class Member {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "login_id", unique = true, length = 30)
    private String loginId;

    /** BCrypt 해시 (평문 비밀번호는 저장하지 않음) */
    @Column(name = "password_hash", length = 100)
    private String passwordHash;

    @Column(name = "failed_login_count", nullable = false)
    private int failedLoginCount;

    @Column(name = "locked_until")
    private LocalDateTime lockedUntil;

    @Column(name = "google_sub", unique = true)
    private String googleSub;

    private String email;

    @Column(nullable = false, unique = true, length = 50)
    private String nickname;

    @Column(length = 20)
    private String region;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    protected Member() {
    }

    public static Member signup(String loginId, String passwordHash, String nickname,
                                String email, String region, LocalDateTime now) {
        Member m = new Member();
        m.loginId = loginId;
        m.passwordHash = passwordHash;
        m.nickname = nickname;
        m.email = email;
        m.region = region;
        m.role = Role.USER;
        m.failedLoginCount = 0;
        m.createdAt = now;
        m.updatedAt = now;
        return m;
    }

    // ── 로그인 실패 잠금 ──

    public boolean isLocked(LocalDateTime now) {
        return lockedUntil != null && lockedUntil.isAfter(now);
    }

    /** 실패 횟수 증가, 기준 횟수에 도달하면 일정 시간 잠금 */
    public void loginFailed(LocalDateTime now, int maxFailures, Duration lockFor) {
        failedLoginCount++;
        if (failedLoginCount >= maxFailures) {
            lockedUntil = now.plus(lockFor);
            failedLoginCount = 0;
        }
    }

    public void loginSucceeded() {
        failedLoginCount = 0;
        lockedUntil = null;
    }

    // ── 정보 수정 ──

    public void changeNickname(String nickname, LocalDateTime now) {
        this.nickname = nickname;
        this.updatedAt = now;
    }

    public void changeRegion(String region, LocalDateTime now) {
        this.region = region;
        this.updatedAt = now;
    }

    public void changeEmail(String email, LocalDateTime now) {
        this.email = email;
        this.updatedAt = now;
    }

    public void changePasswordHash(String passwordHash, LocalDateTime now) {
        this.passwordHash = passwordHash;
        this.updatedAt = now;
    }

    public Long getId() { return id; }
    public String getLoginId() { return loginId; }
    public String getPasswordHash() { return passwordHash; }
    public int getFailedLoginCount() { return failedLoginCount; }
    public LocalDateTime getLockedUntil() { return lockedUntil; }
    public String getGoogleSub() { return googleSub; }
    public String getEmail() { return email; }
    public String getNickname() { return nickname; }
    public String getRegion() { return region; }
    public Role getRole() { return role; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
