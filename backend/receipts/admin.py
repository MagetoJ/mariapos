from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Receipt, ReceiptItem, ReceiptTemplate, ReceiptPrintQueue

class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    extra = 0
    readonly_fields = ('item_name', 'quantity', 'unit_price', 'line_total', 'tax_amount')

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'customer_name', 'receipt_type', 'status', 'total_amount_display', 'payment_method', 'is_emailed', 'is_printed', 'created_at')
    list_filter = ('receipt_type', 'status', 'payment_method', 'is_emailed', 'is_printed', 'created_at')
    search_fields = ('receipt_number', 'customer_name', 'customer_email', 'order__order_number')
    readonly_fields = ('id', 'receipt_number', 'total_amount_display', 'created_at', 'updated_at', 'email_sent_at', 'voided_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [ReceiptItemInline]
    
    fieldsets = (
        ('Receipt Information', {
            'fields': ('id', 'receipt_number', 'order', 'payment', 'receipt_type', 'status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_room')
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_address', 'business_phone', 'business_email', 'tax_id'),
            'classes': ('collapse',)
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'service_charge', 'discount_amount', 'total_amount_display', 'amount_paid', 'change_amount')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference')
        }),
        ('Receipt Generation', {
            'fields': ('generated_by', 'receipt_data'),
            'classes': ('collapse',)
        }),
        ('Delivery Status', {
            'fields': ('is_emailed', 'email_sent_at', 'is_printed', 'print_count')
        }),
        ('Voiding Information', {
            'fields': ('void_reason', 'voided_by', 'voided_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount_display(self, obj):
        return f"KSh {obj.total_amount:,.2f}"
    total_amount_display.short_description = 'Total Amount'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'payment', 'generated_by', 'voided_by')
    
    actions = ['send_email_receipts', 'mark_as_printed']
    
    def send_email_receipts(self, request, queryset):
        sent_count = 0
        for receipt in queryset:
            if receipt.customer_email and receipt.send_email():
                sent_count += 1
        self.message_user(request, f"Successfully sent {sent_count} receipt emails.")
    send_email_receipts.short_description = "Send email receipts"
    
    def mark_as_printed(self, request, queryset):
        queryset.update(is_printed=True)
        self.message_user(request, f"Marked {queryset.count()} receipts as printed.")
    mark_as_printed.short_description = "Mark as printed"

@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ('receipt', 'item_name', 'quantity', 'unit_price_display', 'line_total_display', 'tax_amount_display', 'category')
    list_filter = ('is_taxable', 'category', 'created_at')
    search_fields = ('receipt__receipt_number', 'item_name', 'category')
    readonly_fields = ('id', 'created_at')
    
    def unit_price_display(self, obj):
        return f"KSh {obj.unit_price:,.2f}"
    unit_price_display.short_description = 'Unit Price'
    
    def line_total_display(self, obj):
        return f"KSh {obj.line_total:,.2f}"
    line_total_display.short_description = 'Line Total'
    
    def tax_amount_display(self, obj):
        return f"KSh {obj.tax_amount:,.2f}"
    tax_amount_display.short_description = 'Tax Amount'

@admin.register(ReceiptTemplate)
class ReceiptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'is_default', 'show_logo', 'paper_width', 'created_at')
    list_filter = ('template_type', 'is_active', 'is_default', 'show_logo', 'created_at')
    search_fields = ('name', 'thank_you_message')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('id', 'name', 'template_type', 'is_active', 'is_default')
        }),
        ('Template Content', {
            'fields': ('header_template', 'body_template', 'footer_template')
        }),
        ('Styling Options', {
            'fields': ('font_size', 'paper_width')
        }),
        ('Business Info Display', {
            'fields': ('show_logo', 'logo_url', 'show_address', 'show_tax_info')
        }),
        ('Receipt Elements', {
            'fields': ('show_order_details', 'show_payment_details', 'show_qr_code', 'qr_code_data')
        }),
        ('Footer Messages', {
            'fields': ('thank_you_message', 'return_policy', 'promotional_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ReceiptPrintQueue)
class ReceiptPrintQueueAdmin(admin.ModelAdmin):
    list_display = ('receipt', 'printer_name', 'printer_type', 'status', 'priority', 'copies', 'print_attempts', 'queued_at', 'printed_at')
    list_filter = ('status', 'printer_type', 'priority', 'queued_at')
    search_fields = ('receipt__receipt_number', 'printer_name', 'queued_by__name')
    readonly_fields = ('id', 'queued_at', 'printed_at')
    ordering = ('priority', 'queued_at')
    
    fieldsets = (
        ('Print Job Information', {
            'fields': ('id', 'receipt', 'printer_name', 'printer_type', 'copies')
        }),
        ('Queue Management', {
            'fields': ('priority', 'status', 'queued_by')
        }),
        ('Processing Status', {
            'fields': ('print_attempts', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('queued_at', 'printed_at')
        }),
    )
    
    actions = ['retry_failed_prints', 'cancel_pending_prints']
    
    def retry_failed_prints(self, request, queryset):
        failed_prints = queryset.filter(status='failed')
        failed_prints.update(status='pending', print_attempts=0, error_message='')
        self.message_user(request, f"Retried {failed_prints.count()} failed print jobs.")
    retry_failed_prints.short_description = "Retry failed prints"
    
    def cancel_pending_prints(self, request, queryset):
        pending_prints = queryset.filter(status='pending')
        pending_prints.update(status='cancelled')
        self.message_user(request, f"Cancelled {pending_prints.count()} pending print jobs.")
    cancel_pending_prints.short_description = "Cancel pending prints"
