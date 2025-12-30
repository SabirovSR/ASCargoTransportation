import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Users, Key } from 'lucide-react'
import { useUsers, useCreateUser, useUpdateUser, useResetPassword } from '../hooks/useUsers'
import { useAuthStore } from '../store/auth'
import { User, UserRole } from '../api/types'
import { LoadingSpinner, EmptyState, Modal, Pagination } from '../components'
import { format } from 'date-fns'

const LIMIT = 10

const createUserSchema = z.object({
  email: z.string().email('Invalid email address'),
  full_name: z.string().min(1, 'Name is required'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  role: z.enum(['admin', 'dispatcher', 'viewer'] as const),
})

type CreateUserForm = z.infer<typeof createUserSchema>

export default function UsersPage() {
  const { user: currentUser } = useAuthStore()
  const [offset, setOffset] = useState(0)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [resetPasswordUser, setResetPasswordUser] = useState<User | null>(null)
  const [newPassword, setNewPassword] = useState('')

  const { data, isLoading } = useUsers({ limit: LIMIT, offset })
  const createMutation = useCreateUser()
  const updateMutation = useUpdateUser()
  const resetPasswordMutation = useResetPassword()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateUserForm>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      role: 'viewer',
    },
  })

  const onCreateSubmit = (data: CreateUserForm) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        setShowCreateModal(false)
        reset()
      },
    })
  }

  const handleUpdateRole = (userId: string, role: UserRole) => {
    updateMutation.mutate({ id: userId, data: { role } })
  }

  const handleToggleActive = (userId: string, isActive: boolean) => {
    updateMutation.mutate({ id: userId, data: { is_active: !isActive } })
  }

  const handleResetPassword = () => {
    if (resetPasswordUser && newPassword) {
      resetPasswordMutation.mutate(
        { id: resetPasswordUser.id, newPassword },
        {
          onSuccess: () => {
            setResetPasswordUser(null)
            setNewPassword('')
          },
        }
      )
    }
  }

  if (currentUser?.role !== 'admin') {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">You don't have permission to view this page.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Users</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          New User
        </button>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : data?.items.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No users found"
            description="Create your first user to get started"
            action={
              <button onClick={() => setShowCreateModal(true)} className="btn-primary">
                <Plus className="h-4 w-4 mr-2" />
                Create User
              </button>
            }
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created At
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data?.items.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                            <span className="text-primary-600 font-medium">
                              {user.full_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="font-medium text-gray-900">{user.full_name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <select
                          value={user.role}
                          onChange={(e) => handleUpdateRole(user.id, e.target.value as UserRole)}
                          disabled={user.id === currentUser?.id}
                          className="input py-1 px-2 w-32"
                        >
                          <option value="admin">Admin</option>
                          <option value="dispatcher">Dispatcher</option>
                          <option value="viewer">Viewer</option>
                        </select>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleToggleActive(user.id, user.is_active)}
                          disabled={user.id === currentUser?.id}
                          className={`badge ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {format(new Date(user.created_at), 'MMM d, yyyy')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => setResetPasswordUser(user)}
                          className="text-primary-600 hover:text-primary-800"
                          title="Reset Password"
                        >
                          <Key className="h-4 w-4" />
                        </button>
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

      {/* Create User Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          reset()
        }}
        title="Create User"
      >
        <form onSubmit={handleSubmit(onCreateSubmit)} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input
              {...register('email')}
              type="email"
              className={`input ${errors.email ? 'input-error' : ''}`}
              placeholder="user@example.com"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="label">Full Name</label>
            <input
              {...register('full_name')}
              className={`input ${errors.full_name ? 'input-error' : ''}`}
              placeholder="John Doe"
            />
            {errors.full_name && (
              <p className="mt-1 text-sm text-red-600">{errors.full_name.message}</p>
            )}
          </div>

          <div>
            <label className="label">Password</label>
            <input
              {...register('password')}
              type="password"
              className={`input ${errors.password ? 'input-error' : ''}`}
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label className="label">Role</label>
            <select {...register('role')} className="input">
              <option value="viewer">Viewer</option>
              <option value="dispatcher">Dispatcher</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                setShowCreateModal(false)
                reset()
              }}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="btn-primary"
            >
              {createMutation.isPending ? <LoadingSpinner size="sm" /> : 'Create'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Reset Password Modal */}
      <Modal
        isOpen={!!resetPasswordUser}
        onClose={() => {
          setResetPasswordUser(null)
          setNewPassword('')
        }}
        title="Reset Password"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Reset password for <strong>{resetPasswordUser?.full_name}</strong>
          </p>
          <div>
            <label className="label">New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="input"
              placeholder="••••••••"
              minLength={6}
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => {
                setResetPasswordUser(null)
                setNewPassword('')
              }}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleResetPassword}
              disabled={resetPasswordMutation.isPending || newPassword.length < 6}
              className="btn-primary"
            >
              {resetPasswordMutation.isPending ? <LoadingSpinner size="sm" /> : 'Reset'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
