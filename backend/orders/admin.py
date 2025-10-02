from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Order, OrderItem, OrderItemModifier, OrderStatusHistory

class OrderItemModifierInline(admin.TabularInline):
    model = OrderItemModifier
    extra = 0
    readonly_fields = ('modifier_name', 'modifier_type', 'price_adjustment', 'quantity')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item_name', 'menu_item_price', 'unit_price', 'line_total')
    fields = ('menu_item', 'menu_item_name', 'quantity', 'unit_price', 'line_total', 'status', 'special_instructions')

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'changed_by', 'timestamp', 'notes')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'waiter', 'type', 'status', 'payment_status', 'total_amount_display', 'location', 'created_at')
    list_filter = ('status', 'payment_status', 'type', 'priority', 'created_at', 'waiter')
    search_fields = ('order_number', 'customer__name', 'customer__email', 'table_number', 'room_number')
    readonly_fields = ('id', 'order_number', 'subtotal', 'tax_amount', 'service_charge', 'total_amount', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'order_number', 'type', 'status', 'payment_status', 'priority')
        }),
        ('Customer & Staff', {
            'fields': ('customer', 'waiter')
        }),
        ('Location', {
            'fields': ('table_number', 'room_number')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'service_charge', 'discount_amount', 'total_amount')
        }),
        ('Instructions & Notes', {
            'fields': ('special_instructions', 'kitchen_notes')
        }),
        ('Timing', {
            'fields': ('estimated_preparation_time', 'prepared_at', 'served_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount_display(self, obj):
        return f"KSh {obj.total_amount:,.2f}"
    total_amount_display.short_description = 'Total Amount'
    
    def location(self, obj):
        if obj.room_number:
            return f"Room {obj.room_number}"
        elif obj.table_number:
            return f"Table {obj.table_number}"
        return "Takeaway"
    location.short_description = 'Location'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'waiter')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item_name', 'quantity', 'unit_price_display', 'line_total_display', 'status')
    list_filter = ('status', 'menu_item__category', 'created_at')
    search_fields = ('order__order_number', 'menu_item_name', 'menu_item__name')
    readonly_fields = ('id', 'menu_item_name', 'menu_item_price', 'unit_price', 'line_total', 'created_at', 'updated_at')
    inlines = [OrderItemModifierInline]
    
    fieldsets = (
        ('Order Details', {
            'fields': ('id', 'order', 'menu_item', 'status')
        }),
        ('Item Information', {
            'fields': ('menu_item_name', 'menu_item_price', 'quantity', 'unit_price', 'line_total')
        }),
        ('Special Instructions', {
            'fields': ('special_instructions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def unit_price_display(self, obj):
        return f"KSh {obj.unit_price:,.2f}"
    unit_price_display.short_description = 'Unit Price'
    
    def line_total_display(self, obj):
        return f"KSh {obj.line_total:,.2f}"
    line_total_display.short_description = 'Line Total'

@admin.register(OrderItemModifier)
class OrderItemModifierAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'modifier_name', 'modifier_type', 'price_adjustment_display', 'quantity')
    list_filter = ('modifier_type',)
    search_fields = ('order_item__order__order_number', 'modifier_name')
    readonly_fields = ('id',)
    
    def price_adjustment_display(self, obj):
        return f"KSh {obj.price_adjustment:,.2f}"
    price_adjustment_display.short_description = 'Price Adjustment'

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_by', 'timestamp', 'notes_preview')
    list_filter = ('status', 'timestamp', 'changed_by')
    search_fields = ('order__order_number', 'notes')
    readonly_fields = ('id', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + "..." if len(obj.notes) > 50 else obj.notes
        return "-"
    notes_preview.short_description = 'Notes'
