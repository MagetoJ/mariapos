from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
import uuid

class Guest(models.Model):
    """Hotel guest model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Check-in'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ]
    
    GUEST_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('family', 'Family'),
        ('group', 'Group'),
        ('corporate', 'Corporate'),
        ('vip', 'VIP'),
    ]
    
    ID_TYPE_CHOICES = [
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('other', 'Other'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest_number = models.CharField(max_length=20, unique=True)
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_validator], max_length=17)
    
    # Address information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Identification
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, default='national_id')
    id_number = models.CharField(max_length=50)
    
    # Guest details
    guest_type = models.CharField(max_length=20, choices=GUEST_TYPE_CHOICES, default='individual')
    company = models.CharField(max_length=200, blank=True, help_text="For corporate guests")
    
    # Stay information
    room_number = models.CharField(max_length=10)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Check-in/out details
    expected_checkin = models.DateTimeField()
    actual_checkin = models.DateTimeField(null=True, blank=True)
    expected_checkout = models.DateTimeField()
    actual_checkout = models.DateTimeField(null=True, blank=True)
    
    # Guest preferences
    dietary_preferences = models.TextField(blank=True, help_text="Vegetarian, allergies, etc.")
    special_requests = models.TextField(blank=True)
    preferred_language = models.CharField(max_length=20, default='english')
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Billing information
    billing_address = models.TextField(blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('card', 'Credit/Debit Card'),
            ('mobile_money', 'Mobile Money'),
            ('bank_transfer', 'Bank Transfer'),
            ('corporate', 'Corporate Account'),
        ],
        default='cash'
    )
    
    # Service preferences
    housekeeping_preferences = models.TextField(blank=True)
    minibar_access = models.BooleanField(default=True)
    
    # Marketing preferences
    marketing_consent = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=False)
    
    # VIP services
    is_vip = models.BooleanField(default=False)
    loyalty_number = models.CharField(max_length=50, blank=True)
    previous_stays = models.PositiveIntegerField(default=0)
    
    # Staff assignment
    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_guests',
        limit_choices_to={'role__in': ['receptionist', 'manager', 'admin']}
    )
    
    # Notes and comments
    notes = models.TextField(blank=True, help_text="Internal staff notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'guests'
        ordering = ['-created_at']
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'
        unique_together = ['room_number', 'expected_checkin']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - Room {self.room_number}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_checked_in(self):
        return self.status == 'checked_in'
    
    @property
    def stay_duration(self):
        """Calculate stay duration in days"""
        if self.actual_checkout and self.actual_checkin:
            return (self.actual_checkout.date() - self.actual_checkin.date()).days
        elif self.actual_checkin:
            from django.utils import timezone
            return (timezone.now().date() - self.actual_checkin.date()).days
        return 0
    
    def save(self, *args, **kwargs):
        if not self.guest_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_guest = Guest.objects.filter(
                guest_number__startswith=f'GST-{today}'
            ).order_by('-guest_number').first()
            
            if last_guest:
                last_seq = int(last_guest.guest_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.guest_number = f'GST-{today}-{new_seq:04d}'
        
        super().save(*args, **kwargs)
    
    def check_in(self):
        """Mark guest as checked in"""
        from django.utils import timezone
        self.status = 'checked_in'
        self.actual_checkin = timezone.now()
        self.save()
        
        # Create user account for room service if it doesn't exist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(email=self.email, role='guest').exists():
            guest_user = User.objects.create_user(
                email=self.email,
                password='temp123',  # Should be changed by guest
                name=self.full_name,
                role='guest',
                phone=self.phone,
                room_number=self.room_number,
                is_active=True
            )
            return guest_user
        
        return None
    
    def check_out(self):
        """Mark guest as checked out"""
        from django.utils import timezone
        self.status = 'checked_out'
        self.actual_checkout = timezone.now()
        self.save()
        
        # Deactivate guest user account
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        guest_users = User.objects.filter(
            email=self.email, 
            role='guest',
            room_number=self.room_number
        )
        guest_users.update(is_active=False)


class GuestGroup(models.Model):
    """Group/Family guest bookings"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=200)
    group_leader = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='led_groups')
    
    # Group details
    total_guests = models.PositiveIntegerField()
    group_type = models.CharField(
        max_length=20,
        choices=[
            ('family', 'Family'),
            ('friends', 'Friends'),
            ('corporate', 'Corporate'),
            ('wedding', 'Wedding Party'),
            ('tour', 'Tour Group'),
            ('conference', 'Conference'),
            ('other', 'Other'),
        ]
    )
    
    # Special arrangements
    group_rate_applied = models.BooleanField(default=False)
    group_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    special_arrangements = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'guest_groups'
        verbose_name = 'Guest Group'
        verbose_name_plural = 'Guest Groups'
    
    def __str__(self):
        return f"{self.group_name} ({self.total_guests} guests)"


class GuestPreference(models.Model):
    """Track guest preferences for personalized service"""
    
    PREFERENCE_CATEGORIES = [
        ('room', 'Room Preferences'),
        ('food', 'Food & Dining'),
        ('service', 'Service Preferences'),
        ('communication', 'Communication'),
        ('amenities', 'Amenities'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='preferences')
    
    category = models.CharField(max_length=20, choices=PREFERENCE_CATEGORIES)
    preference_key = models.CharField(max_length=100)
    preference_value = models.TextField()
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'guest_preferences'
        unique_together = ['guest', 'category', 'preference_key']
        verbose_name = 'Guest Preference'
        verbose_name_plural = 'Guest Preferences'
    
    def __str__(self):
        return f"{self.guest.full_name} - {self.preference_key}"


class GuestFeedback(models.Model):
    """Guest feedback and ratings"""
    
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1-5 star rating
    
    FEEDBACK_CATEGORIES = [
        ('room', 'Room Quality'),
        ('service', 'Service Quality'),
        ('food', 'Food & Dining'),
        ('cleanliness', 'Cleanliness'),
        ('staff', 'Staff Behavior'),
        ('amenities', 'Amenities'),
        ('value', 'Value for Money'),
        ('overall', 'Overall Experience'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='feedback')
    
    # Rating and feedback
    category = models.CharField(max_length=20, choices=FEEDBACK_CATEGORIES)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True)
    
    # Feedback metadata
    is_anonymous = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Management response
    management_response = models.TextField(blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='guest_responses'
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'guest_feedback'
        ordering = ['-created_at']
        verbose_name = 'Guest Feedback'
        verbose_name_plural = 'Guest Feedback'
    
    def __str__(self):
        return f"{self.guest.full_name} - {self.category} ({self.rating}★)"