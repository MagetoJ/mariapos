from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid

class Receipt(models.Model):
    """Receipt model for completed orders"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent'),
        ('printed', 'Printed'),
        ('voided', 'Voided'),
    ]
    
    RECEIPT_TYPES = [
        ('sale', 'Sale Receipt'),
        ('refund', 'Refund Receipt'),
        ('partial_refund', 'Partial Refund Receipt'),
        ('void', 'Void Receipt'),
        ('credit_note', 'Credit Note'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt_number = models.CharField(max_length=20, unique=True)
    
    # Related records
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='receipts')
    payment = models.ForeignKey('payments.Payment', on_delete=models.CASCADE, related_name='receipts', null=True, blank=True)
    
    # Receipt details
    receipt_type = models.CharField(max_length=20, choices=RECEIPT_TYPES, default='sale')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    
    # Customer information (snapshot)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=17, blank=True)
    customer_room = models.CharField(max_length=10, blank=True)
    
    # Business information (snapshot)
    business_name = models.CharField(max_length=200, default='Maria Havens Hotel')
    business_address = models.TextField(default='Nairobi, Kenya')
    business_phone = models.CharField(max_length=17, default='+254700000000')
    business_email = models.EmailField(default='info@mariahavens.com')
    tax_id = models.CharField(max_length=50, default='PIN: P051234567A')
    
    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment method (snapshot)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Receipt generation
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='generated_receipts',
        limit_choices_to={'role__in': ['cashier', 'waiter', 'admin', 'manager']}
    )
    
    # Receipt content
    receipt_data = models.JSONField(default=dict, help_text="Full receipt data for regeneration")
    
    # Delivery information
    is_emailed = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    is_printed = models.BooleanField(default=False)
    print_count = models.PositiveIntegerField(default=0)
    
    # Voiding information
    void_reason = models.TextField(blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voided_receipts'
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'receipts'
        ordering = ['-created_at']
        verbose_name = 'Receipt'
        verbose_name_plural = 'Receipts'
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_receipt = Receipt.objects.filter(
                receipt_number__startswith=f'RCP-{today}'
            ).order_by('-receipt_number').first()
            
            if last_receipt:
                last_seq = int(last_receipt.receipt_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.receipt_number = f'RCP-{today}-{new_seq:04d}'
        
        super().save(*args, **kwargs)
    
    @classmethod
    def create_from_order(cls, order, payment=None):
        """Create receipt from order and payment"""
        receipt = cls.objects.create(
            order=order,
            payment=payment,
            customer_name=order.customer.name,
            customer_email=order.customer.email,
            customer_phone=order.customer.phone,
            customer_room=order.room_number or '',
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            service_charge=order.service_charge,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            amount_paid=payment.amount if payment else order.total_amount,
            payment_method=payment.get_method_display() if payment else '',
            payment_reference=payment.transaction_reference if payment else '',
            receipt_data=cls._build_receipt_data(order, payment)
        )
        return receipt
    
    @staticmethod
    def _build_receipt_data(order, payment):
        """Build comprehensive receipt data"""
        items = []
        for item in order.items.all():
            item_data = {
                'name': item.menu_item_name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'line_total': float(item.line_total),
                'special_instructions': item.special_instructions,
                'modifiers': [
                    {
                        'name': mod.modifier_name,
                        'price': float(mod.price_adjustment)
                    }
                    for mod in item.modifiers.all()
                ]
            }
            items.append(item_data)
        
        return {
            'order_number': order.order_number,
            'order_type': order.get_type_display(),
            'table_number': order.table_number,
            'room_number': order.room_number,
            'waiter': order.waiter.name if order.waiter else '',
            'items': items,
            'special_instructions': order.special_instructions,
            'payment_status': order.get_payment_status_display(),
        }
    
    def generate_receipt_content(self):
        """Generate formatted receipt content"""
        from django.template.loader import render_to_string
        
        context = {
            'receipt': self,
            'order': self.order,
            'payment': self.payment,
            'items': self.receipt_data.get('items', []),
        }
        
        return render_to_string('receipts/receipt_template.html', context)
    
    def send_email(self):
        """Send receipt via email"""
        if not self.customer_email:
            return False
        
        from django.core.mail import send_mail
        from django.utils import timezone
        
        subject = f"Receipt for Order {self.order.order_number} - Maria Havens Hotel"
        message = self.generate_receipt_content()
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.business_email,
                recipient_list=[self.customer_email],
                html_message=message
            )
            
            self.is_emailed = True
            self.email_sent_at = timezone.now()
            self.save()
            return True
        except Exception as e:
            print(f"Failed to send receipt email: {e}")
            return False
    
    def void_receipt(self, reason, user):
        """Void the receipt"""
        from django.utils import timezone
        
        self.status = 'voided'
        self.void_reason = reason
        self.voided_by = user
        self.voided_at = timezone.now()
        self.save()


class ReceiptItem(models.Model):
    """Individual items on a receipt (for detailed tracking)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    
    # Item details (snapshot from order)
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tax information
    is_taxable = models.BooleanField(default=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16)  # 16% VAT
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Category for reporting
    category = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'receipt_items'
        verbose_name = 'Receipt Item'
        verbose_name_plural = 'Receipt Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.item_name} - {self.receipt.receipt_number}"


class ReceiptTemplate(models.Model):
    """Receipt template configuration"""
    
    TEMPLATE_TYPES = [
        ('standard', 'Standard Receipt'),
        ('thermal', 'Thermal Printer Receipt'),
        ('email', 'Email Receipt'),
        ('invoice', 'Invoice Format'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    
    # Template content
    header_template = models.TextField()
    body_template = models.TextField()
    footer_template = models.TextField()
    
    # Styling options
    font_size = models.PositiveIntegerField(default=12)
    paper_width = models.PositiveIntegerField(default=80)  # mm for thermal printers
    
    # Business info customization
    show_logo = models.BooleanField(default=True)
    logo_url = models.URLField(blank=True)
    show_address = models.BooleanField(default=True)
    show_tax_info = models.BooleanField(default=True)
    
    # Receipt elements
    show_order_details = models.BooleanField(default=True)
    show_payment_details = models.BooleanField(default=True)
    show_qr_code = models.BooleanField(default=False)
    qr_code_data = models.CharField(max_length=100, blank=True, help_text="URL or data for QR code")
    
    # Footer messages
    thank_you_message = models.TextField(default="Thank you for dining with us!")
    return_policy = models.TextField(blank=True)
    promotional_message = models.TextField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'receipt_templates'
        ordering = ['name']
        verbose_name = 'Receipt Template'
        verbose_name_plural = 'Receipt Templates'
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class ReceiptPrintQueue(models.Model):
    """Queue for receipt printing"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('printing', 'Printing'),
        ('printed', 'Printed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRINTER_TYPES = [
        ('thermal', 'Thermal Printer'),
        ('laser', 'Laser Printer'),
        ('pdf', 'PDF Generation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='print_queue')
    
    # Print settings
    printer_name = models.CharField(max_length=100)
    printer_type = models.CharField(max_length=20, choices=PRINTER_TYPES, default='thermal')
    copies = models.PositiveIntegerField(default=1)
    
    # Queue management
    priority = models.PositiveIntegerField(default=5)  # 1=highest, 10=lowest
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Processing info
    queued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='queued_prints'
    )
    
    error_message = models.TextField(blank=True)
    print_attempts = models.PositiveIntegerField(default=0)
    
    # Timestamps
    queued_at = models.DateTimeField(auto_now_add=True)
    printed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'receipt_print_queue'
        ordering = ['priority', 'queued_at']
        verbose_name = 'Receipt Print Queue'
        verbose_name_plural = 'Receipt Print Queue'
    
    def __str__(self):
        return f"Print Job - {self.receipt.receipt_number} ({self.status})"


class DailySalesReport(models.Model):
    """Daily sales summary for receipts/transactions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    
    # Receipt counts
    total_receipts = models.PositiveIntegerField(default=0)
    sale_receipts = models.PositiveIntegerField(default=0)
    refund_receipts = models.PositiveIntegerField(default=0)
    void_receipts = models.PositiveIntegerField(default=0)
    
    # Financial totals
    gross_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_service_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_discounts = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_refunds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment method breakdown
    cash_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mobile_money_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_charge_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Report generation
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='daily_sales_reports'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_sales_reports'
        ordering = ['-date']
        verbose_name = 'Daily Sales Report'
        verbose_name_plural = 'Daily Sales Reports'
    
    def __str__(self):
        return f"Sales Report - {self.date}"


class ReceiptEmailLog(models.Model):
    """Log of receipt email deliveries"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
        ('opened', 'Opened'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='email_logs')
    
    # Email details
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Delivery tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    bounced_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Email content reference
    email_id = models.CharField(max_length=100, blank=True, help_text="External email service ID")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'receipt_email_logs'
        ordering = ['-created_at']
        verbose_name = 'Receipt Email Log'
        verbose_name_plural = 'Receipt Email Logs'
    
    def __str__(self):
        return f"Email Log - {self.receipt.receipt_number} to {self.recipient_email}"
    
    def mark_as_sent(self, email_id=None):
        """Mark email as successfully sent"""
        from django.utils import timezone
        
        self.status = 'sent'
        self.sent_at = timezone.now()
        if email_id:
            self.email_id = email_id
        self.save()
    
    def mark_as_failed(self, error_message):
        """Mark email as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()
    
    def can_retry(self):
        """Check if email can be retried"""
        return self.retry_count < self.max_retries and self.status == 'failed'