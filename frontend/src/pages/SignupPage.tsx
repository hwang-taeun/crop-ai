import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { errorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { REGIONS } from './regions'

/** 서버 규칙(api-spec 4.1)과 같은 검사를 화면에서 먼저 함 — 최종 판단은 서버 */
function validate(loginId: string, password: string, confirm: string, nickname: string): string {
  if (!/^[a-z0-9_]{4,20}$/.test(loginId)) return '아이디는 영문 소문자·숫자·밑줄(_) 4~20자입니다.'
  if (password.length < 8 || password.length > 64) return '비밀번호는 8~64자입니다.'
  if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) return '비밀번호는 영문과 숫자를 모두 포함해야 합니다.'
  if (password.toLowerCase().includes(loginId)) return '비밀번호에 아이디를 포함할 수 없습니다.'
  if (password !== confirm) return '비밀번호 확인이 일치하지 않습니다.'
  const n = nickname.trim()
  if (n.length < 2 || n.length > 20) return '닉네임은 2~20자입니다.'
  return ''
}

export default function SignupPage() {
  const { member, signup } = useAuth()
  const navigate = useNavigate()
  const [loginId, setLoginId] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [nickname, setNickname] = useState('')
  const [region, setRegion] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (member) return <Navigate to="/" replace />

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const problem = validate(loginId, password, confirm, nickname)
    if (problem) { setError(problem); return }
    setError('')
    setBusy(true)
    try {
      await signup({ loginId, password, nickname: nickname.trim(), region: region || undefined })
      navigate('/', { replace: true })
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card narrow">
      <h1>회원가입</h1>
      <form onSubmit={submit} className="form">
        <label>아이디 <small className="muted">영문 소문자·숫자·밑줄 4~20자</small>
          <input value={loginId} onChange={(e) => setLoginId(e.target.value.toLowerCase())} autoComplete="username" required />
        </label>
        <label>비밀번호 <small className="muted">8자 이상, 영문+숫자</small>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" required />
        </label>
        <label>비밀번호 확인
          <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" required />
        </label>
        <label>닉네임
          <input value={nickname} onChange={(e) => setNickname(e.target.value)} required />
        </label>
        <label>지역 <small className="muted">선택</small>
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="">선택 안 함</option>
            {REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={busy}>{busy ? '가입 중…' : '가입하기'}</button>
      </form>
      <p className="muted center">이미 계정이 있나요? <Link to="/login">로그인</Link></p>
    </section>
  )
}
