"use client"

import type { Order } from "@/lib/types"
import { formatCurrency, formatDateTime } from "@/lib/utils/format"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Eye, Printer } from "lucide-react"

interface ReceiptListProps {
  orders: Order[]
  onViewReceipt: (order: Order) => void
}

export function ReceiptList({ orders, onViewReceipt }: ReceiptListProps) {
  if (orders.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium mb-2">No receipts found</p>
          <p className="text-sm">Completed orders will appear here</p>
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
                <Badge variant="secondary" className="capitalize">
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
                  <p className="text-muted-foreground">Date</p>
                  <p className="font-medium">{formatDateTime(order.createdAt)}</p>
                </div>
              </div>
              {order.waiter && <p className="text-xs text-muted-foreground mt-2">Served by: {order.waiter.name}</p>}
            </div>
            <div className="flex gap-2 ml-4">
              <Button variant="outline" size="sm" onClick={() => onViewReceipt(order)}>
                <Eye className="mr-2 h-4 w-4" />
                View
              </Button>
              <Button size="sm" onClick={() => onViewReceipt(order)}>
                <Printer className="mr-2 h-4 w-4" />
                Print
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
