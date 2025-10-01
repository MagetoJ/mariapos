"use client"

import { useState } from "react"
import type { Table } from "@/lib/types"
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

interface ReservationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  table: Table | null
  tables: Table[]
  onUpdateTable: (tableId: string, updates: Partial<Table>) => void
}

export function ReservationDialog({ open, onOpenChange, table, tables, onUpdateTable }: ReservationDialogProps) {
  const [selectedTableId, setSelectedTableId] = useState<string>(table?.id || "")
  const [customerName, setCustomerName] = useState("")
  const [reservationDate, setReservationDate] = useState("")
  const [reservationTime, setReservationTime] = useState("")

  const handleSubmit = () => {
    if (!selectedTableId || !customerName || !reservationDate || !reservationTime) {
      return
    }

    const reservationDateTime = new Date(`${reservationDate}T${reservationTime}`)

    onUpdateTable(selectedTableId, {
      status: "reserved",
      reservedBy: customerName,
      reservedAt: reservationDateTime.toISOString(),
    })

    resetForm()
    onOpenChange(false)
  }

  const resetForm = () => {
    setSelectedTableId("")
    setCustomerName("")
    setReservationDate("")
    setReservationTime("")
  }

  // Get today's date in YYYY-MM-DD format for min attribute
  const today = new Date().toISOString().split("T")[0]

  return (
    <Dialog
      open={open}
      onOpenChange={(isOpen) => {
        onOpenChange(isOpen)
        if (!isOpen) resetForm()
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Reservation</DialogTitle>
          <DialogDescription>Reserve a table for a customer</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Table</Label>
            <Select value={selectedTableId} onValueChange={setSelectedTableId}>
              <SelectTrigger>
                <SelectValue placeholder="Select table" />
              </SelectTrigger>
              <SelectContent>
                {tables.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    Table {t.number} - {t.capacity} seats ({t.section})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Customer Name</Label>
            <Input
              placeholder="Enter customer name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Date</Label>
              <Input
                type="date"
                min={today}
                value={reservationDate}
                onChange={(e) => setReservationDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Time</Label>
              <Input type="time" value={reservationTime} onChange={(e) => setReservationTime(e.target.value)} />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!selectedTableId || !customerName || !reservationDate || !reservationTime}
          >
            Create Reservation
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
