"use client"

import { useState, useEffect } from "react"
import { useAuthStore } from "@/lib/store/auth-store"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Download, TrendingUp, Users, Package, DollarSign } from "lucide-react"
import { SalesReport } from "@/components/reports/sales-report"
import { StaffReport } from "@/components/reports/staff-report"
import { InventoryReport } from "@/components/reports/inventory-report"
import { getReports } from "@/lib/api/data-service"

function ReportsPage() {
  const { user } = useAuthStore()
  const [reports, setReports] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [dateRange, setDateRange] = useState({
    from: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split("T")[0],
    to: new Date().toISOString().split("T")[0],
  })

  useEffect(() => {
    loadReports()
  }, [dateRange])

  const loadReports = async () => {
    setLoading(true)
    const data = await getReports(dateRange.from, dateRange.to)
    setReports(data)
    setLoading(false)
  }

  const exportReport = (type: string) => {
    // In production, this would generate and download CSV/PDF
    console.log(`Exporting ${type} report for ${dateRange.from} to ${dateRange.to}`)
    alert(`${type} report export would be generated here`)
  }

  return (
    <ProtectedRoute allowedRoles={["admin", "manager"]}>
      <AppLayout>
        <div className="space-y-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Reports & Analytics</h1>
              <p className="text-muted-foreground">View detailed business insights and performance metrics</p>
            </div>
            <div className="flex gap-2">
              <input
                type="date"
                value={dateRange.from}
                onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <span className="flex items-center text-muted-foreground">to</span>
              <input
                type="date"
                value={dateRange.to}
                onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>

          {loading ? (
            <div className="grid gap-4 md:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-20 rounded bg-muted" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">KES {reports?.summary.totalRevenue.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground">
                      +{reports?.summary.revenueGrowth}% from previous period
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Orders</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{reports?.summary.totalOrders}</div>
                    <p className="text-xs text-muted-foreground">
                      Avg: KES {reports?.summary.averageOrderValue.toLocaleString()} per order
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Customers Served</CardTitle>
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{reports?.summary.customersServed}</div>
                    <p className="text-xs text-muted-foreground">
                      {reports?.summary.repeatCustomers}% repeat customers
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
                    <Package className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{reports?.summary.lowStockItems}</div>
                    <p className="text-xs text-muted-foreground">Requires immediate attention</p>
                  </CardContent>
                </Card>
              </div>

              <Tabs defaultValue="sales" className="space-y-4">
                <TabsList>
                  <TabsTrigger value="sales">Sales Report</TabsTrigger>
                  <TabsTrigger value="staff">Staff Performance</TabsTrigger>
                  <TabsTrigger value="inventory">Inventory Report</TabsTrigger>
                </TabsList>

                <TabsContent value="sales" className="space-y-4">
                  <div className="flex justify-end">
                    <Button onClick={() => exportReport("Sales")} variant="outline">
                      <Download className="mr-2 h-4 w-4" />
                      Export CSV
                    </Button>
                  </div>
                  <SalesReport data={reports?.sales} />
                </TabsContent>

                <TabsContent value="staff" className="space-y-4">
                  <div className="flex justify-end">
                    <Button onClick={() => exportReport("Staff")} variant="outline">
                      <Download className="mr-2 h-4 w-4" />
                      Export CSV
                    </Button>
                  </div>
                  <StaffReport data={reports?.staff} />
                </TabsContent>

                <TabsContent value="inventory" className="space-y-4">
                  <div className="flex justify-end">
                    <Button onClick={() => exportReport("Inventory")} variant="outline">
                      <Download className="mr-2 h-4 w-4" />
                      Export CSV
                    </Button>
                  </div>
                  <InventoryReport data={reports?.inventory} />
                </TabsContent>
              </Tabs>
            </>
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  )
}

export default ReportsPage
