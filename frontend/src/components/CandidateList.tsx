import { Link } from 'react-router-dom'
import type { Candidate } from '../api/types'

/**
 * 확률 표시: 모델은 모르는 병에도 확신하는 경우가 있어서 100%·0% 로 단정해 보이지 않게 표시
 * 0.995 이상 → "99% 이상", 0.005 미만 → "1% 미만", 그 외 → 정수 %
 */
function formatPct(c: number): string {
  if (c >= 0.995) return '99% 이상'
  if (c < 0.005) return '1% 미만'
  return `${Math.round(c * 100)}%`
}

/** 후보 3개 + 확률 막대 — 누르면 병 상세 */
export default function CandidateList({ candidates }: { candidates: Candidate[] }) {
  return (
    <ol className="candidates">
      {candidates.map((c) => {
        const width = Math.max(1, Math.round(c.confidence * 100))
        return (
          <li key={c.rank}>
            <Link to={`/diseases/${c.disease.id}`} className="candidate">
              <div className="candidate-head">
                <span className="rank">{c.rank}</span>
                <span className="name">{c.disease.nameKo}</span>
                <span className="pct">{formatPct(c.confidence)}</span>
              </div>
              <div className="bar"><div className={c.disease.healthy ? 'fill healthy' : 'fill'} style={{ width: `${width}%` }} /></div>
            </Link>
          </li>
        )
      })}
    </ol>
  )
}
