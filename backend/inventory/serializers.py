from rest_framework import serializers
from decimal import Decimal
from .models import (
    InventoryItem, StockMovement, PurchaseOrder, PurchaseOrderItem,
    Supplier, WasteLog
)
from accounts.serializers import UserListSerializer

class SupplierSerializer(serializers.ModelSerializer):
    """Supplier serializer"""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone',
            'address', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class InventoryItemListSerializer(serializers.ModelSerializer):
    """Simplified inventory item serializer for list views"""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'category', 'sku', 'current_stock',
            'reorder_point', 'unit', 'unit_cost', 'supplier',
            'supplier_name', 'is_low_stock', 'stock_value', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_is_low_stock(self, obj):
        return obj.current_stock <= obj.reorder_point
    
    def get_stock_value(self, obj):
        return obj.current_stock * obj.unit_cost

class InventoryItemSerializer(serializers.ModelSerializer):
    """Full inventory item serializer"""
    
    supplier_data = SupplierSerializer(source='supplier', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'category', 'sku',
            'current_stock', 'reorder_point', 'max_stock',
            'unit', 'unit_cost', 'supplier', 'supplier_data',
            'is_low_stock', 'stock_value', 'expiry_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_low_stock(self, obj):
        return obj.current_stock <= obj.reorder_point
    
    def get_stock_value(self, obj):
        return obj.current_stock * obj.unit_cost

class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Inventory item serializer for create/update operations"""
    
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'description', 'category', 'sku',
            'current_stock', 'reorder_point', 'max_stock',
            'unit', 'unit_cost', 'supplier', 'expiry_date'
        ]
    
    def validate_current_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
    
    def validate_unit_cost(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit cost must be greater than zero")
        return value

class StockMovementSerializer(serializers.ModelSerializer):
    """Stock movement serializer"""
    
    item_name = serializers.CharField(source='item.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_name', 'movement_type', 'quantity',
            'unit_cost', 'total_cost', 'reason', 'reference_number',
            'performed_by', 'performed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'total_cost', 'created_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value

class WasteLogSerializer(serializers.ModelSerializer):
    """Waste log serializer"""
    
    item_name = serializers.CharField(source='item.name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.name', read_only=True)
    waste_value = serializers.SerializerMethodField()
    
    class Meta:
        model = WasteLog
        fields = [
            'id', 'item', 'item_name', 'quantity', 'reason',
            'unit_cost', 'waste_value', 'reported_by',
            'reported_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'unit_cost', 'created_at']
    
    def get_waste_value(self, obj):
        return obj.quantity * obj.unit_cost

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Purchase order item serializer"""
    
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'item', 'item_name', 'quantity',
            'unit_cost', 'total_cost'
        ]
        read_only_fields = ['id', 'total_cost']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Purchase order serializer"""
    
    supplier_data = SupplierSerializer(source='supplier', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'supplier_data',
            'status', 'total_amount', 'created_by', 'created_by_name',
            'order_date', 'expected_delivery', 'actual_delivery',
            'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'total_amount', 
            'created_at', 'updated_at'
        ]

class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """Purchase order serializer for create operations"""
    
    items = PurchaseOrderItemSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'expected_delivery', 'notes', 'items'
        ]
    
    def validate_items(self, items_data):
        if not items_data:
            raise serializers.ValidationError("Purchase order must have at least one item")
        return items_data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                **item_data
            )
        
        # Calculate total amount
        purchase_order.calculate_total()
        return purchase_order

class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for stock adjustments"""
    
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(max_length=200)
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Quantity cannot be zero")
        return value

class BulkStockUpdateSerializer(serializers.Serializer):
    """Serializer for bulk stock updates"""
    
    updates = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    def validate_updates(self, updates_data):
        validated_updates = []
        for update in updates_data:
            item_id = update.get('item_id')
            quantity = update.get('quantity')
            reason = update.get('reason', 'Bulk update')
            
            if not item_id:
                raise serializers.ValidationError("item_id is required for each update")
            
            if quantity is None:
                raise serializers.ValidationError("quantity is required for each update")
            
            try:
                quantity = Decimal(str(quantity))
                if quantity == 0:
                    raise serializers.ValidationError("Quantity cannot be zero")
                    
                # Verify item exists
                InventoryItem.objects.get(id=item_id)
                
                validated_updates.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'reason': reason
                })
            except (ValueError, TypeError):
                raise serializers.ValidationError("Invalid quantity value")
            except InventoryItem.DoesNotExist:
                raise serializers.ValidationError(f"Item with id {item_id} does not exist")
        
        return validated_updates

class LowStockReportSerializer(serializers.Serializer):
    """Serializer for low stock report"""
    
    item_id = serializers.UUIDField()
    item_name = serializers.CharField()
    current_stock = serializers.DecimalField(max_digits=10, decimal_places=2)
    reorder_point = serializers.DecimalField(max_digits=10, decimal_places=2)
    supplier_name = serializers.CharField()
    category = serializers.CharField()
    
    class Meta:
        fields = [
            'item_id', 'item_name', 'current_stock', 
            'reorder_point', 'supplier_name', 'category'
        ]