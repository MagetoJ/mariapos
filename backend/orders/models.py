from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Order(models.Model):
    """Order model for both dine-in and room service"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ]
    
    TYPE_CHOICES = [
        ('dine_in', 'Dine In'),
        ('room_service', 'Room Service'),
        ('takeaway', 'Takeaway'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('refunded', 'Refunded'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True)  # Auto-generated
    
    # Customer information
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    # Staff assignment
    waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='waiter_orders',
        limit_choices_to={'role__in': ['waiter', 'admin', 'manager']}
    )
    
    # Order details
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Location information
    table_number = models.CharField(max_length=10, blank=True, null=True)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Special instructions
    special_instructions = models.TextField(blank=True)
    kitchen_notes = models.TextField(blank=True)
    
    # Timing
    estimated_preparation_time = models.PositiveIntegerField(default=30, help_text="Minutes")
    prepared_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    
    # Priority
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        default='normal'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        # Generate order number if not set
        if not self.order_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(
                order_number__startswith=f'ORD-{today}'
            ).order_by('-order_number').first()
            
            if last_order:
                last_seq = int(last_order.order_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.order_number = f'ORD-{today}-{new_seq:04d}'
        
        # Only calculate totals if this is not a new object or skip_calculate_totals is not set
        if not kwargs.pop('skip_calculate_totals', False) and self.pk is not None:
            self.calculate_totals()
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate order totals based on items"""
        items_total = sum(item.line_total for item in self.items.all())
        self.subtotal = items_total
        
        # Calculate tax (16% VAT in Kenya)
        tax_rate = Decimal('0.16')
        self.tax_amount = self.subtotal * tax_rate
        
        # Service charge (10% for dine-in)
        if self.type == 'dine_in':
            service_rate = Decimal('0.10')
            self.service_charge = self.subtotal * service_rate
        else:
            self.service_charge = Decimal('0.00')
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount + self.service_charge - self.discount_amount
    
    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed']
    
    @property
    def is_room_service(self):
        return self.type == 'room_service'


class OrderItem(models.Model):
    """Individual items within an order"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Menu item details (stored to preserve data even if menu item is deleted)
    menu_item = models.ForeignKey(
        'menu.MenuItem', 
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    menu_item_name = models.CharField(max_length=200)  # Snapshot
    menu_item_price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot
    
    # Order details
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Special instructions for this item
    special_instructions = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('preparing', 'Preparing'),
            ('ready', 'Ready'),
            ('served', 'Served'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item_name} (Order {self.order.order_number})"
    
    def save(self, *args, **kwargs):
        # Store snapshot of menu item data
        if self.menu_item:
            self.menu_item_name = self.menu_item.name
            self.menu_item_price = self.menu_item.price
        
        # Calculate line total
        self.unit_price = self.menu_item_price
        self.line_total = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)


class OrderItemModifier(models.Model):
    """Modifiers applied to order items"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='modifiers')
    
    # Modifier details (stored as snapshot)
    modifier_name = models.CharField(max_length=100)
    modifier_type = models.CharField(max_length=20)
    price_adjustment = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'order_item_modifiers'
        verbose_name = 'Order Item Modifier'
        verbose_name_plural = 'Order Item Modifiers'
    
    def __str__(self):
        return f"{self.modifier_name} for {self.order_item}"


class OrderStatusHistory(models.Model):
    """Track order status changes"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_status_history'
        ordering = ['-timestamp']
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
    
    def __str__(self):
        return f"Order {self.order.order_number} - {self.status} at {self.timestamp}"