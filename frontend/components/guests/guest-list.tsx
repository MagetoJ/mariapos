"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Eye, User, Phone, Calendar, DoorOpen } from "lucide-react"
import { formatCurrency, formatDate } from "@/lib/utils"
import type { Guest } from "@/lib/types"

interface GuestListProps {
  guests: Guest[]
  loading: boolean
  onViewDetails: (guest: Guest) => void
  onRefresh: () => void
}

export function GuestList({ guests, loading, onViewDetails, onRefresh }: GuestListProps) {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-32 rounded bg-muted" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (guests.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <User className="mb-4 h-12 w-12 text-muted-foreground" />
          <p className="text-lg font-medium text-muted-foreground">No guests found</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {guests.map((guest) => (
        <Card key={guest.id} className={guest.status === "checked-in" ? "border-primary" : ""}>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                    <User className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">{guest.name}</h3>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <DoorOpen className="h-3 w-3" />
                      Room {guest.roomNumber}
                    </div>
                  </div>
                </div>
                <Badge variant={guest.status === "checked-in" ? "default" : "secondary"}>
                  {guest.status === "checked-in" ? "Checked In" : "Checked Out"}
                </Badge>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Phone className="h-3 w-3" />
                  {guest.phone}
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Calendar className="h-3 w-3" />
                  {formatDate(guest.checkInDate)} - {formatDate(guest.checkOutDate)}
                </div>
              </div>

              <div className="flex items-center justify-between border-t pt-3">
                <div>
                  <p className="text-xs text-muted-foreground">Total Spent</p>
                  <p className="font-semibold">{formatCurrency(guest.totalSpent)}</p>
                </div>
                <Button size="sm" onClick={() => onViewDetails(guest)}>
                  <Eye className="mr-2 h-4 w-4" />
                  Details
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
