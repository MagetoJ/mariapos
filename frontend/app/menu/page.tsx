"use client"

import { useEffect, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { menuService } from "@/lib/api/data-service"
import type { MenuItem } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search } from "lucide-react"
import { MenuItemCard } from "@/components/menu/menu-item-card"
import { MenuItemDialog } from "@/components/menu/menu-item-dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
// Menu categories
const menuCategories = ["All", "Appetizers", "Main Course", "Beverages", "Desserts"]

export default function MenuPage() {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null)

  useEffect(() => {
    fetchMenuItems()
  }, [])

  const fetchMenuItems = async () => {
    try {
      const items = await menuService.getMenuItems()
      setMenuItems(items)
    } catch (error) {
      console.error("Failed to fetch menu items:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateItem = async (item: FormData) => {
    try {
      const newItem = await menuService.createMenuItem(item)
      setMenuItems([...menuItems, newItem])
      setDialogOpen(false)
    } catch (error) {
      console.error("Failed to create menu item:", error)
      throw error;
    }
  }

  const handleUpdateItem = async (id: string, updates: FormData) => {
    try {
      const updatedItem = await menuService.updateMenuItem(id, updates)
      setMenuItems(menuItems.map((item) => (item.id === id ? updatedItem : item)))
      setDialogOpen(false)
      setSelectedItem(null)
    } catch (error) {
      console.error("Failed to update menu item:", error)
      throw error;
    }
  }

  const handleDeleteItem = async (id: string) => {
    try {
      await menuService.deleteMenuItem(id)
      setMenuItems(menuItems.filter((item) => item.id !== id))
    } catch (error) {
      console.error("Failed to delete menu item:", error)
    }
  }

  const handleEditItem = (item: MenuItem) => {
    setSelectedItem(item)
    setDialogOpen(true)
  }

  const handleNewItem = () => {
    setSelectedItem(null)
    setDialogOpen(true)
  }

  // CORRECTED: Create FormData object and append 'is_available'
  const handleToggleAvailability = async (id: string, isAvailable: boolean) => {
    const formData = new FormData();
    // Use 'is_available' to match Django backend's model field name
    formData.append("is_available", String(isAvailable));
    try {
      await handleUpdateItem(id, formData);
      await fetchMenuItems(); // Refresh the list to show the updated status
    } catch (error) {
      console.error("Failed to toggle item availability:", error);
    }
  };

  const filteredItems = menuItems.filter(
    (item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading menu...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
        <h2 className="text-3xl font-bold tracking-tight text-balance">Menu Management</h2>
        <p className="text-muted-foreground">Manage menu items and categories</p>
        </div>
        <Button onClick={handleNewItem}>
        <Plus className="mr-2 h-4 w-4" />
        Add Item
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search menu items..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
        </div>
      </div>

      <Tabs defaultValue="All" className="space-y-4">
        <TabsList>
        {menuCategories.map((category) => {
          const count =
          category === "All"
            ? filteredItems.length
            : filteredItems.filter((item) => item.category === category).length
          return (
          <TabsTrigger key={category} value={category}>
            {category} ({count})
          </TabsTrigger>
          )
        })}
        </TabsList>

        {menuCategories.map((category) => {
        const items =
          category === "All" ? filteredItems : filteredItems.filter((item) => item.category === category)

        return (
          <TabsContent key={category} value={category} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {items.map((item) => (
            <MenuItemCard
              key={item.id}
              item={item}
              onEdit={handleEditItem}
              onDelete={handleDeleteItem}
              onToggleAvailability={handleToggleAvailability}
            />
            ))}
          </div>
          {items.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
            <p className="text-lg font-medium mb-2">No items found</p>
            <p className="text-sm">Try adjusting your search or add a new item</p>
            </div>
          )}
          </TabsContent>
        )
        })}
      </Tabs>
      </div>

      <MenuItemDialog
      open={dialogOpen}
      onOpenChange={(open) => {
        setDialogOpen(open)
        if (!open) setSelectedItem(null)
      }}
      item={selectedItem}
      onSave={async (data) => {
        if (selectedItem) {
        // If editing, update the item
        await handleUpdateItem(selectedItem.id, data)
        await fetchMenuItems()
        } else {
        // If creating, create the item
        await handleCreateItem(data)
        await fetchMenuItems()
        }
      }}
      />
    </AppLayout>
  )
}