"use client"

import { useState } from "react"
import type { Order, PaymentMethod } from "@/lib/types"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { formatCurrency } from "@/lib/utils/format"
import { CreditCard, Smartphone, Banknote, Building } from "lucide-react"

interface PaymentDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  order: Order | null
  onPaymentComplete: (orderId: string) => void
}

const paymentMethods = [
  { value: "cash", label: "Cash", icon: Banknote },
  { value: "card", label: "Card", icon: CreditCard },
  { value: "mpesa", label: "M-Pesa", icon: Smartphone },
  { value: "bank-transfer", label: "Bank Transfer", icon: Building },
]

export function PaymentDialog({ open, onOpenChange, order, onPaymentComplete }: PaymentDialogProps) {
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("cash")
  const [amountReceived, setAmountReceived] = useState("")
  const [mpesaCode, setMpesaCode] = useState("")
  const [processing, setProcessing] = useState(false)

  if (!order) return null

  const change = Number.parseFloat(amountReceived) - order.total
  const isValidPayment =
    paymentMethod === "cash"
      ? Number.parseFloat(amountReceived) >= order.total
      : paymentMethod === "mpesa"
        ? mpesaCode.trim() !== ""
        : true

  const handleProcessPayment = async () => {
    setProcessing(true)

    // Simulate payment processing
    await new Promise((resolve) => setTimeout(resolve, 2000))

    onPaymentComplete(order.id)
    setProcessing(false)
    resetForm()
  }

  const resetForm = () => {
    setPaymentMethod("cash")
    setAmountReceived("")
    setMpesaCode("")
  }

  const SelectedIcon = paymentMethods.find((m) => m.value === paymentMethod)?.icon || CreditCard

  return (
    <Dialog
      open={open}
      onOpenChange={(isOpen) => {
        onOpenChange(isOpen)
        if (!isOpen) resetForm()
      }}
    >
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Process Payment - {order.orderNumber}
          </DialogTitle>
          <DialogDescription>Complete the payment for this order</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Order Summary */}
          <Card className="p-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Customer:</span>
                <span className="font-medium">{order.customerName}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Items:</span>
                <span className="font-medium">{order.items.length}</span>
              </div>
              <Separator />
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal:</span>
                <span>{formatCurrency(order.subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Tax:</span>
                <span>{formatCurrency(order.tax)}</span>
              </div>
              {order.discount > 0 && (
                <div className="flex justify-between text-sm text-green-600">
                  <span>Discount:</span>
                  <span>-{formatCurrency(order.discount)}</span>
                </div>
              )}
              <Separator />
              <div className="flex justify-between text-lg font-bold">
                <span>Total:</span>
                <span className="text-primary">{formatCurrency(order.total)}</span>
              </div>
            </div>
          </Card>

          {/* Payment Method */}
          <div className="space-y-2">
            <Label>Payment Method</Label>
            <Select value={paymentMethod} onValueChange={(value) => setPaymentMethod(value as PaymentMethod)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {paymentMethods.map((method) => {
                  const Icon = method.icon
                  return (
                    <SelectItem key={method.value} value={method.value}>
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4" />
                        {method.label}
                      </div>
                    </SelectItem>
                  )
                })}
              </SelectContent>
            </Select>
          </div>

          {/* Payment Details */}
          {paymentMethod === "cash" && (
            <div className="space-y-2">
              <Label>Amount Received</Label>
              <Input
                type="number"
                placeholder="0.00"
                value={amountReceived}
                onChange={(e) => setAmountReceived(e.target.value)}
                min={order.total}
                step="0.01"
              />
              {amountReceived && Number.parseFloat(amountReceived) >= order.total && (
                <div className="text-sm">
                  <span className="text-muted-foreground">Change: </span>
                  <span className="font-bold text-green-600">{formatCurrency(change)}</span>
                </div>
              )}
            </div>
          )}

          {paymentMethod === "mpesa" && (
            <div className="space-y-2">
              <Label>M-Pesa Transaction Code</Label>
              <Input placeholder="Enter M-Pesa code" value={mpesaCode} onChange={(e) => setMpesaCode(e.target.value)} />
              <p className="text-xs text-muted-foreground">
                Customer should send {formatCurrency(order.total)} to the restaurant M-Pesa number
              </p>
            </div>
          )}

          {paymentMethod === "card" && (
            <div className="p-4 rounded-lg bg-muted text-center">
              <CreditCard className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Process card payment using the POS terminal</p>
            </div>
          )}

          {paymentMethod === "bank-transfer" && (
            <div className="p-4 rounded-lg bg-muted text-center">
              <Building className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Verify bank transfer receipt before completing</p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={processing}>
            Cancel
          </Button>
          <Button onClick={handleProcessPayment} disabled={!isValidPayment || processing}>
            <SelectedIcon className="mr-2 h-4 w-4" />
            {processing ? "Processing..." : "Complete Payment"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
