import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { api, tokenStore, UNAUTHORIZED_EVENT } from '../api/client'
import type { AuthResponse, Member } from '../api/types'

interface AuthState {
  member: Member | null
  /** 저장된 토큰으로 내 정보를 확인하는 중 */
  loading: boolean
  login: (loginId: string, password: string) => Promise<void>
  signup: (body: Parameters<typeof api.signup>[0]) => Promise<void>
  logout: () => void
  setMember: (m: Member) => void
}

const AuthContext = createContext<AuthState | null>(null)

/** JWT 의 exp(만료 시각, 초) 읽기 — 서명 검증은 서버가 함 */
function tokenExpiresAt(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return typeof payload.exp === 'number' ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [member, setMember] = useState<Member | null>(null)
  // 저장된 토큰이 없거나 이미 만료됐으면 바로 '로그인 안 됨' 상태로 시작
  const [loading, setLoading] = useState(() => {
    const token = tokenStore.get()
    if (!token) return false
    const exp = tokenExpiresAt(token)
    if (exp !== null && exp <= Date.now()) {
      tokenStore.clear()
      return false
    }
    return true
  })

  const logout = useCallback(() => {
    tokenStore.clear()
    setMember(null)
  }, [])

  const accept = useCallback((res: AuthResponse) => {
    tokenStore.set(res.accessToken)
    setMember(res.member)
  }, [])

  // 새로고침 시: 저장된 토큰이 살아 있으면 내 정보로 로그인 상태 복원
  useEffect(() => {
    if (!tokenStore.get()) return
    api.me()
      .then(setMember)
      .catch(() => logout())
      .finally(() => setLoading(false))
  }, [logout])

  // 토큰 만료 시각이 되면 자동 로그아웃
  useEffect(() => {
    const token = tokenStore.get()
    if (!member || !token) return
    const exp = tokenExpiresAt(token)
    if (exp === null) return
    const timer = window.setTimeout(logout, Math.max(0, exp - Date.now()))
    return () => window.clearTimeout(timer)
  }, [member, logout])

  // API 가 401 을 돌려주면 로그아웃
  useEffect(() => {
    window.addEventListener(UNAUTHORIZED_EVENT, logout)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, logout)
  }, [logout])

  const value = useMemo<AuthState>(() => ({
    member,
    loading,
    login: async (loginId, password) => accept(await api.login(loginId, password)),
    signup: async (body) => accept(await api.signup(body)),
    logout,
    setMember,
  }), [member, loading, accept, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth 는 AuthProvider 안에서만 사용할 수 있습니다.')
  return ctx
}
