import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { cropLabel } from '../api/types'
import type { Diagnosis, Feedback } from '../api/types'
import AuthImage from '../components/AuthImage'
import CandidateList from '../components/CandidateList'
import StatusBanner from '../components/StatusBanner'
import { formatDate } from './format'

/** 진단 결과 / 기록 상세 (api-spec 5.1, 5.3) */
export default function ResultPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const fromState = (location.state as { result?: Diagnosis } | null)?.result
  const [d, setD] = useState<Diagnosis | null>(fromState && String(fromState.id) === id ? fromState : null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (d) return
    api.diagnosis(Number(id)).then(setD).catch((e) => setError(errorMessage(e)))
  }, [id, d])

  if (error) return <p className="error center">{error}</p>
  if (!d) return <p className="center muted">불러오는 중…</p>

  const sendFeedback = async (fb: Feedback) => {
    try {
      const r = await api.feedback(d.id, fb)
      setD({ ...d, feedback: r.feedback })
    } catch (e) {
      setError(errorMessage(e))
    }
  }

  const remove = async () => {
    if (!window.confirm('이 진단 기록과 사진을 삭제할까요?')) return
    try {
      await api.deleteDiagnosis(d.id)
      navigate('/history', { replace: true })
    } catch (e) {
      setError(errorMessage(e))
    }
  }

  return (
    <section className="card">
      <p className="muted small">{cropLabel(d.crop)} · {formatDate(d.createdAt)}</p>
      <AuthImage src={d.imageUrl} alt="진단한 잎 사진" className="result-image" />
      <StatusBanner status={d.status} top={d.candidates[0]} />

      <h2>가능성 높은 병</h2>
      <CandidateList candidates={d.candidates} />
      <p className="muted small">
        확률이 높은 3개만 보여 줍니다. AI가 구분할 수 있는 {cropLabel(d.crop)} 병은 정해져 있어서,
        목록에 없는 병은 비슷한 다른 병으로 나올 수 있습니다. <Link to="/diseases">진단 가능한 병 전체 보기 →</Link>
      </p>

      <p className="notice">⚠ {d.notice}</p>

      <div className="feedback">
        <p>결과가 맞았나요? <small className="muted">(틀린 사진은 모델 개선에 사용됩니다)</small></p>
        <div className="row">
          <button type="button" className={d.feedback === 'CORRECT' ? 'chip on' : 'chip'} onClick={() => sendFeedback('CORRECT')}>👍 맞아요</button>
          <button type="button" className={d.feedback === 'INCORRECT' ? 'chip on' : 'chip'} onClick={() => sendFeedback('INCORRECT')}>👎 틀려요</button>
        </div>
      </div>

      <div className="row space">
        <Link to="/" className="button secondary">새로 진단</Link>
        <button type="button" className="danger" onClick={remove}>기록 삭제</button>
      </div>
      {d.modelVersion && <p className="muted small center">모델 {d.modelVersion}</p>}
    </section>
  )
}
