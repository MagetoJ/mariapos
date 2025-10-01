from django.db import models
from django.conf import settings
import uuid

class Table(models.Model):
    """Restaurant table model"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Cleaning'),
        ('out_of_order', 'Out of Order'),
    ]
    
    SECTION_CHOICES = [
        ('main_dining', 'Main Dining'),
        ('terrace', 'Terrace'),
        ('private_dining', 'Private Dining'),
        ('bar_area', 'Bar Area'),
        ('garden', 'Garden'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=10, unique=True)
    
    # Table properties
    capacity = models.PositiveIntegerField(default=4)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='main_dining')
    
    # Status and availability
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    
    # Physical properties
    shape = models.CharField(
        max_length=15,
        choices=[
            ('round', 'Round'),
            ('square', 'Square'),
            ('rectangular', 'Rectangular'),
            ('booth', 'Booth'),
        ],
        default='round'
    )
    
    # Location details
    position_x = models.IntegerField(default=0, help_text="X coordinate for floor plan")
    position_y = models.IntegerField(default=0, help_text="Y coordinate for floor plan")
    
    # Current assignment
    assigned_waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tables',
        limit_choices_to={'role': 'waiter'}
    )
    
    current_order = models.OneToOneField(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='table'
    )
    
    # Timestamps
    last_occupied_at = models.DateTimeField(null=True, blank=True)
    last_cleaned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Special features
    has_view = models.BooleanField(default=False)
    is_accessible = models.BooleanField(default=True, help_text="Wheelchair accessible")
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tables'
        ordering = ['section', 'number']
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
    
    def __str__(self):
        return f"Table {self.number} ({self.section})"
    
    @property
    def is_available(self):
        return self.status == 'available' and self.is_active
    
    @property
    def is_occupied(self):
        return self.status == 'occupied'
    
    @property
    def display_name(self):
        return f"T{self.number}"
    
    def occupy(self, order=None, waiter=None):
        """Mark table as occupied"""
        self.status = 'occupied'
        self.last_occupied_at = models.timezone.now()
        if order:
            self.current_order = order
        if waiter:
            self.assigned_waiter = waiter
        self.save()
    
    def free(self):
        """Mark table as available and clear assignments"""
        self.status = 'available'
        self.current_order = None
        self.save()
    
    def mark_for_cleaning(self):
        """Mark table as needing cleaning"""
        self.status = 'cleaning'
        self.current_order = None
        self.save()
    
    def mark_cleaned(self):
        """Mark table as cleaned and available"""
        self.status = 'available'
        self.last_cleaned_at = models.timezone.now()
        self.save()


class TableReservation(models.Model):
    """Table reservation model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('seated', 'Seated'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation_number = models.CharField(max_length=20, unique=True)
    
    # Table and guest information
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    guest_name = models.CharField(max_length=100)
    guest_phone = models.CharField(max_length=17)
    guest_email = models.EmailField(blank=True)
    party_size = models.PositiveIntegerField()
    
    # Reservation details
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=120)
    
    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Special requests
    special_requests = models.TextField(blank=True)
    occasion = models.CharField(
        max_length=20,
        choices=[
            ('birthday', 'Birthday'),
            ('anniversary', 'Anniversary'),
            ('business', 'Business Meeting'),
            ('date', 'Date Night'),
            ('family', 'Family Gathering'),
            ('other', 'Other'),
        ],
        blank=True
    )
    
    # Staff assignment
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_reservations'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'table_reservations'
        ordering = ['reservation_date', 'reservation_time']
        verbose_name = 'Table Reservation'
        verbose_name_plural = 'Table Reservations'
        unique_together = ['table', 'reservation_date', 'reservation_time']
    
    def __str__(self):
        return f"Reservation {self.reservation_number} - {self.guest_name}"
    
    def save(self, *args, **kwargs):
        if not self.reservation_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_reservation = TableReservation.objects.filter(
                reservation_number__startswith=f'RES-{today}'
            ).order_by('-reservation_number').first()
            
            if last_reservation:
                last_seq = int(last_reservation.reservation_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.reservation_number = f'RES-{today}-{new_seq:04d}'
        
        super().save(*args, **kwargs)
    
    @property
    def is_today(self):
        from django.utils import timezone
        return self.reservation_date == timezone.now().date()
    
    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed']


class TableLayout(models.Model):
    """Restaurant floor plan/layout configuration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Layout dimensions
    width = models.PositiveIntegerField(default=800, help_text="Layout width in pixels")
    height = models.PositiveIntegerField(default=600, help_text="Layout height in pixels")
    
    # Floor plan image
    floor_plan_image = models.URLField(blank=True, null=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'table_layouts'
        verbose_name = 'Table Layout'
        verbose_name_plural = 'Table Layouts'
    
    def __str__(self):
        return self.name