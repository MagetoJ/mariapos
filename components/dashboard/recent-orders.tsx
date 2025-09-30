"use client"

import type { Order } from "@/lib/types"
import { formatCurrency, getRelativeTime } from "@/lib/utils/format"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface RecentOrdersProps {
  orders: Order[]
}

const statusColors = {
  pending: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400",
  preparing: "bg-blue-500/10 text-blue-700 dark:text-blue-400",
  ready: "bg-green-500/10 text-green-700 dark:text-green-400",
  served: "bg-purple-500/10 text-purple-700 dark:text-purple-400",
  completed: "bg-gray-500/10 text-gray-700 dark:text-gray-400",
  cancelled: "bg-red-500/10 text-red-700 dark:text-red-400",
}

export function RecentOrders({ orders }: RecentOrdersProps) {
  if (orders.length === 0) {
    return <p className="text-muted-foreground text-center py-8">No recent orders</p>
  }

  return (
    <div className="space-y-4">
      {orders.map((order) => (
        <div
          key={order.id}
          className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
        >
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <p className="font-semibold">{order.orderNumber}</p>
              <Badge variant="outline" className="capitalize">
                {order.type.replace("-", " ")}
              </Badge>
              <Badge className={cn("capitalize", statusColors[order.status])}>{order.status}</Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {order.customerName} • {order.items.length} items • {getRelativeTime(order.createdAt)}
            </p>
          </div>
          <div className="text-right">
            <p className="font-bold">{formatCurrency(order.total)}</p>
            {order.waiter && <p className="text-xs text-muted-foreground">{order.waiter.name}</p>}
          </div>
        </div>
      ))}
    </div>
  )
}
