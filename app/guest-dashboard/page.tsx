"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { AppLayout } from "@/components/layout/app-layout"
import { useAuthStore } from "@/lib/store/auth-store"
import { TermsOfServiceDialog } from "@/components/guest/terms-of-service-dialog"
import { ServiceRequestDialog } from "@/components/guest/service-request-dialog"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { orderService } from "@/lib/api/data-service"
import type { Order, ServiceRequest } from "@/lib/types"
import { formatCurrency, formatDate } from "@/lib/utils/format"
import { ShoppingBag, Utensils, Clock, CheckCircle, XCircle, Loader2 } from "lucide-react"
import { TERMS_VERSION } from "@/lib/mock-data/terms-of-service"

export default function GuestDashboardPage() {
  const router = useRouter()
  const { user, setUser } = useAuthStore()
  const [showTerms, setShowTerms] = useState(false)
  const [orders, setOrders] = useState<Order[]>([])
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is a guest
    if (user?.role !== "guest") {
      router.push("/dashboard")
      return
    }

    // Check if terms have been accepted
    if (!user.acceptedTermsAt || user.termsVersion !== TERMS_VERSION) {
      setShowTerms(true)
      setLoading(false)
      return
    }

    // Load guest data
    loadGuestData()
  }, [user, router])

  const loadGuestData = async () => {
    try {
      const [ordersData] = await Promise.all([
        orderService.getOrders(),
        // Load service requests when API is ready
      ])

      // Filter orders for this guest (by room number or guest ID)
      const guestOrders = ordersData.filter((order) => order.roomNumber === user?.roomNumber)
      setOrders(guestOrders)
    } catch (error) {
      console.error("Failed to load guest data:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleAcceptTerms = () => {
    if (user) {
      const updatedUser = {
        ...user,
        acceptedTermsAt: new Date().toISOString(),
        termsVersion: TERMS_VERSION,
      }
      setUser(updatedUser)
      setShowTerms(false)
      loadGuestData()
    }
  }

  const handleDeclineTerms = () => {
    router.push("/")
  }

  if (showTerms) {
    return <TermsOfServiceDialog open={showTerms} onAccept={handleAcceptTerms} onDecline={handleDeclineTerms} />
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </AppLayout>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "cancelled":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "preparing":
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-600" />
      default:
        return <Clock className="h-4 w-4 text-blue-600" />
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-balance">Welcome, {user?.name}</h2>
            <p className="text-muted-foreground">Room {user?.roomNumber}</p>
          </div>
          <ServiceRequestDialog
            guestId={user?.id || ""}
            guestName={user?.name || ""}
            roomNumber={user?.roomNumber || ""}
            onRequestCreated={loadGuestData}
          />
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card
            className="cursor-pointer hover:border-primary transition-colors"
            onClick={() => router.push("/orders")}
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Utensils className="h-5 w-5" />
                Order Food
              </CardTitle>
              <CardDescription>Browse our menu and place an order</CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full">View Menu & Order</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingBag className="h-5 w-5" />
                Service Requests
              </CardTitle>
              <CardDescription>Request housekeeping, maintenance, or other services</CardDescription>
            </CardHeader>
            <CardContent>
              <ServiceRequestDialog
                guestId={user?.id || ""}
                guestName={user?.name || ""}
                roomNumber={user?.roomNumber || ""}
                onRequestCreated={loadGuestData}
              />
            </CardContent>
          </Card>
        </div>

        {/* Recent Orders */}
        <Card>
          <CardHeader>
            <CardTitle>Your Orders</CardTitle>
            <CardDescription>Track your recent food and beverage orders</CardDescription>
          </CardHeader>
          <CardContent>
            {orders.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Utensils className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No orders yet</p>
                <p className="text-sm">Place your first order from our menu</p>
              </div>
            ) : (
              <div className="space-y-4">
                {orders.map((order) => (
                  <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium">{order.orderNumber}</span>
                        <Badge variant={order.status === "completed" ? "default" : "secondary"} className="capitalize">
                          {getStatusIcon(order.status)}
                          <span className="ml-1">{order.status}</span>
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {order.items.length} item(s) • {formatDate(order.createdAt)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{formatCurrency(order.total)}</p>
                      <p className="text-xs text-muted-foreground capitalize">{order.type}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Service Requests */}
        <Card>
          <CardHeader>
            <CardTitle>Service Requests</CardTitle>
            <CardDescription>Your recent service requests and their status</CardDescription>
          </CardHeader>
          <CardContent>
            {serviceRequests.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <ShoppingBag className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No service requests</p>
                <p className="text-sm">Request a service when you need assistance</p>
              </div>
            ) : (
              <div className="space-y-4">
                {serviceRequests.map((request) => (
                  <div key={request.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium capitalize">{request.type.replace("-", " ")}</span>
                        <Badge
                          variant={request.status === "completed" ? "default" : "secondary"}
                          className="capitalize"
                        >
                          {getStatusIcon(request.status)}
                          <span className="ml-1">{request.status}</span>
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{request.description}</p>
                      <p className="text-xs text-muted-foreground mt-1">{formatDate(request.createdAt)}</p>
                    </div>
                    <Badge variant="outline" className="capitalize">
                      {request.priority}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
