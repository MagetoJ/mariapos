// Core Types for Maria Havens POS System

export type UserRole = "admin" | "manager" | "receptionist" | "waiter" | "kitchen" | "cashier" | "guest"

export type OrderStatus = "pending" | "preparing" | "ready" | "served" | "completed" | "cancelled"

export type OrderType = "dine-in" | "takeaway" | "room-service"

export type TableStatus = "available" | "occupied" | "reserved" | "cleaning"

export type PaymentMethod = "cash" | "card" | "mpesa" | "bank-transfer"

export type PaymentStatus = "pending" | "completed" | "refunded" | "failed"

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  phone?: string
  avatar?: string
  isActive: boolean
  createdAt: string
  acceptedTermsAt?: string
  termsVersion?: string
  roomNumber?: string // For guest accounts linked to rooms
}

export interface MenuItem {
  id: string
  name: string
  description: string
  category: string
  price: number
  // UPDATED: image is the File/URL from the server's database field
  image?: string | File | null 
  // ADDED: image_url is the absolute path to display the image
  image_url?: string | null
  isAvailable: boolean
  preparationTime: number // in minutes
  ingredients?: string[]
  allergens?: string[]
}

export interface OrderItem {
  id: string
  menuItemId: string
  menuItem: MenuItem
  quantity: number
  price: number
  notes?: string
}

export interface Order {
  id: string
  orderNumber: string
  tableId?: string
  tableNumber?: string
  guestId?: string
  guestName?: string
  items: OrderItem[]
  total: number
  status: OrderStatus
  type: OrderType
  waiterId: string
  waiterName: string
  createdAt: string
  updatedAt: string
}

export interface Table {
  id: string
  number: string
  capacity: number
  status: TableStatus
  section: string
  currentOrderId?: string
}

export interface InventoryItem {
  id: string
  name: string
  category: string
  currentStock: number
  unit: string
  unitCost: number
  minimumStock: number
  maximumStock: number
  supplier: string
  lastRestock: string
}

export interface StockMovement {
  id: string
  itemId: string
  type: "in" | "out" | "waste" | "adjustment"
  quantity: number
  reason?: string
  performedBy: string
  createdAt: string
}

export interface Guest {
  id: string
  name: string
  email?: string
  phone: string
  roomNumber: string
  checkInDate: string
  checkOutDate: string
  status: "checked-in" | "checked-out"
  totalSpent: number
}

export interface DashboardStats {
  todayRevenue: number
  todayOrders: number
  activeOrders: number
  availableTables: number
  customersServed: number
  averageOrderValue: number
  salesGrowth: number
  ordersGrowth: number
  pendingServiceRequests: number
  occupiedRooms: number
  lowStockItems: number
  outOfStockItems: number
}

export interface SalesData {
  date: string
  revenue: number
  orders: number
  averageOrderValue: number
  dineInRevenue: number
  takeawayRevenue: number
  roomServiceRevenue: number
}

export interface CategorySales {
  category: string
  revenue: number
  orders: number
  itemsSold: number
  percentageOfTotal: number
}

export interface ServiceRequest {
  id: string
  guestId: string
  guestName: string
  roomNumber: string
  type: "housekeeping" | "maintenance" | "room-service" | "concierge" | "other"
  description: string
  priority: "low" | "medium" | "high"
  status: "pending" | "in-progress" | "completed" | "cancelled"
  createdAt: string
  updatedAt: string
}

export interface Receipt {
  id: string
  orderId: string
  orderTotal: number
  paymentMethod: PaymentMethod
  paymentStatus: PaymentStatus
  createdAt: string
  customerEmail?: string
}