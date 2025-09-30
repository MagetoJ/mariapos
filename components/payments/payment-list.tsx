"use client"

import type { Order } from "@/lib/types"
import { formatCurrency, formatDateTime } from "@/lib/utils/format"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { CreditCard, Clock } from "lucide-react"
import { cn } from "@/lib/utils"

interface PaymentListProps {
  orders: Order[]
  onProcessPayment: (order: Order) => void
}

const statusColors = {
  ready: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
  served: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
  completed: "bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20",
}

export function PaymentList({ orders, onProcessPayment }: PaymentListProps) {
  if (orders.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium mb-2">No orders found</p>
          <p className="text-sm">Orders ready for payment will appear here</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {orders.map((order) => (
        <Card key={order.id} className="p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <p className="font-bold text-lg">{order.orderNumber}</p>
                <Badge variant="outline" className="capitalize">
                  {order.type.replace("-", " ")}
                </Badge>
                <Badge
                  variant="outline"
                  className={cn("capitalize", statusColors[order.status as keyof typeof statusColors])}
                >
                  {order.status}
                </Badge>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Customer</p>
                  <p className="font-medium">{order.customerName}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Items</p>
                  <p className="font-medium">{order.items.length}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Total</p>
                  <p className="font-bold text-primary">{formatCurrency(order.total)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Time</p>
                  <p className="font-medium flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDateTime(order.createdAt)}
                  </p>
                </div>
              </div>
              {order.waiter && <p className="text-xs text-muted-foreground mt-2">Served by: {order.waiter.name}</p>}
            </div>
            <div className="flex gap-2 ml-4">
              {order.status !== "completed" ? (
                <Button onClick={() => onProcessPayment(order)}>
                  <CreditCard className="mr-2 h-4 w-4" />
                  Process Payment
                </Button>
              ) : (
                <Button variant="outline" onClick={() => onProcessPayment(order)}>
                  <CreditCard className="mr-2 h-4 w-4" />
                  View Payment
                </Button>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
