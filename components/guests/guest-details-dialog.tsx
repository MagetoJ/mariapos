"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { User, Phone, Mail, Calendar, DoorOpen, DollarSign, LogOut } from "lucide-react"
import { formatCurrency, formatDate } from "@/lib/utils"
import { checkOutGuest } from "@/lib/api/data-service"
import type { Guest } from "@/lib/types"

interface GuestDetailsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  guest: Guest
  onSuccess: () => void
}

export function GuestDetailsDialog({ open, onOpenChange, guest, onSuccess }: GuestDetailsDialogProps) {
  const [loading, setLoading] = useState(false)

  const handleCheckOut = async () => {
    if (!confirm(`Check out ${guest.name} from Room ${guest.roomNumber}?`)) return

    setLoading(true)
    try {
      await checkOutGuest(guest.id)
      onSuccess()
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to check out guest:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Guest Details</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <User className="h-8 w-8 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">{guest.name}</h3>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <DoorOpen className="h-4 w-4" />
                  Room {guest.roomNumber}
                </div>
              </div>
            </div>
            <Badge variant={guest.status === "checked-in" ? "default" : "secondary"}>
              {guest.status === "checked-in" ? "Checked In" : "Checked Out"}
            </Badge>
          </div>

          <Separator />

          <div className="space-y-4">
            <div className="flex items-center gap-3 text-sm">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span>{guest.phone}</span>
            </div>

            {guest.email && (
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>{guest.email}</span>
              </div>
            )}

            <div className="flex items-center gap-3 text-sm">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="font-medium">Check In: {formatDate(guest.checkInDate)}</p>
                <p className="text-muted-foreground">Check Out: {formatDate(guest.checkOutDate)}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 text-sm">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="font-medium">Total Spent</p>
                <p className="text-lg font-bold text-primary">{formatCurrency(guest.totalSpent)}</p>
              </div>
            </div>
          </div>

          {guest.status === "checked-in" && (
            <>
              <Separator />
              <Button className="w-full" variant="destructive" onClick={handleCheckOut} disabled={loading}>
                <LogOut className="mr-2 h-4 w-4" />
                {loading ? "Checking Out..." : "Check Out Guest"}
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
