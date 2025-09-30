"use client"

import { useState, useEffect } from "react"
import { useAuthStore } from "@/lib/store/auth-store"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search } from "lucide-react"
import { GuestList } from "@/components/guests/guest-list"
import { CheckInDialog } from "@/components/guests/check-in-dialog"
import { GuestDetailsDialog } from "@/components/guests/guest-details-dialog"
import { getGuests } from "@/lib/api/data-service"
import type { Guest } from "@/lib/types"

function GuestsPage() {
  const { user } = useAuthStore()
  const [guests, setGuests] = useState<Guest[]>([])
  const [filteredGuests, setFilteredGuests] = useState<Guest[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<"all" | "checked-in" | "checked-out">("all")
  const [showCheckInDialog, setShowCheckInDialog] = useState(false)
  const [selectedGuest, setSelectedGuest] = useState<Guest | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGuests()
  }, [])

  useEffect(() => {
    filterGuests()
  }, [guests, searchQuery, statusFilter])

  const loadGuests = async () => {
    setLoading(true)
    const data = await getGuests()
    setGuests(data)
    setLoading(false)
  }

  const filterGuests = () => {
    let filtered = guests

    if (searchQuery) {
      filtered = filtered.filter(
        (guest) =>
          guest.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          guest.roomNumber.includes(searchQuery) ||
          guest.phone.includes(searchQuery),
      )
    }

    if (statusFilter !== "all") {
      filtered = filtered.filter((guest) => guest.status === statusFilter)
    }

    setFilteredGuests(filtered)
  }

  const checkedInCount = guests.filter((g) => g.status === "checked-in").length

  return (
    <ProtectedRoute allowedRoles={["admin", "manager", "receptionist"]}>
      <AppLayout>
        <div className="space-y-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Guest Management</h1>
              <p className="text-muted-foreground">Manage hotel guests and room assignments</p>
            </div>
            <Button onClick={() => setShowCheckInDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Check In Guest
            </Button>
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Currently Checked In</p>
                <p className="text-2xl font-bold">{checkedInCount} Guests</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Total Guests</p>
                <p className="text-2xl font-bold">{guests.length}</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-4 md:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name, room, or phone..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="flex gap-2">
              <Button variant={statusFilter === "all" ? "default" : "outline"} onClick={() => setStatusFilter("all")}>
                All
              </Button>
              <Button
                variant={statusFilter === "checked-in" ? "default" : "outline"}
                onClick={() => setStatusFilter("checked-in")}
              >
                Checked In
              </Button>
              <Button
                variant={statusFilter === "checked-out" ? "default" : "outline"}
                onClick={() => setStatusFilter("checked-out")}
              >
                Checked Out
              </Button>
            </div>
          </div>

          <GuestList
            guests={filteredGuests}
            loading={loading}
            onViewDetails={(guest) => setSelectedGuest(guest)}
            onRefresh={loadGuests}
          />

          {showCheckInDialog && (
            <CheckInDialog open={showCheckInDialog} onOpenChange={setShowCheckInDialog} onSuccess={loadGuests} />
          )}

          {selectedGuest && (
            <GuestDetailsDialog
              open={!!selectedGuest}
              onOpenChange={(open) => !open && setSelectedGuest(null)}
              guest={selectedGuest}
              onSuccess={loadGuests}
            />
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  )
}

export default GuestsPage
