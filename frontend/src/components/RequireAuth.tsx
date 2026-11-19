import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

/** 로그인이 필요한 화면 — 로그인 안 했으면 로그인 화면으로 (돌아올 주소 기억) */
export default function RequireAuth() {
  const { member, loading } = useAuth()
  const location = useLocation()
  if (loading) return <p className="center muted">불러오는 중…</p>
  if (!member) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return <Outlet />
}
