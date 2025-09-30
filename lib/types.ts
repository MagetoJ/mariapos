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
  image?: string
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
  status: OrderStatus
}

export interface Order {
  id: string
  orderNumber: string
  type: OrderType
  tableId?: string
  roomNumber?: string
  customerId?: string
  customerName?: string
  items: OrderItem[]
  subtotal: number
  tax: number
  discount: number
  total: number
  status: OrderStatus
  waiterId?: string
  waiter?: User
  notes?: string
  createdAt: string
  updatedAt: string
  completedAt?: string
}

export interface Table {
  id: string
  number: string
  capacity: number
  status: TableStatus
  currentOrderId?: string
  waiterId?: string
  waiter?: User
  section?: string
  reservedBy?: string
  reservedAt?: string
}

export interface Payment {
  id: string
  orderId: string
  amount: number
  method: PaymentMethod
  status: PaymentStatus
  transactionId?: string
  mpesaCode?: string
  cashierId?: string
  cashier?: User
  createdAt: string
  refundedAt?: string
  refundReason?: string
}

export interface Receipt {
  id: string
  receiptNumber: string
  orderId: string
  order: Order
  payment: Payment
  issuedBy: string
  issuedAt: string
  printedAt?: string
}

export interface InventoryItem {
  id: string
  name: string
  category: string
  unit: string
  quantity: number
  reorderLevel: number
  unitPrice?: number
  supplier?: string
  lastRestocked?: string
  expiryDate?: string
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
  todaySales: number
  todayOrders: number
  activeOrders: number
  availableTables: number
  customersServed: number
  averageOrderValue: number
  salesGrowth: number
  ordersGrowth: number
}

export interface SalesData {
  date: string
  sales: number
  orders: number
}

export interface CategorySales {
  category: string
  sales: number
  orders: number
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
  completedAt?: string
  assignedTo?: string
}

export interface Notification {
  id: string
  type: "order" | "service-request" | "inventory" | "guest" | "system"
  title: string
  message: string
  priority: "low" | "medium" | "high"
  isRead: boolean
  createdAt: string
  relatedId?: string
  actionUrl?: string
}
