import apiClient from './client'
import {
  Route,
  RouteCreate,
  RouteUpdate,
  StopsUpdate,
  PaginatedResponse,
  RouteFilters,
} from './types'

export const routesApi = {
  list: async (filters?: RouteFilters): Promise<PaginatedResponse<Route>> => {
    const response = await apiClient.get<PaginatedResponse<Route>>('/routes', {
      params: filters,
    })
    return response.data
  },

  get: async (id: string): Promise<Route> => {
    const response = await apiClient.get<Route>(`/routes/${id}`)
    return response.data
  },

  create: async (data: RouteCreate): Promise<Route> => {
    const response = await apiClient.post<Route>('/routes', data)
    return response.data
  },

  update: async (id: string, data: RouteUpdate): Promise<Route> => {
    const response = await apiClient.patch<Route>(`/routes/${id}`, data)
    return response.data
  },

  updateStops: async (id: string, data: StopsUpdate): Promise<Route> => {
    const response = await apiClient.put<Route>(`/routes/${id}/stops`, data)
    return response.data
  },

  cancel: async (id: string): Promise<Route> => {
    const response = await apiClient.post<Route>(`/routes/${id}/cancel`)
    return response.data
  },
}
