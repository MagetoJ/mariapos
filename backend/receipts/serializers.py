from rest_framework import serializers
from django.utils import timezone
from .models import (
    Receipt, ReceiptItem, ReceiptTemplate, ReceiptPrintQueue, ReceiptEmailLog
)
from accounts.serializers import UserListSerializer
from orders.serializers import OrderListSerializer
from payments.serializers import PaymentListSerializer

class ReceiptItemSerializer(serializers.ModelSerializer):
    """Receipt item serializer"""
    
    class Meta:
        model = ReceiptItem
        fields = [
            'id', 'item_name', 'quantity', 'unit_price', 'line_total',
            'is_taxable', 'tax_rate', 'tax_amount', 'category', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ReceiptListSerializer(serializers.ModelSerializer):
    """Simplified receipt serializer for list views"""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_receipt_type_display', read_only=True)
    
    class Meta:
        model = Receipt
        fields = [
            'id', 'receipt_number', 'order', 'order_number', 'receipt_type',
            'status', 'customer_name', 'customer_email', 'total_amount',
            'amount_paid', 'payment_method', 'payment_method_display',
            'generated_by', 'generated_by_name', 'is_emailed', 'is_printed',
            'created_at'
        ]
        read_only_fields = ['id', 'receipt_number', 'created_at']

class ReceiptDetailSerializer(serializers.ModelSerializer):
    """Full receipt serializer with all details"""
    
    order_data = OrderListSerializer(source='order', read_only=True)
    payment_data = PaymentListSerializer(source='payment', read_only=True)
    generated_by_data = UserListSerializer(source='generated_by', read_only=True)
    voided_by_data = UserListSerializer(source='voided_by', read_only=True)
    items = ReceiptItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Receipt
        fields = [
            'id', 'receipt_number', 'order', 'order_data', 'payment',
            'payment_data', 'receipt_type', 'status', 'customer_name',
            'customer_email', 'customer_phone', 'customer_room',
            'business_name', 'business_address', 'business_phone',
            'business_email', 'tax_id', 'subtotal', 'tax_amount',
            'service_charge', 'discount_amount', 'total_amount',
            'amount_paid', 'change_amount', 'payment_method',
            'payment_reference', 'generated_by', 'generated_by_data',
            'receipt_data', 'is_emailed', 'email_sent_at', 'is_printed',
            'print_count', 'void_reason', 'voided_by', 'voided_by_data',
            'voided_at', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'receipt_number', 'email_sent_at', 'voided_at',
            'created_at', 'updated_at'
        ]

class ReceiptCreateSerializer(serializers.ModelSerializer):
    """Receipt serializer for creation"""
    
    class Meta:
        model = Receipt
        fields = [
            'order', 'payment', 'receipt_type', 'customer_name',
            'customer_email', 'customer_phone', 'customer_room',
            'business_name', 'business_address', 'business_phone',
            'business_email', 'tax_id', 'subtotal', 'tax_amount',
            'service_charge', 'discount_amount', 'total_amount',
            'amount_paid', 'change_amount', 'payment_method',
            'payment_reference', 'receipt_data'
        ]
    
    def validate(self, data):
        """Cross-field validation"""
        order = data.get('order')
        payment = data.get('payment')
        
        if payment and payment.order != order:
            raise serializers.ValidationError(
                "Payment must belong to the specified order"
            )
        
        total_amount = data.get('total_amount', 0)
        amount_paid = data.get('amount_paid', 0)
        
        if amount_paid > total_amount:
            change_amount = amount_paid - total_amount
            data['change_amount'] = change_amount
        
        return data

class ReceiptFromOrderSerializer(serializers.Serializer):
    """Serializer for creating receipt from order"""
    
    order_id = serializers.UUIDField()
    payment_id = serializers.UUIDField(required=False)
    receipt_type = serializers.ChoiceField(
        choices=Receipt.RECEIPT_TYPES, 
        default='sale'
    )
    email_to_customer = serializers.BooleanField(default=False)
    print_receipt = serializers.BooleanField(default=False)
    
    def validate_order_id(self, value):
        """Validate order exists"""
        from orders.models import Order
        try:
            Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        return value
    
    def validate_payment_id(self, value):
        """Validate payment exists if provided"""
        if value:
            from payments.models import Payment
            try:
                Payment.objects.get(id=value)
            except Payment.DoesNotExist:
                raise serializers.ValidationError("Payment not found")
        return value

class ReceiptVoidSerializer(serializers.Serializer):
    """Serializer for voiding receipts"""
    
    reason = serializers.CharField(max_length=500)
    
    def validate_reason(self, value):
        """Ensure reason is provided"""
        if not value or not value.strip():
            raise serializers.ValidationError("Void reason is required")
        return value
    
    def validate(self, data):
        """Validate receipt can be voided"""
        receipt = self.context.get('receipt')
        if not receipt:
            return data
        
        if receipt.status == 'voided':
            raise serializers.ValidationError("Receipt is already voided")
        
        # Add business logic for void restrictions
        hours_since_creation = (timezone.now() - receipt.created_at).total_seconds() / 3600
        if hours_since_creation > 24:  # Example: can't void after 24 hours
            raise serializers.ValidationError(
                "Cannot void receipts older than 24 hours"
            )
        
        return data

class ReceiptTemplateSerializer(serializers.ModelSerializer):
    """Receipt template serializer"""
    
    class Meta:
        model = ReceiptTemplate
        fields = [
            'id', 'name', 'template_type', 'header_template', 'body_template',
            'footer_template', 'font_size', 'paper_width', 'show_logo',
            'logo_url', 'show_address', 'show_tax_info', 'show_order_details',
            'show_payment_details', 'show_qr_code', 'qr_code_data',
            'thank_you_message', 'return_policy', 'promotional_message',
            'is_active', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate template configuration"""
        if data.get('show_qr_code') and not data.get('qr_code_data'):
            raise serializers.ValidationError(
                "QR code data is required when QR code display is enabled"
            )
        
        # Ensure only one default template per type
        if data.get('is_default'):
            template_type = data.get('template_type')
            existing_default = ReceiptTemplate.objects.filter(
                template_type=template_type, 
                is_default=True
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing_default = existing_default.exclude(id=self.instance.id)
            
            if existing_default.exists():
                raise serializers.ValidationError(
                    f"A default template for {template_type} already exists"
                )
        
        return data

class ReceiptPrintQueueSerializer(serializers.ModelSerializer):
    """Receipt print queue serializer"""
    
    receipt_number = serializers.CharField(source='receipt.receipt_number', read_only=True)
    customer_name = serializers.CharField(source='receipt.customer_name', read_only=True)
    queued_by_name = serializers.CharField(source='queued_by.name', read_only=True)
    
    class Meta:
        model = ReceiptPrintQueue
        fields = [
            'id', 'receipt', 'receipt_number', 'customer_name',
            'printer_name', 'printer_type', 'copies', 'priority',
            'status', 'queued_by', 'queued_by_name', 'error_message',
            'print_attempts', 'queued_at', 'printed_at'
        ]
        read_only_fields = ['id', 'print_attempts', 'queued_at', 'printed_at']

class ReceiptPrintRequestSerializer(serializers.Serializer):
    """Serializer for print requests"""
    
    printer_name = serializers.CharField(max_length=100)
    printer_type = serializers.ChoiceField(
        choices=ReceiptPrintQueue.PRINTER_TYPES,
        default='thermal'
    )
    copies = serializers.IntegerField(min_value=1, max_value=10, default=1)
    priority = serializers.IntegerField(min_value=1, max_value=10, default=5)
    
    def validate_printer_name(self, value):
        """Validate printer exists (placeholder)"""
        # In a real implementation, you'd validate against configured printers
        available_printers = ['Kitchen-Printer', 'POS-Printer', 'Receipt-Printer']
        if value not in available_printers:
            raise serializers.ValidationError(
                f"Printer '{value}' not found. Available: {', '.join(available_printers)}"
            )
        return value

class ReceiptEmailLogSerializer(serializers.ModelSerializer):
    """Receipt email log serializer"""
    
    receipt_number = serializers.CharField(source='receipt.receipt_number', read_only=True)
    sent_by_name = serializers.CharField(source='sent_by.name', read_only=True)
    
    class Meta:
        model = ReceiptEmailLog
        fields = [
            'id', 'receipt', 'receipt_number', 'email_address',
            'subject', 'status', 'sent_by', 'sent_by_name',
            'sent_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'created_at']

class ReceiptEmailRequestSerializer(serializers.Serializer):
    """Serializer for email requests"""
    
    email_address = serializers.EmailField()
    include_pdf = serializers.BooleanField(default=True)
    custom_message = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True
    )
    
    def validate_email_address(self, value):
        """Basic email validation"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Valid email address is required")
        return value.lower()

class ReceiptStatsSerializer(serializers.Serializer):
    """Receipt statistics serializer"""
    
    total_receipts = serializers.IntegerField()
    receipts_today = serializers.IntegerField()
    emailed_receipts = serializers.IntegerField()
    printed_receipts = serializers.IntegerField()
    voided_receipts = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_receipt_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Type breakdown
    receipt_type_breakdown = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    
    # Daily trends
    daily_trends = serializers.ListField(
        child=serializers.DictField(), required=False
    )

class ReceiptReportSerializer(serializers.Serializer):
    """Receipt report data serializer"""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_receipts = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    voided_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Breakdown by type
    by_type = serializers.ListField(child=serializers.DictField())
    
    # Breakdown by payment method
    by_payment_method = serializers.ListField(child=serializers.DictField())
    
    # Top items
    top_items = serializers.ListField(child=serializers.DictField())
    
    # Daily breakdown
    daily_breakdown = serializers.ListField(child=serializers.DictField())

class ReceiptPreviewSerializer(serializers.Serializer):
    """Receipt preview data serializer"""
    
    receipt_html = serializers.CharField()
    receipt_data = serializers.DictField()
    template_used = serializers.CharField()
    estimated_print_lines = serializers.IntegerField()

class BulkReceiptActionSerializer(serializers.Serializer):
    """Serializer for bulk receipt actions"""
    
    ACTION_CHOICES = [
        ('email', 'Send Email'),
        ('print', 'Print'),
        ('void', 'Void'),
        ('regenerate', 'Regenerate'),
    ]
    
    receipt_ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    
    # Action-specific parameters
    email_address = serializers.EmailField(required=False)
    printer_name = serializers.CharField(max_length=100, required=False)
    void_reason = serializers.CharField(max_length=500, required=False)
    
    def validate(self, data):
        """Validate action-specific requirements"""
        action = data.get('action')
        
        if action == 'email' and not data.get('email_address'):
            raise serializers.ValidationError(
                "Email address is required for email action"
            )
        
        if action == 'print' and not data.get('printer_name'):
            raise serializers.ValidationError(
                "Printer name is required for print action"
            )
        
        if action == 'void' and not data.get('void_reason'):
            raise serializers.ValidationError(
                "Void reason is required for void action"
            )
        
        # Validate receipt IDs exist
        receipt_ids = data.get('receipt_ids', [])
        if not receipt_ids:
            raise serializers.ValidationError("At least one receipt ID is required")
        
        existing_count = Receipt.objects.filter(id__in=receipt_ids).count()
        if existing_count != len(receipt_ids):
            raise serializers.ValidationError("Some receipt IDs are invalid")
        
        return data