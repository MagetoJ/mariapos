"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { userService } from "@/lib/api/data-service"
import type { User } from "@/lib/types"

interface StaffDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  staff?: User
  onSuccess: () => void
}

export function StaffDialog({ open, onOpenChange, staff, onSuccess }: StaffDialogProps) {
  const [formData, setFormData] = useState<{
    name: string
    email: string
    password?: string
    confirm_password?: string
    role: User["role"]
    isActive: boolean
  }>({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "waiter" as User["role"],
    isActive: true,
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (staff) {
      setFormData({
        name: staff.name,
        email: staff.email,
        password: "",
        confirm_password: "",
        role: staff.role,
        isActive: staff.isActive,
      })
    } else {
      setFormData({
        name: "",
        email: "",
        password: "",
        confirm_password: "",
        role: "waiter",
        isActive: true,
      })
    }
  }, [staff])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Validate passwords match for new users
      if (!staff && formData.password !== formData.confirm_password) {
        alert("Passwords do not match")
        setLoading(false)
        return
      }

      if (staff) {
        // For updates, don't send password fields if empty
        const updateData = { ...formData }
        if (!updateData.password) {
          delete updateData.password
          delete updateData.confirm_password
        }
        await userService.updateUser(staff.id, updateData)
      } else {
        await userService.createUser(formData)
      }
      onSuccess()
      onOpenChange(false)
    } catch (error: any) {
      console.error("Error saving staff:", error)
      const errorMessage = error?.message || "Failed to save staff member"
      alert(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{staff ? "Edit Staff Member" : "Add Staff Member"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          {!staff && (
            <>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required={!staff}
                  placeholder={staff ? "Leave blank to keep current password" : ""}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirm Password</Label>
                <Input
                  id="confirm_password"
                  type="password"
                  value={formData.confirm_password}
                  onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                  required={!staff}
                  placeholder="Confirm your password"
                />
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select
              value={formData.role}
              onValueChange={(value) => setFormData({ ...formData, role: value as User["role"] })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="admin">Admin</SelectItem>
                <SelectItem value="manager">Manager</SelectItem>
                <SelectItem value="receptionist">Receptionist</SelectItem>
                <SelectItem value="waiter">Waiter</SelectItem>
                <SelectItem value="kitchen">Kitchen Staff</SelectItem>
                <SelectItem value="cashier">Cashier</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : staff ? "Update" : "Create"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
