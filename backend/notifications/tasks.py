from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from decimal import Decimal

from .models import Notification, NotificationPreference

User = get_user_model()

@shared_task
def send_notification_email(notification_id):
    """Send notification via email"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Check user preferences
        preferences, _ = NotificationPreference.objects.get_or_create(
            user=notification.recipient
        )
        
        # Determine if email should be sent based on notification type
        should_send_email = False
        if notification.notification_type == 'order' and preferences.email_orders:
            should_send_email = True
        elif notification.notification_type == 'inventory' and preferences.email_inventory:
            should_send_email = True
        elif notification.notification_type == 'shift' and preferences.email_shifts:
            should_send_email = True
        elif notification.notification_type == 'payment' and preferences.email_payments:
            should_send_email = True
        elif notification.notification_type == 'system' and preferences.email_system:
            should_send_email = True
        
        if should_send_email and notification.recipient.email:
            subject = f"[Maria Havens POS] {notification.title}"
            message = notification.message
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [notification.recipient.email],
                fail_silently=False,
            )
            
            # Mark as sent
            notification.sent_at = timezone.now()
            notification.save()
            
        return f"Email notification processed for {notification.recipient.email}"
        
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@shared_task
def send_realtime_notification(notification_id):
    """Send real-time notification via WebSocket"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Check user preferences
        preferences, _ = NotificationPreference.objects.get_or_create(
            user=notification.recipient
        )
        
        # Determine if real-time notification should be sent
        should_send_realtime = False
        if notification.notification_type == 'order' and preferences.realtime_orders:
            should_send_realtime = True
        elif notification.notification_type == 'inventory' and preferences.realtime_inventory:
            should_send_realtime = True
        elif notification.notification_type == 'shift' and preferences.realtime_shifts:
            should_send_realtime = True
        elif notification.notification_type == 'payment' and preferences.realtime_payments:
            should_send_realtime = True
        elif notification.notification_type == 'system' and preferences.realtime_system:
            should_send_realtime = True
        
        if should_send_realtime:
            channel_layer = get_channel_layer()
            
            # Send to user's personal channel
            user_group = f"user_{notification.recipient.id}"
            
            async_to_sync(channel_layer.group_send)(
                user_group,
                {
                    'type': 'notification_message',
                    'notification': {
                        'id': str(notification.id),
                        'title': notification.title,
                        'message': notification.message,
                        'type': notification.notification_type,
                        'priority': notification.priority,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
        
        return f"Real-time notification sent to user {notification.recipient.id}"
        
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"
    except Exception as e:
        return f"Error sending real-time notification: {str(e)}"

@shared_task
def create_and_send_notification(recipient_id, title, message, notification_type='system', priority='medium', send_email=True, send_realtime=True):
    """Create and send a notification"""
    try:
        recipient = User.objects.get(id=recipient_id)
        
        # Create notification
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority
        )
        
        # Send via different channels
        if send_email:
            send_notification_email.delay(str(notification.id))
        
        if send_realtime:
            send_realtime_notification.delay(str(notification.id))
        
        return f"Notification created and queued: {notification.id}"
        
    except User.DoesNotExist:
        return f"User {recipient_id} not found"
    except Exception as e:
        return f"Error creating notification: {str(e)}"

@shared_task
def notify_low_inventory(item_id):
    """Send low inventory notifications"""
    try:
        from inventory.models import InventoryItem
        
        item = InventoryItem.objects.get(id=item_id)
        
        # Get all staff users
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        
        title = f"Low Inventory Alert: {item.name}"
        message = f"The inventory for {item.name} is running low. Current quantity: {item.quantity}"
        
        for user in staff_users:
            create_and_send_notification.delay(
                str(user.id),
                title,
                message,
                'inventory',
                'high'
            )
        
        return f"Low inventory notifications sent for {item.name}"
        
    except Exception as e:
        return f"Error sending low inventory notification: {str(e)}"

@shared_task
def notify_new_order(order_id):
    """Send new order notifications to kitchen staff"""
    try:
        from orders.models import Order
        
        order = Order.objects.get(id=order_id)
        
        # Get kitchen staff (you might want to add a specific role field)
        kitchen_staff = User.objects.filter(
            is_staff=True,
            is_active=True,
            user_type='staff'  # Assuming you have user types
        )
        
        title = f"New Order #{order.id}"
        message = f"New order from Table {order.table.number if order.table else 'N/A'}. Total: ${order.total_amount}"
        
        for user in kitchen_staff:
            create_and_send_notification.delay(
                str(user.id),
                title,
                message,
                'order',
                'high'
            )
        
        return f"New order notifications sent for order {order_id}"
        
    except Exception as e:
        return f"Error sending new order notification: {str(e)}"

@shared_task
def notify_shift_start(shift_report_id):
    """Send shift start notifications"""
    try:
        from reports.models import ShiftReport
        
        shift_report = ShiftReport.objects.get(id=shift_report_id)
        
        title = f"Shift Started: {shift_report.shift_type.title()}"
        message = f"Your {shift_report.shift_type} shift has started. Good luck!"
        
        create_and_send_notification.delay(
            str(shift_report.user.id),
            title,
            message,
            'shift',
            'medium'
        )
        
        return f"Shift start notification sent to {shift_report.user.name}"
        
    except Exception as e:
        return f"Error sending shift start notification: {str(e)}"

@shared_task
def notify_shift_end(shift_report_id):
    """Send shift end notifications with performance summary"""
    try:
        from reports.models import ShiftReport
        
        shift_report = ShiftReport.objects.get(id=shift_report_id)
        
        title = f"Shift Completed: {shift_report.shift_type.title()}"
        message = f"""Your {shift_report.shift_type} shift has ended.
        
Performance Summary:
- Orders handled: {shift_report.orders_handled}
- Revenue generated: ${shift_report.total_revenue}
- Average order value: ${shift_report.average_order_value}
- Customers served: {shift_report.customer_count}

Great work!"""
        
        create_and_send_notification.delay(
            str(shift_report.user.id),
            title,
            message,
            'shift',
            'low'
        )
        
        return f"Shift end notification sent to {shift_report.user.name}"
        
    except Exception as e:
        return f"Error sending shift end notification: {str(e)}"

@shared_task
def cleanup_old_notifications():
    """Clean up old notifications (older than 30 days)"""
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()[0]
        
        return f"Cleaned up {deleted_count} old notifications"
        
    except Exception as e:
        return f"Error cleaning up notifications: {str(e)}"

@shared_task
def generate_daily_reports():
    """Generate daily reports for all dates that need them"""
    try:
        from reports.models import DailyReport
        from django.utils import timezone
        from datetime import timedelta
        
        # Generate reports for the last 7 days if they don't exist
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        generated_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            if not DailyReport.objects.filter(date=current_date).exists():
                DailyReport.generate_for_date(current_date)
                generated_count += 1
            
            current_date += timedelta(days=1)
        
        return f"Generated {generated_count} daily reports"
        
    except Exception as e:
        return f"Error generating daily reports: {str(e)}"