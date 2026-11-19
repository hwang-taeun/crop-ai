// docs/api-spec.md v1.1 의 요청·응답 형식

export type Crop = 'TOMATO' | 'POTATO' | 'CORN'
export type DiagnosisStatus = 'HEALTHY' | 'LIKELY' | 'POSSIBLE' | 'UNCERTAIN'
export type Feedback = 'CORRECT' | 'INCORRECT'

export const CROPS: { value: Crop; label: string; emoji: string }[] = [
  { value: 'TOMATO', label: '토마토', emoji: '🍅' },
  { value: 'POTATO', label: '감자', emoji: '🥔' },
  { value: 'CORN', label: '옥수수', emoji: '🌽' },
]

export const cropLabel = (c: Crop) => CROPS.find((x) => x.value === c)?.label ?? c

export interface ApiErrorBody {
  code: string
  message: string
  timestamp: string
}

export interface Member {
  id: number
  loginId: string
  nickname: string
  email: string | null
  region: string | null
  role: 'USER' | 'ADMIN'
  createdAt: string
}

export interface AuthResponse {
  accessToken: string
  tokenType: 'Bearer'
  expiresIn: number
  member: Member
}

export interface DiseaseSummary {
  id: number
  label: string
  nameKo: string
  crop: Crop
  healthy: boolean
}

export interface DiseaseDetail extends DiseaseSummary {
  description: string
  treatment: string
  source: string
  notice: string
}

export interface Candidate {
  rank: number
  confidence: number
  disease: DiseaseSummary
}

export interface Diagnosis {
  id: number
  crop: Crop
  status: DiagnosisStatus
  modelVersion: string | null
  createdAt: string
  imageUrl: string
  thumbnailUrl: string
  candidates: Candidate[]
  feedback: Feedback | null
  notice: string
}

export interface DiagnosisListItem {
  id: number
  crop: Crop
  status: DiagnosisStatus
  topCandidate: Candidate | null
  thumbnailUrl: string
  feedback: Feedback | null
  createdAt: string
}

export interface Page<T> {
  items: T[]
  page: number
  size: number
  totalItems: number
  totalPages: number
}
