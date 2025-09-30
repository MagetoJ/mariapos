"use client"

import { useRef } from "react"
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
import { Separator } from "@/components/ui/separator"
import { formatCurrency, formatDateTime } from "@/lib/utils/format"
import { Printer } from "lucide-react"
import { useReactToPrint } from "react-to-print"

interface ReceiptDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  order: Order | null
}

export function ReceiptDialog({ open, onOpenChange, order }: ReceiptDialogProps) {
  const receiptRef = useRef<HTMLDivElement>(null)

  const handlePrint = useReactToPrint({
    content: () => receiptRef.current,
    documentTitle: `Receipt-${order?.orderNumber}`,
  })

  if (!order) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Receipt - {order.orderNumber}</DialogTitle>
          <DialogDescription>Order receipt for printing</DialogDescription>
        </DialogHeader>

        <div ref={receiptRef} className="space-y-4 p-4 bg-white text-black print:p-0">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-bold">Maria Havens</h1>
            <p className="text-sm">Hotel & Restaurant</p>
            <p className="text-xs">Nairobi, Kenya</p>
            <p className="text-xs">Tel: +254 700 000 000</p>
          </div>

          <Separator />

          {/* Order Info */}
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>Receipt #:</span>
              <span className="font-mono">{order.orderNumber}</span>
            </div>
            <div className="flex justify-between">
              <span>Date:</span>
              <span>{formatDateTime(order.createdAt)}</span>
            </div>
            <div className="flex justify-between">
              <span>Customer:</span>
              <span>{order.customerName}</span>
            </div>
            <div className="flex justify-between">
              <span>Type:</span>
              <span className="capitalize">{order.type.replace("-", " ")}</span>
            </div>
            {order.tableId && (
              <div className="flex justify-between">
                <span>Table:</span>
                <span>{order.tableId}</span>
              </div>
            )}
            {order.waiter && (
              <div className="flex justify-between">
                <span>Served by:</span>
                <span>{order.waiter.name}</span>
              </div>
            )}
          </div>

          <Separator />

          {/* Items */}
          <div className="space-y-2">
            <h3 className="font-semibold text-sm">Items</h3>
            {order.items.map((item, index) => (
              <div key={index} className="flex justify-between text-sm">
                <div className="flex-1">
                  <p className="font-medium">{item.menuItem.name}</p>
                  <p className="text-xs text-gray-600">
                    {item.quantity} × {formatCurrency(item.price)}
                  </p>
                </div>
                <span className="font-medium">{formatCurrency(item.quantity * item.price)}</span>
              </div>
            ))}
          </div>

          <Separator />

          {/* Totals */}
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>Subtotal:</span>
              <span>{formatCurrency(order.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Tax (10%):</span>
              <span>{formatCurrency(order.tax)}</span>
            </div>
            {order.discount > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Discount:</span>
                <span>-{formatCurrency(order.discount)}</span>
              </div>
            )}
            <Separator />
            <div className="flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span>{formatCurrency(order.total)}</span>
            </div>
          </div>

          <Separator />

          {/* Footer */}
          <div className="text-center text-xs space-y-1">
            <p>Thank you for dining with us!</p>
            <p>Visit us again soon</p>
            <p className="mt-2">www.mariahavens.com</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
          <Button onClick={handlePrint}>
            <Printer className="mr-2 h-4 w-4" />
            Print Receipt
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
