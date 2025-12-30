import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/auth'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import RoutesPage from './pages/RoutesPage'
import RouteDetailPage from './pages/RouteDetailPage'
import NewRoutePage from './pages/NewRoutePage'
import UsersPage from './pages/UsersPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="routes" element={<RoutesPage />} />
        <Route path="routes/new" element={<NewRoutePage />} />
        <Route path="routes/:id" element={<RouteDetailPage />} />
        <Route path="admin/users" element={<UsersPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
