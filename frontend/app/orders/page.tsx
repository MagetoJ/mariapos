"use client"

import { useEffect, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { orderService, menuService, tableService } from "@/lib/api/data-service"
import type { Order, MenuItem, Table } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search } from "lucide-react"
import { OrderList } from "@/components/orders/order-list"
import { CreateOrderDialog } from "@/components/orders/create-order-dialog"
import { OrderDetailsDialog } from "@/components/orders/order-details-dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuthStore } from "@/lib/store/auth-store"

export default function OrdersPage() {
  const { user } = useAuthStore()
  const [orders, setOrders] = useState<Order[]>([])
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [ordersData, menuData, tablesData] = await Promise.all([
        orderService.getOrders().catch((e) => {
          console.error("❌ getOrders failed:", e)
          return []
        }),
        menuService.getMenuItems().catch((e) => {
          console.error("❌ getMenuItems failed:", e)
          return []
        }),
        tableService.getTables().catch((e) => {
          console.error("❌ getTables failed:", e)
          return []
        }),
      ])

      setOrders(ordersData)
      setMenuItems(menuData)
      setTables(tablesData)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOrder = async (
    order: Omit<Order, "id" | "orderNumber" | "createdAt" | "updatedAt">,
  ) => {
    try {
      const newOrder = await orderService.createOrder(order)
      setOrders([newOrder, ...orders])
      setCreateDialogOpen(false)
    } catch (error) {
      console.error("❌ Failed to create order:", error)
    }
  }

  const handleUpdateOrder = async (orderId: string, updates: Partial<Order>) => {
    try {
      const updatedOrder = await orderService.updateOrder(orderId, updates)
      setOrders(orders.map((o) => (o.id === orderId ? updatedOrder : o)))
      if (selectedOrder?.id === orderId) {
        setSelectedOrder(updatedOrder)
      }
    } catch (error) {
      console.error("❌ Failed to update order:", error)
    }
  }

  const handleViewOrder = (order: Order) => {
    setSelectedOrder(order)
    setDetailsDialogOpen(true)
  }

  const filteredOrders = orders.filter(
    (order) =>
      order.orderNumber?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customerName?.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const activeOrders = filteredOrders.filter((o) =>
    ["pending", "preparing", "ready"].includes(o.status),
  )
  const completedOrders = filteredOrders.filter((o) => o.status === "completed")
  const cancelledOrders = filteredOrders.filter((o) => o.status === "cancelled")

  // Waiters only see their assigned orders
  const displayOrders =
    user?.role === "waiter"
      ? filteredOrders.filter((o) => o.waiterId === user.id)
      : filteredOrders

  const canCreateOrder = user?.role !== "kitchen"

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading orders...</p>
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
            <h2 className="text-3xl font-bold tracking-tight text-balance">
              Orders
            </h2>
            <p className="text-muted-foreground">Manage and track all orders</p>
          </div>
          {canCreateOrder && (
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Order
            </Button>
          )}
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

        <Tabs defaultValue="active" className="space-y-4">
          <TabsList>
            <TabsTrigger value="active">Active ({activeOrders.length})</TabsTrigger>
            <TabsTrigger value="completed">
              Completed ({completedOrders.length})
            </TabsTrigger>
            <TabsTrigger value="cancelled">
              Cancelled ({cancelledOrders.length})
            </TabsTrigger>
            <TabsTrigger value="all">All ({displayOrders.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="space-y-4">
            <OrderList
              orders={activeOrders}
              onViewOrder={handleViewOrder}
              onUpdateOrder={handleUpdateOrder}
            />
          </TabsContent>

          <TabsContent value="completed" className="space-y-4">
            <OrderList
              orders={completedOrders}
              onViewOrder={handleViewOrder}
              onUpdateOrder={handleUpdateOrder}
            />
          </TabsContent>

          <TabsContent value="cancelled" className="space-y-4">
            <OrderList
              orders={cancelledOrders}
              onViewOrder={handleViewOrder}
              onUpdateOrder={handleUpdateOrder}
            />
          </TabsContent>

          <TabsContent value="all" className="space-y-4">
            <OrderList
              orders={displayOrders}
              onViewOrder={handleViewOrder}
              onUpdateOrder={handleUpdateOrder}
            />
          </TabsContent>
        </Tabs>
      </div>

      <CreateOrderDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onCreateOrder={handleCreateOrder}
        menuItems={menuItems}
        tables={tables}
      />

      <OrderDetailsDialog
        open={detailsDialogOpen}
        onOpenChange={setDetailsDialogOpen}
        order={selectedOrder}
        onUpdateOrder={handleUpdateOrder}
      />
    </AppLayout>
  )
}
