import type { DashboardStats, SalesData, CategorySales } from "@/lib/types"

export const mockDashboardStats: DashboardStats = {
  todaySales: 45680,
  todayOrders: 32,
  activeOrders: 8,
  availableTables: 12,
  customersServed: 87,
  averageOrderValue: 1427.5,
  salesGrowth: 12.5,
  ordersGrowth: 8.3,
}

export const mockSalesData: SalesData[] = [
  { date: "2024-01-01", sales: 32000, orders: 24 },
  { date: "2024-01-02", sales: 38000, orders: 28 },
  { date: "2024-01-03", sales: 35000, orders: 26 },
  { date: "2024-01-04", sales: 42000, orders: 31 },
  { date: "2024-01-05", sales: 39000, orders: 29 },
  { date: "2024-01-06", sales: 45000, orders: 34 },
  { date: "2024-01-07", sales: 45680, orders: 32 },
]

export const mockCategorySales: CategorySales[] = [
  { category: "Main Course", sales: 18500, orders: 45 },
  { category: "Breakfast", sales: 12300, orders: 38 },
  { category: "Beverages", sales: 8900, orders: 72 },
  { category: "Desserts", sales: 5980, orders: 28 },
]
