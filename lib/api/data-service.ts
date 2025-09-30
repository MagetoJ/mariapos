/**
 * Data Service Layer
 *
 * This file provides an abstraction layer for data access.
 * Currently uses mock data, but can be easily replaced with real API calls to Django backend.
 *
 * To integrate with Django:
 * 1. Replace mock data imports with fetch/axios calls
 * 2. Update the base URL to point to your Django API
 * 3. Add authentication headers (JWT tokens, etc.)
 * 4. Handle API responses and errors appropriately
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
} from "@/lib/types"

// Mock data imports
import { mockUsers, mockCredentials } from "@/lib/mock-data/users"
import { mockMenuItems } from "@/lib/mock-data/menu"
import { mockOrders } from "@/lib/mock-data/orders"
import { mockTables } from "@/lib/mock-data/tables"
import { mockInventory } from "@/lib/mock-data/inventory"
import { mockDashboardStats, mockSalesData, mockCategorySales } from "@/lib/mock-data/dashboard"
import { mockReports } from "@/lib/mock-data/reports"
import { mockGuests } from "@/lib/mock-data/guests"
import { mockServiceRequests } from "@/lib/mock-data/service-requests"

// Base URL for API - change this when integrating with Django
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api"

// Helper function for API calls (ready for Django integration)
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // For now, return mock data
  // When integrating with Django, uncomment below:
  /*
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`, // Add your auth token
      ...options?.headers,
    },
  })
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`)
  }
  
  return response.json()
  */

  // Mock implementation - remove when integrating with Django
  return new Promise((resolve) => {
    setTimeout(() => resolve({} as T), 100)
  })
}

// Authentication
export const authService = {
  async login(email: string, password: string, roomNumber?: string): Promise<User | null> {
    // Django integration: POST /api/auth/login
    // return apiCall<User>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password, roomNumber }) })

    // Mock implementation
    const validCredential = Object.values(mockCredentials).find(
      (cred) => cred.email === email && cred.password === password,
    )

    if (validCredential) {
      const user = mockUsers.find((u) => u.email === email)

      if (user?.role === "guest") {
        if (!roomNumber) {
          return null // Room number required for guests
        }
        // Verify room number matches guest record
        const guest = mockGuests.find((g) => g.roomNumber === roomNumber && g.status === "checked-in")
        if (!guest) {
          return null // Invalid room number or guest not checked in
        }
        // Return user with room number
        return { ...user, roomNumber }
      }

      return user || null
    }
    return null
  },

  async logout(): Promise<void> {
    // Django integration: POST /api/auth/logout
    // return apiCall('/auth/logout', { method: 'POST' })

    // Mock implementation
    return Promise.resolve()
  },

  async getCurrentUser(): Promise<User | null> {
    // Django integration: GET /api/auth/me
    // return apiCall<User>('/auth/me')

    // Mock implementation - return first user for demo
    return mockUsers[0]
  },
}

// Users
export const userService = {
  async getUsers(): Promise<User[]> {
    // Django integration: GET /api/users
    // return apiCall<User[]>('/users')

    return mockUsers
  },

  async getUserById(id: string): Promise<User | null> {
    // Django integration: GET /api/users/:id
    // return apiCall<User>(`/users/${id}`)

    return mockUsers.find((u) => u.id === id) || null
  },

  async createUser(user: Omit<User, "id" | "createdAt">): Promise<User> {
    // Django integration: POST /api/users
    // return apiCall<User>('/users', { method: 'POST', body: JSON.stringify(user) })

    const newUser: User = {
      ...user,
      id: `u${Date.now()}`,
      createdAt: new Date().toISOString(),
    }
    mockUsers.push(newUser)
    return newUser
  },

  async updateUser(id: string, updates: Partial<User>): Promise<User> {
    // Django integration: PATCH /api/users/:id
    // return apiCall<User>(`/users/${id}`, { method: 'PATCH', body: JSON.stringify(updates) })

    const index = mockUsers.findIndex((u) => u.id === id)
    if (index !== -1) {
      mockUsers[index] = { ...mockUsers[index], ...updates }
      return mockUsers[index]
    }
    throw new Error("User not found")
  },
}

// Menu
export const menuService = {
  async getMenuItems(): Promise<MenuItem[]> {
    // Django integration: GET /api/menu
    // return apiCall<MenuItem[]>('/menu')

    return mockMenuItems
  },

  async getMenuItemById(id: string): Promise<MenuItem | null> {
    // Django integration: GET /api/menu/:id
    // return apiCall<MenuItem>(`/menu/${id}`)

    return mockMenuItems.find((item) => item.id === id) || null
  },

  async createMenuItem(item: Omit<MenuItem, "id">): Promise<MenuItem> {
    // Django integration: POST /api/menu
    // return apiCall<MenuItem>('/menu', { method: 'POST', body: JSON.stringify(item) })

    const newItem: MenuItem = {
      ...item,
      id: `m${Date.now()}`,
    }
    mockMenuItems.push(newItem)
    return newItem
  },

  async updateMenuItem(id: string, updates: Partial<MenuItem>): Promise<MenuItem> {
    // Django integration: PATCH /api/menu/:id
    // return apiCall<MenuItem>(`/menu/${id}`, { method: 'PATCH', body: JSON.stringify(updates) })

    const index = mockMenuItems.findIndex((item) => item.id === id)
    if (index !== -1) {
      mockMenuItems[index] = { ...mockMenuItems[index], ...updates }
      return mockMenuItems[index]
    }
    throw new Error("Menu item not found")
  },

  async deleteMenuItem(id: string): Promise<void> {
    // Django integration: DELETE /api/menu/:id
    // return apiCall(`/menu/${id}`, { method: 'DELETE' })

    const index = mockMenuItems.findIndex((item) => item.id === id)
    if (index !== -1) {
      mockMenuItems.splice(index, 1)
    }
  },
}

// Orders
export const orderService = {
  async getOrders(): Promise<Order[]> {
    // Django integration: GET /api/orders
    // return apiCall<Order[]>('/orders')

    return mockOrders
  },

  async getOrderById(id: string): Promise<Order | null> {
    // Django integration: GET /api/orders/:id
    // return apiCall<Order>(`/orders/${id}`)

    return mockOrders.find((order) => order.id === id) || null
  },

  async createOrder(order: Omit<Order, "id" | "orderNumber" | "createdAt" | "updatedAt">): Promise<Order> {
    // Django integration: POST /api/orders
    // return apiCall<Order>('/orders', { method: 'POST', body: JSON.stringify(order) })

    const newOrder: Order = {
      ...order,
      id: `o${Date.now()}`,
      orderNumber: `ORD-${String(mockOrders.length + 1).padStart(3, "0")}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    mockOrders.push(newOrder)
    return newOrder
  },

  async updateOrder(id: string, updates: Partial<Order>): Promise<Order> {
    // Django integration: PATCH /api/orders/:id
    // return apiCall<Order>(`/orders/${id}`, { method: 'PATCH', body: JSON.stringify(updates) })

    const index = mockOrders.findIndex((order) => order.id === id)
    if (index !== -1) {
      mockOrders[index] = {
        ...mockOrders[index],
        ...updates,
        updatedAt: new Date().toISOString(),
      }
      return mockOrders[index]
    }
    throw new Error("Order not found")
  },
}

// Tables
export const tableService = {
  async getTables(): Promise<Table[]> {
    // Django integration: GET /api/tables
    // return apiCall<Table[]>('/tables')

    return mockTables
  },

  async getTableById(id: string): Promise<Table | null> {
    // Django integration: GET /api/tables/:id
    // return apiCall<Table>(`/tables/${id}`)

    return mockTables.find((table) => table.id === id) || null
  },

  async updateTable(id: string, updates: Partial<Table>): Promise<Table> {
    // Django integration: PATCH /api/tables/:id
    // return apiCall<Table>(`/tables/${id}`, { method: 'PATCH', body: JSON.stringify(updates) })

    const index = mockTables.findIndex((table) => table.id === id)
    if (index !== -1) {
      mockTables[index] = { ...mockTables[index], ...updates }
      return mockTables[index]
    }
    throw new Error("Table not found")
  },
}

// Inventory
export const inventoryService = {
  async getInventory(): Promise<InventoryItem[]> {
    // Django integration: GET /api/inventory
    // return apiCall<InventoryItem[]>('/inventory')

    return mockInventory
  },

  async getInventoryItemById(id: string): Promise<InventoryItem | null> {
    // Django integration: GET /api/inventory/:id
    // return apiCall<InventoryItem>(`/inventory/${id}`)

    return mockInventory.find((item) => item.id === id) || null
  },

  async updateInventoryItem(id: string, updates: Partial<InventoryItem>): Promise<InventoryItem> {
    // Django integration: PATCH /api/inventory/:id
    // return apiCall<InventoryItem>(`/inventory/${id}`, { method: 'PATCH', body: JSON.stringify(updates) })

    const index = mockInventory.findIndex((item) => item.id === id)
    if (index !== -1) {
      mockInventory[index] = { ...mockInventory[index], ...updates }
      return mockInventory[index]
    }
    throw new Error("Inventory item not found")
  },

  async getLowStockItems(): Promise<InventoryItem[]> {
    // Django integration: GET /api/inventory/low-stock
    // return apiCall<InventoryItem[]>('/inventory/low-stock')

    return mockInventory.filter((item) => item.quantity <= item.reorderLevel)
  },
}

// Dashboard
export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    // Django integration: GET /api/dashboard/stats
    // return apiCall<DashboardStats>('/dashboard/stats')

    return mockDashboardStats
  },

  async getSalesData(days = 7): Promise<SalesData[]> {
    // Django integration: GET /api/dashboard/sales?days=7
    // return apiCall<SalesData[]>(`/dashboard/sales?days=${days}`)

    return mockSalesData.slice(-days)
  },

  async getCategorySales(): Promise<CategorySales[]> {
    // Django integration: GET /api/dashboard/category-sales
    // return apiCall<CategorySales[]>('/dashboard/category-sales')

    return mockCategorySales
  },
}

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

export const createUser = userService.createUser
export const updateUser = userService.updateUser

export async function deleteUser(id: string): Promise<void> {
  // Django integration: DELETE /api/users/:id
  // return apiCall(`/users/${id}`, { method: 'DELETE' })

  const index = mockUsers.findIndex((u) => u.id === id)
  if (index !== -1) {
    mockUsers.splice(index, 1)
  }
}

export async function changeUserPassword(id: string, newPassword: string): Promise<void> {
  // Django integration: POST /api/users/:id/change-password
  // return apiCall(`/users/${id}/change-password`, { method: 'POST', body: JSON.stringify({ password: newPassword }) })

  // Mock implementation - in production this would update the password in the database
  const credential = Object.values(mockCredentials).find((c) => {
    const user = mockUsers.find((u) => u.id === id)
    return user && c.email === user.email
  })

  if (credential) {
    credential.password = newPassword
  }
}

export async function createInventoryItem(item: Omit<InventoryItem, "id">): Promise<InventoryItem> {
  // Django integration: POST /api/inventory
  const newItem: InventoryItem = {
    ...item,
    id: `inv${Date.now()}`,
  }
  mockInventory.push(newItem)
  return newItem
}

export async function trackWaste(itemId: string, quantity: number, reason: string): Promise<void> {
  // Django integration: POST /api/inventory/waste
  const item = mockInventory.find((i) => i.id === itemId)
  if (item) {
    item.quantity -= quantity
  }
}

export async function getReports(startDate: string, endDate: string): Promise<any> {
  // Django integration: GET /api/reports?start={startDate}&end={endDate}
  return mockReports
}

export async function getGuests(): Promise<Guest[]> {
  // Django integration: GET /api/guests
  return mockGuests
}

export async function getGuestById(id: string): Promise<Guest | null> {
  // Django integration: GET /api/guests/:id
  return mockGuests.find((g) => g.id === id) || null
}

export async function checkInGuest(guest: Omit<Guest, "id" | "status" | "totalSpent">): Promise<Guest> {
  // Django integration: POST /api/guests/check-in
  const newGuest: Guest = {
    ...guest,
    id: `g${Date.now()}`,
    status: "checked-in",
    totalSpent: 0,
  }
  mockGuests.push(newGuest)
  return newGuest
}

export async function checkOutGuest(id: string): Promise<Guest> {
  // Django integration: POST /api/guests/:id/check-out
  const index = mockGuests.findIndex((g) => g.id === id)
  if (index !== -1) {
    mockGuests[index] = {
      ...mockGuests[index],
      status: "checked-out",
    }
    return mockGuests[index]
  }
  throw new Error("Guest not found")
}

export async function updateGuest(id: string, updates: Partial<Guest>): Promise<Guest> {
  // Django integration: PATCH /api/guests/:id
  const index = mockGuests.findIndex((g) => g.id === id)
  if (index !== -1) {
    mockGuests[index] = { ...mockGuests[index], ...updates }
    return mockGuests[index]
  }
  throw new Error("Guest not found")
}

// Service Requests
export const serviceRequestService = {
  async getServiceRequests(guestId?: string): Promise<ServiceRequest[]> {
    // Django integration: GET /api/service-requests?guestId={guestId}
    if (guestId) {
      return mockServiceRequests.filter((req) => req.guestId === guestId)
    }
    return mockServiceRequests
  },

  async createServiceRequest(request: Omit<ServiceRequest, "id" | "createdAt" | "status">): Promise<ServiceRequest> {
    // Django integration: POST /api/service-requests
    const newRequest: ServiceRequest = {
      ...request,
      id: `sr${Date.now()}`,
      status: "pending",
      createdAt: new Date().toISOString(),
    }
    mockServiceRequests.push(newRequest)
    return newRequest
  },

  async updateServiceRequest(id: string, updates: Partial<ServiceRequest>): Promise<ServiceRequest> {
    // Django integration: PATCH /api/service-requests/:id
    const index = mockServiceRequests.findIndex((req) => req.id === id)
    if (index !== -1) {
      mockServiceRequests[index] = { ...mockServiceRequests[index], ...updates }
      return mockServiceRequests[index]
    }
    throw new Error("Service request not found")
  },
}

export const getServiceRequests = serviceRequestService.getServiceRequests
export const createServiceRequest = serviceRequestService.createServiceRequest
export const updateServiceRequest = serviceRequestService.updateServiceRequest
