import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter, Route } from 'lucide-react'
import { useRoutes } from '../hooks/useRoutes'
import { useAuthStore } from '../store/auth'
import { RouteStatus } from '../api/types'
import { LoadingSpinner, EmptyState, StatusBadge, Pagination } from '../components'
import { format } from 'date-fns'

const LIMIT = 10

export default function RoutesPage() {
  const { user } = useAuthStore()
  const [offset, setOffset] = useState(0)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<RouteStatus | ''>('')

  const { data, isLoading } = useRoutes({
    limit: LIMIT,
    offset,
    q: search || undefined,
    status: status || undefined,
  })

  const canCreateRoute = user?.role === 'admin' || user?.role === 'dispatcher'

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setOffset(0)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Маршруты</h1>
        {canCreateRoute && (
          <Link to="/routes/new" className="btn-primary">
            <Plus className="h-4 w-4 mr-2" />
            Новый маршрут
          </Link>
        )}
      </div>

      {/* Filters */}
      <div className="card p-4">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по номеру или названию маршрута..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>
          <div className="w-full sm:w-48">
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value as RouteStatus | '')
                setOffset(0)
              }}
              className="input"
            >
              <option value="">Все статусы</option>
              <option value="draft">Черновик</option>
              <option value="active">Активен</option>
              <option value="completed">Завершён</option>
              <option value="cancelled">Отменён</option>
            </select>
          </div>
          <button type="submit" className="btn-secondary">
            <Filter className="h-4 w-4 mr-2" />
            Фильтр
          </button>
        </form>
      </div>

      {/* Routes list */}
      <div className="card">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : data?.items.length === 0 ? (
          <EmptyState
            icon={Route}
            title="Маршруты не найдены"
            description={search || status ? "Попробуйте изменить фильтры" : "Создайте первый маршрут для начала работы"}
            action={
              canCreateRoute && !search && !status && (
                <Link to="/routes/new" className="btn-primary">
                  <Plus className="h-4 w-4 mr-2" />
                  Создать маршрут
                </Link>
              )
            }
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Маршрут
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Статус
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Остановки
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Создал
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Дата создания
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data?.items.map((route) => (
                    <tr key={route.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link to={`/routes/${route.id}`} className="flex flex-col">
                          <span className="text-primary-600 hover:text-primary-800 font-medium">
                            {route.route_number}
                          </span>
                          <span className="text-sm text-gray-500">{route.title}</span>
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={route.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {route.stops.length} ост.
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {route.created_by_user?.full_name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {format(new Date(route.created_at), 'MMM d, yyyy HH:mm')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              total={data?.total || 0}
              limit={LIMIT}
              offset={offset}
              onPageChange={setOffset}
            />
          </>
        )}
      </div>
    </div>
  )
}
