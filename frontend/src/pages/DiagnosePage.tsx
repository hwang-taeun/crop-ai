import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { CROPS } from '../api/types'
import type { Crop } from '../api/types'

const MAX_BYTES = 10 * 1024 * 1024

/** 진단하기: 작물 선택 → 사진 촬영/선택 → 진단 요청 → 결과 화면 */
export default function DiagnosePage() {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const [crop, setCrop] = useState<Crop | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview) }, [preview])

  const pick = (f: File | undefined) => {
    setError('')
    if (!f) return
    if (!['image/jpeg', 'image/png'].includes(f.type)) { setError('jpg 또는 png 사진만 올릴 수 있습니다.'); return }
    if (f.size > MAX_BYTES) { setError('사진은 10MB 이하만 올릴 수 있습니다.'); return }
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }

  const submit = async () => {
    if (!crop || !file) return
    setError('')
    setBusy(true)
    try {
      const result = await api.diagnose(file, crop)
      navigate(`/diagnoses/${result.id}`, { state: { result } })
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card">
      <h1>잎 사진으로 진단하기</h1>

      <h2 className="step">1. 작물 선택</h2>
      <div className="crop-buttons">
        {CROPS.map((c) => (
          <button key={c.value} type="button" className={crop === c.value ? 'crop selected' : 'crop'}
                  onClick={() => setCrop(c.value)}>
            <span className="emoji">{c.emoji}</span>{c.label}
          </button>
        ))}
      </div>

      <h2 className="step">2. 잎 사진</h2>
      <input ref={inputRef} type="file" accept="image/jpeg,image/png" capture="environment" hidden
             onChange={(e) => pick(e.target.files?.[0])} />
      <button type="button" className="secondary wide" onClick={() => inputRef.current?.click()}>
        {file ? '다른 사진 선택' : '📷 사진 찍기 / 고르기'}
      </button>
      {preview && <img src={preview} alt="선택한 잎 사진" className="preview" />}
      <p className="muted small">잎 한 장이 화면을 가득 채우도록, 밝은 곳에서 찍으면 정확도가 올라갑니다.</p>

      {error && <p className="error">{error}</p>}
      <button type="button" className="wide" disabled={!crop || !file || busy} onClick={submit}>
        {busy ? '진단 중… (최대 10초)' : '진단하기'}
      </button>
    </section>
  )
}
