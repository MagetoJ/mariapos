"use client"

import { useState } from "react"
import type { Order, MenuItem, Table, OrderItem, OrderType } from "@/lib/types"
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
import { Badge } from "@/components/ui/badge"
import { Plus, Minus, Trash2 } from "lucide-react"
import { formatCurrency } from "@/lib/utils/format"
import { useAuthStore } from "@/lib/store/auth-store"

interface CreateOrderDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreateOrder: (order: Omit<Order, "id" | "orderNumber" | "createdAt" | "updatedAt">) => void
  menuItems: MenuItem[]
  tables: Table[]
}

export function CreateOrderDialog({ open, onOpenChange, onCreateOrder, menuItems, tables }: CreateOrderDialogProps) {
  const { user } = useAuthStore()
  const [orderType, setOrderType] = useState<OrderType>("dine-in")
  const [tableId, setTableId] = useState<string>("")
  const [roomNumber, setRoomNumber] = useState("")
  const [customerName, setCustomerName] = useState("")
  const [selectedItems, setSelectedItems] = useState<OrderItem[]>([])
  const [notes, setNotes] = useState("")
  const [searchQuery, setSearchQuery] = useState("")

  const availableTables = tables.filter((t) => t.status === "available")

  const handleAddItem = (menuItem: MenuItem) => {
    const existingItem = selectedItems.find((item) => item.menuItemId === menuItem.id)

    if (existingItem) {
      setSelectedItems(
        selectedItems.map((item) =>
          item.menuItemId === menuItem.id ? { ...item, quantity: item.quantity + 1 } : item,
        ),
      )
    } else {
      const newItem: OrderItem = {
        id: `temp-${Date.now()}`,
        menuItemId: menuItem.id,
        menuItem,
        quantity: 1,
        price: menuItem.price,
        status: "pending",
      }
      setSelectedItems([...selectedItems, newItem])
    }
  }

  const handleUpdateQuantity = (itemId: string, delta: number) => {
    setSelectedItems(
      selectedItems
        .map((item) => (item.id === itemId ? { ...item, quantity: Math.max(0, item.quantity + delta) } : item))
        .filter((item) => item.quantity > 0),
    )
  }

  const handleRemoveItem = (itemId: string) => {
    setSelectedItems(selectedItems.filter((item) => item.id !== itemId))
  }

  const calculateTotals = () => {
    const subtotal = selectedItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
    const tax = subtotal * 0.1 // 10% tax
    const total = subtotal + tax
    return { subtotal, tax, total }
  }

  const handleSubmit = () => {
    if (selectedItems.length === 0) return

    const { subtotal, tax, total } = calculateTotals()

    const order: Omit<Order, "id" | "orderNumber" | "createdAt" | "updatedAt"> = {
      type: orderType,
      tableId: orderType === "dine-in" ? tableId : undefined,
      roomNumber: orderType === "room-service" ? roomNumber : undefined,
      customerName: customerName || (orderType === "dine-in" ? `Table ${tableId}` : "Customer"),
      items: selectedItems,
      subtotal,
      tax,
      discount: 0,
      total,
      status: "pending",
      waiterId: user?.id,
      waiter: user || undefined,
      notes,
    }

    onCreateOrder(order)
    resetForm()
  }

  const resetForm = () => {
    setOrderType("dine-in")
    setTableId("")
    setRoomNumber("")
    setCustomerName("")
    setSelectedItems([])
    setNotes("")
    setSearchQuery("")
  }

  const filteredMenuItems = menuItems.filter(
    (item) =>
      item.isAvailable &&
      (item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.category.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const { subtotal, tax, total } = calculateTotals()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Order</DialogTitle>
          <DialogDescription>Add items to create a new order</DialogDescription>
        </DialogHeader>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Left: Order Details */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Order Type</Label>
              <Select value={orderType} onValueChange={(value) => setOrderType(value as OrderType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dine-in">Dine In</SelectItem>
                  <SelectItem value="takeaway">Takeaway</SelectItem>
                  <SelectItem value="room-service">Room Service</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {orderType === "dine-in" && (
              <div className="space-y-2">
                <Label>Table</Label>
                <Select value={tableId} onValueChange={setTableId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select table" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableTables.map((table) => (
                      <SelectItem key={table.id} value={table.id}>
                        Table {table.number} (Capacity: {table.capacity})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {orderType === "room-service" && (
              <div className="space-y-2">
                <Label>Room Number</Label>
                <Input
                  placeholder="Enter room number"
                  value={roomNumber}
                  onChange={(e) => setRoomNumber(e.target.value)}
                />
              </div>
            )}

            <div className="space-y-2">
              <Label>Customer Name (Optional)</Label>
              <Input
                placeholder="Enter customer name"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Notes (Optional)</Label>
              <Input placeholder="Special instructions" value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>

            {/* Selected Items */}
            <div className="space-y-2">
              <Label>Order Items ({selectedItems.length})</Label>
              <Card className="p-4 max-h-64 overflow-y-auto">
                {selectedItems.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">No items added yet</p>
                ) : (
                  <div className="space-y-2">
                    {selectedItems.map((item) => (
                      <div key={item.id} className="flex items-center justify-between gap-2 p-2 rounded bg-muted">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{item.menuItem.name}</p>
                          <p className="text-xs text-muted-foreground">{formatCurrency(item.price)}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-6 w-6 bg-transparent"
                            onClick={() => handleUpdateQuantity(item.id, -1)}
                          >
                            <Minus className="h-3 w-3" />
                          </Button>
                          <span className="text-sm font-medium w-6 text-center">{item.quantity}</span>
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-6 w-6 bg-transparent"
                            onClick={() => handleUpdateQuantity(item.id, 1)}
                          >
                            <Plus className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => handleRemoveItem(item.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>

            {/* Totals */}
            <Card className="p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal:</span>
                <span>{formatCurrency(subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Tax (10%):</span>
                <span>{formatCurrency(tax)}</span>
              </div>
              <div className="flex justify-between text-lg font-bold pt-2 border-t">
                <span>Total:</span>
                <span className="text-primary">{formatCurrency(total)}</span>
              </div>
            </Card>
          </div>

          {/* Right: Menu Items */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Search Menu</Label>
              <Input
                placeholder="Search items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="max-h-[500px] overflow-y-auto space-y-2">
              {filteredMenuItems.map((item) => (
                <Card
                  key={item.id}
                  className="p-3 cursor-pointer hover:bg-accent transition-colors"
                  onClick={() => handleAddItem(item)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{item.name}</p>
                      <p className="text-xs text-muted-foreground line-clamp-1">{item.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="text-xs">
                          {item.category}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{item.preparationTime} min</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary">{formatCurrency(item.price)}</p>
                      <Button size="sm" variant="ghost" className="h-6 mt-1">
                        <Plus className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={selectedItems.length === 0}>
            Create Order
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
