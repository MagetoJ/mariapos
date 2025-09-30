"use client"

import type { Table, User } from "@/lib/types"
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Users, MapPin } from "lucide-react"
import { cn } from "@/lib/utils"
import { formatDateTime } from "@/lib/utils/format"
import { useState } from "react"

interface TableDetailsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  table: Table | null
  waiters: User[]
  onUpdateTable: (tableId: string, updates: Partial<Table>) => void
}

const statusColors = {
  available: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
  occupied: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
  reserved: "bg-purple-500/10 text-purple-700 dark:text-purple-400 border-purple-500/20",
  cleaning: "bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20",
}

export function TableDetailsDialog({ open, onOpenChange, table, waiters, onUpdateTable }: TableDetailsDialogProps) {
  const [selectedWaiterId, setSelectedWaiterId] = useState<string>("")

  if (!table) return null

  const assignedWaiter = waiters.find((w) => w.id === table.waiterId)

  const handleAssignWaiter = () => {
    if (selectedWaiterId) {
      onUpdateTable(table.id, { waiterId: selectedWaiterId })
      setSelectedWaiterId("")
    }
  }

  const handleChangeStatus = (status: Table["status"]) => {
    const updates: Partial<Table> = { status }
    if (status === "available") {
      updates.currentOrderId = undefined
      updates.waiterId = undefined
      updates.reservedBy = undefined
      updates.reservedAt = undefined
    }
    onUpdateTable(table.id, updates)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span>Table {table.number}</span>
            <Badge variant="outline" className={cn("capitalize", statusColors[table.status])}>
              {table.status}
            </Badge>
          </DialogTitle>
          <DialogDescription>Table details and management</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Card className="p-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground flex items-center gap-1">
                  <Users className="h-3 w-3" />
                  Capacity
                </p>
                <p className="font-medium text-lg">{table.capacity} seats</p>
              </div>
              {table.section && (
                <div>
                  <p className="text-muted-foreground flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    Section
                  </p>
                  <p className="font-medium text-lg">{table.section}</p>
                </div>
              )}
            </div>
          </Card>

          {assignedWaiter && (
            <Card className="p-4">
              <p className="text-sm text-muted-foreground mb-2">Assigned Waiter</p>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                  {assignedWaiter.name.charAt(0)}
                </div>
                <div>
                  <p className="font-medium">{assignedWaiter.name}</p>
                  <p className="text-xs text-muted-foreground">{assignedWaiter.email}</p>
                </div>
              </div>
            </Card>
          )}

          {table.reservedBy && table.reservedAt && (
            <Card className="p-4">
              <p className="text-sm text-muted-foreground mb-2">Reservation Details</p>
              <div className="space-y-1">
                <p className="font-medium">{table.reservedBy}</p>
                <p className="text-sm text-muted-foreground">{formatDateTime(table.reservedAt)}</p>
              </div>
            </Card>
          )}

          {table.currentOrderId && (
            <Card className="p-4">
              <p className="text-sm text-muted-foreground mb-2">Current Order</p>
              <p className="font-medium">{table.currentOrderId}</p>
            </Card>
          )}

          <div className="space-y-2">
            <Label>Assign Waiter</Label>
            <div className="flex gap-2">
              <Select value={selectedWaiterId} onValueChange={setSelectedWaiterId}>
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder="Select waiter" />
                </SelectTrigger>
                <SelectContent>
                  {waiters.map((waiter) => (
                    <SelectItem key={waiter.id} value={waiter.id}>
                      {waiter.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button onClick={handleAssignWaiter} disabled={!selectedWaiterId}>
                Assign
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Change Status</Label>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant={table.status === "available" ? "default" : "outline"}
                size="sm"
                onClick={() => handleChangeStatus("available")}
                className="bg-transparent"
              >
                Available
              </Button>
              <Button
                variant={table.status === "occupied" ? "default" : "outline"}
                size="sm"
                onClick={() => handleChangeStatus("occupied")}
                className="bg-transparent"
              >
                Occupied
              </Button>
              <Button
                variant={table.status === "reserved" ? "default" : "outline"}
                size="sm"
                onClick={() => handleChangeStatus("reserved")}
                className="bg-transparent"
              >
                Reserved
              </Button>
              <Button
                variant={table.status === "cleaning" ? "default" : "outline"}
                size="sm"
                onClick={() => handleChangeStatus("cleaning")}
                className="bg-transparent"
              >
                Cleaning
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
