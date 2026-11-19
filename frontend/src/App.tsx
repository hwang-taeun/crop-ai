import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import RequireAuth from './components/RequireAuth'
import DiagnosePage from './pages/DiagnosePage'
import DiseaseListPage from './pages/DiseaseListPage'
import DiseasePage from './pages/DiseasePage'
import HistoryPage from './pages/HistoryPage'
import LoginPage from './pages/LoginPage'
import MePage from './pages/MePage'
import ResultPage from './pages/ResultPage'
import SignupPage from './pages/SignupPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/diseases" element={<DiseaseListPage />} />
        <Route path="/diseases/:id" element={<DiseasePage />} />
        <Route element={<RequireAuth />}>
          <Route path="/" element={<DiagnosePage />} />
          <Route path="/diagnoses/:id" element={<ResultPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/me" element={<MePage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
