"use client"

import { useEffect, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { orderService } from "@/lib/api/data-service"
import type { Order } from "@/lib/types"
import { Input } from "@/components/ui/input"
import { Search, CreditCard } from "lucide-react"
import { PaymentList } from "@/components/payments/payment-list"
import { PaymentDialog } from "@/components/payments/payment-dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function PaymentsPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      const ordersData = await orderService.getOrders()
      // Filter orders that need payment (ready, served, or completed)
      const payableOrders = ordersData.filter((order) => ["ready", "served", "completed"].includes(order.status))
      setOrders(payableOrders)
    } catch (error) {
      console.error("Failed to fetch orders:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleProcessPayment = (order: Order) => {
    setSelectedOrder(order)
    setPaymentDialogOpen(true)
  }

  const handlePaymentComplete = (orderId: string) => {
    // Update order status to completed after payment
    setOrders(orders.map((order) => (order.id === orderId ? { ...order, status: "completed" as const } : order)))
    setPaymentDialogOpen(false)
    setSelectedOrder(null)
  }

  const filteredOrders = orders.filter(
    (order) =>
      order.orderNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customerName?.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const pendingPayments = filteredOrders.filter((order) => ["ready", "served"].includes(order.status))
  const completedPayments = filteredOrders.filter((order) => order.status === "completed")

  const totalPending = pendingPayments.reduce((sum, order) => sum + order.total, 0)
  const totalCompleted = completedPayments.reduce((sum, order) => sum + order.total, 0)

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading payments...</p>
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
            <h2 className="text-3xl font-bold tracking-tight text-balance">Payments</h2>
            <p className="text-muted-foreground">Process payments and manage transactions</p>
          </div>
          <div className="flex items-center gap-2">
            <CreditCard className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">{filteredOrders.length} orders</span>
          </div>
        </div>

        {/* Payment Summary */}
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm font-medium text-muted-foreground">Pending Payments</p>
            <p className="text-2xl font-bold text-orange-600">KSh {totalPending.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground mt-1">{pendingPayments.length} orders</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm font-medium text-muted-foreground">Completed Today</p>
            <p className="text-2xl font-bold text-green-600">KSh {totalCompleted.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground mt-1">{completedPayments.length} orders</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search orders..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        <Tabs defaultValue="pending" className="space-y-4">
          <TabsList>
            <TabsTrigger value="pending">Pending ({pendingPayments.length})</TabsTrigger>
            <TabsTrigger value="completed">Completed ({completedPayments.length})</TabsTrigger>
            <TabsTrigger value="all">All ({filteredOrders.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="pending" className="space-y-4">
            <PaymentList orders={pendingPayments} onProcessPayment={handleProcessPayment} />
          </TabsContent>

          <TabsContent value="completed" className="space-y-4">
            <PaymentList orders={completedPayments} onProcessPayment={handleProcessPayment} />
          </TabsContent>

          <TabsContent value="all" className="space-y-4">
            <PaymentList orders={filteredOrders} onProcessPayment={handleProcessPayment} />
          </TabsContent>
        </Tabs>
      </div>

      <PaymentDialog
        open={paymentDialogOpen}
        onOpenChange={setPaymentDialogOpen}
        order={selectedOrder}
        onPaymentComplete={handlePaymentComplete}
      />
    </AppLayout>
  )
}
