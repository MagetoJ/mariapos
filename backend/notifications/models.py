from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    """Model for system notifications"""
    NOTIFICATION_TYPES = [
        ('order_new', 'New Order'),
        ('order_updated', 'Order Updated'),
        ('order_completed', 'Order Completed'),
        ('inventory_low', 'Low Inventory'),
        ('shift_start', 'Shift Started'),
        ('shift_end', 'Shift Ended'),
        ('payment_received', 'Payment Received'),
        ('guest_request', 'Guest Request'),
        ('system_alert', 'System Alert'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Metadata
    data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.name}"

class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email notifications
    email_orders = models.BooleanField(default=True)
    email_inventory = models.BooleanField(default=True)
    email_shifts = models.BooleanField(default=False)
    email_payments = models.BooleanField(default=True)
    
    # Real-time notifications
    realtime_orders = models.BooleanField(default=True)
    realtime_inventory = models.BooleanField(default=True)
    realtime_shifts = models.BooleanField(default=True)
    realtime_payments = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.name}"