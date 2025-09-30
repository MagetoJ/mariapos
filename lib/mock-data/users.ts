import type { User } from "@/lib/types"

export const mockUsers: User[] = [
  {
    id: "1",
    name: "John Admin",
    email: "admin@mariahavens.com",
    role: "admin",
    phone: "+254712345678",
    isActive: true,
    createdAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "2",
    name: "Sarah Manager",
    email: "manager@mariahavens.com",
    role: "manager",
    phone: "+254723456789",
    isActive: true,
    createdAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "3",
    name: "Mary Receptionist",
    email: "reception@mariahavens.com",
    role: "receptionist",
    phone: "+254734567890",
    isActive: true,
    createdAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "4",
    name: "James Waiter",
    email: "waiter1@mariahavens.com",
    role: "waiter",
    phone: "+254745678901",
    isActive: true,
    createdAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "5",
    name: "Peter Chef",
    email: "kitchen@mariahavens.com",
    role: "kitchen",
    phone: "+254756789012",
    isActive: true,
    createdAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "6",
    name: "Lucy Cashier",
    email: "cashier@mariahavens.com",
    role: "cashier",
    phone: "+254767890123",
    isActive: true,
    createdAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "7",
    name: "Guest User",
    email: "guest@mariahavens.com",
    role: "guest",
    phone: "+254778901234",
    isActive: true,
    createdAt: "2024-03-15T00:00:00Z",
    roomNumber: "101",
    acceptedTermsAt: undefined, // Will be set when guest accepts terms
    termsVersion: undefined,
  },
]

// Default login credentials for testing
export const mockCredentials = {
  admin: { email: "admin@mariahavens.com", password: "admin123" },
  manager: { email: "manager@mariahavens.com", password: "manager123" },
  receptionist: { email: "reception@mariahavens.com", password: "reception123" },
  waiter: { email: "waiter1@mariahavens.com", password: "waiter123" },
  kitchen: { email: "kitchen@mariahavens.com", password: "kitchen123" },
  cashier: { email: "cashier@mariahavens.com", password: "cashier123" },
  guest: { email: "guest@mariahavens.com", password: "guest123" },
}
