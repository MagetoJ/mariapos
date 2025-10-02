"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import type { MenuItem } from "@/lib/types"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Alert, AlertDescription } from "@/components/ui/alert" // Added for form error display

// Menu categories (Placeholder list for categories)
const menuCategories = ["Appetizers", "Main Course", "Beverages", "Desserts", "Sides"]

interface FormDataState {
  name: string
  description: string
  category: string
  price: string
  preparationTime: string
  isAvailable: boolean
  // ADDED fields for image handling
  imageFile: File | null
  imageUrlPreview: string | null
}

interface MenuItemDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  item: MenuItem | null
  onSave: (itemData: FormData) => void // Changed signature to accept FormData
}

export function MenuItemDialog({ open, onOpenChange, item, onSave }: MenuItemDialogProps) {
  const initialState: FormDataState = {
    name: "",
    description: "",
    category: "Main Course",
    price: "",
    preparationTime: "",
    isAvailable: true,
    imageFile: null,
    imageUrlPreview: null,
  }

  const [formData, setFormData] = useState<FormDataState>(initialState)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (item) {
      setFormData({
        name: item.name,
        description: item.description,
        category: item.category,
        price: item.price.toString(),
        preparationTime: item.preparationTime.toString(),
        isAvailable: item.isAvailable,
        // When editing, set the existing image URL for preview
        imageFile: null,
        imageUrlPreview: item.image_url || null,
      })
    } else {
      setFormData(initialState)
    }
    setError(null)
  }, [item, open])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files ? e.target.files[0] : null
    if (file) {
      const preview = URL.createObjectURL(file)
      setFormData({
        ...formData,
        imageFile: file,
        imageUrlPreview: preview,
      })
    } else {
      setFormData({
        ...formData,
        imageFile: null,
        imageUrlPreview: item?.image_url || null,
      })
    }
  }

  const handleClearImage = () => {
    // Clears the selected file/preview but keeps the original server image if editing
    setFormData({
        ...formData,
        imageFile: null,
        imageUrlPreview: item?.image_url || null,
    });
    // Clear file input manually if needed (not always necessary with React state)
    (document.getElementById('image') as HTMLInputElement).value = '';
  }

  const isValid = useMemo(() => {
    return (
      formData.name.trim() !== "" &&
      formData.category.trim() !== "" &&
      !isNaN(parseFloat(formData.price)) &&
      parseFloat(formData.price) >= 0 &&
      !isNaN(parseInt(formData.preparationTime)) &&
      parseInt(formData.preparationTime) > 0
    )
  }, [formData])

  const handleSubmit = useCallback(() => {
    if (!isValid) {
      setError("Please fill all required fields correctly.")
      return
    }

    const itemData = {
      name: formData.name,
      description: formData.description,
      category: formData.category,
      price: parseFloat(formData.price),
      preparation_time: parseInt(formData.preparationTime),
      is_available: formData.isAvailable,
      // Pass category_id instead of category name if backend expects UUID,
      // but assuming backend can handle category name string for now based on other files.
      // If categories were separate model, this would be category: categoryId
    }

    // 1. Create FormData object for file upload
    const data = new FormData()

    // 2. Append standard fields
    // Use underscore_case for backend compatibility
    for (const key in itemData) {
      data.append(key, (itemData as any)[key])
    }

    // 3. Append image file if a new file was selected
    if (formData.imageFile) {
      data.append('image', formData.imageFile)
    } 
    // IMPORTANT: To signal to Django to clear an existing image, you usually send a null or an empty string,
    // but often leaving it off the FormData is sufficient if no new file is provided. 
    // If the image was intentionally cleared (not implemented here), a separate flag would be required.
    // For simplicity, if imageFile is null, the existing image is kept (PATCH behavior).

    onSave(data)
  }, [formData, isValid, onSave, item])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{item ? "Edit Menu Item" : "Add New Menu Item"}</DialogTitle>
          <DialogDescription>
            {item ? "Update the details for this menu item." : "Fill in the details for a new menu item."}
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">Item Name *</Label>
            <Input
              id="name"
              placeholder="Cheeseburger"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="A juicy burger with cheddar cheese..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          
          {/* ADDED: Image Upload Field */}
          <div className="space-y-2">
            <Label htmlFor="image">Item Image</Label>
            <Input
              id="image"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="py-2"
            />
            {(formData.imageUrlPreview || (item && item.image_url)) && (
              <div className="mt-2 flex items-center gap-4">
                <img 
                    src={formData.imageUrlPreview || item?.image_url || ''} 
                    alt="Image Preview" 
                    className="w-24 h-24 object-cover rounded-md border"
                />
                <Button variant="ghost" onClick={handleClearImage} className="text-destructive">
                    Clear Image
                </Button>
              </div>
            )}
          </div>
          {/* END ADDED BLOCK */}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData({ ...formData, category: value })}
              >
                <SelectTrigger id="category">
                  <SelectValue placeholder="Select Category" />
                </SelectTrigger>
                <SelectContent>
                  {menuCategories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="price">Price ($) *</Label>
              <Input
                id="price"
                type="number"
                placeholder="12.99"
                min="0.00"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="prepTime">Preparation Time (minutes) *</Label>
            <Input
              id="prepTime"
              type="number"
              placeholder="15"
              min="1"
              value={formData.preparationTime}
              onChange={(e) => setFormData({ ...formData, preparationTime: e.target.value })}
            />
          </div>

          <div className="flex items-center justify-between p-4 rounded-lg border">
            <div className="space-y-0.5">
              <Label htmlFor="available">Available for Order</Label>
              <p className="text-sm text-muted-foreground">Make this item available to customers</p>
            </div>
            <Switch
              id="available"
              checked={formData.isAvailable}
              onCheckedChange={(checked) => setFormData({ ...formData, isAvailable: checked })}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!isValid}>
            {item ? "Update Item" : "Add Item"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
