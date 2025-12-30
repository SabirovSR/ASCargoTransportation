import apiClient from './client'
import { User, UserCreate, UserUpdate, PaginatedResponse } from './types'

export const usersApi = {
  list: async (params?: { limit?: number; offset?: number }): Promise<PaginatedResponse<User>> => {
    const response = await apiClient.get<PaginatedResponse<User>>('/users', { params })
    return response.data
  },

  get: async (id: string): Promise<User> => {
    const response = await apiClient.get<User>(`/users/${id}`)
    return response.data
  },

  create: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users', data)
    return response.data
  },

  update: async (id: string, data: UserUpdate): Promise<User> => {
    const response = await apiClient.patch<User>(`/users/${id}`, data)
    return response.data
  },

  resetPassword: async (id: string, newPassword: string): Promise<User> => {
    const response = await apiClient.post<User>(`/users/${id}/reset-password`, {
      new_password: newPassword,
    })
    return response.data
  },
}
