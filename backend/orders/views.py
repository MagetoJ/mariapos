from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, OrderStatusUpdateSerializer
)

class OrderListCreateView(generics.ListCreateAPIView):
    """List and create orders"""
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        queryset = Order.objects.select_related(
            'customer', 'waiter', 'table'
        ).prefetch_related('items')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by order type
        order_type = self.request.query_params.get('type')
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        
        # Filter by waiter
        waiter_id = self.request.query_params.get('waiterId')
        if waiter_id:
            queryset = queryset.filter(waiter_id=waiter_id)
        
        # Filter by room number
        room_number = self.request.query_params.get('roomNumber')
        if room_number:
            queryset = queryset.filter(room_number=room_number)
        
        # Filter by date range
        start_date = self.request.query_params.get('startDate')
        end_date = self.request.query_params.get('endDate')
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__lte=end_date)
            except ValueError:
                pass
        
        # Filter by customer for guests
        if self.request.user.role == 'guest':
            queryset = queryset.filter(customer=self.request.user)
        
        # For waiters, show their own orders by default
        elif self.request.user.role == 'waiter' and not waiter_id:
            show_all = self.request.query_params.get('showAll', 'false').lower() == 'true'
            if not show_all:
                queryset = queryset.filter(waiter=self.request.user)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Set waiter to current user if waiter role
        if self.request.user.role == 'waiter':
            serializer.save(waiter=self.request.user)
        else:
            serializer.save()

class OrderDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update an order"""
    queryset = Order.objects.select_related(
        'customer', 'waiter', 'table'
    ).prefetch_related(
        'items__menu_item',
        'items__modifiers__modifier',
        'status_history__changed_by'
    )
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderUpdateSerializer
        return OrderDetailSerializer
    
    def get_queryset(self):
        # Guests can only view their own orders
        if self.request.user.role == 'guest':
            return super().get_queryset().filter(customer=self.request.user)
        
        # Waiters can view their own orders and orders they're assigned to
        elif self.request.user.role == 'waiter':
            return super().get_queryset().filter(
                Q(waiter=self.request.user) | Q(customer=self.request.user)
            )
        
        return super().get_queryset()

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, pk):
    """Update order status with history tracking"""
    try:
        order = Order.objects.get(pk=pk)
        
        # Permission check
        if request.user.role == 'guest' and order.customer != request.user:
            return Response(
                {"error": "You can only update your own orders"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderStatusUpdateSerializer(
            data=request.data, 
            context={'order': order, 'request': request}
        )
        
        if serializer.is_valid():
            old_status = order.status
            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            
            # Update order status
            order.status = new_status
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                changed_by=request.user,
                notes=notes or f"Status changed from {old_status} to {new_status}"
            )
            
            return Response(OrderDetailSerializer(order).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, pk):
    """Cancel an order"""
    try:
        order = Order.objects.get(pk=pk)
        
        # Permission check
        if request.user.role == 'guest' and order.customer != request.user:
            return Response(
                {"error": "You can only cancel your own orders"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Business logic check
        if order.status in ['completed', 'cancelled']:
            return Response(
                {"error": f"Cannot cancel {order.status} order"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel order
        order.status = 'cancelled'
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            changed_by=request.user,
            notes=request.data.get('reason', 'Order cancelled by user')
        )
        
        return Response(OrderDetailSerializer(order).data)
    
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_kitchen_orders(request):
    """Get orders for kitchen display"""
    if request.user.role not in ['admin', 'manager', 'kitchen']:
        return Response(
            {"error": "Only kitchen staff can access kitchen orders"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get orders that are pending or preparing
    orders = Order.objects.filter(
        status__in=['pending', 'preparing']
    ).select_related(
        'customer', 'waiter', 'table'
    ).prefetch_related(
        'items__menu_item',
        'items__modifiers__modifier'
    ).order_by('created_at')
    
    serializer = OrderDetailSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_waiter_orders(request, waiter_id=None):
    """Get orders for a specific waiter"""
    if request.user.role == 'waiter':
        # Waiters can only see their own orders
        waiter_id = request.user.id
    elif waiter_id is None:
        waiter_id = request.user.id
    
    orders = Order.objects.filter(
        waiter_id=waiter_id
    ).select_related(
        'customer', 'waiter', 'table'
    ).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by today if requested
    today_only = request.query_params.get('todayOnly', 'false').lower() == 'true'
    if today_only:
        today = timezone.now().date()
        orders = orders.filter(created_at__date=today)
    
    serializer = OrderListSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_room_service_orders(request):
    """Get room service orders"""
    if request.user.role not in ['admin', 'manager', 'receptionist', 'waiter']:
        return Response(
            {"error": "Access denied"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    orders = Order.objects.filter(
        order_type='room_service'
    ).select_related(
        'customer', 'waiter'
    ).order_by('-created_at')
    
    # Filter by status
    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by room number
    room_number = request.query_params.get('roomNumber')
    if room_number:
        orders = orders.filter(room_number=room_number)
    
    serializer = OrderListSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_order_statistics(request):
    """Get order statistics"""
    if request.user.role not in ['admin', 'manager']:
        return Response(
            {"error": "Only admin and manager can view statistics"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get date range
    days = int(request.query_params.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    orders = Order.objects.filter(created_at__gte=start_date)
    
    # Count by status
    status_counts = orders.values('status').annotate(count=Count('id'))
    
    # Count by type
    type_counts = orders.values('order_type').annotate(count=Count('id'))
    
    # Daily counts
    daily_counts = []
    for i in range(days):
        date = (timezone.now() - timedelta(days=i)).date()
        count = orders.filter(created_at__date=date).count()
        daily_counts.append({
            'date': date.isoformat(),
            'count': count
        })
    
    return Response({
        'total_orders': orders.count(),
        'status_breakdown': list(status_counts),
        'type_breakdown': list(type_counts),
        'daily_counts': daily_counts
    })