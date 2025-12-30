import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { routesApi, RouteCreate, RouteUpdate, RouteFilters, StopsUpdate } from '../api'

export function useRoutes(filters?: RouteFilters) {
  return useQuery({
    queryKey: ['routes', filters],
    queryFn: () => routesApi.list(filters),
  })
}

export function useRoute(id: string) {
  return useQuery({
    queryKey: ['routes', id],
    queryFn: () => routesApi.get(id),
    enabled: !!id,
  })
}

export function useCreateRoute() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: RouteCreate) => routesApi.create(data),
    onSuccess: (route) => {
      queryClient.invalidateQueries({ queryKey: ['routes'] })
      navigate(`/routes/${route.id}`)
    },
  })
}

export function useUpdateRoute() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: RouteUpdate }) =>
      routesApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['routes'] })
      queryClient.invalidateQueries({ queryKey: ['routes', id] })
    },
  })
}

export function useUpdateRouteStops() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: StopsUpdate }) =>
      routesApi.updateStops(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['routes'] })
      queryClient.invalidateQueries({ queryKey: ['routes', id] })
    },
  })
}

export function useCancelRoute() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => routesApi.cancel(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['routes'] })
      queryClient.invalidateQueries({ queryKey: ['routes', id] })
    },
  })
}
