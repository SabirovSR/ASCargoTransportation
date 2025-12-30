import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authApi, LoginRequest } from '../api'
import { useAuthStore } from '../store/auth'

export function useLogin() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setAuth(response.user, response.access_token, response.refresh_token)
      navigate('/')
    },
  })
}

export function useLogout() {
  const navigate = useNavigate()
  const { refreshToken, logout } = useAuthStore()

  return useMutation({
    mutationFn: () => {
      if (refreshToken) {
        return authApi.logout(refreshToken)
      }
      return Promise.resolve()
    },
    onSettled: () => {
      logout()
      navigate('/login')
    },
  })
}

export function useCurrentUser() {
  const { isAuthenticated, user } = useAuthStore()

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authApi.getMe(),
    enabled: isAuthenticated,
    initialData: user || undefined,
  })
}

export function useChangePassword() {
  const { setUser } = useAuthStore()

  return useMutation({
    mutationFn: (data: { current_password: string; new_password: string }) =>
      authApi.changePassword(data),
    onSuccess: (user) => {
      setUser(user)
    },
  })
}
