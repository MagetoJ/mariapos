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

const API_BASE_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, '')

type MenuItemApiResponse = {
  id: string
  name: string
  description?: string
  category?: string
  price?: number | string
  image?: string | null
  image_url?: string | null
  is_available?: boolean
  isAvailable?: boolean
  preparation_time?: number | string
  preparationTime?: number | string
  ingredients?: string[]
  allergens?: string[]
}

function resolveMediaUrl(path?: string | null): string | null {
  if (!path) {
    return null
  }

  if (/^https?:\/\//i.test(path)) {
    return path
  }

  const base = API_BASE_ORIGIN || ''
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${base}${normalizedPath}`
}

function transformMenuItem(data: MenuItemApiResponse): MenuItem {
  const price = typeof data.price === 'string' ? Number(data.price) : data.price
  const preparationTimeValue =
    data.preparation_time ?? data.preparationTime ?? 0
  const preparationTime =
    typeof preparationTimeValue === 'string'
      ? Number(preparationTimeValue)
      : preparationTimeValue ?? 0

  const isAvailableValue = data.is_available ?? data.isAvailable

  const imageUrl = data.image_url ?? resolveMediaUrl(data.image)

  return {
    id: data.id,
    name: data.name,
    description: data.description ?? '',
    category: data.category ?? '',
    price: Number(price) || 0,
    image: data.image ?? null,
    image_url: imageUrl,
    isAvailable: Boolean(isAvailableValue),
    preparationTime: Number(preparationTime) || 0,
    ingredients: data.ingredients,
    allergens: data.allergens,
  }
}

// Helper function for Django API calls
// MODIFICATION: Check for FormData and adjust headers accordingly
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = getAuthToken()
  
  const headers: HeadersInit = {
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
  
  // If the body is not FormData, set Content-Type to application/json
  if (!(options?.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
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
  
  // Handle empty responses
  if (response.status === 204) {
    return null as T; // Return null for successful deletion or empty content
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
  // CORRECTED: Endpoint URL for getting menu items
  async getMenuItems(params?: { category?: string; isAvailable?: boolean }): Promise<MenuItem[]> {
    const queryParams = new URLSearchParams()
    if (params?.category) queryParams.append('category', params.category)
    if (params?.isAvailable !== undefined) {
      queryParams.append('is_available', params.isAvailable ? 'true' : 'false')
    }

    const query = queryParams.toString()
    const endpoint = `/menu/menu-items/${query ? `?${query}` : ''}`
    const data = await apiCall<MenuItemApiResponse[] | { results: MenuItemApiResponse[] }>(endpoint)
    const items = Array.isArray(data) ? data : data.results || []
    return items.map(transformMenuItem)
  },

  async getMenuItemById(id: string): Promise<MenuItem | null> {
    try {
      const item = await apiCall<MenuItemApiResponse>(`/menu/menu-items/${id}/`)
      return transformMenuItem(item)
    } catch (error) {
      console.error('Get menu item by ID failed:', error)
      return null
    }
  },

  // MODIFICATION: Accept FormData for file uploads
  async createMenuItem(itemData: FormData): Promise<MenuItem> {
    const created = await apiCall<MenuItemApiResponse>('/menu/menu-items/', {
      method: 'POST',
      body: itemData,
    })
    return transformMenuItem(created)
  },

  // MODIFICATION: Accept FormData for file uploads
  async updateMenuItem(id: string, updates: FormData): Promise<MenuItem> {
    const updated = await apiCall<MenuItemApiResponse>(`/menu/menu-items/${id}/`, {
      method: 'PATCH',
      body: updates,
    })
    return transformMenuItem(updated)
  },

  async deleteMenuItem(id: string): Promise<void> {
    return apiCall(`/menu/menu-items/${id}/`, { method: 'DELETE' })
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
    const endpoint = `/inventory/items/${query ? `?${query}` : ''}`
    const data = await apiCall<InventoryItem[] | { results: InventoryItem[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getInventoryItemById(id: string): Promise<InventoryItem | null> {
    try {
      return await apiCall<InventoryItem>(`/inventory/items/${id}/`)
    } catch (error) {
      console.error('Get inventory item by ID failed:', error)
      return null
    }
  },

  async createInventoryItem(item: Omit<InventoryItem, "id">): Promise<InventoryItem> {
    return apiCall<InventoryItem>('/inventory/items/', { 
      method: 'POST', 
      body: JSON.stringify(item) 
    })
  },

  async updateInventoryItem(id: string, updates: Partial<InventoryItem>): Promise<InventoryItem> {
    return apiCall<InventoryItem>(`/inventory/items/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },

  async deleteInventoryItem(id: string): Promise<void> {
    return apiCall(`/inventory/items/${id}/`, { method: 'DELETE' })
  },

  async getLowStockItems(): Promise<InventoryItem[]> {
    return apiCall<InventoryItem[]>('/inventory/items/low_stock/')
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
  // CORRECTED: Endpoint URL for stats
  async getStats(): Promise<DashboardStats> {
    const stats = await apiCall<any>('/dashboard/stats/');
    return {
      todayRevenue: Number(stats.today_revenue) || 0,
      todayOrders: Number(stats.today_orders) || 0,
      activeOrders: Number(stats.active_orders) || 0,
      availableTables: Number(stats.occupied_tables) ? Math.max(0, Number(stats.total_tables || 0) - Number(stats.occupied_tables)) : Number(stats.available_tables ?? 0) || 0,
      customersServed: Number(stats.today_guests ?? stats.today_checkins) || 0,
      averageOrderValue: Number(stats.average_order_value) || 0,
      salesGrowth: Number(stats.sales_growth ?? 0),
      ordersGrowth: Number(stats.orders_growth ?? 0),
      pendingServiceRequests: Number(stats.pending_service_requests) || 0,
      occupiedRooms: Number(stats.occupied_rooms) || 0,
      lowStockItems: Number(stats.low_stock_items) || 0,
      outOfStockItems: Number(stats.out_of_stock_items) || 0,
    }
  },

  async getSalesData(days = 7): Promise<SalesData[]> {
    const response = await apiCall<any[]>(`/dashboard/sales_data/?days=${days}`)
    return response.map((entry) => ({
      date: entry.date,
      revenue: Number(entry.revenue) || 0,
      orders: Number(entry.orders) || 0,
      averageOrderValue: Number(entry.average_order_value) || 0,
      dineInRevenue: Number(entry.dine_in_revenue) || 0,
      takeawayRevenue: Number(entry.takeaway_revenue) || 0,
      roomServiceRevenue: Number(entry.room_service_revenue) || 0,
    }))
  },

  async getCategorySales(): Promise<CategorySales[]> {
    const response = await apiCall<any[]>('/dashboard/category_sales/')
    return response.map((entry) => ({
      category: entry.category,
      revenue: Number(entry.revenue) || 0,
      orders: Number(entry.orders) || 0,
      itemsSold: Number(entry.items_sold) || 0,
      percentageOfTotal: Number(entry.percentage_of_total) || 0,
    }))
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
    const endpoint = `/guests/guests/${query ? `?${query}` : ''}`
    const data = await apiCall<Guest[] | { results: Guest[] }>(endpoint)
    return Array.isArray(data) ? data : data.results || []
  },

  async getGuestById(id: string): Promise<Guest | null> {
    try {
      return await apiCall<Guest>(`/guests/guests/${id}/`)
    } catch (error) {
      console.error('Get guest by ID failed:', error)
      return null
    }
  },

  async checkInGuest(guest: Omit<Guest, "id" | "checkInTime" | "status">): Promise<Guest> {
    return apiCall<Guest>('/guests/guests/', { 
      method: 'POST', 
      body: JSON.stringify(guest) 
    })
  },

  async checkOutGuest(id: string): Promise<Guest> {
    return apiCall<Guest>(`/guests/guests/${id}/check_out/`, { method: 'POST' })
  },

  async updateGuest(id: string, updates: Partial<Guest>): Promise<Guest> {
    return apiCall<Guest>(`/guests/guests/${id}/`, { 
      method: 'PATCH', 
      body: JSON.stringify(updates) 
    })
  },

  async deleteGuest(id: string): Promise<void> {
    return apiCall(`/guests/guests/${id}/`, { method: 'DELETE' })
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