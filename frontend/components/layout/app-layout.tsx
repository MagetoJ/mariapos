"use client"

import type React from "react"

import { AppSidebar } from "./app-sidebar"
import { AppHeader } from "./app-header"
import { ProtectedRoute } from "@/components/auth/protected-route"
import type { UserRole } from "@/lib/types"

interface AppLayoutProps {
  children: React.ReactNode
  allowedRoles?: UserRole[]
}

export function AppLayout({ children, allowedRoles }: AppLayoutProps) {
  return (
    <ProtectedRoute allowedRoles={allowedRoles}>
      <div className="flex h-screen overflow-hidden">
        <aside className="w-64 flex-shrink-0">
          <AppSidebar />
        </aside>
        <div className="flex-1 flex flex-col overflow-hidden">
          <AppHeader />
          <main className="flex-1 overflow-y-auto bg-background p-6">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
