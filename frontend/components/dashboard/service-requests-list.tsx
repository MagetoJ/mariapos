"use client"

import type { ServiceRequest } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Clock, CheckCircle } from "lucide-react"
import { getRelativeTime } from "@/lib/utils/format"
import { updateServiceRequest } from "@/lib/api/data-service"
import { useState } from "react"

interface ServiceRequestsListProps {
  requests: ServiceRequest[]
}

const priorityColors = {
  low: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
  medium: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20",
  high: "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20",
}

const statusColors = {
  pending: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400",
  "in-progress": "bg-blue-500/10 text-blue-700 dark:text-blue-400",
  completed: "bg-green-500/10 text-green-700 dark:text-green-400",
  cancelled: "bg-red-500/10 text-red-700 dark:text-red-400",
}

export function ServiceRequestsList({ requests }: ServiceRequestsListProps) {
  const [localRequests, setLocalRequests] = useState(requests)

  const handleUpdateStatus = async (id: string, status: ServiceRequest["status"]) => {
    try {
      await updateServiceRequest(id, { status })
      setLocalRequests(localRequests.map((r) => (r.id === id ? { ...r, status } : r)))
    } catch (error) {
      console.error("Failed to update service request:", error)
    }
  }

  if (localRequests.length === 0) {
    return <p className="text-muted-foreground text-center py-4">No pending service requests</p>
  }

  return (
    <div className="space-y-3">
      {localRequests.map((request) => (
        <div key={request.id} className="flex items-start justify-between p-4 rounded-lg border bg-card">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className={cn("capitalize", priorityColors[request.priority])}>
                {request.priority}
              </Badge>
              <Badge variant="outline" className={cn("capitalize", statusColors[request.status])}>
                {request.status.replace("-", " ")}
              </Badge>
              <Badge variant="secondary" className="capitalize">
                {request.type.replace("-", " ")}
              </Badge>
            </div>
            <p className="font-semibold mb-1">
              Room {request.roomNumber} - {request.guestName}
            </p>
            <p className="text-sm text-muted-foreground mb-2">{request.description}</p>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {getRelativeTime(request.createdAt)}
            </p>
          </div>
          <div className="flex gap-2 ml-4">
            {request.status === "pending" && (
              <Button size="sm" onClick={() => handleUpdateStatus(request.id, "in-progress")}>
                Start
              </Button>
            )}
            {request.status === "in-progress" && (
              <Button size="sm" onClick={() => handleUpdateStatus(request.id, "completed")}>
                <CheckCircle className="mr-2 h-4 w-4" />
                Complete
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
