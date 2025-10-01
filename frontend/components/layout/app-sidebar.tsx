"use client"

import type React from "react"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuthStore } from "@/lib/store/auth-store"
import type { UserRole } from "@/lib/types"
import {
  LayoutDashboard,
  ShoppingBag,
  Utensils,
  Receipt,
  Package,
  BarChart3,
  Users,
  Settings,
  Hotel,
  ChefHat,
  DollarSign,
  Bell,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  roles: UserRole[]
  badge?: number
}

const navItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    roles: ["admin", "manager", "receptionist", "waiter", "kitchen", "cashier"],
  },
  {
    title: "Guest Dashboard",
    href: "/guest-dashboard",
    icon: Hotel,
    roles: ["guest"],
  },
  {
    title: "Notifications",
    href: "/notifications",
    icon: Bell,
    roles: ["admin", "manager", "receptionist", "waiter", "kitchen", "cashier"],
  },
  {
    title: "Orders",
    href: "/orders",
    icon: ShoppingBag,
    roles: ["admin", "manager", "receptionist", "waiter", "kitchen", "cashier", "guest"],
  },
  {
    title: "Tables",
    href: "/tables",
    icon: Utensils,
    roles: ["admin", "manager", "receptionist", "waiter"],
  },
  {
    title: "Menu",
    href: "/menu",
    icon: ChefHat,
    roles: ["admin", "manager", "kitchen"],
  },
  {
    title: "Receipts",
    href: "/receipts",
    icon: Receipt,
    roles: ["admin", "manager", "receptionist", "waiter", "cashier"],
  },
  {
    title: "Payments",
    href: "/payments",
    icon: DollarSign,
    roles: ["admin", "manager", "cashier"],
  },
  {
    title: "Inventory",
    href: "/inventory",
    icon: Package,
    roles: ["admin", "manager", "kitchen"],
  },
  {
    title: "Reports",
    href: "/reports",
    icon: BarChart3,
    roles: ["admin", "manager"],
  },
  {
    title: "Guests",
    href: "/guests",
    icon: Hotel,
    roles: ["admin", "manager", "receptionist"],
  },
  {
    title: "Staff",
    href: "/staff",
    icon: Users,
    roles: ["admin", "manager"],
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
    roles: ["admin", "manager"],
  },
]

export function AppSidebar() {
  const pathname = usePathname()
  const { user } = useAuthStore()

  const filteredNavItems = navItems.filter((item) => user && item.roles.includes(user.role))

  return (
    <div className="flex flex-col h-full bg-sidebar border-r border-sidebar-border">
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="bg-sidebar-primary text-sidebar-primary-foreground p-2 rounded-lg">
            <Hotel className="h-6 w-6" />
          </div>
          <div>
            <h2 className="font-bold text-lg text-sidebar-foreground">Maria Havens</h2>
            <p className="text-xs text-sidebar-foreground/60">POS System</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {filteredNavItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground",
              )}
            >
              <Icon className="h-5 w-5" />
              {item.title}
              {item.badge && item.badge > 0 && (
                <Badge variant="destructive" className="ml-auto h-5 w-5 flex items-center justify-center p-0 text-xs">
                  {item.badge > 9 ? "9+" : item.badge}
                </Badge>
              )}
            </Link>
          )
        })}
      </nav>

      {user && (
        <div className="p-4 border-t border-sidebar-border">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="h-8 w-8 rounded-full bg-sidebar-primary text-sidebar-primary-foreground flex items-center justify-center text-sm font-semibold">
              {user.name.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-sidebar-foreground truncate">{user.name}</p>
              <p className="text-xs text-sidebar-foreground/60 capitalize">{user.role}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
