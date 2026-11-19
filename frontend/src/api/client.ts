import type {
  ApiErrorBody, AuthResponse, Crop, Diagnosis, DiagnosisListItem, DiseaseDetail,
  DiseaseSummary, Feedback, Member, Page,
} from './types'

/** 서버가 돌려준 오류 { code, message } 를 그대로 담는 예외 */
export class ApiError extends Error {
  readonly code: string
  readonly status: number

  constructor(status: number, code: string, message: string) {
    super(message)
    this.status = status
    this.code = code
  }
}

// ── 토큰 보관 ──
// localStorage: 새로고침해도 로그인이 유지됨. (XSS 에 노출될 수 있으므로 화면에 사용자 입력을 HTML로 넣지 않음)
const TOKEN_KEY = 'crop.accessToken'

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

/** 401(토큰 만료·위조)이 오면 로그아웃 처리하도록 AuthContext 에 알림 */
export const UNAUTHORIZED_EVENT = 'crop:unauthorized'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  json?: unknown
  form?: FormData
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {}
  const token = tokenStore.get()
  if (token) headers.Authorization = `Bearer ${token}`

  let body: BodyInit | undefined
  if (opts.json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(opts.json)
  } else if (opts.form) {
    body = opts.form // Content-Type(boundary)은 브라우저가 붙임
  }

  let res: Response
  try {
    res = await fetch(`/api/v1${path}`, { method: opts.method ?? 'GET', headers, body })
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', '서버에 연결할 수 없습니다. 서버가 켜져 있는지 확인하세요.')
  }

  if (res.status === 204) return undefined as T
  const text = await res.text()
  let data: unknown
  try {
    data = text ? JSON.parse(text) : undefined
  } catch {
    data = undefined // JSON 이 아닌 응답 (개발 서버 프록시 오류 등)
  }

  if (!res.ok) {
    // Spring 이 아직 켜지는 중이거나 꺼져 있으면 개발 서버 프록시가 본문 없이 502/504 를 돌려줌
    if (data === undefined && [502, 503, 504].includes(res.status)) {
      throw new ApiError(res.status, 'BACKEND_UNAVAILABLE', '백엔드 서버가 아직 준비되지 않았습니다. 잠시 후 다시 시도하세요.')
    }
    const err = (data ?? {}) as Partial<ApiErrorBody>
    if (res.status === 401 && token) window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    throw new ApiError(res.status, err.code ?? 'UNKNOWN', err.message ?? `요청 실패 (${res.status})`)
  }
  return data as T
}

/** 로그인이 필요한 이미지(<img>는 헤더를 못 붙임) → fetch 로 받아 blob URL 로 변환 */
export async function fetchImageUrl(path: string): Promise<string> {
  const token = tokenStore.get()
  const res = await fetch(path, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
  if (!res.ok) throw new ApiError(res.status, 'IMAGE_ERROR', '사진을 불러올 수 없습니다.')
  return URL.createObjectURL(await res.blob())
}

export const api = {
  // 4장 인증·회원
  signup: (body: { loginId: string; password: string; nickname: string; region?: string; email?: string }) =>
    request<AuthResponse>('/auth/signup', { method: 'POST', json: body }),
  login: (loginId: string, password: string) =>
    request<AuthResponse>('/auth/login', { method: 'POST', json: { loginId, password } }),
  me: () => request<Member>('/members/me'),
  updateMe: (body: { nickname?: string; region?: string; email?: string }) =>
    request<Member>('/members/me', { method: 'PATCH', json: body }),
  changePassword: (currentPassword: string, newPassword: string) =>
    request<void>('/members/me/password', { method: 'PUT', json: { currentPassword, newPassword } }),
  deleteMe: () => request<void>('/members/me', { method: 'DELETE' }),

  // 5장 진단
  diagnose: (image: File, crop: Crop) => {
    const form = new FormData()
    form.append('image', image)
    form.append('crop', crop)
    return request<Diagnosis>('/diagnoses', { method: 'POST', form })
  },
  diagnoses: (page: number, size: number, crop?: Crop) =>
    request<Page<DiagnosisListItem>>(`/diagnoses?page=${page}&size=${size}${crop ? `&crop=${crop}` : ''}`),
  diagnosis: (id: number) => request<Diagnosis>(`/diagnoses/${id}`),
  feedback: (id: number, feedback: Feedback) =>
    request<{ id: number; feedback: Feedback; feedbackAt: string }>(`/diagnoses/${id}/feedback`, { method: 'PUT', json: { feedback } }),
  deleteDiagnosis: (id: number) => request<void>(`/diagnoses/${id}`, { method: 'DELETE' }),

  // 6장 병 정보
  diseases: (crop?: Crop) => request<DiseaseSummary[]>(`/diseases${crop ? `?crop=${crop}` : ''}`),
  disease: (id: number) => request<DiseaseDetail>(`/diseases/${id}`),
}

/** 화면 표시용 오류 문구 */
export const errorMessage = (e: unknown) =>
  e instanceof ApiError ? e.message : '알 수 없는 오류가 발생했습니다.'
