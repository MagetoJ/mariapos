"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/store/auth-store"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Hotel, Loader2 } from "lucide-react"

export default function LoginPage() {
  const router = useRouter()
  const { login, isLoading } = useAuthStore()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [roomNumber, setRoomNumber] = useState("")
  const [isGuestLogin, setIsGuestLogin] = useState(false)
  const [error, setError] = useState("")

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (isGuestLogin && !roomNumber.trim()) {
      setError("Room number is required for guest login")
      return
    }

    const success = await login(email, password, roomNumber)
    if (success) {
      router.push("/dashboard")
    } else {
      setError("Invalid credentials or room number")
    }
  }

  const quickLogin = (role: string) => {
    const credentials: Record<string, { email: string; password: string }> = {
      admin: { email: "admin@mariahavens.com", password: "admin123" },
      manager: { email: "manager@mariahavens.com", password: "manager123" },
      receptionist: { email: "reception@mariahavens.com", password: "reception123" },
      waiter: { email: "waiter1@mariahavens.com", password: "waiter123" },
      kitchen: { email: "kitchen@mariahavens.com", password: "kitchen123" },
      cashier: { email: "cashier@mariahavens.com", password: "cashier123" },
      guest: { email: "guest@mariahavens.com", password: "guest123" },
    }

    const cred = credentials[role]
    setEmail(cred.email)
    setPassword(cred.password)
    if (role === "guest") {
      setIsGuestLogin(true)
      setRoomNumber("101")
    } else {
      setIsGuestLogin(false)
      setRoomNumber("")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-accent/10 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-lg">
              <Hotel className="h-8 w-8" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">Maria Havens POS</CardTitle>
          <CardDescription>Hotel & Restaurant Management System</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="user@mariahavens.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setIsGuestLogin(e.target.value.includes("guest"))
                }}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>

            {isGuestLogin && (
              <div className="space-y-2">
                <Label htmlFor="roomNumber">Room Number *</Label>
                <Input
                  id="roomNumber"
                  type="text"
                  placeholder="Enter your room number"
                  value={roomNumber}
                  onChange={(e) => setRoomNumber(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          <div className="mt-6">
            <p className="text-sm text-muted-foreground text-center mb-3">Quick Login (Demo)</p>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" size="sm" onClick={() => quickLogin("admin")} disabled={isLoading}>
                Admin
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin("manager")} disabled={isLoading}>
                Manager
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin("receptionist")} disabled={isLoading}>
                Receptionist
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin("waiter")} disabled={isLoading}>
                Waiter
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin("kitchen")} disabled={isLoading}>
                Kitchen
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin("cashier")} disabled={isLoading}>
                Cashier
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => quickLogin("guest")}
                disabled={isLoading}
                className="col-span-2"
              >
                Guest Account (Room 101)
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
