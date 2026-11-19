import type { Candidate, DiagnosisStatus } from '../api/types'

/** docs/api-spec.md 3장 — status 별 안내 문구 */
export default function StatusBanner({ status, top }: { status: DiagnosisStatus; top?: Candidate }) {
  const name = top?.disease.nameKo ?? ''
  const text: Record<DiagnosisStatus, string> = {
    HEALTHY: '건강한 잎으로 보입니다.',
    LIKELY: `${name} 가능성이 높습니다.`,
    POSSIBLE: '다음 병 중 하나일 수 있습니다.',
    UNCERTAIN: '판단하기 어렵습니다. 잎이 잘 보이도록 다른 각도에서 다시 찍어 주세요.',
  }
  return <div className={`banner banner-${status.toLowerCase()}`}>{text[status]}</div>
}
