"use client"

import type { Order } from "@/lib/types"
import { formatCurrency, getRelativeTime } from "@/lib/utils/format"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Eye, Clock, CheckCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/lib/store/auth-store"

interface OrderListProps {
  orders: Order[]
  onViewOrder: (order: Order) => void
  onUpdateOrder: (orderId: string, updates: Partial<Order>) => void
}

const statusColors = {
  pending: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20",
  preparing: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
  ready: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
  served: "bg-purple-500/10 text-purple-700 dark:text-purple-400 border-purple-500/20",
  completed: "bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20",
  cancelled: "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20",
}

export function OrderList({ orders, onViewOrder, onUpdateOrder }: OrderListProps) {
  const { user } = useAuthStore()

  if (orders.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium mb-2">No orders found</p>
          <p className="text-sm">Orders will appear here once created</p>
        </div>
      </Card>
    )
  }

  const canUpdateStatus = (order: Order) => {
    if (user?.role === "kitchen") {
      return ["pending", "preparing"].includes(order.status)
    }
    if (user?.role === "waiter") {
      return order.waiterId === user.id && ["ready", "served"].includes(order.status)
    }
    return ["admin", "manager"].includes(user?.role || "")
  }

  const getNextStatus = (currentStatus: string) => {
    const statusFlow: Record<string, string> = {
      pending: "preparing",
      preparing: "ready",
      ready: "served",
      served: "completed",
    }
    return statusFlow[currentStatus]
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {orders.map((order) => (
        <Card key={order.id} className="p-4 hover:shadow-md transition-shadow">
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-bold text-lg">{order.orderNumber}</p>
                <p className="text-sm text-muted-foreground">{order.customerName}</p>
              </div>
              <Badge variant="outline" className={cn("capitalize", statusColors[order.status])}>
                {order.status}
              </Badge>
            </div>

            <div className="space-y-1 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Type:</span>
                <Badge variant="secondary" className="capitalize">
                  {order.type.replace("-", " ")}
                </Badge>
              </div>
              {order.tableId && (
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Table:</span>
                  <span className="font-medium">
                    {tables.find((t) => t.id === order.tableId)?.number || order.tableId}
                  </span>
                </div>
              )}
              {order.roomNumber && (
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Room:</span>
                  <span className="font-medium">{order.roomNumber}</span>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Items:</span>
                <span className="font-medium">{order.items.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Total:</span>
                <span className="font-bold text-primary">{formatCurrency(order.total)}</span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              {getRelativeTime(order.createdAt)}
              {order.waiter && <span>• {order.waiter.name}</span>}
            </div>

            <div className="flex gap-2 pt-2">
              <Button variant="outline" size="sm" className="flex-1 bg-transparent" onClick={() => onViewOrder(order)}>
                <Eye className="mr-2 h-4 w-4" />
                View
              </Button>
              {canUpdateStatus(order) && getNextStatus(order.status) && (
                <Button
                  size="sm"
                  className="flex-1"
                  onClick={() => onUpdateOrder(order.id, { status: getNextStatus(order.status) as any })}
                >
                  <CheckCircle className="mr-2 h-4 w-4" />
                  {getNextStatus(order.status)}
                </Button>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

// Mock tables for display - in real app this would come from props
const tables = [
  { id: "t1", number: "1" },
  { id: "t2", number: "2" },
  { id: "t3", number: "3" },
  { id: "t4", number: "4" },
  { id: "t5", number: "5" },
]
