"use client"

import { useEffect, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { dashboardService, inventoryService, orderService, getServiceRequests } from "@/lib/api/data-service"
import type { DashboardStats, SalesData, CategorySales, InventoryItem, Order, ServiceRequest } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { formatCurrency } from "@/lib/utils/format"
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Clock, Users, AlertTriangle } from "lucide-react"
import { SalesChart } from "@/components/dashboard/sales-chart"
import { CategoryChart } from "@/components/dashboard/category-chart"
import { RecentOrders } from "@/components/dashboard/recent-orders"
import { LowStockAlert } from "@/components/dashboard/low-stock-alert"
import { ServiceRequestsList } from "@/components/dashboard/service-requests-list"
import { useAuthStore } from "@/lib/store/auth-store"

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [salesData, setSalesData] = useState<SalesData[]>([])
  const [categorySales, setCategorySales] = useState<CategorySales[]>([])
  const [lowStockItems, setLowStockItems] = useState<InventoryItem[]>([])
  const [recentOrders, setRecentOrders] = useState<Order[]>([])
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, salesChartData, categoryData, lowStock, orders, requests] = await Promise.all([
          dashboardService.getStats(),
          dashboardService.getSalesData(7),
          dashboardService.getCategorySales(),
          inventoryService.getLowStockItems(),
          orderService.getOrders(),
          getServiceRequests(),
        ])

        setStats(statsData)
        setSalesData(salesChartData)
        setCategorySales(categoryData)
        setLowStockItems(lowStock)
        setRecentOrders(orders.slice(0, 5))
        setServiceRequests(requests.filter((r) => r.status === "pending" || r.status === "in-progress"))
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading || !stats) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  const showInventory = user?.role === "admin" || user?.role === "manager" || user?.role === "kitchen"
  const showReports = user?.role === "admin" || user?.role === "manager"
  const showServiceRequests = user?.role === "admin" || user?.role === "manager" || user?.role === "receptionist"

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-balance">Dashboard</h2>
          <p className="text-muted-foreground">Welcome back, {user?.name}</p>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Today's Sales</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(stats.todaySales)}</div>
              <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                {stats.salesGrowth >= 0 ? (
                  <>
                    <TrendingUp className="h-3 w-3 text-green-600" />
                    <span className="text-green-600">+{stats.salesGrowth}%</span>
                  </>
                ) : (
                  <>
                    <TrendingDown className="h-3 w-3 text-red-600" />
                    <span className="text-red-600">{stats.salesGrowth}%</span>
                  </>
                )}
                <span>from yesterday</span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Orders Today</CardTitle>
              <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.todayOrders}</div>
              <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                {stats.ordersGrowth >= 0 ? (
                  <>
                    <TrendingUp className="h-3 w-3 text-green-600" />
                    <span className="text-green-600">+{stats.ordersGrowth}%</span>
                  </>
                ) : (
                  <>
                    <TrendingDown className="h-3 w-3 text-red-600" />
                    <span className="text-red-600">{stats.ordersGrowth}%</span>
                  </>
                )}
                <span>from yesterday</span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Orders</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeOrders}</div>
              <p className="text-xs text-muted-foreground mt-1">Currently processing</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Customers Served</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.customersServed}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Avg: {formatCurrency(stats.averageOrderValue)} per order
              </p>
            </CardContent>
          </Card>
        </div>

        {showServiceRequests && serviceRequests.length > 0 && (
          <Card className="border-primary/50 bg-primary/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-primary">
                <AlertTriangle className="h-5 w-5" />
                Pending Service Requests
              </CardTitle>
              <CardDescription>Guest service requests requiring attention</CardDescription>
            </CardHeader>
            <CardContent>
              <ServiceRequestsList requests={serviceRequests} />
            </CardContent>
          </Card>
        )}

        {/* Low Stock Alert */}
        {showInventory && lowStockItems.length > 0 && (
          <Card className="border-destructive/50 bg-destructive/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                Low Stock Alert
              </CardTitle>
              <CardDescription>The following items need restocking</CardDescription>
            </CardHeader>
            <CardContent>
              <LowStockAlert items={lowStockItems} />
            </CardContent>
          </Card>
        )}

        {/* Charts */}
        {showReports && (
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Sales Trend</CardTitle>
                <CardDescription>Last 7 days sales performance</CardDescription>
              </CardHeader>
              <CardContent>
                <SalesChart data={salesData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Sales by Category</CardTitle>
                <CardDescription>Revenue distribution across menu categories</CardDescription>
              </CardHeader>
              <CardContent>
                <CategoryChart data={categorySales} />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Recent Orders */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Orders</CardTitle>
            <CardDescription>Latest orders from the system</CardDescription>
          </CardHeader>
          <CardContent>
            <RecentOrders orders={recentOrders} />
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
