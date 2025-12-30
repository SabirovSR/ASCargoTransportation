import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Truck, AlertCircle } from 'lucide-react'
import { useLogin } from '../hooks/useAuth'
import { LoadingSpinner } from '../components'

const loginSchema = z.object({
  email: z.string().email('Неверный адрес электронной почты'),
  password: z.string().min(1, 'Пароль обязателен'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const loginMutation = useLogin()
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginForm) => {
    loginMutation.mutate(data)
  }

  const errorMessage = loginMutation.error
    ? (loginMutation.error as any)?.response?.data?.error?.message || 'Ошибка входа'
    : null

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="flex justify-center">
            <div className="bg-primary-100 p-3 rounded-full">
              <Truck className="h-12 w-12 text-primary-600" />
            </div>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Грузоперевозки
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Войдите в свой аккаунт
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {errorMessage && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-700">{errorMessage}</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="label">
                Электронная почта
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                {...register('email')}
                className={`input ${errors.email ? 'input-error' : ''}`}
                placeholder="admin@freight.local"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="label">
                Пароль
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register('password')}
                className={`input ${errors.password ? 'input-error' : ''}`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="btn-primary w-full py-3"
          >
            {loginMutation.isPending ? (
              <LoadingSpinner size="sm" />
            ) : (
              'Войти'
            )}
          </button>

          <p className="text-center text-xs text-gray-500">
            Данные по умолчанию: admin@freight.local / admin123
          </p>
        </form>
      </div>
    </div>
  )
}
