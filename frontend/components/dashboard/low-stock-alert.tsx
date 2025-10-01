"use client"

import type { InventoryItem } from "@/lib/types"
import { AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface LowStockAlertProps {
  items: InventoryItem[]
}

export function LowStockAlert({ items }: LowStockAlertProps) {
  return (
    <div className="space-y-3">
      {items.slice(0, 5).map((item) => (
        <div key={item.id} className="flex items-center justify-between p-3 rounded-lg bg-background border">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-4 w-4 text-destructive" />
            <div>
              <p className="font-medium">{item.name}</p>
              <p className="text-sm text-muted-foreground">
                Current: {item.quantity} {item.unit} • Min: {item.reorderLevel} {item.unit}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-destructive">Low Stock</p>
            <p className="text-xs text-muted-foreground">{item.category}</p>
          </div>
        </div>
      ))}
      {items.length > 5 && (
        <p className="text-sm text-muted-foreground text-center">And {items.length - 5} more items need restocking</p>
      )}
      <Button asChild className="w-full mt-4">
        <Link href="/inventory">View Inventory</Link>
      </Button>
    </div>
  )
}
