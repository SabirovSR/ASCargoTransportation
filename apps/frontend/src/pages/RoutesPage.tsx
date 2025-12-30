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
        <h1 className="text-2xl font-bold text-gray-900">Routes</h1>
        {canCreateRoute && (
          <Link to="/routes/new" className="btn-primary">
            <Plus className="h-4 w-4 mr-2" />
            New Route
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
                placeholder="Search by route number or title..."
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
              <option value="">All statuses</option>
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <button type="submit" className="btn-secondary">
            <Filter className="h-4 w-4 mr-2" />
            Filter
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
            title="No routes found"
            description={search || status ? "Try adjusting your filters" : "Create your first route to get started"}
            action={
              canCreateRoute && !search && !status && (
                <Link to="/routes/new" className="btn-primary">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Route
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
                      Route
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stops
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created By
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created At
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
                        {route.stops.length} stops
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
