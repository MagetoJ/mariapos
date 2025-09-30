"use client"

import { useState, useEffect } from "react"
import { useAuthStore } from "@/lib/store/auth-store"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search } from "lucide-react"
import { StaffList } from "@/components/staff/staff-list"
import { StaffDialog } from "@/components/staff/staff-dialog"
import { ChangePasswordDialog } from "@/components/staff/change-password-dialog"
import { getUsers } from "@/lib/api/data-service"
import type { User } from "@/lib/types"

function StaffPage() {
  const { user } = useAuthStore()
  const [staff, setStaff] = useState<User[]>([])
  const [filteredStaff, setFilteredStaff] = useState<User[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [roleFilter, setRoleFilter] = useState<string>("all")
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [editingStaff, setEditingStaff] = useState<User | null>(null)
  const [changingPassword, setChangingPassword] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStaff()
  }, [])

  useEffect(() => {
    filterStaff()
  }, [staff, searchQuery, roleFilter])

  const loadStaff = async () => {
    setLoading(true)
    const data = await getUsers()
    setStaff(data)
    setLoading(false)
  }

  const filterStaff = () => {
    let filtered = staff

    if (searchQuery) {
      filtered = filtered.filter(
        (member) =>
          member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          member.email.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    }

    if (roleFilter !== "all") {
      filtered = filtered.filter((member) => member.role === roleFilter)
    }

    setFilteredStaff(filtered)
  }

  const roles = ["all", "admin", "manager", "receptionist", "waiter", "kitchen", "cashier"]

  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AppLayout>
        <div className="space-y-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Staff Management</h1>
              <p className="text-muted-foreground">Manage staff accounts and permissions</p>
            </div>
            <Button onClick={() => setShowAddDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Staff Member
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <div className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">Total Staff</p>
              <p className="text-2xl font-bold">{staff.length}</p>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">Admins</p>
              <p className="text-2xl font-bold">{staff.filter((s) => s.role === "admin").length}</p>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">Managers</p>
              <p className="text-2xl font-bold">{staff.filter((s) => s.role === "manager").length}</p>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">Waiters</p>
              <p className="text-2xl font-bold">{staff.filter((s) => s.role === "waiter").length}</p>
            </div>
          </div>

          <div className="flex flex-col gap-4 md:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search staff by name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="flex gap-2 overflow-x-auto">
              {roles.map((role) => (
                <Button
                  key={role}
                  variant={roleFilter === role ? "default" : "outline"}
                  onClick={() => setRoleFilter(role)}
                  className="whitespace-nowrap"
                >
                  {role.charAt(0).toUpperCase() + role.slice(1)}
                </Button>
              ))}
            </div>
          </div>

          <StaffList
            staff={filteredStaff}
            loading={loading}
            onEdit={(member) => setEditingStaff(member)}
            onChangePassword={(member) => setChangingPassword(member)}
            onRefresh={loadStaff}
          />

          {showAddDialog && <StaffDialog open={showAddDialog} onOpenChange={setShowAddDialog} onSuccess={loadStaff} />}

          {editingStaff && (
            <StaffDialog
              open={!!editingStaff}
              onOpenChange={(open) => !open && setEditingStaff(null)}
              staff={editingStaff}
              onSuccess={loadStaff}
            />
          )}

          {changingPassword && (
            <ChangePasswordDialog
              open={!!changingPassword}
              onOpenChange={(open) => !open && setChangingPassword(null)}
              staff={changingPassword}
              onSuccess={loadStaff}
            />
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  )
}

export default StaffPage
