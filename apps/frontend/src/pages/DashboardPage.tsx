import { Link } from 'react-router-dom'
import { Route, CheckCircle, XCircle, Clock, Plus } from 'lucide-react'
import { useRoutes } from '../hooks/useRoutes'
import { useAuthStore } from '../store/auth'
import { LoadingSpinner } from '../components'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { data: allRoutes, isLoading } = useRoutes({ limit: 100 })
  
  const stats = {
    total: allRoutes?.total || 0,
    draft: allRoutes?.items.filter(r => r.status === 'draft').length || 0,
    active: allRoutes?.items.filter(r => r.status === 'active').length || 0,
    completed: allRoutes?.items.filter(r => r.status === 'completed').length || 0,
    cancelled: allRoutes?.items.filter(r => r.status === 'cancelled').length || 0,
  }

  const canCreateRoute = user?.role === 'admin' || user?.role === 'dispatcher'

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Панель управления</h1>
          <p className="text-gray-600">Добро пожаловать, {user?.full_name}</p>
        </div>
        {canCreateRoute && (
          <Link to="/routes/new" className="btn-primary">
            <Plus className="h-4 w-4 mr-2" />
            Новый маршрут
          </Link>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-primary-100">
              <Route className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Всего маршрутов</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Активные</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.active}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Черновики</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.draft}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-red-100">
              <XCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Отменённые</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.cancelled}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Routes */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Последние маршруты</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Номер маршрута
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Название
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Статус
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Остановки
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {allRoutes?.items.slice(0, 5).map((route) => (
                <tr key={route.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link to={`/routes/${route.id}`} className="text-primary-600 hover:text-primary-800">
                      {route.route_number}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {route.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge badge-${route.status}`}>
                      {route.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {route.stops.length} ост.
                  </td>
                </tr>
              ))}
              {allRoutes?.items.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                    Пока нет маршрутов. Создайте первый маршрут!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        {(allRoutes?.total || 0) > 5 && (
          <div className="px-6 py-4 border-t border-gray-200">
            <Link to="/routes" className="text-primary-600 hover:text-primary-800 text-sm font-medium">
              Посмотреть все маршруты →
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
