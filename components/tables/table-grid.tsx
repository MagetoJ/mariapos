"use client"

import type React from "react"

import type { Table, User } from "@/lib/types"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Users, Calendar, CheckCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { formatTime } from "@/lib/utils/format"

interface TableGridProps {
  tables: Table[]
  waiters: User[]
  onTableClick: (table: Table) => void
  onReserveClick: (table: Table) => void
  onUpdateTable: (tableId: string, updates: Partial<Table>) => void
}

const statusConfig = {
  available: {
    color: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
    bgColor: "bg-green-50 dark:bg-green-950/20",
    borderColor: "border-green-200 dark:border-green-800",
  },
  occupied: {
    color: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
    bgColor: "bg-blue-50 dark:bg-blue-950/20",
    borderColor: "border-blue-200 dark:border-blue-800",
  },
  reserved: {
    color: "bg-purple-500/10 text-purple-700 dark:text-purple-400 border-purple-500/20",
    bgColor: "bg-purple-50 dark:bg-purple-950/20",
    borderColor: "border-purple-200 dark:border-purple-800",
  },
  cleaning: {
    color: "bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20",
    bgColor: "bg-orange-50 dark:bg-orange-950/20",
    borderColor: "border-orange-200 dark:border-orange-800",
  },
}

export function TableGrid({ tables, waiters, onTableClick, onReserveClick, onUpdateTable }: TableGridProps) {
  if (tables.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium mb-2">No tables found</p>
          <p className="text-sm">Tables matching this filter will appear here</p>
        </div>
      </Card>
    )
  }

  const handleMarkAvailable = (table: Table, e: React.MouseEvent) => {
    e.stopPropagation()
    onUpdateTable(table.id, {
      status: "available",
      currentOrderId: undefined,
      waiterId: undefined,
      reservedBy: undefined,
      reservedAt: undefined,
    })
  }

  const handleMarkCleaning = (table: Table, e: React.MouseEvent) => {
    e.stopPropagation()
    onUpdateTable(table.id, { status: "cleaning" })
  }

  return (
    <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      {tables.map((table) => {
        const config = statusConfig[table.status]
        const waiter = waiters.find((w) => w.id === table.waiterId)

        return (
          <Card
            key={table.id}
            className={cn(
              "p-4 cursor-pointer hover:shadow-lg transition-all",
              config.bgColor,
              config.borderColor,
              "border-2",
            )}
            onClick={() => onTableClick(table)}
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-2xl font-bold">Table {table.number}</p>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                    <Users className="h-3 w-3" />
                    <span>{table.capacity} seats</span>
                  </div>
                </div>
                <Badge variant="outline" className={cn("capitalize", config.color)}>
                  {table.status}
                </Badge>
              </div>

              {table.section && (
                <div className="text-xs text-muted-foreground">
                  <span className="font-medium">{table.section}</span>
                </div>
              )}

              {waiter && (
                <div className="text-sm">
                  <p className="text-muted-foreground text-xs">Waiter</p>
                  <p className="font-medium">{waiter.name}</p>
                </div>
              )}

              {table.reservedBy && table.reservedAt && (
                <div className="text-sm">
                  <p className="text-muted-foreground text-xs">Reserved by</p>
                  <p className="font-medium">{table.reservedBy}</p>
                  <p className="text-xs text-muted-foreground">{formatTime(table.reservedAt)}</p>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                {table.status === "available" && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 bg-transparent"
                    onClick={(e) => {
                      e.stopPropagation()
                      onReserveClick(table)
                    }}
                  >
                    <Calendar className="mr-1 h-3 w-3" />
                    Reserve
                  </Button>
                )}
                {table.status === "occupied" && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 bg-transparent"
                    onClick={(e) => handleMarkCleaning(table, e)}
                  >
                    Clear
                  </Button>
                )}
                {table.status === "cleaning" && (
                  <Button size="sm" className="flex-1" onClick={(e) => handleMarkAvailable(table, e)}>
                    <CheckCircle className="mr-1 h-3 w-3" />
                    Ready
                  </Button>
                )}
                {table.status === "reserved" && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 bg-transparent"
                    onClick={(e) => handleMarkAvailable(table, e)}
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
