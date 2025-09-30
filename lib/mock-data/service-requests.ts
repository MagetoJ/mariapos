import type { ServiceRequest } from "@/lib/types"

export const mockServiceRequests: ServiceRequest[] = [
  {
    id: "sr1",
    guestId: "g1",
    guestName: "John Doe",
    roomNumber: "101",
    type: "housekeeping",
    description: "Need extra towels and toiletries",
    priority: "medium",
    status: "completed",
    createdAt: "2024-03-15T10:30:00Z",
    completedAt: "2024-03-15T11:00:00Z",
    assignedTo: "Mary Receptionist",
  },
  {
    id: "sr2",
    guestId: "g2",
    guestName: "Jane Smith",
    roomNumber: "205",
    type: "maintenance",
    description: "Air conditioning not working properly",
    priority: "high",
    status: "in-progress",
    createdAt: "2024-03-15T14:20:00Z",
    assignedTo: "Maintenance Team",
  },
]
