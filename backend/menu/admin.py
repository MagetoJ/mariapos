from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, MenuItemIngredient, MenuItemModifier

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview', 'display_order', 'is_active', 'menu_items_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'image_preview', 'created_at', 'updated_at')
    ordering = ('display_order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'display_order', 'is_active')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    def menu_items_count(self, obj):
        return obj.menu_items.count()
    menu_items_count.short_description = 'Items'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    # FIX: Removed non-existent fields (is_popular, spice_level, is_vegetarian, etc.)
    list_display = ('name', 'price_display', 'category', 'is_available', 'image_preview', 'created_at')
    # FIX: Removed non-existent fields from list_filter
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('id', 'image_preview', 'created_at', 'updated_at')
    # FIX: Corrected ordering to only use existing fields
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'category', 'price', 'preparation_time', 'is_available')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        # FIX: Removed Dietary/Spice section fields
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'

    def price_display(self, obj):
        return f"KSh {obj.price:,.2f}"
    price_display.short_description = 'Price'

@admin.register(MenuItemIngredient)
class MenuItemIngredientAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'ingredient_name', 'quantity_required', 'unit', 'is_optional')
    list_filter = ('is_optional', 'unit')
    search_fields = ('menu_item__name', 'ingredient_name')
    readonly_fields = ('id',)

@admin.register(MenuItemModifier)
class MenuItemModifierAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'name', 'price_adjustment', 'modifier_type', 'is_required')
    list_filter = ('modifier_type', 'is_required')
    search_fields = ('menu_item__name', 'name')
    readonly_fields = ('id',)
