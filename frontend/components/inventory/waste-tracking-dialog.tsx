"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { trackWaste } from "@/lib/api/data-service"
import type { InventoryItem } from "@/lib/types"

interface WasteTrackingDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  inventory: InventoryItem[]
  onSuccess: () => void
}

export function WasteTrackingDialog({ open, onOpenChange, inventory, onSuccess }: WasteTrackingDialogProps) {
  const [formData, setFormData] = useState({
    itemId: "",
    quantity: 0,
    reason: "",
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await trackWaste(formData.itemId, formData.quantity, formData.reason)
      onSuccess()
      onOpenChange(false)
      setFormData({ itemId: "", quantity: 0, reason: "" })
    } catch (error) {
      console.error("Failed to track waste:", error)
    } finally {
      setLoading(false)
    }
  }

  const selectedItem = inventory.find((item) => item.id === formData.itemId)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Track Waste</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="item">Item</Label>
            <Select value={formData.itemId} onValueChange={(value) => setFormData({ ...formData, itemId: value })}>
              <SelectTrigger>
                <SelectValue placeholder="Select item" />
              </SelectTrigger>
              <SelectContent>
                {inventory.map((item) => (
                  <SelectItem key={item.id} value={item.id}>
                    {item.name} ({item.quantity} {item.unit} available)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity Wasted</Label>
            <div className="flex gap-2">
              <Input
                id="quantity"
                type="number"
                min="0"
                step="0.1"
                max={selectedItem?.quantity || 0}
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: Number.parseFloat(e.target.value) })}
                required
              />
              {selectedItem && (
                <div className="flex items-center rounded-md border px-3 text-sm text-muted-foreground">
                  {selectedItem.unit}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="reason">Reason</Label>
            <Textarea
              id="reason"
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              placeholder="e.g., Expired, Damaged, Spoiled"
              required
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !formData.itemId}>
              {loading ? "Tracking..." : "Track Waste"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
