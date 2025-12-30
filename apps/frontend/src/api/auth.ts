import apiClient from './client'
import { LoginRequest, TokenResponse, User, ChangePasswordRequest } from './types'

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', data)
    return response.data
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken })
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },

  changePassword: async (data: ChangePasswordRequest): Promise<User> => {
    const response = await apiClient.post<User>('/auth/change-password', data)
    return response.data
  },
}
