"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Edit, Key, Trash2 } from "lucide-react"
import type { User } from "@/lib/types"
import { deleteUser } from "@/lib/api/data-service"

interface StaffListProps {
  staff: User[]
  loading: boolean
  onEdit: (staff: User) => void
  onChangePassword: (staff: User) => void
  onRefresh: () => void
}

const roleColors = {
  admin: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100",
  manager: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100",
  receptionist: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
  waiter: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100",
  kitchen: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100",
  cashier: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100",
}

export function StaffList({ staff, loading, onEdit, onChangePassword, onRefresh }: StaffListProps) {
  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to delete ${name}? This action cannot be undone.`)) {
      await deleteUser(id)
      onRefresh()
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-16 rounded bg-muted" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (staff.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <p className="text-muted-foreground">No staff members found</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {staff.map((member) => (
        <Card key={member.id}>
          <CardContent className="p-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-semibold">{member.name}</h3>
                  <Badge className={roleColors[member.role as keyof typeof roleColors]}>
                    {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{member.email}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => onEdit(member)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit
                </Button>
                <Button variant="outline" size="sm" onClick={() => onChangePassword(member)}>
                  <Key className="mr-2 h-4 w-4" />
                  Password
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleDelete(member.id, member.name)}>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
