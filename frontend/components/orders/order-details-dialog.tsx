"use client"

import type { Order } from "@/lib/types"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { formatCurrency, formatDateTime } from "@/lib/utils/format"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/lib/store/auth-store"

interface OrderDetailsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  order: Order | null
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

export function OrderDetailsDialog({ open, onOpenChange, order, onUpdateOrder }: OrderDetailsDialogProps) {
  const { user } = useAuthStore()

  if (!order) return null

  const canCancel = ["admin", "manager"].includes(user?.role || "") && order.status !== "completed"

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span>Order {order.orderNumber}</span>
            <Badge variant="outline" className={cn("capitalize", statusColors[order.status])}>
              {order.status}
            </Badge>
          </DialogTitle>
          <DialogDescription>Order details and items</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Order Info */}
          <Card className="p-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Customer</p>
                <p className="font-medium">{order.customerName}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Type</p>
                <p className="font-medium capitalize">{order.type.replace("-", " ")}</p>
              </div>
              {order.tableId && (
                <div>
                  <p className="text-muted-foreground">Table</p>
                  <p className="font-medium">{order.tableId}</p>
                </div>
              )}
              {order.roomNumber && (
                <div>
                  <p className="text-muted-foreground">Room</p>
                  <p className="font-medium">{order.roomNumber}</p>
                </div>
              )}
              {order.waiter && (
                <div>
                  <p className="text-muted-foreground">Waiter</p>
                  <p className="font-medium">{order.waiter.name}</p>
                </div>
              )}
              <div>
                <p className="text-muted-foreground">Created</p>
                <p className="font-medium">{formatDateTime(order.createdAt)}</p>
              </div>
            </div>
            {order.notes && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-muted-foreground text-sm">Notes</p>
                <p className="text-sm">{order.notes}</p>
              </div>
            )}
          </Card>

          {/* Order Items */}
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Order Items</h3>
            <div className="space-y-3">
              {order.items.map((item) => (
                <div key={item.id} className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-medium">{item.menuItem.name}</p>
                    <p className="text-sm text-muted-foreground">{item.menuItem.description}</p>
                    {item.notes && <p className="text-xs text-muted-foreground mt-1">Note: {item.notes}</p>}
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      {item.quantity} × {formatCurrency(item.price)}
                    </p>
                    <p className="text-sm font-bold text-primary">{formatCurrency(item.quantity * item.price)}</p>
                  </div>
                </div>
              ))}
            </div>

            <Separator className="my-4" />

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal</span>
                <span>{formatCurrency(order.subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Tax</span>
                <span>{formatCurrency(order.tax)}</span>
              </div>
              {order.discount > 0 && (
                <div className="flex justify-between text-sm text-green-600">
                  <span>Discount</span>
                  <span>-{formatCurrency(order.discount)}</span>
                </div>
              )}
              <Separator />
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span className="text-primary">{formatCurrency(order.total)}</span>
              </div>
            </div>
          </Card>
        </div>

        <DialogFooter>
          {canCancel && (
            <Button variant="destructive" onClick={() => onUpdateOrder(order.id, { status: "cancelled" })}>
              Cancel Order
            </Button>
          )}
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
