import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { formatDate } from './format'
import { REGIONS } from './regions'

/** 내 정보 (api-spec 4.3~4.6) */
export default function MePage() {
  const { member, setMember, logout } = useAuth()
  const navigate = useNavigate()
  const [nickname, setNickname] = useState(member?.nickname ?? '')
  const [region, setRegion] = useState(member?.region ?? '')
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  if (!member) return null

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      setMember(await api.updateMe({ nickname: nickname.trim(), region }))
      setMsg('저장했습니다.')
    } catch (err) { setError(errorMessage(err)) }
  }

  const savePassword = async (e: FormEvent) => {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      await api.changePassword(current, next)
      setCurrent(''); setNext('')
      setMsg('비밀번호를 바꿨습니다.')
    } catch (err) { setError(errorMessage(err)) }
  }

  const withdraw = async () => {
    if (!window.confirm('탈퇴하면 진단 기록과 사진이 모두 삭제됩니다. 계속할까요?')) return
    try {
      await api.deleteMe()
      logout()
      navigate('/login', { replace: true })
    } catch (err) { setError(errorMessage(err)) }
  }

  return (
    <section className="card">
      <h1>내 정보</h1>
      <p className="muted small">아이디 {member.loginId} · 가입 {formatDate(member.createdAt)}</p>
      {msg && <p className="ok">{msg}</p>}
      {error && <p className="error">{error}</p>}

      <form onSubmit={saveProfile} className="form">
        <label>닉네임<input value={nickname} onChange={(e) => setNickname(e.target.value)} minLength={2} maxLength={20} required /></label>
        <label>지역
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="">선택 안 함</option>
            {REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </label>
        <button type="submit">저장</button>
      </form>

      <h2>비밀번호 변경</h2>
      <form onSubmit={savePassword} className="form">
        <label>현재 비밀번호<input type="password" value={current} onChange={(e) => setCurrent(e.target.value)} autoComplete="current-password" required /></label>
        <label>새 비밀번호 <small className="muted">8자 이상, 영문+숫자</small>
          <input type="password" value={next} onChange={(e) => setNext(e.target.value)} autoComplete="new-password" minLength={8} required /></label>
        <button type="submit" className="secondary">비밀번호 변경</button>
      </form>

      <div className="row space">
        <button type="button" className="secondary" onClick={() => { logout(); navigate('/login') }}>로그아웃</button>
        <button type="button" className="danger" onClick={withdraw}>회원 탈퇴</button>
      </div>
    </section>
  )
}
