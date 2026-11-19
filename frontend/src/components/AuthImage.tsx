import { useEffect, useState } from 'react'
import { fetchImageUrl } from '../api/client'

/** 로그인이 필요한 사진(진단 원본·썸네일)을 토큰을 붙여 받아 표시 */
export default function AuthImage({ src, alt, className }: { src: string; alt: string; className?: string }) {
  const [url, setUrl] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let objectUrl: string | null = null
    let cancelled = false
    fetchImageUrl(src)
      .then((u) => {
        if (cancelled) { URL.revokeObjectURL(u); return }
        objectUrl = u
        setUrl(u)
      })
      .catch(() => { if (!cancelled) setFailed(true) })
    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [src])

  if (failed) return <div className={`img-placeholder ${className ?? ''}`}>사진 없음</div>
  if (!url) return <div className={`img-placeholder ${className ?? ''}`}>…</div>
  return <img src={url} alt={alt} className={className} />
}
