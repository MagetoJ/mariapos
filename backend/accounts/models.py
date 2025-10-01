from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
import uuid

class UserManager(BaseUserManager):
    """Custom user manager for handling email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class WorkShift(models.Model):
    """Work shift model for tracking user sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'work_shifts'
        verbose_name = 'Work Shift'
        verbose_name_plural = 'Work Shifts'
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for Maria Havens POS system"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('receptionist', 'Receptionist'),
        ('waiter', 'Waiter'),
        ('kitchen', 'Kitchen Staff'),
        ('cashier', 'Cashier'),
        ('guest', 'Guest'),
    ]
    
    # Use UUID for ID to match frontend expectations
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic user information
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Contact information
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_validator], max_length=17, blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Shift assignment
    assigned_shift = models.ForeignKey(
        WorkShift, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_users'
    )
    
    # For guest users
    room_number = models.CharField(max_length=10, blank=True, null=True)
    table_number = models.CharField(max_length=10, blank=True, null=True)
    check_in_date = models.DateField(blank=True, null=True)
    check_out_date = models.DateField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    @property
    def is_guest(self):
        return self.role == 'guest'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role in ['admin', 'manager']
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        permissions = {
            'admin': ['all'],
            'manager': ['view_dashboard', 'manage_users', 'manage_inventory', 'view_reports'],
            'receptionist': ['manage_guests', 'view_dashboard'],
            'waiter': ['take_orders', 'view_tables', 'manage_service_requests'],
            'kitchen': ['view_orders', 'update_order_status'],
            'cashier': ['process_payments', 'generate_receipts'],
            'guest': ['place_orders', 'view_menu', 'request_service']
        }
        
        user_permissions = permissions.get(self.role, [])
        return 'all' in user_permissions or permission in user_permissions

class UserSession(models.Model):
    """Track user work sessions for reporting"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    shift = models.ForeignKey(WorkShift, on_delete=models.CASCADE, related_name='sessions')
    
    # Session timing
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    
    # Session metrics
    orders_handled = models.PositiveIntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Session status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.name} - {self.shift.name} - {self.login_time.date()}"
    
    @property
    def duration(self):
        """Calculate session duration"""
        if self.logout_time:
            return self.logout_time - self.login_time
        return None