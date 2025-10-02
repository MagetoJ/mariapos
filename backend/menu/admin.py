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
    menu_items_count.short_description = 'Menu Items'

class MenuItemIngredientInline(admin.TabularInline):
    model = MenuItemIngredient
    extra = 0
    fields = ('ingredient_name', 'quantity_required', 'unit', 'is_optional')

class MenuItemModifierInline(admin.TabularInline):
    model = MenuItemModifier
    extra = 0
    fields = ('name', 'modifier_type', 'price_adjustment', 'is_required', 'max_quantity')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_display', 'image_preview', 'is_available', 'is_popular', 'dietary_info', 'preparation_time', 'created_at')
    list_filter = ('category', 'is_available', 'is_popular', 'is_vegetarian', 'is_vegan', 'is_gluten_free', 'spice_level', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('id', 'image_preview', 'created_at', 'updated_at')
    ordering = ('category', 'display_order', 'name')
    inlines = [MenuItemIngredientInline, MenuItemModifierInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'category', 'price', 'display_order')
        }),
        ('Availability & Status', {
            'fields': ('is_available', 'is_popular', 'requires_ingredients')
        }),
        ('Dietary Information', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'calories', 'spice_level')
        }),
        ('Preparation', {
            'fields': ('preparation_time',)
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
    
    def price_display(self, obj):
        return f"KSh {obj.price:,.2f}"
    price_display.short_description = 'Price'
    
    def dietary_info(self, obj):
        info = []
        if obj.is_vegetarian:
            info.append("🥗 Vegetarian")
        if obj.is_vegan:
            info.append("🌱 Vegan")
        if obj.is_gluten_free:
            info.append("🌾 Gluten-Free")
        return " | ".join(info) if info else "Regular"
    dietary_info.short_description = 'Dietary Info'

@admin.register(MenuItemIngredient)
class MenuItemIngredientAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'ingredient_name', 'quantity_required', 'unit', 'is_optional')
    list_filter = ('is_optional', 'unit')
    search_fields = ('menu_item__name', 'ingredient_name')
    readonly_fields = ('id',)

@admin.register(MenuItemModifier)
class MenuItemModifierAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'name', 'modifier_type', 'price_adjustment', 'is_required', 'max_quantity')
    list_filter = ('modifier_type', 'is_required')
    search_fields = ('menu_item__name', 'name')
    readonly_fields = ('id',)
