import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { cropLabel } from '../api/types'
import type { DiseaseDetail } from '../api/types'

/** 병 상세 (api-spec 6.2) — 설명·방제법은 줄바꿈만 살린 순수 텍스트로 표시 */
export default function DiseasePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [d, setD] = useState<DiseaseDetail | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.disease(Number(id)).then(setD).catch((e) => setError(errorMessage(e)))
  }, [id])

  if (error) return <p className="error center">{error}</p>
  if (!d) return <p className="center muted">불러오는 중…</p>

  return (
    <section className="card">
      <button type="button" className="link-button" onClick={() => navigate(-1)}>← 뒤로</button>
      <p className="muted small">{cropLabel(d.crop)}</p>
      <h1>{d.nameKo}</h1>
      <h2>설명</h2>
      <p className="pre">{d.description}</p>
      {!d.healthy && (<><h2>방제 방법</h2><p className="pre">{d.treatment}</p></>)}
      <p className="notice">⚠ {d.notice}</p>
      <p className="muted small">출처: {d.source}</p>
    </section>
  )
}
