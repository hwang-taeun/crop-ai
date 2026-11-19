import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { CROPS, cropLabel } from '../api/types'
import type { Crop, DiagnosisListItem } from '../api/types'
import AuthImage from '../components/AuthImage'
import { formatDate } from './format'

const SIZE = 10
const STATUS_TEXT = { HEALTHY: '정상', LIKELY: '가능성 높음', POSSIBLE: '의심', UNCERTAIN: '불확실' } as const

/** 내 진단 기록 (api-spec 5.2) — 작물 필터 + 더 보기 */
export default function HistoryPage() {
  const [crop, setCrop] = useState<Crop | undefined>(undefined)
  const [items, setItems] = useState<DiagnosisListItem[]>([])
  const [page, setPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    api.diagnoses(page, SIZE, crop)
      .then((r) => {
        if (cancelled) return
        setItems((prev) => (page === 0 ? r.items : [...prev, ...r.items]))
        setTotalPages(r.totalPages)
      })
      .catch((e) => { if (!cancelled) setError(errorMessage(e)) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [page, crop])

  const changeCrop = (c: Crop | undefined) => {
    setCrop(c)
    setPage(0)
    setItems([])
    setLoading(true)
  }

  return (
    <section className="card">
      <h1>진단 기록</h1>
      <div className="row wrap">
        <button type="button" className={!crop ? 'chip on' : 'chip'} onClick={() => changeCrop(undefined)}>전체</button>
        {CROPS.map((c) => (
          <button key={c.value} type="button" className={crop === c.value ? 'chip on' : 'chip'} onClick={() => changeCrop(c.value)}>
            {c.emoji} {c.label}
          </button>
        ))}
      </div>

      {error && <p className="error">{error}</p>}
      {!loading && items.length === 0 && <p className="muted center">아직 진단 기록이 없습니다. <Link to="/">진단하러 가기</Link></p>}

      <ul className="history">
        {items.map((it) => (
          <li key={it.id}>
            <Link to={`/diagnoses/${it.id}`} className="history-item">
              <AuthImage src={it.thumbnailUrl} alt="" className="thumb" />
              <div>
                <strong>{it.topCandidate?.disease.nameKo ?? '결과 없음'}</strong>
                <span className={`tag tag-${it.status.toLowerCase()}`}>{STATUS_TEXT[it.status]}</span>
                <p className="muted small">{cropLabel(it.crop)} · {formatDate(it.createdAt)}
                  {it.feedback === 'CORRECT' && ' · 👍'}{it.feedback === 'INCORRECT' && ' · 👎'}</p>
              </div>
            </Link>
          </li>
        ))}
      </ul>

      {loading && <p className="muted center">불러오는 중…</p>}
      {!loading && page + 1 < totalPages && (
        <button type="button" className="secondary wide" onClick={() => { setLoading(true); setPage(page + 1) }}>더 보기</button>
      )}
    </section>
  )
}
