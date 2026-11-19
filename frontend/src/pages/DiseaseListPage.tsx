import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { CROPS } from '../api/types'
import type { DiseaseSummary } from '../api/types'

/** 진단 가능한 병 목록 (api-spec 6.1) — 모델이 아는 병은 이 17개뿐임을 안내 */
export default function DiseaseListPage() {
  const [list, setList] = useState<DiseaseSummary[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.diseases().then(setList).catch((e) => setError(errorMessage(e)))
  }, [])

  return (
    <section className="card">
      <h1>진단 가능한 병</h1>
      <p className="muted small">AI는 아래 {list.length || 17}가지만 구분할 수 있습니다. 목록에 없는 병은 비슷한 다른 병으로 나올 수 있습니다.</p>
      {error && <p className="error">{error}</p>}
      {CROPS.map((c) => (
        <div key={c.value}>
          <h2>{c.emoji} {c.label}</h2>
          <ul className="links">
            {list.filter((d) => d.crop === c.value).map((d) => (
              <li key={d.id}><Link to={`/diseases/${d.id}`}>{d.nameKo}</Link></li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  )
}
