import { AxiosError } from 'axios'
import { ErrorResponse } from '../api/types'

/**
 * Извлекает сообщение об ошибке из axios error
 */
export function getErrorMessage(error: unknown, defaultMessage = 'Произошла ошибка'): string {
  if (error instanceof AxiosError) {
    const errorResponse = error.response?.data as ErrorResponse | undefined
    return errorResponse?.error?.message || defaultMessage
  }
  
  if (error instanceof Error) {
    return error.message
  }
  
  return defaultMessage
}

