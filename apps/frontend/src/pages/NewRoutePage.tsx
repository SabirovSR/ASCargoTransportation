import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { ArrowLeft, Plus, Trash2, GripVertical } from 'lucide-react'
import { useCreateRoute } from '../hooks/useRoutes'
import { LoadingSpinner } from '../components'
import { StopType } from '../api/types'

const stopSchema = z.object({
  seq: z.number().min(1),
  type: z.enum(['origin', 'stop', 'destination'] as const),
  address: z.string().min(1, 'Address is required'),
  contact_name: z.string().optional().nullable(),
  contact_phone: z.string().optional().nullable(),
})

const routeSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  route_number: z.string().optional().nullable(),
  planned_departure_at: z.string().optional().nullable(),
  comment: z.string().optional().nullable(),
  stops: z.array(stopSchema).min(2, 'At least 2 stops are required'),
}).refine((data) => {
  const types = data.stops.map(s => s.type)
  return types.includes('origin') && types.includes('destination')
}, {
  message: 'Route must have origin and destination stops',
  path: ['stops'],
})

type RouteForm = z.infer<typeof routeSchema>

const defaultStop = (seq: number, type: StopType) => ({
  seq,
  type,
  address: '',
  contact_name: null,
  contact_phone: null,
})

export default function NewRoutePage() {
  const createMutation = useCreateRoute()

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RouteForm>({
    resolver: zodResolver(routeSchema),
    defaultValues: {
      title: '',
      route_number: null,
      planned_departure_at: null,
      comment: null,
      stops: [
        defaultStop(1, 'origin'),
        defaultStop(2, 'destination'),
      ],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'stops',
  })

  const onSubmit = (data: RouteForm) => {
    // Re-sequence stops
    const stops = data.stops.map((stop, index) => ({
      ...stop,
      seq: index + 1,
    }))
    createMutation.mutate({ ...data, stops })
  }

  const addIntermediateStop = () => {
    const newSeq = fields.length
    append(defaultStop(newSeq, 'stop'))
  }

  const errorMessage = createMutation.error
    ? (createMutation.error as any)?.response?.data?.error?.message || 'Failed to create route'
    : null

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/routes" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">New Route</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {errorMessage && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-700">{errorMessage}</p>
          </div>
        )}

        {/* Basic Info */}
        <div className="card p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Route Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Title *</label>
              <input
                {...register('title')}
                className={`input ${errors.title ? 'input-error' : ''}`}
                placeholder="Moscow - Saint Petersburg"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label className="label">Route Number (optional)</label>
              <input
                {...register('route_number')}
                className="input"
                placeholder="Auto-generated if empty"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Planned Departure</label>
              <input
                type="datetime-local"
                {...register('planned_departure_at')}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="label">Comment</label>
            <textarea
              {...register('comment')}
              rows={3}
              className="input"
              placeholder="Additional notes..."
            />
          </div>
        </div>

        {/* Stops */}
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Route Stops</h2>
            <button
              type="button"
              onClick={addIntermediateStop}
              className="btn-secondary btn-sm"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Stop
            </button>
          </div>

          {errors.stops && typeof errors.stops.message === 'string' && (
            <p className="text-sm text-red-600">{errors.stops.message}</p>
          )}

          <div className="space-y-4">
            {fields.map((field, index) => (
              <div
                key={field.id}
                className="flex gap-4 p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center text-gray-400">
                  <GripVertical className="h-5 w-5" />
                </div>

                <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="label">Type</label>
                    <select
                      {...register(`stops.${index}.type`)}
                      className="input"
                    >
                      <option value="origin">Origin</option>
                      <option value="stop">Intermediate</option>
                      <option value="destination">Destination</option>
                    </select>
                  </div>

                  <div className="md:col-span-2">
                    <label className="label">Address *</label>
                    <input
                      {...register(`stops.${index}.address`)}
                      className={`input ${errors.stops?.[index]?.address ? 'input-error' : ''}`}
                      placeholder="Enter address"
                    />
                    {errors.stops?.[index]?.address && (
                      <p className="mt-1 text-sm text-red-600">
                        {errors.stops[index]?.address?.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="label">Contact Name</label>
                    <input
                      {...register(`stops.${index}.contact_name`)}
                      className="input"
                      placeholder="John Doe"
                    />
                  </div>

                  <div>
                    <label className="label">Contact Phone</label>
                    <input
                      {...register(`stops.${index}.contact_phone`)}
                      className="input"
                      placeholder="+7 999 123 4567"
                    />
                  </div>
                </div>

                {fields.length > 2 && (
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded self-start"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Link to="/routes" className="btn-secondary">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="btn-primary"
          >
            {createMutation.isPending ? (
              <LoadingSpinner size="sm" />
            ) : (
              'Create Route'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
