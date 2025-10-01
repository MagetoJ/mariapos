"use client"

import { useState } from "react"
import { useAuthStore } from "@/lib/store/auth-store"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save, Bell, DollarSign, Printer, Shield } from "lucide-react"

function SettingsPage() {
  const { user } = useAuthStore()
  const [saving, setSaving] = useState(false)

  // General Settings
  const [businessName, setBusinessName] = useState("Maria Havens")
  const [businessEmail, setBusinessEmail] = useState("info@mariahavens.com")
  const [businessPhone, setBusinessPhone] = useState("+254 700 000 000")
  const [currency, setCurrency] = useState("KES")
  const [taxRate, setTaxRate] = useState("16")

  // Notification Settings
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [lowStockAlerts, setLowStockAlerts] = useState(true)
  const [orderNotifications, setOrderNotifications] = useState(true)
  const [dailyReports, setDailyReports] = useState(false)

  // Payment Settings
  const [mpesaEnabled, setMpesaEnabled] = useState(true)
  const [mpesaShortcode, setMpesaShortcode] = useState("")
  const [mpesaPasskey, setMpesaPasskey] = useState("")

  // Receipt Settings
  const [receiptHeader, setReceiptHeader] = useState("Maria Havens Hotel & Restaurant")
  const [receiptFooter, setReceiptFooter] = useState("Thank you for your business!")
  const [showLogo, setShowLogo] = useState(true)

  const handleSave = async (section: string) => {
    setSaving(true)
    // In production, this would save to backend
    await new Promise((resolve) => setTimeout(resolve, 1000))
    alert(`${section} settings saved successfully`)
    setSaving(false)
  }

  return (
    <ProtectedRoute allowedRoles={["admin", "manager"]}>
      <AppLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Settings</h1>
            <p className="text-muted-foreground">Manage your system preferences and configurations</p>
          </div>

          <Tabs defaultValue="general" className="space-y-4">
            <TabsList>
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="notifications">Notifications</TabsTrigger>
              <TabsTrigger value="payments">Payments</TabsTrigger>
              <TabsTrigger value="receipts">Receipts</TabsTrigger>
              {user?.role === "admin" && <TabsTrigger value="security">Security</TabsTrigger>}
            </TabsList>

            <TabsContent value="general" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Business Information</CardTitle>
                  <CardDescription>Update your business details and preferences</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="businessName">Business Name</Label>
                      <Input id="businessName" value={businessName} onChange={(e) => setBusinessName(e.target.value)} />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="businessEmail">Business Email</Label>
                      <Input
                        id="businessEmail"
                        type="email"
                        value={businessEmail}
                        onChange={(e) => setBusinessEmail(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="businessPhone">Business Phone</Label>
                      <Input
                        id="businessPhone"
                        value={businessPhone}
                        onChange={(e) => setBusinessPhone(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="currency">Currency</Label>
                      <Input id="currency" value={currency} onChange={(e) => setCurrency(e.target.value)} />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="taxRate">Tax Rate (%)</Label>
                      <Input id="taxRate" type="number" value={taxRate} onChange={(e) => setTaxRate(e.target.value)} />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <Button onClick={() => handleSave("General")} disabled={saving}>
                      <Save className="mr-2 h-4 w-4" />
                      {saving ? "Saving..." : "Save Changes"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="notifications" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Notification Preferences
                  </CardTitle>
                  <CardDescription>Configure how you receive notifications</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                    </div>
                    <Switch checked={emailNotifications} onCheckedChange={setEmailNotifications} />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Low Stock Alerts</Label>
                      <p className="text-sm text-muted-foreground">Get notified when items are running low</p>
                    </div>
                    <Switch checked={lowStockAlerts} onCheckedChange={setLowStockAlerts} />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Order Notifications</Label>
                      <p className="text-sm text-muted-foreground">Receive alerts for new orders</p>
                    </div>
                    <Switch checked={orderNotifications} onCheckedChange={setOrderNotifications} />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Daily Reports</Label>
                      <p className="text-sm text-muted-foreground">Receive daily sales reports via email</p>
                    </div>
                    <Switch checked={dailyReports} onCheckedChange={setDailyReports} />
                  </div>
                  <div className="flex justify-end">
                    <Button onClick={() => handleSave("Notification")} disabled={saving}>
                      <Save className="mr-2 h-4 w-4" />
                      {saving ? "Saving..." : "Save Changes"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="payments" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    Payment Configuration
                  </CardTitle>
                  <CardDescription>Configure payment methods and integrations</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>M-Pesa Integration</Label>
                      <p className="text-sm text-muted-foreground">Enable M-Pesa payments</p>
                    </div>
                    <Switch checked={mpesaEnabled} onCheckedChange={setMpesaEnabled} />
                  </div>
                  {mpesaEnabled && (
                    <div className="space-y-4 rounded-lg border p-4">
                      <div className="space-y-2">
                        <Label htmlFor="mpesaShortcode">M-Pesa Shortcode</Label>
                        <Input
                          id="mpesaShortcode"
                          value={mpesaShortcode}
                          onChange={(e) => setMpesaShortcode(e.target.value)}
                          placeholder="Enter your M-Pesa shortcode"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="mpesaPasskey">M-Pesa Passkey</Label>
                        <Input
                          id="mpesaPasskey"
                          type="password"
                          value={mpesaPasskey}
                          onChange={(e) => setMpesaPasskey(e.target.value)}
                          placeholder="Enter your M-Pesa passkey"
                        />
                      </div>
                    </div>
                  )}
                  <div className="flex justify-end">
                    <Button onClick={() => handleSave("Payment")} disabled={saving}>
                      <Save className="mr-2 h-4 w-4" />
                      {saving ? "Saving..." : "Save Changes"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="receipts" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Printer className="h-5 w-5" />
                    Receipt Configuration
                  </CardTitle>
                  <CardDescription>Customize your receipt appearance</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="receiptHeader">Receipt Header</Label>
                    <Input
                      id="receiptHeader"
                      value={receiptHeader}
                      onChange={(e) => setReceiptHeader(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="receiptFooter">Receipt Footer</Label>
                    <Input
                      id="receiptFooter"
                      value={receiptFooter}
                      onChange={(e) => setReceiptFooter(e.target.value)}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Show Logo on Receipt</Label>
                      <p className="text-sm text-muted-foreground">Display business logo on printed receipts</p>
                    </div>
                    <Switch checked={showLogo} onCheckedChange={setShowLogo} />
                  </div>
                  <div className="flex justify-end">
                    <Button onClick={() => handleSave("Receipt")} disabled={saving}>
                      <Save className="mr-2 h-4 w-4" />
                      {saving ? "Saving..." : "Save Changes"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {user?.role === "admin" && (
              <TabsContent value="security" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5" />
                      Security Settings
                    </CardTitle>
                    <CardDescription>Manage security and access control</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 dark:border-orange-900 dark:bg-orange-950">
                      <p className="text-sm text-orange-900 dark:text-orange-100">
                        Security settings should be configured carefully. Changes here affect all users.
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Session Timeout (minutes)</Label>
                      <Input type="number" defaultValue="30" />
                    </div>
                    <div className="space-y-2">
                      <Label>Minimum Password Length</Label>
                      <Input type="number" defaultValue="6" />
                    </div>
                    <div className="flex justify-end">
                      <Button onClick={() => handleSave("Security")} disabled={saving}>
                        <Save className="mr-2 h-4 w-4" />
                        {saving ? "Saving..." : "Save Changes"}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            )}
          </Tabs>
        </div>
      </AppLayout>
    </ProtectedRoute>
  )
}

export default SettingsPage
