// Temporary simple auth store without Zustand
import { useEffect, useState } from "react"
import type { User } from "@/lib/types"
import { authService } from "@/lib/api/data-service"

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}

// Simple localStorage-based auth store
class AuthStore {
  private state: AuthState = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
  }

  private listeners: Set<() => void> = new Set()

  constructor() {
    if (typeof window !== 'undefined') {
      this.loadFromStorage()
    }
  }

  private loadFromStorage() {
    try {
      const stored = localStorage.getItem('auth-storage')
      if (stored) {
        const parsed = JSON.parse(stored)
        this.state = { ...this.state, ...parsed }
      }
    } catch (error) {
      console.error('Failed to load auth state from storage:', error)
    }
  }

  private saveToStorage() {
    try {
      localStorage.setItem('auth-storage', JSON.stringify({
        user: this.state.user,
        isAuthenticated: this.state.isAuthenticated,
      }))
    } catch (error) {
      console.error('Failed to save auth state to storage:', error)
    }
  }

  private notify() {
    this.listeners.forEach(listener => listener())
  }

  subscribe(listener: () => void) {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  getState() {
    return this.state
  }

  setUser(user: User | null) {
    this.state = {
      ...this.state,
      user,
      isAuthenticated: !!user,
    }
    this.saveToStorage()
    this.notify()
  }

  async login(email: string, password: string, roomNumber?: string): Promise<boolean> {
    this.state = { ...this.state, isLoading: true }
    this.notify()

    try {
      const user = await authService.login(email, password, roomNumber)
      if (user) {
        this.state = {
          ...this.state,
          user,
          isAuthenticated: true,
          isLoading: false,
        }
        this.saveToStorage()
        this.notify()
        return true
      }
      this.state = { ...this.state, isLoading: false }
      this.notify()
      return false
    } catch (error) {
      this.state = { ...this.state, isLoading: false }
      this.notify()
      return false
    }
  }

  async logout() {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
    this.state = {
      ...this.state,
      user: null,
      isAuthenticated: false,
    }
    this.saveToStorage()
    this.notify()
  }
}

const authStore = new AuthStore()

export function useAuthStore() {
  const [state, setState] = useState(authStore.getState())

  useEffect(() => {
    return authStore.subscribe(() => {
      setState(authStore.getState())
    })
  }, [])

  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    setUser: (user: User | null) => authStore.setUser(user),
    login: (email: string, password: string, roomNumber?: string) => authStore.login(email, password, roomNumber),
    logout: () => authStore.logout(),
  }
}