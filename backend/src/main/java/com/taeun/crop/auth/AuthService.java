package com.taeun.crop.auth;

import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.ErrorCode;
import com.taeun.crop.common.Times;
import com.taeun.crop.member.Member;
import com.taeun.crop.member.MemberRepository;
import com.taeun.crop.member.MemberResponse;
import java.time.Duration;
import java.time.LocalDateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthService.class);

    private final MemberRepository members;
    private final PasswordEncoder passwordEncoder;
    private final PasswordPolicy passwordPolicy;
    private final TokenService tokens;
    private final int maxFailures;
    private final Duration lockFor;
    /** 없는 아이디로 로그인할 때도 같은 시간이 걸리도록 비교에 쓰는 더미 해시 */
    private final String dummyHash;

    public AuthService(MemberRepository members, PasswordEncoder passwordEncoder, PasswordPolicy passwordPolicy,
                       TokenService tokens,
                       @Value("${app.auth.max-login-failures}") int maxFailures,
                       @Value("${app.auth.lock-minutes}") long lockMinutes) {
        this.members = members;
        this.passwordEncoder = passwordEncoder;
        this.passwordPolicy = passwordPolicy;
        this.tokens = tokens;
        this.maxFailures = maxFailures;
        this.lockFor = Duration.ofMinutes(lockMinutes);
        this.dummyHash = passwordEncoder.encode("timing-equalizer-not-a-real-password");
    }

    @Transactional
    public AuthResponse signup(SignupRequest req) {
        String loginId = req.loginId();
        String nickname = req.nickname().strip();
        passwordPolicy.check(loginId, req.password());
        if (members.existsByLoginId(loginId)) {
            throw new ApiException(ErrorCode.DUPLICATE_LOGIN_ID);
        }
        if (members.existsByNickname(nickname)) {
            throw new ApiException(ErrorCode.DUPLICATE_NICKNAME);
        }
        Member m = Member.signup(loginId, passwordEncoder.encode(req.password()), nickname,
                blankToNull(req.email()), blankToNull(req.region()), Times.now());
        members.saveAndFlush(m);
        log.info("회원 가입: id={}, loginId={}", m.getId(), loginId);
        return toResponse(m);
    }

    /**
     * 로그인. 실패 횟수 기록은 예외가 나도 커밋되어야 하므로 noRollbackFor 지정.
     * 없는 아이디·틀린 비밀번호는 같은 메시지로 응답 (아이디 존재 여부를 알려주지 않음)
     */
    @Transactional(noRollbackFor = ApiException.class)
    public AuthResponse login(LoginRequest req) {
        LocalDateTime now = Times.now();
        Member m = members.findByLoginId(req.loginId()).orElse(null);
        if (m == null) {
            passwordEncoder.matches(req.password(), dummyHash);
            throw new ApiException(ErrorCode.LOGIN_FAILED);
        }
        if (m.isLocked(now)) {
            throw new ApiException(ErrorCode.ACCOUNT_LOCKED);
        }
        if (m.getPasswordHash() == null || !passwordEncoder.matches(req.password(), m.getPasswordHash())) {
            m.loginFailed(now, maxFailures, lockFor);
            log.warn("로그인 실패: loginId={}, 잠금={}", req.loginId(), m.isLocked(now));
            throw new ApiException(ErrorCode.LOGIN_FAILED);
        }
        m.loginSucceeded();
        return toResponse(m);
    }

    private AuthResponse toResponse(Member m) {
        TokenService.IssuedToken t = tokens.issue(m);
        return new AuthResponse(t.value(), "Bearer", t.expiresIn(), MemberResponse.from(m));
    }

    private static String blankToNull(String s) {
        if (s == null) {
            return null;
        }
        String t = s.strip();
        return t.isEmpty() ? null : t;
    }
}
