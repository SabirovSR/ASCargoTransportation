import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, User, Phone, Edit, XCircle, CheckCircle } from 'lucide-react'
import { format } from 'date-fns'
import { useRoute, useUpdateRoute, useCancelRoute } from '../hooks/useRoutes'
import { useAuthStore } from '../store/auth'
import { LoadingSpinner, StatusBadge, Modal } from '../components'

export default function RouteDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuthStore()
  const { data: route, isLoading, error } = useRoute(id!)
  const updateMutation = useUpdateRoute()
  const cancelMutation = useCancelRoute()
  
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editComment, setEditComment] = useState('')

  const canEdit = (user?.role === 'admin' || user?.role === 'dispatcher') && 
    route?.status !== 'cancelled' && route?.status !== 'completed'
  const canCancel = canEdit && route?.status !== 'cancelled'
  const canActivate = canEdit && route?.status === 'draft'

  const handleCancel = () => {
    if (id) {
      cancelMutation.mutate(id, {
        onSuccess: () => setShowCancelModal(false),
      })
    }
  }

  const handleActivate = () => {
    if (id) {
      updateMutation.mutate({
        id,
        data: { status: 'active' },
      })
    }
  }

  const handleSaveEdit = () => {
    if (id) {
      updateMutation.mutate({
        id,
        data: { 
          title: editTitle || undefined,
          comment: editComment || undefined,
        },
      }, {
        onSuccess: () => setIsEditing(false),
      })
    }
  }

  const startEdit = () => {
    setEditTitle(route?.title || '')
    setEditComment(route?.comment || '')
    setIsEditing(true)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error || !route) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Route not found</p>
        <Link to="/routes" className="text-primary-600 hover:underline mt-4 inline-block">
          Back to routes
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/routes" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{route.route_number}</h1>
              <StatusBadge status={route.status} />
            </div>
            <p className="text-gray-600">{route.title}</p>
          </div>
        </div>

        <div className="flex gap-2">
          {canActivate && (
            <button
              onClick={handleActivate}
              disabled={updateMutation.isPending}
              className="btn-primary"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Activate
            </button>
          )}
          {canEdit && (
            <button onClick={startEdit} className="btn-secondary">
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </button>
          )}
          {canCancel && (
            <button
              onClick={() => setShowCancelModal(true)}
              className="btn-danger"
            >
              <XCircle className="h-4 w-4 mr-2" />
              Cancel Route
            </button>
          )}
        </div>
      </div>

      {/* Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Route Stops */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Route Stops</h2>
            <div className="space-y-4">
              {route.stops.map((stop, index) => (
                <div key={stop.id} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                      stop.type === 'origin' ? 'bg-green-500' :
                      stop.type === 'destination' ? 'bg-red-500' : 'bg-blue-500'
                    }`}>
                      {stop.seq}
                    </div>
                    {index < route.stops.length - 1 && (
                      <div className="w-0.5 h-12 bg-gray-300 my-1" />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className={`text-xs font-medium uppercase ${
                          stop.type === 'origin' ? 'text-green-600' :
                          stop.type === 'destination' ? 'text-red-600' : 'text-blue-600'
                        }`}>
                          {stop.type}
                        </span>
                        <p className="font-medium text-gray-900 mt-1">{stop.address}</p>
                      </div>
                    </div>
                    {(stop.contact_name || stop.contact_phone) && (
                      <div className="mt-2 flex gap-4 text-sm text-gray-500">
                        {stop.contact_name && (
                          <span className="flex items-center gap-1">
                            <User className="h-4 w-4" />
                            {stop.contact_name}
                          </span>
                        )}
                        {stop.contact_phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="h-4 w-4" />
                            {stop.contact_phone}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Comment */}
          {route.comment && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Comment</h2>
              <p className="text-gray-600 whitespace-pre-wrap">{route.comment}</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Details</h2>
            <dl className="space-y-4">
              <div>
                <dt className="text-sm text-gray-500">Created by</dt>
                <dd className="font-medium text-gray-900">
                  {route.created_by_user?.full_name || '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Created at</dt>
                <dd className="font-medium text-gray-900">
                  {format(new Date(route.created_at), 'MMM d, yyyy HH:mm')}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Updated at</dt>
                <dd className="font-medium text-gray-900">
                  {format(new Date(route.updated_at), 'MMM d, yyyy HH:mm')}
                </dd>
              </div>
              {route.planned_departure_at && (
                <div>
                  <dt className="text-sm text-gray-500">Planned departure</dt>
                  <dd className="font-medium text-gray-900">
                    {format(new Date(route.planned_departure_at), 'MMM d, yyyy HH:mm')}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>

      {/* Cancel Modal */}
      <Modal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        title="Cancel Route"
      >
        <p className="text-gray-600 mb-4">
          Are you sure you want to cancel route <strong>{route.route_number}</strong>?
          This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={() => setShowCancelModal(false)}
            className="btn-secondary"
          >
            No, keep it
          </button>
          <button
            onClick={handleCancel}
            disabled={cancelMutation.isPending}
            className="btn-danger"
          >
            {cancelMutation.isPending ? <LoadingSpinner size="sm" /> : 'Yes, cancel'}
          </button>
        </div>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditing}
        onClose={() => setIsEditing(false)}
        title="Edit Route"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Title</label>
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="label">Comment</label>
            <textarea
              value={editComment}
              onChange={(e) => setEditComment(e.target.value)}
              rows={3}
              className="input"
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setIsEditing(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveEdit}
              disabled={updateMutation.isPending}
              className="btn-primary"
            >
              {updateMutation.isPending ? <LoadingSpinner size="sm" /> : 'Save'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
