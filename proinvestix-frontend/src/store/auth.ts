import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '@/lib/api'

export interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.login({ username, password })
          const { access_token, refresh_token } = response.data
          
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          
          // Fetch user data
          await get().fetchUser()
          
          set({ isAuthenticated: true, isLoading: false })
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Inloggen mislukt'
          set({ error: message, isLoading: false })
          throw error
        }
      },
      
      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          await authApi.register({ username, email, password })
          set({ isLoading: false })
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Registratie mislukt'
          set({ error: message, isLoading: false })
          throw error
        }
      },
      
      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, isAuthenticated: false })
      },
      
      fetchUser: async () => {
        try {
          const response = await authApi.me()
          set({ user: response.data, isAuthenticated: true })
        } catch (error) {
          set({ user: null, isAuthenticated: false })
        }
      },
      
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
