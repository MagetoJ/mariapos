from django.db import models
from django.conf import settings
import uuid

class ServiceRequest(models.Model):
    """Service request model for guest services"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    TYPE_CHOICES = [
        ('housekeeping', 'Housekeeping'),
        ('maintenance', 'Maintenance'),
        ('room_service', 'Room Service'),
        ('concierge', 'Concierge'),
        ('transport', 'Transportation'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa & Wellness'),
        ('dining', 'Dining Reservation'),
        ('complaint', 'Complaint'),
        ('lost_found', 'Lost & Found'),
        ('other', 'Other'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_number = models.CharField(max_length=20, unique=True)
    
    # Request details
    guest = models.ForeignKey('guests.Guest', on_delete=models.CASCADE, related_name='service_requests')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Request information
    title = models.CharField(max_length=200)
    description = models.TextField()
    room_number = models.CharField(max_length=10)
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_service_requests'
    )
    department = models.CharField(
        max_length=20,
        choices=[
            ('housekeeping', 'Housekeeping'),
            ('maintenance', 'Maintenance'),
            ('food_beverage', 'Food & Beverage'),
            ('front_desk', 'Front Desk'),
            ('concierge', 'Concierge'),
            ('security', 'Security'),
            ('management', 'Management'),
        ],
        blank=True
    )
    
    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Additional details
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Communication
    guest_notified = models.BooleanField(default=False)
    guest_phone = models.CharField(max_length=17, blank=True)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    guest_satisfaction = models.PositiveIntegerField(
        null=True, blank=True,
        choices=[(i, f"{i} stars") for i in range(1, 6)],
        help_text="Guest satisfaction rating (1-5 stars)"
    )
    
    # Follow-up
    requires_followup = models.BooleanField(default=False)
    followup_date = models.DateTimeField(null=True, blank=True)
    followup_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_requests'
        ordering = ['-priority', '-requested_at']
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'
    
    def __str__(self):
        return f"{self.request_number} - {self.title} (Room {self.room_number})"
    
    def save(self, *args, **kwargs):
        if not self.request_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_request = ServiceRequest.objects.filter(
                request_number__startswith=f'SR-{today}'
            ).order_by('-request_number').first()
            
            if last_request:
                last_seq = int(last_request.request_number.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.request_number = f'SR-{today}-{new_seq:04d}'
        
        super().save(*args, **kwargs)
    
    @property
    def response_time(self):
        """Calculate response time in minutes"""
        if self.acknowledged_at and self.requested_at:
            delta = self.acknowledged_at - self.requested_at
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def resolution_time(self):
        """Calculate resolution time in minutes"""
        if self.completed_at and self.requested_at:
            delta = self.completed_at - self.requested_at
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def is_overdue(self):
        """Check if request is overdue"""
        if self.estimated_completion and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return timezone.now() > self.estimated_completion
        return False
    
    def acknowledge(self, staff_member):
        """Mark request as acknowledged"""
        from django.utils import timezone
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.assigned_to = staff_member
        self.save()
    
    def start_work(self):
        """Mark request as in progress"""
        from django.utils import timezone
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def complete(self, resolution_notes=''):
        """Mark request as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        self.save()


class ServiceRequestUpdate(models.Model):
    """Track updates and communication for service requests"""
    
    UPDATE_TYPES = [
        ('status_change', 'Status Change'),
        ('assignment', 'Assignment Change'),
        ('guest_communication', 'Guest Communication'),
        ('internal_note', 'Internal Note'),
        ('cost_update', 'Cost Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='updates')
    
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES)
    message = models.TextField()
    
    # Staff information
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='service_request_updates'
    )
    
    # Guest communication
    communicated_to_guest = models.BooleanField(default=False)
    guest_response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_request_updates'
        ordering = ['-created_at']
        verbose_name = 'Service Request Update'
        verbose_name_plural = 'Service Request Updates'
    
    def __str__(self):
        return f"{self.service_request.request_number} - {self.update_type}"


class ServiceRequestTemplate(models.Model):
    """Pre-defined service request templates for common requests"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=ServiceRequest.TYPE_CHOICES)
    department = models.CharField(max_length=20)
    
    # Template content
    title_template = models.CharField(max_length=200)
    description_template = models.TextField()
    
    # Default settings
    default_priority = models.CharField(max_length=10, choices=ServiceRequest.PRIORITY_CHOICES, default='medium')
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_guest_selectable = models.BooleanField(default=True, help_text="Can guests select this template?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_request_templates'
        ordering = ['type', 'name']
        verbose_name = 'Service Request Template'
        verbose_name_plural = 'Service Request Templates'
    
    def __str__(self):
        return f"{self.name} ({self.type})"


class ServiceMetrics(models.Model):
    """Track service performance metrics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Time period
    date = models.DateField()
    department = models.CharField(max_length=20, blank=True)
    
    # Metrics
    total_requests = models.PositiveIntegerField(default=0)
    completed_requests = models.PositiveIntegerField(default=0)
    cancelled_requests = models.PositiveIntegerField(default=0)
    overdue_requests = models.PositiveIntegerField(default=0)
    
    # Timing metrics (in minutes)
    avg_response_time = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    avg_resolution_time = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Satisfaction
    avg_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_satisfaction_responses = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_metrics'
        unique_together = ['date', 'department']
        ordering = ['-date']
        verbose_name = 'Service Metrics'
        verbose_name_plural = 'Service Metrics'
    
    def __str__(self):
        dept_str = f" - {self.department}" if self.department else ""
        return f"Service Metrics {self.date}{dept_str}"