/**
 * Data Service Layer
 *
 * This file provides an abstraction layer for data access.
 * Integrates with Django backend API for the Maria Havens POS system.
 */

import type {
  User,
  MenuItem,
  Order,
  Table,
  InventoryItem,
  DashboardStats,
  SalesData,
  CategorySales,
  Guest,
  ServiceRequest,
  Receipt,
} from "@/lib/types"

// Base URL for Django API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

// Auth token management
function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth-token')
  }
  return null
}

function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth-token', token)
  }
}

function removeAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth-token')
  }
}

// Helper function for Django API calls
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = getAuthToken()
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options?.headers,
    },
  })
  
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid, remove from storage
      removeAuthToken()
      throw new Error('Authentication required')
    }
    
    let errorData
    try {
      errorData = await response.json()
    } catch (e) {
      errorData = { error: response.statusText }
    }
    
    const errorMessage = errorData.error || errorData.message || errorData.detail || `API Error: ${response.statusText}`
    throw new Error(errorMessage)
  }
  
  return response.json()
}

// Authentication
export const authService = {
  async login(email: string, password: string, roomNumber?: string): Promise<User | null> {
    try {
      const loginData: any = { email, password }
      if (roomNumber) {
        loginData.room_number = roomNumber // Use underscore format expected by Django
      }

      const response = await apiCall<{ user: User; access: string; refresh: string }>('/auth/login/', {
        method: 'POST',
        body: JSON.stringify(loginData),
      })

      // Store the JWT access token
      setAuthToken(response.access)
      
      // Store refresh token
      if (typeof window !== 'undefined' && response.refresh) {
        localStorage.setItem('refresh-token', response.refresh)
      }

      return response.user
    } catch (error) {
      console.error('Login failed:', error)
      return null
    }
  },

  async logout(): Promise<void> {
    try {
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh-token') : null
      if (refreshToken) {
        await apiCall('/auth/logout/', { 
          method: 'POST',
          body: JSON.stringify({ refresh_token: refreshToken })
        })
      }
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      // Always remove tokens from storage
      removeAuthToken()
      if (typeof window !== 'undefined') {
        localStorage.removeItem('refresh-token')
      }
    }
  },

  async getCurrentUser(): Promise<User | null> {
    try {
      return await apiCall<User>('/auth/me/')
    } catch (error) {
      console.error('Get current user failed:', error)
      return null
    }
  },

  async refreshToken(): Promise<string | null> {
    try {
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh-token') : null
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      const response = await apiCall<{ token: string; refreshToken: string }>('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refreshToken }),
      })

      setAuthToken(response.token)
      if (typeof window !== 'undefined') {
        localStorage.setItem('refresh-token', response.refreshToken)
      }

      return response.token
    } catch (error) {
      console.error('Token refresh failed:', error)
      removeAuthToken()
      if (typeof window !== 'undefined') {
        localStorage.removeItem('refresh-token')
      }
      return null
    }
  },
}

// Users
export const userService = {
  async getUsers(params?: { role?: string; isActive?: boolean }): Promise<User[]> {
    const queryParams = new URLSearchParams()
    if (params?.role) queryParams.append('role', params.role)
    if (params?.isActive !== undefined) queryParams.append('isActive', params.isActive.toString())
    
    const query = queryParams.toString()
    // FIX APPLIED: Ensures trailing slash is present before query string
    const endpoint = `/users/${query ? `?${query}` : ''}`
    const data = await apiCall<User[] | { results: User[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getUserById(id: string): Promise<User | null> {
    try {
      return await apiCall<User>(`/users/${id}/`)
    } catch (error) {
      console.error('Get user by ID failed:', error)
      return null
    }
  },

  async createUser(user: Omit<User, "id" | "createdAt">): Promise<User> {
    return apiCall<User>('/users/', { 
      method: 'POST', 
      body: JSON.stringify(user) 
    })
  },

  async updateUser(id: string, updates: Partial<User>): Promise<User> {
    return apiCall<User>(`/users/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },

  async deleteUser(id: string): Promise<void> {
    return apiCall(`/users/${id}/`, { method: 'DELETE' })
  },

  async changePassword(id: string, currentPassword: string, newPassword: string): Promise<void> {
    return apiCall(`/users/${id}/change-password/`, {
      method: 'POST',
      body: JSON.stringify({ currentPassword, newPassword })
    })
  },
}

// Menu
export const menuService = {
  async getMenuItems(params?: { category?: string; isAvailable?: boolean }): Promise<MenuItem[]> {
    const queryParams = new URLSearchParams()
    if (params?.category) queryParams.append('category', params.category)
    if (params?.isAvailable !== undefined) queryParams.append('isAvailable', params.isAvailable.toString())
    
    const query = queryParams.toString()
    // FIX APPLIED: Ensures trailing slash is present before query string
    const endpoint = `/menu/${query ? `?${query}` : ''}`
    const data = await apiCall<MenuItem[] | { results: MenuItem[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getMenuItemById(id: string): Promise<MenuItem | null> {
    try {
      return await apiCall<MenuItem>(`/menu/${id}/`)
    } catch (error) {
      console.error('Get menu item by ID failed:', error)
      return null
    }
  },

  async createMenuItem(item: Omit<MenuItem, "id">): Promise<MenuItem> {
    return apiCall<MenuItem>('/menu/', { 
      method: 'POST', 
      body: JSON.stringify(item) 
    })
  },

  async updateMenuItem(id: string, updates: Partial<MenuItem>): Promise<MenuItem> {
    return apiCall<MenuItem>(`/menu/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },

  async deleteMenuItem(id: string): Promise<void> {
    return apiCall(`/menu/${id}/`, { method: 'DELETE' })
  },
}

// Orders
export const orderService = {
  async getOrders(params?: { 
    status?: string; 
    type?: string; 
    waiterId?: string; 
    roomNumber?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<Order[]> {
    const queryParams = new URLSearchParams()
    if (params?.status) queryParams.append('status', params.status)
    if (params?.type) queryParams.append('type', params.type)
    if (params?.waiterId) queryParams.append('waiterId', params.waiterId)
    if (params?.roomNumber) queryParams.append('roomNumber', params.roomNumber)
    if (params?.startDate) queryParams.append('startDate', params.startDate)
    if (params?.endDate) queryParams.append('endDate', params.endDate)
    
    const query = queryParams.toString()
    // FIX APPLIED: Ensures trailing slash is present before query string
    const endpoint = `/orders/${query ? `?${query}` : ''}`
    const data = await apiCall<Order[] | { results: Order[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getOrderById(id: string): Promise<Order | null> {
    try {
      return await apiCall<Order>(`/orders/${id}/`)
    } catch (error) {
      console.error('Get order by ID failed:', error)
      return null
    }
  },

  async createOrder(order: Omit<Order, "id" | "orderNumber" | "createdAt" | "updatedAt">): Promise<Order> {
    return apiCall<Order>('/orders/', { 
      method: 'POST', 
      body: JSON.stringify(order) 
    })
  },

  async updateOrder(id: string, updates: Partial<Order>): Promise<Order> {
    return apiCall<Order>(`/orders/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },
}

// Tables
export const tableService = {
  async getTables(params?: { status?: string; section?: string }): Promise<Table[]> {
    const queryParams = new URLSearchParams()
    if (params?.status) queryParams.append('status', params.status)
    if (params?.section) queryParams.append('section', params.section)
    
    const query = queryParams.toString()
    // FIX APPLIED: Ensures trailing slash is present before query string
    const endpoint = `/tables/${query ? `?${query}` : ''}`
    const data = await apiCall<Table[] | { results: Table[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getTableById(id: string): Promise<Table | null> {
    try {
      return await apiCall<Table>(`/tables/${id}/`)
    } catch (error) {
      console.error('Get table by ID failed:', error)
      return null
    }
  },

  async updateTable(id: string, updates: Partial<Table>): Promise<Table> {
    return apiCall<Table>(`/tables/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },
}

// Inventory
export const inventoryService = {
  async getInventory(params?: { category?: string; lowStock?: boolean }): Promise<InventoryItem[]> {
    const queryParams = new URLSearchParams()
    if (params?.category) queryParams.append('category', params.category)
    if (params?.lowStock !== undefined) queryParams.append('lowStock', params.lowStock.toString())
    
    const query = queryParams.toString()
    // FIX APPLIED: Ensures trailing slash is present before query string
    const endpoint = `/inventory/${query ? `?${query}` : ''}`
    const data = await apiCall<InventoryItem[] | { results: InventoryItem[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getInventoryItemById(id: string): Promise<InventoryItem | null> {
    try {
      return await apiCall<InventoryItem>(`/inventory/${id}/`)
    } catch (error) {
      console.error('Get inventory item by ID failed:', error)
      return null
    }
  },

  async createInventoryItem(item: Omit<InventoryItem, "id">): Promise<InventoryItem> {
    return apiCall<InventoryItem>('/inventory/', { 
      method: 'POST', 
      body: JSON.stringify(item) 
    })
  },

  async updateInventoryItem(id: string, updates: Partial<InventoryItem>): Promise<InventoryItem> {
    return apiCall<InventoryItem>(`/inventory/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },

  async getLowStockItems(): Promise<InventoryItem[]> {
    return apiCall<InventoryItem[]>('/inventory/low-stock/')
  },

  async trackWaste(itemId: string, quantity: number, reason: string): Promise<void> {
    return apiCall('/inventory/waste/', {
      method: 'POST',
      body: JSON.stringify({ itemId, quantity, reason })
    })
  },
}

// Dashboard
export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    return apiCall<DashboardStats>('/dashboard/stats/')
  },

  async getSalesData(days = 7): Promise<SalesData[]> {
    return apiCall<SalesData[]>(`/dashboard/sales/?days=${days}`)
  },

  async getCategorySales(): Promise<CategorySales[]> {
    return apiCall<CategorySales[]>('/dashboard/category-sales/')
  },
}

// Guests
export const guestService = {
  async getGuests(params?: { status?: string; roomNumber?: string }): Promise<Guest[]> {
    const queryParams = new URLSearchParams()
    if (params?.status) queryParams.append('status', params.status)
    if (params?.roomNumber) queryParams.append('roomNumber', params.roomNumber)
    
    const query = queryParams.toString()
    // FIX APPLIED: Ensures trailing slash is present before query string
    const endpoint = `/guests/${query ? `?${query}` : ''}`
    const data = await apiCall<Guest[] | { results: Guest[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getGuestById(id: string): Promise<Guest | null> {
    try {
      return await apiCall<Guest>(`/guests/${id}/`)
    } catch (error) {
      console.error('Get guest by ID failed:', error)
      return null
    }
  },

  async checkInGuest(guest: Omit<Guest, "id" | "checkInTime" | "status">): Promise<Guest> {
    return apiCall<Guest>('/guests/check-in/', { 
      method: 'POST', 
      body: JSON.stringify(guest) 
    })
  },

  async checkOutGuest(id: string): Promise<Guest> {
    return apiCall<Guest>(`/guests/${id}/check-out/`, { method: 'POST' })
  },

  async updateGuest(id: string, updates: Partial<Guest>): Promise<Guest> {
    return apiCall<Guest>(`/guests/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },
}

// Service Requests
export const serviceRequestService = {
  async getServiceRequests(params?: { status?: string; type?: string; roomNumber?: string }): Promise<ServiceRequest[]> {
    const queryParams = new URLSearchParams()
    if (params?.status) queryParams.append('status', params.status)
    if (params?.type) queryParams.append('type', params.type)
    if (params?.roomNumber) queryParams.append('roomNumber', params.roomNumber)
    
    const query = queryParams.toString()
    // FIX APPLIED: Ensures trailing slash is present before query string
    const endpoint = `/service-requests/${query ? `?${query}` : ''}`
    const data = await apiCall<ServiceRequest[] | { results: ServiceRequest[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async createServiceRequest(request: Omit<ServiceRequest, "id" | "createdAt" | "updatedAt">): Promise<ServiceRequest> {
    return apiCall<ServiceRequest>('/service-requests/', { 
      method: 'POST', 
      body: JSON.stringify(request) 
    })
  },

  async updateServiceRequest(id: string, updates: Partial<ServiceRequest>): Promise<ServiceRequest> {
    return apiCall<ServiceRequest>(`/service-requests/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },
}

// Receipts
export const receiptService = {
  async getReceipts(params?: { orderId?: string; dateFrom?: string; dateTo?: string }): Promise<Receipt[]> {
    const queryParams = new URLSearchParams()
    if (params?.orderId) queryParams.append('orderId', params.orderId)
    if (params?.dateFrom) queryParams.append('dateFrom', params.dateFrom)
    if (params?.dateTo) queryParams.append('dateTo', params.dateTo)
    
    const query = queryParams.toString()
    const endpoint = `/receipts/${query ? `?${query}` : ''}`
    const data = await apiCall<Receipt[] | { results: Receipt[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getReceiptById(id: string): Promise<Receipt | null> {
    try {
      return await apiCall<Receipt>(`/receipts/${id}/`)
    } catch (error) {
      console.error('Get receipt by ID failed:', error)
      return null
    }
  },

  async createReceipt(receipt: Omit<Receipt, "id" | "receiptNumber" | "issuedAt">): Promise<Receipt> {
    return apiCall<Receipt>('/receipts/', { 
      method: 'POST', 
      body: JSON.stringify(receipt) 
    })
  },

  async downloadReceipt(id: string): Promise<Blob> {
    const token = getAuthToken()
    const response = await fetch(`${API_BASE_URL}/receipts/${id}/download/`, {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    })
    
    if (!response.ok) {
      throw new Error('Failed to download receipt')
    }
    
    return response.blob()
  },

  async printReceipt(id: string): Promise<void> {
    return apiCall(`/receipts/${id}/print/`, { method: 'POST' })
  },
}

// Export all services
export const getUsers = userService.getUsers
export const getMenuItems = menuService.getMenuItems
export const getOrders = orderService.getOrders
export const createOrder = orderService.createOrder
export const updateOrder = orderService.updateOrder
export const getTables = tableService.getTables
export const updateTable = tableService.updateTable
export const getInventory = inventoryService.getInventory
export const updateInventoryItem = inventoryService.updateInventoryItem
export const getDashboardStats = dashboardService.getStats
export const getSalesData = dashboardService.getSalesData
export const getCategorySales = dashboardService.getCategorySales

// Additional exports for compatibility
export const createUser = userService.createUser
export const updateUser = userService.updateUser
export const deleteUser = userService.deleteUser
export const changeUserPassword = userService.changePassword
export const createInventoryItem = inventoryService.createInventoryItem
export const trackWaste = inventoryService.trackWaste

// Service request exports
export const getServiceRequests = serviceRequestService.getServiceRequests
export const updateServiceRequest = serviceRequestService.updateServiceRequest

// Guest exports
export const getGuests = guestService.getGuests
export const checkInGuest = guestService.checkInGuest
export const checkOutGuest = guestService.checkOutGuest

// Receipt exports
export const getReceipts = receiptService.getReceipts
export const getReceiptById = receiptService.getReceiptById
export const createReceipt = receiptService.createReceipt
export const downloadReceipt = receiptService.downloadReceipt
export const printReceipt = receiptService.printReceipt

// Reports export (placeholder)
export const getReports = async (from?: Date, to?: Date) => {
  const params = new URLSearchParams()
  if (from) params.append('from', from.toISOString())
  if (to) params.append('to', to.toISOString())
  const query = params.toString()
  const endpoint = `/reports/${query ? `?${query}` : ''}`
  return apiCall<any[]>(endpoint)
}

// Export token management functions for use in other parts of the app
export { getAuthToken, setAuthToken, removeAuthToken }
