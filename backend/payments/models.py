from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Payment(models.Model):
    """Payment processing model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partial_refund', 'Partially Refunded'),
    ]
    
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('digital_wallet', 'Digital Wallet'),
        ('voucher', 'Voucher/Gift Card'),
        ('room_charge', 'Room Charge'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_number = models.CharField(max_length=20, unique=True)
    
    # Payment details
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer information
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Transaction details
    transaction_reference = models.CharField(max_length=100, blank=True)
    gateway_reference = models.CharField(max_length=100, blank=True)
    authorization_code = models.CharField(max_length=50, blank=True)
    
    # Card details (for card payments)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)  # Visa, Mastercard, etc.
    card_type = models.CharField(max_length=10, blank=True)  # Credit, Debit
    
    # Mobile money details
    mobile_money_number = models.CharField(max_length=17, blank=True)
    mobile_money_provider = models.CharField(
        max_length=20,
        choices=[
            ('mpesa', 'M-Pesa'),
            ('airtel_money', 'Airtel Money'),
            ('tkash', 'T-Kash'),
            ('other', 'Other'),
        ],
        blank=True
    )
    
    # Processing information
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='processed_payments',
        limit_choices_to={'role__in': ['cashier', 'admin', 'manager']}
    )
    
    # Timing
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Fees and charges
    gateway_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Refund information
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)
    
    # Notes and metadata
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment {self.payment_number} - KSh {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_payment = Payment.objects.filter(
                payment_number__startswith=f'PAY-{today}'
            ).order_by('-payment_number').first()
            
            if last_payment:
                last_seq = int(last_payment.payment_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.payment_number = f'PAY-{today}-{new_seq:04d}'
        
        super().save(*args, **kwargs)
    
    @property
    def net_amount(self):
        """Amount after fees"""
        return self.amount - self.gateway_fee - self.processing_fee
    
    @property
    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return self.status == 'completed' and self.refunded_amount < self.amount
    
    @property
    def remaining_refundable_amount(self):
        """Amount that can still be refunded"""
        return self.amount - self.refunded_amount
    
    def process_payment(self):
        """Mark payment as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def fail_payment(self, reason=''):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason:
            self.notes = reason
        self.save()
    
    def refund(self, amount=None, reason=''):
        """Process a refund"""
        if not self.can_be_refunded:
            raise ValueError("Payment cannot be refunded")
        
        refund_amount = amount or self.remaining_refundable_amount
        
        if refund_amount > self.remaining_refundable_amount:
            raise ValueError("Refund amount exceeds refundable amount")
        
        self.refunded_amount += refund_amount
        self.refund_reason = reason
        
        if self.refunded_amount >= self.amount:
            self.status = 'refunded'
        else:
            self.status = 'partial_refund'
        
        self.save()
        
        # Create refund record
        PaymentRefund.objects.create(
            payment=self,
            amount=refund_amount,
            reason=reason,
            processed_by=self.processed_by
        )


class PaymentRefund(models.Model):
    """Payment refund records"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refund_number = models.CharField(max_length=20, unique=True)
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Processing details
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='processed_refunds'
    )
    
    # Gateway information
    gateway_reference = models.CharField(max_length=100, blank=True)
    gateway_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Timing
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_refunds'
        ordering = ['-created_at']
        verbose_name = 'Payment Refund'
        verbose_name_plural = 'Payment Refunds'
    
    def __str__(self):
        return f"Refund {self.refund_number} - KSh {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.refund_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_refund = PaymentRefund.objects.filter(
                refund_number__startswith=f'REF-{today}'
            ).order_by('-refund_number').first()
            
            if last_refund:
                last_seq = int(last_refund.refund_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.refund_number = f'REF-{today}-{new_seq:04d}'
        
        super().save(*args, **kwargs)


class PaymentGateway(models.Model):
    """Payment gateway configuration"""
    
    GATEWAY_TYPES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('flutterwave', 'Flutterwave'),
        ('pesapal', 'PesaPal'),
        ('mpesa', 'M-Pesa STK Push'),
        ('manual', 'Manual Processing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    
    # Settings (stored as JSON)
    settings = models.JSONField(default=dict)
    
    # Supported payment methods
    supports_cards = models.BooleanField(default=False)
    supports_mobile_money = models.BooleanField(default=False)
    supports_bank_transfers = models.BooleanField(default=False)
    
    # Fees
    transaction_fee_fixed = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    transaction_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_gateways'
        ordering = ['name']
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'
    
    def __str__(self):
        return f"{self.name} ({self.gateway_type})"
    
    def calculate_fee(self, amount):
        """Calculate gateway fee for given amount"""
        percent_fee = amount * (self.transaction_fee_percent / 100)
        return self.transaction_fee_fixed + percent_fee


class PaymentAttempt(models.Model):
    """Track payment attempts and failures"""
    
    ATTEMPT_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timeout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='attempts')
    
    # Attempt details
    attempt_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=ATTEMPT_STATUS_CHOICES)
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Gateway response
    gateway_response = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_attempts'
        ordering = ['-started_at']
        unique_together = ['payment', 'attempt_number']
        verbose_name = 'Payment Attempt'
        verbose_name_plural = 'Payment Attempts'
    
    def __str__(self):
        return f"Payment Attempt #{self.attempt_number} - {self.payment.payment_number}"


class PaymentSplit(models.Model):
    """For splitting payments between multiple parties or accounts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='splits')
    
    # Split details
    recipient_name = models.CharField(max_length=100)
    recipient_account = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Status
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_splits'
        verbose_name = 'Payment Split'
        verbose_name_plural = 'Payment Splits'
    
    def __str__(self):
        return f"Split {self.payment.payment_number} - {self.recipient_name} (KSh {self.amount})"


class PaymentReport(models.Model):
    """Payment reports and reconciliation"""
    
    REPORT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('reconciliation', 'Reconciliation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Summary data
    total_payments = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_refunds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment method breakdown
    cash_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mobile_money_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Fees and costs
    total_gateway_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_processing_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Report metadata
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payment_reports'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_reports'
        ordering = ['-created_at']
        verbose_name = 'Payment Report'
        verbose_name_plural = 'Payment Reports'
    
    def __str__(self):
        return f"{self.report_type.title()} Payment Report - {self.start_date} to {self.end_date}"