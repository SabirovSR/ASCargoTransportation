// User types
export type UserRole = 'admin' | 'dispatcher' | 'viewer'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  must_change_password: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  email: string
  full_name: string
  password: string
  role: UserRole
}

export interface UserUpdate {
  full_name?: string
  role?: UserRole
  is_active?: boolean
}

// Auth types
export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

// Route types
export type RouteStatus = 'draft' | 'active' | 'completed' | 'cancelled'
export type StopType = 'origin' | 'stop' | 'destination'

export interface RouteStop {
  id: string
  route_id: string
  seq: number
  type: StopType
  address: string
  lat?: number | null
  lng?: number | null
  time_window_from?: string | null
  time_window_to?: string | null
  contact_name?: string | null
  contact_phone?: string | null
  created_at: string
}

export interface RouteStopCreate {
  seq: number
  type: StopType
  address: string
  lat?: number | null
  lng?: number | null
  time_window_from?: string | null
  time_window_to?: string | null
  contact_name?: string | null
  contact_phone?: string | null
}

export interface Route {
  id: string
  route_number: string
  title: string
  status: RouteStatus
  created_by: string
  created_by_user?: User | null
  planned_departure_at?: string | null
  comment?: string | null
  stops: RouteStop[]
  created_at: string
  updated_at: string
}

export interface RouteCreate {
  route_number?: string | null
  title: string
  planned_departure_at?: string | null
  comment?: string | null
  stops: RouteStopCreate[]
}

export interface RouteUpdate {
  title?: string
  planned_departure_at?: string | null
  comment?: string | null
  status?: RouteStatus
}

export interface StopsUpdate {
  stops: RouteStopCreate[]
}

// API response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface ErrorResponse {
  error: {
    code: string
    message: string
    details: Array<{ field?: string; message: string }>
  }
}

// Filter types
export interface RouteFilters {
  status?: RouteStatus
  q?: string
  created_by?: string
  from?: string
  to?: string
  limit?: number
  offset?: number
}
