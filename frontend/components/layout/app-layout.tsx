"use client"

import React, { useEffect, useState } from "react"
import { AppSidebar } from "./app-sidebar"
import { AppHeader } from "./app-header"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { useIsMobile } from "@/hooks/use-mobile"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Menu } from "lucide-react"
import type { UserRole } from "@/lib/types"

interface AppLayoutProps {
  children: React.ReactNode
  allowedRoles?: UserRole[]
}

export function AppLayout({ children, allowedRoles }: AppLayoutProps) {
  const [mounted, setMounted] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const isMobile = useIsMobile()

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    // 👇 This ensures SSR & CSR match (same empty container)
    return <div className="flex h-screen overflow-hidden" />
  }

  return (
    <ProtectedRoute allowedRoles={allowedRoles}>
      <div className="flex h-screen overflow-hidden">
        {/* Desktop Sidebar */}
        {!isMobile && (
          <aside className="w-64 flex-shrink-0 hidden md:block">
            <AppSidebar />
          </aside>
        )}

        {/* Mobile Sidebar */}
        {isMobile && (
          <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
            <SheetContent side="left" className="w-64 p-0">
              <AppSidebar onItemClick={() => setSidebarOpen(false)} />
            </SheetContent>
          </Sheet>
        )}

        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header with mobile menu trigger */}
          <div className="flex items-center">
            {isMobile && (
              <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="md:hidden ml-2">
                    <Menu className="h-6 w-6" />
                  </Button>
                </SheetTrigger>
              </Sheet>
            )}
            <div className="flex-1">
              <AppHeader />
            </div>
          </div>
          
          <main className="flex-1 overflow-y-auto bg-background p-3 md:p-6">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
