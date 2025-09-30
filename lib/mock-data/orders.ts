import type { Order, OrderItem } from "@/lib/types"
import { mockMenuItems } from "./menu"
import { mockUsers } from "./users"

const createOrderItem = (menuItemId: string, quantity: number): OrderItem => {
  const menuItem = mockMenuItems.find((item) => item.id === menuItemId)!
  return {
    id: `oi-${menuItemId}-${Date.now()}`,
    menuItemId,
    menuItem,
    quantity,
    price: menuItem.price,
    status: "pending",
  }
}

export const mockOrders: Order[] = [
  {
    id: "o1",
    orderNumber: "ORD-001",
    type: "dine-in",
    tableId: "t2",
    customerName: "Table 2",
    items: [createOrderItem("m4", 2), createOrderItem("m8", 2), createOrderItem("m11", 1)],
    subtotal: 3150,
    tax: 315,
    discount: 0,
    total: 3465,
    status: "preparing",
    waiterId: "4",
    waiter: mockUsers.find((u) => u.id === "4"),
    createdAt: new Date(Date.now() - 1800000).toISOString(),
    updatedAt: new Date(Date.now() - 900000).toISOString(),
  },
  {
    id: "o2",
    orderNumber: "ORD-002",
    type: "dine-in",
    tableId: "t5",
    customerName: "Table 5",
    items: [createOrderItem("m1", 1), createOrderItem("m9", 1)],
    subtotal: 1000,
    tax: 100,
    discount: 0,
    total: 1100,
    status: "pending",
    waiterId: "4",
    waiter: mockUsers.find((u) => u.id === "4"),
    createdAt: new Date(Date.now() - 600000).toISOString(),
    updatedAt: new Date(Date.now() - 600000).toISOString(),
  },
  {
    id: "o3",
    orderNumber: "ORD-003",
    type: "takeaway",
    customerName: "Jane Smith",
    items: [createOrderItem("m6", 2), createOrderItem("m10", 2)],
    subtotal: 2140,
    tax: 214,
    discount: 100,
    total: 2254,
    status: "ready",
    createdAt: new Date(Date.now() - 1200000).toISOString(),
    updatedAt: new Date(Date.now() - 300000).toISOString(),
  },
]
