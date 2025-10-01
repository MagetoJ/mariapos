from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class InventoryCategory(models.Model):
    """Inventory item categories"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_categories'
        ordering = ['name']
        verbose_name = 'Inventory Category'
        verbose_name_plural = 'Inventory Categories'
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Supplier(models.Model):
    """Supplier/Vendor information"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=17)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Business details
    tax_id = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True, help_text="e.g., Net 30, Cash on delivery")
    
    # Status
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
    
    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """Inventory item model"""
    
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('pcs', 'Pieces'),
        ('bottles', 'Bottles'),
        ('cans', 'Cans'),
        ('boxes', 'Boxes'),
        ('packets', 'Packets'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    description = models.TextField(blank=True)
    
    # Categorization
    category = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE, related_name='items')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    
    # Stock information
    current_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=3)
    max_stock_level = models.DecimalField(max_digits=10, decimal_places=3)
    reorder_point = models.DecimalField(max_digits=10, decimal_places=3)
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Storage information
    storage_location = models.CharField(max_length=100, blank=True, help_text="e.g., Freezer A, Pantry Shelf 3")
    
    # Expiry tracking
    tracks_expiry = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(null=True, blank=True, help_text="Shelf life in days")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_counted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'inventory_items'
        ordering = ['category', 'name']
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_point
    
    @property
    def stock_status(self):
        if self.current_stock <= 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        elif self.current_stock >= self.max_stock_level:
            return 'overstock'
        else:
            return 'normal'
    
    @property
    def stock_value(self):
        return self.current_stock * self.unit_cost
    
    def update_stock(self, quantity, reason, user=None):
        """Update stock and create movement record"""
        old_stock = self.current_stock
        self.current_stock += quantity
        self.save()
        
        # Create stock movement record
        StockMovement.objects.create(
            item=self,
            movement_type='adjustment' if quantity != 0 else 'count',
            quantity=quantity,
            previous_stock=old_stock,
            new_stock=self.current_stock,
            reason=reason,
            created_by=user
        )


class StockMovement(models.Model):
    """Track all inventory movements"""
    
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('waste', 'Waste/Spoilage'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Stock Adjustment'),
        ('count', 'Stock Count'),
        ('return', 'Return to Supplier'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    
    # Stock levels
    previous_stock = models.DecimalField(max_digits=10, decimal_places=3)
    new_stock = models.DecimalField(max_digits=10, decimal_places=3)
    
    # Reference information
    reference_number = models.CharField(max_length=100, blank=True, help_text="Purchase order, waste ticket, etc.")
    reason = models.TextField(blank=True)
    
    # Cost tracking
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_movements'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_movements'
        ordering = ['-created_at']
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
    
    def __str__(self):
        direction = '+' if self.quantity >= 0 else ''
        return f"{self.item.name}: {direction}{self.quantity} {self.item.unit} ({self.movement_type})"


class PurchaseOrder(models.Model):
    """Purchase orders for inventory replenishment"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent to Supplier'),
        ('confirmed', 'Confirmed'),
        ('partial', 'Partially Received'),
        ('received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    po_number = models.CharField(max_length=20, unique=True)
    
    # Supplier information
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    
    # Order details
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_purchase_orders'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-created_at']
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
    
    def __str__(self):
        return f"PO {self.po_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.po_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_po = PurchaseOrder.objects.filter(
                po_number__startswith=f'PO-{today}'
            ).order_by('-po_number').first()
            
            if last_po:
                last_seq = int(last_po.po_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.po_number = f'PO-{today}-{new_seq:04d}'
        
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Items within a purchase order"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    
    # Order details
    quantity_ordered = models.DecimalField(max_digits=10, decimal_places=3)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Receiving details
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'purchase_order_items'
        unique_together = ['purchase_order', 'item']
        verbose_name = 'Purchase Order Item'
        verbose_name_plural = 'Purchase Order Items'
    
    def __str__(self):
        return f"{self.item.name} - {self.quantity_ordered} {self.item.unit}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity_ordered * self.unit_price
        super().save(*args, **kwargs)
    
    @property
    def quantity_remaining(self):
        return self.quantity_ordered - self.quantity_received
    
    @property
    def is_fully_received(self):
        return self.quantity_received >= self.quantity_ordered


class WasteLog(models.Model):
    """Track inventory waste and spoilage"""
    
    WASTE_REASONS = [
        ('expired', 'Expired'),
        ('spoiled', 'Spoiled'),
        ('damaged', 'Damaged'),
        ('contaminated', 'Contaminated'),
        ('overproduction', 'Overproduction'),
        ('mistake', 'Staff Mistake'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='waste_logs')
    
    # Waste details
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    reason = models.CharField(max_length=20, choices=WASTE_REASONS)
    description = models.TextField(blank=True)
    
    # Cost impact
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tracking
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reported_waste'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'waste_logs'
        ordering = ['-created_at']
        verbose_name = 'Waste Log'
        verbose_name_plural = 'Waste Logs'
    
    def __str__(self):
        return f"Waste: {self.quantity} {self.item.unit} of {self.item.name}"
    
    def save(self, *args, **kwargs):
        if not self.unit_cost:
            self.unit_cost = self.item.unit_cost
        self.total_cost = self.quantity * self.unit_cost
        
        super().save(*args, **kwargs)
        
        # Update item stock
        self.item.update_stock(
            quantity=-self.quantity,
            reason=f"Waste: {self.get_reason_display()}",
            user=self.reported_by
        )