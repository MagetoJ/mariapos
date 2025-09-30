export interface Notification {
  id: string
  type: "order" | "service-request" | "inventory" | "guest" | "system"
  title: string
  message: string
  priority: "low" | "medium" | "high"
  isRead: boolean
  createdAt: string
  relatedId?: string
  actionUrl?: string
}

export const mockNotifications: Notification[] = [
  {
    id: "n1",
    type: "service-request",
    title: "New Service Request",
    message: "Room 101 requested housekeeping service",
    priority: "high",
    isRead: false,
    createdAt: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
    relatedId: "sr1",
    actionUrl: "/notifications",
  },
  {
    id: "n2",
    type: "order",
    title: "New Room Service Order",
    message: "Room 205 placed a food order - ORD-004",
    priority: "high",
    isRead: false,
    createdAt: new Date(Date.now() - 600000).toISOString(), // 10 minutes ago
    relatedId: "o4",
    actionUrl: "/orders",
  },
  {
    id: "n3",
    type: "inventory",
    title: "Low Stock Alert",
    message: "Tomatoes stock is below reorder level (5 kg remaining)",
    priority: "medium",
    isRead: false,
    createdAt: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
    actionUrl: "/inventory",
  },
  {
    id: "n4",
    type: "guest",
    title: "Guest Check-in",
    message: "David Mwangi checked into Room 101",
    priority: "low",
    isRead: true,
    createdAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    relatedId: "g1",
    actionUrl: "/guests",
  },
  {
    id: "n5",
    type: "order",
    title: "Order Ready",
    message: "Order ORD-003 is ready for pickup",
    priority: "medium",
    isRead: true,
    createdAt: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    relatedId: "o3",
    actionUrl: "/orders",
  },
  {
    id: "n6",
    type: "service-request",
    title: "Maintenance Request",
    message: "Room 302 reported AC not working",
    priority: "high",
    isRead: false,
    createdAt: new Date(Date.now() - 900000).toISOString(), // 15 minutes ago
    relatedId: "sr2",
    actionUrl: "/notifications",
  },
  {
    id: "n7",
    type: "inventory",
    title: "Stock Restocked",
    message: "Fresh vegetables restocked - 50 kg added",
    priority: "low",
    isRead: true,
    createdAt: new Date(Date.now() - 10800000).toISOString(), // 3 hours ago
    actionUrl: "/inventory",
  },
  {
    id: "n8",
    type: "system",
    title: "Daily Report Generated",
    message: "Sales report for January 29, 2025 is ready",
    priority: "low",
    isRead: true,
    createdAt: new Date(Date.now() - 14400000).toISOString(), // 4 hours ago
    actionUrl: "/reports",
  },
  {
    id: "n9",
    type: "order",
    title: "Order Cancelled",
    message: "Order ORD-002 was cancelled by customer",
    priority: "medium",
    isRead: true,
    createdAt: new Date(Date.now() - 18000000).toISOString(), // 5 hours ago
    relatedId: "o2",
    actionUrl: "/orders",
  },
  {
    id: "n10",
    type: "guest",
    title: "Guest Check-out",
    message: "Grace Wambui checked out from Room 108",
    priority: "low",
    isRead: true,
    createdAt: new Date(Date.now() - 21600000).toISOString(), // 6 hours ago
    relatedId: "g4",
    actionUrl: "/guests",
  },
]
