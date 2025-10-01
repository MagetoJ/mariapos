from rest_framework import serializers
from .models import Notification, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority',
            'is_read', 'data', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_orders', 'email_inventory', 'email_shifts', 'email_payments',
            'realtime_orders', 'realtime_inventory', 'realtime_shifts', 'realtime_payments'
        ]