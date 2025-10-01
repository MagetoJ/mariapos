from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q, F, Sum
from django.utils import timezone
from decimal import Decimal

from accounts.permissions import (
    IsManagerOrAdmin, IsStaffMember, IsManagerAdminOrInventoryStaff
)
from .models import (
    InventoryItem, StockMovement, PurchaseOrder, PurchaseOrderItem,
    Supplier, WasteLog
)
from .serializers import (
    InventoryItemSerializer, InventoryItemListSerializer,
    InventoryItemCreateUpdateSerializer, StockMovementSerializer,
    PurchaseOrderSerializer, PurchaseOrderCreateSerializer,
    SupplierSerializer, WasteLogSerializer, StockAdjustmentSerializer,
    BulkStockUpdateSerializer, LowStockReportSerializer
)

class InventoryItemViewSet(ModelViewSet):
    """
    ViewSet for managing inventory items
    """
    queryset = InventoryItem.objects.all().select_related('supplier')
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InventoryItemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InventoryItemCreateUpdateSerializer
        return InventoryItemSerializer
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerAdminOrInventoryStaff]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by low stock
        low_stock = self.request.query_params.get('low_stock')
        if low_stock and low_stock.lower() == 'true':
            queryset = queryset.filter(current_stock__lte=F('reorder_point'))
        
        # Filter by supplier
        supplier = self.request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def low_stock(self, request):
        """Get items with low stock"""
        low_stock_items = self.get_queryset().filter(
            current_stock__lte=F('reorder_point')
        ).select_related('supplier')
        
        serializer = InventoryItemListSerializer(low_stock_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def categories(self, request):
        """Get available categories"""
        categories = InventoryItem.objects.values_list(
            'category', flat=True
        ).distinct().order_by('category')
        
        return Response(list(categories))
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def stock_summary(self, request):
        """Get inventory stock summary"""
        total_items = self.get_queryset().count()
        low_stock_count = self.get_queryset().filter(
            current_stock__lte=F('reorder_point')
        ).count()
        
        total_value = self.get_queryset().aggregate(
            total_value=Sum(F('current_stock') * F('unit_cost'))
        )['total_value'] or Decimal('0.00')
        
        return Response({
            'total_items': total_items,
            'low_stock_items': low_stock_count,
            'total_value': total_value
        })
    
    @action(detail=True, methods=['post'], 
           permission_classes=[permissions.IsAuthenticated, IsManagerAdminOrInventoryStaff])
    def adjust_stock(self, request, pk=None):
        """Adjust stock for an item"""
        item = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            reason = serializer.validated_data['reason']
            unit_cost = serializer.validated_data.get('unit_cost', item.unit_cost)
            
            with transaction.atomic():
                # Update stock
                old_stock = item.current_stock
                item.current_stock += quantity
                
                if item.current_stock < 0:
                    return Response(
                        {'error': 'Insufficient stock for adjustment'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                item.save()
                
                # Create stock movement
                movement_type = 'IN' if quantity > 0 else 'OUT'
                StockMovement.objects.create(
                    item=item,
                    movement_type=movement_type,
                    quantity=abs(quantity),
                    unit_cost=unit_cost,
                    reason=reason,
                    performed_by=request.user
                )
            
            return Response({
                'message': 'Stock adjusted successfully',
                'old_stock': old_stock,
                'new_stock': item.current_stock,
                'adjustment': quantity
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockMovementViewSet(ModelViewSet):
    """ViewSet for stock movements (read-only)"""
    
    queryset = StockMovement.objects.all().select_related('item', 'performed_by')
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    http_method_names = ['get']  # Read-only
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by item
        item = self.request.query_params.get('item')
        if item:
            queryset = queryset.filter(item_id=item)
        
        # Filter by movement type
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.order_by('-created_at')

class SupplierViewSet(ModelViewSet):
    """ViewSet for managing suppliers"""
    
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerAdminOrInventoryStaff]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('name')

class PurchaseOrderViewSet(ModelViewSet):
    """ViewSet for managing purchase orders"""
    
    queryset = PurchaseOrder.objects.all().select_related(
        'supplier', 'created_by'
    ).prefetch_related('items__item')
    permission_classes = [permissions.IsAuthenticated, IsManagerAdminOrInventoryStaff]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by supplier
        supplier = self.request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Mark purchase order as received and update stock"""
        purchase_order = self.get_object()
        
        if purchase_order.status != 'PENDING':
            return Response(
                {'error': 'Only pending orders can be received'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Update order status
            purchase_order.status = 'RECEIVED'
            purchase_order.actual_delivery = timezone.now().date()
            purchase_order.save()
            
            # Update stock for each item
            for po_item in purchase_order.items.all():
                item = po_item.item
                old_stock = item.current_stock
                item.current_stock += po_item.quantity
                item.save()
                
                # Create stock movement
                StockMovement.objects.create(
                    item=item,
                    movement_type='IN',
                    quantity=po_item.quantity,
                    unit_cost=po_item.unit_cost,
                    reason=f'Purchase Order #{purchase_order.order_number}',
                    reference_number=purchase_order.order_number,
                    performed_by=request.user
                )
        
        return Response({'message': 'Purchase order received successfully'})

class WasteLogViewSet(ModelViewSet):
    """ViewSet for waste tracking"""
    
    queryset = WasteLog.objects.all().select_related('item', 'reported_by')
    serializer_class = WasteLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerAdminOrInventoryStaff]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by item
        item = self.request.query_params.get('item')
        if item:
            queryset = queryset.filter(item_id=item)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

class BulkStockUpdateView(APIView):
    """View for bulk stock updates"""
    
    permission_classes = [permissions.IsAuthenticated, IsManagerAdminOrInventoryStaff]
    
    def post(self, request):
        serializer = BulkStockUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            updates = serializer.validated_data['updates']
            results = []
            
            with transaction.atomic():
                for update in updates:
                    try:
                        item = InventoryItem.objects.get(id=update['item_id'])
                        old_stock = item.current_stock
                        
                        # Apply adjustment
                        item.current_stock += update['quantity']
                        
                        if item.current_stock < 0:
                            results.append({
                                'item_id': update['item_id'],
                                'success': False,
                                'error': 'Would result in negative stock'
                            })
                            continue
                        
                        item.save()
                        
                        # Create stock movement
                        movement_type = 'IN' if update['quantity'] > 0 else 'OUT'
                        StockMovement.objects.create(
                            item=item,
                            movement_type=movement_type,
                            quantity=abs(update['quantity']),
                            unit_cost=item.unit_cost,
                            reason=update['reason'],
                            performed_by=request.user
                        )
                        
                        results.append({
                            'item_id': update['item_id'],
                            'success': True,
                            'old_stock': old_stock,
                            'new_stock': item.current_stock,
                            'adjustment': update['quantity']
                        })
                    
                    except InventoryItem.DoesNotExist:
                        results.append({
                            'item_id': update['item_id'],
                            'success': False,
                            'error': 'Item not found'
                        })
            
            return Response({
                'message': 'Bulk update completed',
                'results': results
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WasteTrackingView(APIView):
    """View for tracking waste"""
    
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def post(self, request):
        """Track waste for an item"""
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        reason = request.data.get('reason')
        
        if not all([item_id, quantity, reason]):
            return Response(
                {'error': 'item_id, quantity, and reason are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = Decimal(str(quantity))
            if quantity <= 0:
                return Response(
                    {'error': 'Quantity must be greater than zero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = InventoryItem.objects.get(id=item_id)
        except InventoryItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if quantity > item.current_stock:
            return Response(
                {'error': 'Cannot waste more than available stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Reduce stock
            item.current_stock -= quantity
            item.save()
            
            # Log waste
            waste_log = WasteLog.objects.create(
                item=item,
                quantity=quantity,
                reason=reason,
                unit_cost=item.unit_cost,
                reported_by=request.user
            )
            
            # Create stock movement
            StockMovement.objects.create(
                item=item,
                movement_type='OUT',
                quantity=quantity,
                unit_cost=item.unit_cost,
                reason=f'Waste: {reason}',
                performed_by=request.user
            )
        
        serializer = WasteLogSerializer(waste_log)
        return Response({
            'message': 'Waste tracked successfully',
            'waste_log': serializer.data
        }, status=status.HTTP_201_CREATED)