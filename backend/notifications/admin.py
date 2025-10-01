from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'recipient__name', 'recipient__email']
    readonly_fields = ['id', 'created_at', 'read_at', 'sent_at']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_orders', 'email_inventory', 'realtime_orders', 'realtime_inventory']
    search_fields = ['user__name', 'user__email']