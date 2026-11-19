import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Layout() {
  const { member } = useAuth()
  return (
    <div className="app">
      <header className="topbar">
        <NavLink to="/" className="brand">🌱 작물 진단</NavLink>
        {member && <span className="muted small">{member.nickname}님</span>}
      </header>

      <main className="content">
        <Outlet />
      </main>

      {member && (
        <nav className="tabbar">
          <NavLink to="/" end>📷 진단</NavLink>
          <NavLink to="/history">🗂 기록</NavLink>
          <NavLink to="/diseases">📖 병 정보</NavLink>
          <NavLink to="/me">👤 내 정보</NavLink>
        </nav>
      )}
    </div>
  )
}
