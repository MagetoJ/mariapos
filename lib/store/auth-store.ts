import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { User } from "@/lib/types"
import { authService } from "@/lib/api/data-service"

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string, roomNumber?: string) => Promise<boolean>
  logout: () => Promise<void>
  setUser: (user: User | null) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string, roomNumber?: string) => {
        set({ isLoading: true })
        try {
          const user = await authService.login(email, password, roomNumber)
          if (user) {
            set({ user, isAuthenticated: true, isLoading: false })
            return true
          }
          set({ isLoading: false })
          return false
        } catch (error) {
          set({ isLoading: false })
          return false
        }
      },

      logout: async () => {
        await authService.logout()
        set({ user: null, isAuthenticated: false })
      },

      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user })
      },
    }),
    {
      name: "auth-storage",
    },
  ),
)
