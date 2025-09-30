"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Edit, Package, AlertTriangle } from "lucide-react"
import type { InventoryItem } from "@/lib/types"

interface InventoryListProps {
  inventory: InventoryItem[]
  loading: boolean
  onEdit?: (item: InventoryItem) => void
  onRefresh: () => void
}

export function InventoryList({ inventory, loading, onEdit, onRefresh }: InventoryListProps) {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-20 rounded bg-muted" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (inventory.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Package className="mb-4 h-12 w-12 text-muted-foreground" />
          <p className="text-lg font-medium text-muted-foreground">No inventory items found</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {inventory.map((item) => {
        const isLowStock = item.quantity <= item.reorderLevel
        const stockPercentage = (item.quantity / (item.reorderLevel * 2)) * 100

        return (
          <Card key={item.id} className={isLowStock ? "border-orange-500" : ""}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-foreground">{item.name}</h3>
                    {isLowStock && <AlertTriangle className="h-4 w-4 text-orange-500" />}
                  </div>
                  <p className="text-sm text-muted-foreground capitalize">{item.category}</p>
                </div>
                {onEdit && (
                  <Button variant="ghost" size="icon" onClick={() => onEdit(item)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                )}
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Current Stock</span>
                  <span className={`font-semibold ${isLowStock ? "text-orange-500" : "text-foreground"}`}>
                    {item.quantity} {item.unit}
                  </span>
                </div>

                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className={`h-full transition-all ${isLowStock ? "bg-orange-500" : "bg-primary"}`}
                    style={{ width: `${Math.min(stockPercentage, 100)}%` }}
                  />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Reorder Level</span>
                  <span className="text-muted-foreground">
                    {item.reorderLevel} {item.unit}
                  </span>
                </div>

                {item.lastRestocked && (
                  <div className="pt-2 text-xs text-muted-foreground">
                    Last restocked: {new Date(item.lastRestocked).toLocaleDateString()}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
