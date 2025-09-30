"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, TrendingDown, Package } from "lucide-react"

interface InventoryReportProps {
  data: any
}

export function InventoryReport({ data }: InventoryReportProps) {
  if (!data) return null

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.summary.totalItems}</div>
            <p className="text-xs text-muted-foreground">Across {data.summary.categories} categories</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Stock</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-500">{data.summary.lowStock}</div>
            <p className="text-xs text-muted-foreground">Requires reordering</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Waste This Period</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">KES {data.summary.wasteValue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">{data.summary.wastePercentage}% of inventory value</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Low Stock Items</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.lowStockItems.map((item: any) => (
              <div key={item.id} className="flex items-center justify-between rounded-lg border p-3">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-5 w-5 text-orange-500" />
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="text-sm text-muted-foreground capitalize">{item.category}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-orange-500">
                    {item.quantity} {item.unit}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Reorder: {item.reorderLevel} {item.unit}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Most Used Items</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.mostUsed.map((item: any, index: number) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {item.used} {item.unit} used
                      </p>
                    </div>
                  </div>
                  <Badge variant="secondary">{item.frequency}</Badge>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div className="h-full bg-primary transition-all" style={{ width: `${item.percentage}%` }} />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Waste Tracking</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.wasteLog.map((entry: any, index: number) => (
              <div key={index} className="flex items-start justify-between rounded-lg border p-3">
                <div>
                  <p className="font-medium">{entry.item}</p>
                  <p className="text-sm text-muted-foreground">{entry.reason}</p>
                  <p className="text-xs text-muted-foreground">{entry.date}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-orange-500">
                    {entry.quantity} {entry.unit}
                  </p>
                  <p className="text-sm text-muted-foreground">KES {entry.value.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
