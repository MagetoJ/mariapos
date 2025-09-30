"use client"

import { useEffect, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { orderService } from "@/lib/api/data-service"
import type { Order } from "@/lib/types"
import { Input } from "@/components/ui/input"
import { Search, Receipt } from "lucide-react"
import { ReceiptList } from "@/components/receipts/receipt-list"
import { ReceiptDialog } from "@/components/receipts/receipt-dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuthStore } from "@/lib/store/auth-store"

export default function ReceiptsPage() {
  const { user } = useAuthStore()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [receiptDialogOpen, setReceiptDialogOpen] = useState(false)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      const ordersData = await orderService.getOrders()
      // Filter orders that can have receipts (completed or served)
      const receiptableOrders = ordersData.filter((order) => ["completed", "served"].includes(order.status))
      setOrders(receiptableOrders)
    } catch (error) {
      console.error("Failed to fetch orders:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleViewReceipt = (order: Order) => {
    setSelectedOrder(order)
    setReceiptDialogOpen(true)
  }

  const filteredOrders = orders.filter(
    (order) =>
      order.orderNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customerName?.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  // Filter orders for waiters - only show their assigned orders
  const displayOrders = user?.role === "waiter" ? filteredOrders.filter((o) => o.waiterId === user.id) : filteredOrders

  const todayOrders = displayOrders.filter((order) => {
    const orderDate = new Date(order.createdAt).toDateString()
    const today = new Date().toDateString()
    return orderDate === today
  })

  const thisWeekOrders = displayOrders.filter((order) => {
    const orderDate = new Date(order.createdAt)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return orderDate >= weekAgo
  })

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading receipts...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-balance">Receipts</h2>
            <p className="text-muted-foreground">View and print order receipts</p>
          </div>
          <div className="flex items-center gap-2">
            <Receipt className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">{displayOrders.length} receipts</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search receipts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        <Tabs defaultValue="today" className="space-y-4">
          <TabsList>
            <TabsTrigger value="today">Today ({todayOrders.length})</TabsTrigger>
            <TabsTrigger value="week">This Week ({thisWeekOrders.length})</TabsTrigger>
            <TabsTrigger value="all">All ({displayOrders.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="today" className="space-y-4">
            <ReceiptList orders={todayOrders} onViewReceipt={handleViewReceipt} />
          </TabsContent>

          <TabsContent value="week" className="space-y-4">
            <ReceiptList orders={thisWeekOrders} onViewReceipt={handleViewReceipt} />
          </TabsContent>

          <TabsContent value="all" className="space-y-4">
            <ReceiptList orders={displayOrders} onViewReceipt={handleViewReceipt} />
          </TabsContent>
        </Tabs>
      </div>

      <ReceiptDialog open={receiptDialogOpen} onOpenChange={setReceiptDialogOpen} order={selectedOrder} />
    </AppLayout>
  )
}
