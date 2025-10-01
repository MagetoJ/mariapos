from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg, F, Case, When, DecimalField
from django.db.models.functions import TruncDate, TruncHour
from datetime import datetime, timedelta, date
import logging
from decimal import Decimal

from accounts.permissions import IsStaffMember
from .serializers import (
    DashboardStatsSerializer, SalesDataSerializer, CategorySalesSerializer,
    PaymentMethodStatsSerializer, TopItemsSerializer, StaffPerformanceSerializer,
    GuestStatsSerializer, ServiceRequestStatsSerializer, InventoryStatsSerializer,
    ComprehensiveReportSerializer, RealtimeStatsSerializer, TrendAnalysisSerializer,
    BusinessInsightsSerializer, AlertsSerializer
)

logger = logging.getLogger(__name__)

class DashboardViewSet(viewsets.ViewSet):
    """Dashboard statistics and analytics ViewSet"""
    
    permission_classes = [IsAuthenticated, IsStaffMember]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get main dashboard statistics"""
        try:
            today = timezone.now().date()
            
            # Import models
            from orders.models import Order
            from guests.models import Guest
            from service_requests.models import ServiceRequest
            from tables.models import Table
            from inventory.models import InventoryItem
            from payments.models import Payment
            
            # Today's revenue and orders
            today_orders = Order.objects.filter(created_at__date=today)
            today_revenue = today_orders.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            
            # Guest statistics
            today_guests = Guest.objects.filter(check_in_date=today).count()
            today_checkins = Guest.objects.filter(
                check_in_time__date=today
            ).count()
            
            # Current status
            active_orders = Order.objects.filter(
                status__in=['pending', 'preparing', 'ready']
            ).count()
            
            pending_service_requests = ServiceRequest.objects.filter(
                status='pending'
            ).count()
            
            occupied_rooms = Guest.objects.filter(status='checked_in').count()
            occupied_tables = Table.objects.filter(status='occupied').count()
            
            # Performance metrics
            all_orders = Order.objects.filter(created_at__date=today)
            avg_order_value = all_orders.aggregate(
                avg=Avg('total')
            )['avg'] or Decimal('0.00')
            
            # Inventory alerts
            low_stock_items = InventoryItem.objects.filter(
                current_stock__lte=F('minimum_stock')
            ).count()
            
            out_of_stock_items = InventoryItem.objects.filter(
                current_stock=0
            ).count()
            
            stats_data = {
                'today_revenue': today_revenue,
                'today_orders': today_orders.count(),
                'today_guests': today_guests,
                'today_checkins': today_checkins,
                'active_orders': active_orders,
                'pending_service_requests': pending_service_requests,
                'occupied_rooms': occupied_rooms,
                'occupied_tables': occupied_tables,
                'average_order_value': avg_order_value,
                'low_stock_items': low_stock_items,
                'out_of_stock_items': out_of_stock_items,
                'pending_purchase_orders': 0,  # Would be calculated from purchase orders
            }
            
            serializer = DashboardStatsSerializer(stats_data)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return Response(
                {'error': 'Failed to load dashboard statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def sales_data(self, request):
        """Get sales data for charts"""
        try:
            days = int(request.query_params.get('days', 7))
            start_date = timezone.now().date() - timedelta(days=days-1)
            
            from orders.models import Order
            
            # Get daily sales data
            sales_data = []
            for i in range(days):
                current_date = start_date + timedelta(days=i)
                
                day_orders = Order.objects.filter(
                    created_at__date=current_date,
                    status='completed'
                )
                
                revenue = day_orders.aggregate(
                    total=Sum('total')
                )['total'] or Decimal('0.00')
                
                orders_count = day_orders.count()
                avg_value = day_orders.aggregate(
                    avg=Avg('total')
                )['avg'] or Decimal('0.00')
                
                # Breakdown by order type
                dine_in_revenue = day_orders.filter(
                    order_type='dine_in'
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
                
                takeaway_revenue = day_orders.filter(
                    order_type='takeaway'
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
                
                room_service_revenue = day_orders.filter(
                    order_type='room_service'
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
                
                sales_data.append({
                    'date': current_date,
                    'revenue': revenue,
                    'orders': orders_count,
                    'average_order_value': avg_value,
                    'dine_in_revenue': dine_in_revenue,
                    'takeaway_revenue': takeaway_revenue,
                    'room_service_revenue': room_service_revenue,
                })
            
            serializer = SalesDataSerializer(sales_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting sales data: {str(e)}")
            return Response(
                {'error': 'Failed to load sales data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def category_sales(self, request):
        """Get sales by menu category"""
        try:
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now().date() - timedelta(days=days-1)
            
            from orders.models import OrderItem
            from menu.models import MenuItem
            
            # Get category sales data
            category_data = OrderItem.objects.filter(
                order__created_at__date__gte=start_date,
                order__status='completed'
            ).values(
                'menu_item__category'
            ).annotate(
                revenue=Sum(F('quantity') * F('price')),
                orders=Count('order__id', distinct=True),
                items_sold=Sum('quantity')
            ).order_by('-revenue')
            
            # Calculate total revenue for percentages
            total_revenue = sum(item['revenue'] for item in category_data)
            
            # Add percentage calculation
            category_sales = []
            for item in category_data:
                percentage = (item['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
                category_sales.append({
                    'category': item['menu_item__category'] or 'Uncategorized',
                    'revenue': item['revenue'],
                    'orders': item['orders'],
                    'items_sold': item['items_sold'],
                    'percentage_of_total': Decimal(str(round(percentage, 2)))
                })
            
            serializer = CategorySalesSerializer(category_sales, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting category sales: {str(e)}")
            return Response(
                {'error': 'Failed to load category sales'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def payment_methods(self, request):
        """Get payment method statistics"""
        try:
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now().date() - timedelta(days=days-1)
            
            from payments.models import Payment
            
            payment_stats = Payment.objects.filter(
                created_at__date__gte=start_date,
                status='completed'
            ).values('payment_method').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            ).order_by('-total_amount')
            
            # Calculate total for percentages
            total_amount = sum(item['total_amount'] for item in payment_stats)
            
            payment_data = []
            for item in payment_stats:
                percentage = (item['total_amount'] / total_amount * 100) if total_amount > 0 else 0
                payment_data.append({
                    'payment_method': item['payment_method'],
                    'count': item['count'],
                    'total_amount': item['total_amount'],
                    'percentage': Decimal(str(round(percentage, 2)))
                })
            
            serializer = PaymentMethodStatsSerializer(payment_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting payment method stats: {str(e)}")
            return Response(
                {'error': 'Failed to load payment method statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def top_items(self, request):
        """Get top selling menu items"""
        try:
            days = int(request.query_params.get('days', 30))
            limit = int(request.query_params.get('limit', 10))
            start_date = timezone.now().date() - timedelta(days=days-1)
            
            from orders.models import OrderItem
            
            top_items = OrderItem.objects.filter(
                order__created_at__date__gte=start_date,
                order__status='completed'
            ).values(
                'menu_item__name',
                'menu_item__category'
            ).annotate(
                quantity_sold=Sum('quantity'),
                revenue=Sum(F('quantity') * F('price'))
            ).order_by('-quantity_sold')[:limit]
            
            top_items_data = []
            for item in top_items:
                top_items_data.append({
                    'item_name': item['menu_item__name'],
                    'category': item['menu_item__category'] or 'Uncategorized',
                    'quantity_sold': item['quantity_sold'],
                    'revenue': item['revenue']
                })
            
            serializer = TopItemsSerializer(top_items_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting top items: {str(e)}")
            return Response(
                {'error': 'Failed to load top items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def guest_stats(self, request):
        """Get guest and room statistics"""
        try:
            from guests.models import Guest
            
            # Room statistics (assuming room numbers 1-100)
            total_rooms = 100  # This should come from a Room model
            occupied_rooms = Guest.objects.filter(status='checked_in').count()
            available_rooms = total_rooms - occupied_rooms
            occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            
            today = timezone.now().date()
            
            # Today's activity
            checkins_today = Guest.objects.filter(
                check_in_time__date=today
            ).count()
            
            checkouts_today = Guest.objects.filter(
                check_out_time__date=today
            ).count()
            
            guest_stats_data = {
                'total_rooms': total_rooms,
                'occupied_rooms': occupied_rooms,
                'available_rooms': available_rooms,
                'occupancy_rate': Decimal(str(round(occupancy_rate, 2))),
                'checkins_today': checkins_today,
                'checkouts_today': checkouts_today,
                'expected_arrivals': 0,  # Would need reservation system
                'expected_departures': 0,  # Would need reservation system
                'total_feedback': 0
            }
            
            serializer = GuestStatsSerializer(guest_stats_data)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting guest stats: {str(e)}")
            return Response(
                {'error': 'Failed to load guest statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def service_requests_stats(self, request):
        """Get service request statistics"""
        try:
            from service_requests.models import ServiceRequest
            
            # Current status counts
            total_requests = ServiceRequest.objects.count()
            pending_requests = ServiceRequest.objects.filter(status='pending').count()
            in_progress_requests = ServiceRequest.objects.filter(status='in_progress').count()
            completed_requests = ServiceRequest.objects.filter(status='completed').count()
            
            # Performance metrics (simplified)
            avg_response_time = 15  # minutes - would be calculated from actual data
            avg_completion_time = 45  # minutes - would be calculated from actual data
            
            # By type breakdown
            by_type = list(ServiceRequest.objects.values('request_type').annotate(
                count=Count('id')
            ).order_by('-count'))
            
            service_stats_data = {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'in_progress_requests': in_progress_requests,
                'completed_requests': completed_requests,
                'average_response_time': avg_response_time,
                'average_completion_time': avg_completion_time,
                'by_type': by_type
            }
            
            serializer = ServiceRequestStatsSerializer(service_stats_data)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting service request stats: {str(e)}")
            return Response(
                {'error': 'Failed to load service request statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def inventory_stats(self, request):
        """Get inventory statistics"""
        try:
            from inventory.models import InventoryItem, StockMovement, WasteLog
            
            # Item counts
            total_items = InventoryItem.objects.count()
            low_stock_items = InventoryItem.objects.filter(
                current_stock__lte=F('minimum_stock')
            ).count()
            out_of_stock_items = InventoryItem.objects.filter(current_stock=0).count()
            overstocked_items = InventoryItem.objects.filter(
                current_stock__gte=F('maximum_stock')
            ).count()
            
            # Inventory values
            total_value = InventoryItem.objects.aggregate(
                total=Sum(F('current_stock') * F('unit_cost'))
            )['total'] or Decimal('0.00')
            
            low_stock_value = InventoryItem.objects.filter(
                current_stock__lte=F('minimum_stock')
            ).aggregate(
                total=Sum(F('current_stock') * F('unit_cost'))
            )['total'] or Decimal('0.00')
            
            # Today's activity
            today = timezone.now().date()
            
            items_received_today = StockMovement.objects.filter(
                created_at__date=today,
                movement_type='received'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            items_used_today = StockMovement.objects.filter(
                created_at__date=today,
                movement_type='used'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            waste_today = WasteLog.objects.filter(created_at__date=today)
            waste_items_today = waste_today.count()
            waste_value_today = waste_today.aggregate(
                total=Sum(F('quantity') * F('unit_cost'))
            )['total'] or Decimal('0.00')
            
            inventory_stats_data = {
                'total_items': total_items,
                'low_stock_items': low_stock_items,
                'out_of_stock_items': out_of_stock_items,
                'overstocked_items': overstocked_items,
                'total_inventory_value': total_value,
                'low_stock_value': low_stock_value,
                'items_received_today': items_received_today,
                'items_used_today': items_used_today,
                'waste_items_today': waste_items_today,
                'waste_value_today': waste_value_today,
                'pending_po_count': 0,  # Would come from purchase orders
                'pending_po_value': Decimal('0.00')
            }
            
            serializer = InventoryStatsSerializer(inventory_stats_data)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting inventory stats: {str(e)}")
            return Response(
                {'error': 'Failed to load inventory statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def realtime(self, request):
        """Get real-time dashboard statistics"""
        try:
            from orders.models import Order
            from service_requests.models import ServiceRequest
            from guests.models import Guest
            from tables.models import Table
            
            now = timezone.now()
            today = now.date()
            
            # Active metrics
            active_orders = Order.objects.filter(
                status__in=['pending', 'preparing', 'ready']
            ).count()
            
            orders_in_kitchen = Order.objects.filter(status='preparing').count()
            orders_ready = Order.objects.filter(status='ready').count()
            
            pending_service_requests = ServiceRequest.objects.filter(
                status='pending'
            ).count()
            
            urgent_service_requests = ServiceRequest.objects.filter(
                status='pending',
                priority='high'
            ).count()
            
            # Today's progress
            hours_into_day = now.hour
            
            today_orders = Order.objects.filter(created_at__date=today)
            revenue_so_far = today_orders.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            
            guests_checked_in = Guest.objects.filter(
                check_in_time__date=today
            ).count()
            
            # Capacity utilization
            total_tables = Table.objects.count()
            occupied_tables = Table.objects.filter(status='occupied').count()
            table_occupancy = (occupied_tables / total_tables * 100) if total_tables > 0 else 0
            
            total_rooms = 100  # Should come from Room model
            occupied_rooms = Guest.objects.filter(status='checked_in').count()
            room_occupancy = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            
            realtime_data = {
                'current_time': now,
                'active_orders': active_orders,
                'orders_in_kitchen': orders_in_kitchen,
                'orders_ready': orders_ready,
                'pending_service_requests': pending_service_requests,
                'hours_into_day': hours_into_day,
                'revenue_so_far': revenue_so_far,
                'orders_so_far': today_orders.count(),
                'guests_checked_in': guests_checked_in,
                'table_occupancy': Decimal(str(round(table_occupancy, 2))),
                'room_occupancy': Decimal(str(round(room_occupancy, 2))),
                'urgent_service_requests': urgent_service_requests,
                'overdue_orders': 0,  # Would need order timing logic
                'low_stock_alerts': 0  # Already calculated in inventory_stats
            }
            
            serializer = RealtimeStatsSerializer(realtime_data)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting realtime stats: {str(e)}")
            return Response(
                {'error': 'Failed to load real-time statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get system alerts and notifications"""
        try:
            alerts = []
            
            from inventory.models import InventoryItem
            from orders.models import Order
            from service_requests.models import ServiceRequest
            
            # Low stock alerts
            low_stock_items = InventoryItem.objects.filter(
                current_stock__lte=F('minimum_stock'),
                current_stock__gt=0
            )
            
            for item in low_stock_items:
                alerts.append({
                    'alert_type': 'inventory',
                    'priority': 'medium',
                    'title': 'Low Stock Alert',
                    'message': f'{item.name} is running low (Current: {item.current_stock}, Min: {item.minimum_stock})',
                    'created_at': timezone.now(),
                    'is_read': False,
                    'related_entity_type': 'inventory_item',
                    'related_entity_id': str(item.id),
                    'action_required': True
                })
            
            # Out of stock alerts
            out_of_stock_items = InventoryItem.objects.filter(current_stock=0)
            
            for item in out_of_stock_items:
                alerts.append({
                    'alert_type': 'inventory',
                    'priority': 'high',
                    'title': 'Out of Stock Alert',
                    'message': f'{item.name} is out of stock',
                    'created_at': timezone.now(),
                    'is_read': False,
                    'related_entity_type': 'inventory_item',
                    'related_entity_id': str(item.id),
                    'action_required': True
                })
            
            # Overdue service requests
            overdue_requests = ServiceRequest.objects.filter(
                status='pending',
                created_at__lt=timezone.now() - timedelta(hours=2)
            )
            
            for request in overdue_requests:
                alerts.append({
                    'alert_type': 'service',
                    'priority': 'high',
                    'title': 'Overdue Service Request',
                    'message': f'Service request #{request.id} has been pending for over 2 hours',
                    'created_at': timezone.now(),
                    'is_read': False,
                    'related_entity_type': 'service_request',
                    'related_entity_id': str(request.id),
                    'action_required': True
                })
            
            # Sort by priority and date
            priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            alerts.sort(
                key=lambda x: (priority_order.get(x['priority'], 0), x['created_at']),
                reverse=True
            )
            
            serializer = AlertsSerializer(alerts[:20], many=True)  # Limit to 20 alerts
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return Response(
                {'error': 'Failed to load alerts'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )