"use client"

import { useState, useEffect } from "react"
import { useAuthStore } from "@/lib/store/auth-store"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search, AlertTriangle } from "lucide-react"
import { InventoryList } from "@/components/inventory/inventory-list"
import { InventoryItemDialog } from "@/components/inventory/inventory-item-dialog"
import { WasteTrackingDialog } from "@/components/inventory/waste-tracking-dialog"
import { getInventory } from "@/lib/api/data-service"
import type { InventoryItem } from "@/lib/types"

function InventoryPage() {
  const { user } = useAuthStore()
  const [inventory, setInventory] = useState<InventoryItem[]>([])
  const [filteredInventory, setFilteredInventory] = useState<InventoryItem[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [showWasteDialog, setShowWasteDialog] = useState(false)
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null)
  const [loading, setLoading] = useState(true)

  const canManage = user?.role === "admin" || user?.role === "manager"

  useEffect(() => {
    loadInventory()
  }, [])

  useEffect(() => {
    filterInventory()
  }, [inventory, searchQuery, selectedCategory])

  const loadInventory = async () => {
    setLoading(true)
    const data = await getInventory()
    setInventory(data)
    setLoading(false)
  }

  const filterInventory = () => {
    let filtered = inventory

    if (searchQuery) {
      filtered = filtered.filter((item) => item.name.toLowerCase().includes(searchQuery.toLowerCase()))
    }

    if (selectedCategory !== "all") {
      filtered = filtered.filter((item) => item.category === selectedCategory)
    }

    setFilteredInventory(filtered)
  }

  const categories = ["all", ...Array.from(new Set(inventory.map((item) => item.category)))]
  const lowStockCount = inventory.filter((item) => item.quantity <= item.reorderLevel).length

  return (
    <ProtectedRoute allowedRoles={["admin", "manager", "kitchen"]}>
      <AppLayout>
        <div className="space-y-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Inventory Management</h1>
              <p className="text-muted-foreground">Track stock levels and manage inventory</p>
            </div>
            {canManage && (
              <div className="flex gap-2">
                <Button onClick={() => setShowWasteDialog(true)} variant="outline">
                  <AlertTriangle className="mr-2 h-4 w-4" />
                  Track Waste
                </Button>
                <Button onClick={() => setShowAddDialog(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Item
                </Button>
              </div>
            )}
          </div>

          {lowStockCount > 0 && (
            <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 dark:border-orange-900 dark:bg-orange-950">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                <p className="font-medium text-orange-900 dark:text-orange-100">
                  {lowStockCount} item{lowStockCount > 1 ? "s" : ""} running low on stock
                </p>
              </div>
            </div>
          )}

          <div className="flex flex-col gap-4 md:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search inventory..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="flex gap-2 overflow-x-auto">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  onClick={() => setSelectedCategory(category)}
                  className="whitespace-nowrap"
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </Button>
              ))}
            </div>
          </div>

          <InventoryList
            inventory={filteredInventory}
            loading={loading}
            onEdit={canManage ? (item) => setEditingItem(item) : undefined}
            onRefresh={loadInventory}
          />

          {showAddDialog && (
            <InventoryItemDialog open={showAddDialog} onOpenChange={setShowAddDialog} onSuccess={loadInventory} />
          )}

          {editingItem && (
            <InventoryItemDialog
              open={!!editingItem}
              onOpenChange={(open) => !open && setEditingItem(null)}
              item={editingItem}
              onSuccess={loadInventory}
            />
          )}

          {showWasteDialog && (
            <WasteTrackingDialog
              open={showWasteDialog}
              onOpenChange={setShowWasteDialog}
              inventory={inventory}
              onSuccess={loadInventory}
            />
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  )
}

export default InventoryPage
