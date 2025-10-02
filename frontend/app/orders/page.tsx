"use client"

import { useEffect, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { OrderList } from "@/components/orders/order-list"
import { CreateOrderDialog } from "@/components/orders/create-order-dialog"
import { menuService, orderService, tableService } from "@/lib/api/data-service"
import type { MenuItem, Order, Table } from "@/lib/types"
import { Plus } from "lucide-react"

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [loading, setLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [tables, setTables] = useState<Table[]>([])

  useEffect(() => {
    void fetchOrders()
    void fetchSupportingData()
  }, [])

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const data = await orderService.getOrders()
      setOrders(data)
    } catch (error) {
      console.error("Failed to fetch orders:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSupportingData = async () => {
    try {
      const [menuData, tableData] = await Promise.all([
        menuService.getMenuItems(),
        tableService.getTables(),
      ])
      setMenuItems(menuData)
      setTables(tableData)
    } catch (error) {
      console.error("Failed to fetch supporting data:", error)
    }
  }

  const handleViewOrder = (order: Order) => {
    console.info("View order", order)
  }

  const handleUpdateOrder = async (orderId: string, updates: Partial<Order>) => {
    try {
      await orderService.updateOrder(orderId, updates)
      await fetchOrders()
    } catch (error) {
      console.error("Failed to update order:", error)
    }
  }

  const handleCreateOrder = async (orderData: Omit<Order, "id" | "orderNumber" | "createdAt" | "updatedAt">) => {
    try {
      await orderService.createOrder(orderData)
      setCreateDialogOpen(false)
      await fetchOrders()
    } catch (error) {
      console.error("Failed to create order:", error)
    }
  }

  const filteredOrders = orders.filter((order) => {
    const normalizedOrderNumber = order.orderNumber?.toLowerCase() ?? ""
    return normalizedOrderNumber.includes(searchQuery.toLowerCase())
  })

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Orders</h1>
            <p className="text-muted-foreground">Manage and monitor ongoing orders</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={fetchOrders}>
              Refresh
            </Button>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Order
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Input
              placeholder="Search orders by number..."
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
              <p className="text-muted-foreground">Loading orders...</p>
            </div>
          </div>
        ) : (
          <OrderList
            orders={filteredOrders}
            onViewOrder={handleViewOrder}
            onUpdateOrder={handleUpdateOrder}
          />
        )}
      </div>

      <CreateOrderDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onCreateOrder={handleCreateOrder}
        menuItems={menuItems}
        tables={tables}
      />
    </AppLayout>
  )
}