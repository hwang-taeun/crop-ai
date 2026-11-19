package com.taeun.crop.member;

import com.taeun.crop.auth.PasswordPolicy;
import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.ErrorCode;
import com.taeun.crop.common.Times;
import com.taeun.crop.diagnosis.Diagnosis;
import com.taeun.crop.diagnosis.DiagnosisRepository;
import com.taeun.crop.storage.ImageStorage;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionTemplate;

@Service
public class MemberService {

    private final MemberRepository members;
    private final DiagnosisRepository diagnoses;
    private final ImageStorage storage;
    private final PasswordEncoder passwordEncoder;
    private final PasswordPolicy passwordPolicy;
    private final TransactionTemplate tx;

    public MemberService(MemberRepository members, DiagnosisRepository diagnoses, ImageStorage storage,
                         PasswordEncoder passwordEncoder, PasswordPolicy passwordPolicy, TransactionTemplate tx) {
        this.members = members;
        this.diagnoses = diagnoses;
        this.storage = storage;
        this.passwordEncoder = passwordEncoder;
        this.passwordPolicy = passwordPolicy;
        this.tx = tx;
    }

    @Transactional(readOnly = true)
    public MemberResponse me(Long memberId) {
        return MemberResponse.from(find(memberId));
    }

    @Transactional
    public MemberResponse update(Long memberId, UpdateMemberRequest req) {
        Member m = find(memberId);
        LocalDateTime now = Times.now();
        if (req.nickname() != null) {
            String nickname = req.nickname().strip();
            if (members.existsByNicknameAndIdNot(nickname, memberId)) {
                throw new ApiException(ErrorCode.DUPLICATE_NICKNAME);
            }
            m.changeNickname(nickname, now);
        }
        if (req.region() != null) {
            m.changeRegion(blankToNull(req.region()), now);
        }
        if (req.email() != null) {
            m.changeEmail(blankToNull(req.email()), now);
        }
        return MemberResponse.from(m);
    }

    @Transactional
    public void changePassword(Long memberId, ChangePasswordRequest req) {
        Member m = find(memberId);
        if (m.getPasswordHash() == null || !passwordEncoder.matches(req.currentPassword(), m.getPasswordHash())) {
            throw new ApiException(ErrorCode.LOGIN_FAILED, "현재 비밀번호가 올바르지 않습니다.");
        }
        passwordPolicy.check(m.getLoginId(), req.newPassword());
        m.changePasswordHash(passwordEncoder.encode(req.newPassword()), Times.now());
    }

    /** 회원 탈퇴 — 진단 기록·후보·사진까지 모두 삭제 (DB 커밋 후 파일 삭제) */
    public void delete(Long memberId) {
        List<String> keys = tx.execute(status -> {
            Member m = find(memberId);
            List<Diagnosis> list = diagnoses.findAllByMember_Id(memberId);
            List<String> k = new ArrayList<>();
            for (Diagnosis d : list) {
                k.add(d.getImageKey());
                k.add(d.getThumbnailKey());
            }
            diagnoses.deleteAll(list);
            members.delete(m);
            return k;
        });
        storage.deleteQuietly(keys.toArray(String[]::new));
    }

    private Member find(Long memberId) {
        return members.findById(memberId)
                .orElseThrow(() -> new ApiException(ErrorCode.UNAUTHORIZED, "회원 정보를 찾을 수 없습니다. 다시 로그인하세요."));
    }

    private static String blankToNull(String s) {
        String t = s.strip();
        return t.isEmpty() ? null : t;
    }
}
