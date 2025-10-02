from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Order, OrderItem, OrderItemModifier, OrderStatusHistory
from menu.models import MenuItem, MenuItemModifier
# CORRECTED: Use MenuItemSerializer instead of MenuItemListSerializer
from menu.serializers import MenuItemSerializer
from accounts.serializers import UserListSerializer

User = get_user_model()

class OrderItemModifierSerializer(serializers.ModelSerializer):
    """Order item modifier serializer"""
    
    modifier_name = serializers.CharField(source='modifier.name', read_only=True)
    
    class Meta:
        model = OrderItemModifier
        fields = ['id', 'modifier', 'modifier_name', 'price']
        read_only_fields = ['id']

class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    # CORRECTED: Use MenuItemSerializer instead of MenuItemListSerializer
    menu_item_data = MenuItemSerializer(source='menu_item', read_only=True)
    modifiers = OrderItemModifierSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'menu_item_name', 'menu_item_data',
            'quantity', 'unit_price', 'special_instructions',
            'modifiers', 'total_price'
        ]
        read_only_fields = ['id', 'total_price']

class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Order item serializer for create operations"""
    
    modifiers = serializers.ListField(
        child=serializers.DictField(
            # CORRECTED: Use a more specific child validator for better data handling
            child=serializers.CharField()
        ),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'special_instructions', 'modifiers']
    
    def validate_menu_item(self, value):
        if not value.is_available:
            raise serializers.ValidationError("This menu item is not available")
        return value
    
    def validate_modifiers(self, modifiers_data):
        """Validate modifier data"""
        validated_modifiers = []
        for modifier_data in modifiers_data:
            modifier_id = modifier_data.get('modifier_id')
            if not modifier_id:
                raise serializers.ValidationError("modifier_id is required for each modifier")
            
            try:
                modifier = MenuItemModifier.objects.get(id=modifier_id)
                # CORRECTED: Use the correct field name 'is_available'
                if not modifier.is_available:
                    raise serializers.ValidationError(f"Modifier {modifier.name} is not available")
                validated_modifiers.append({
                    'modifier': modifier,
                    'price': modifier.price
                })
            except MenuItemModifier.DoesNotExist:
                raise serializers.ValidationError(f"Modifier with id {modifier_id} does not exist")
        
        return validated_modifiers

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Order status history serializer"""
    
    changed_by_name = serializers.CharField(source='changed_by.name', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'changed_by', 'changed_by_name', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class OrderListSerializer(serializers.ModelSerializer):
    """Order serializer for list views"""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    waiter_name = serializers.CharField(source='waiter.name', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'waiter', 'waiter_name', 'table_number',
            'room_number', 'type', 'status', 'total_amount',
            'items_count', 'special_instructions', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']
    
    def get_items_count(self, obj):
        return obj.items.count()

class OrderDetailSerializer(serializers.ModelSerializer):
    """Order serializer for detail views"""
    
    # CORRECTED: UserListSerializer is correctly referenced here
    customer_data = UserListSerializer(source='customer', read_only=True)
    waiter_data = UserListSerializer(source='waiter', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_data',
            'waiter', 'waiter_data', 'table_number',
            'room_number', 'type', 'status', 'subtotal',
            'tax_amount', 'total_amount', 'payment_status',
            'special_instructions', 'items', 'status_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax_amount', 
            'total_amount', 'created_at', 'updated_at'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    """Order serializer for create operations"""
    
    items = OrderItemCreateSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'customer', 'waiter', 'table_number', 'room_number',
            'type', 'special_instructions', 'items'
        ]
    
    def validate_items(self, items_data):
        if not items_data:
            raise serializers.ValidationError("Order must have at least one item")
        return items_data
    
    def validate(self, attrs):
        order_type = attrs.get('type')
        table_number = attrs.get('table_number')
        room_number = attrs.get('room_number')
        
        if order_type == 'dine_in' and not table_number:
            raise serializers.ValidationError("Table number is required for dine-in orders")
        
        if order_type == 'room_service' and not room_number:
            raise serializers.ValidationError("Room number is required for room service orders")
        
        return attrs
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Create order without calculating totals initially
        order = Order(**validated_data)
        order.save(skip_calculate_totals=True)
        
        for item_data in items_data:
            modifiers_data = item_data.pop('modifiers', [])
            
            order_item = OrderItem.objects.create(
                order=order,
                unit_price=item_data['menu_item'].price,
                **item_data
            )
            
            # Create modifiers
            for modifier_data in modifiers_data:
                OrderItemModifier.objects.create(
                    order_item=order_item,
                    **modifier_data
                )
        
        # Now calculate totals and save again
        order.calculate_totals()
        order.save()
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    """Order serializer for update operations"""
    
    class Meta:
        model = Order
        fields = ['status', 'special_instructions', 'payment_status']
    
    def validate_status(self, value):
        # Business logic for status transitions
        current_status = self.instance.status if self.instance else None
        
        if current_status == 'completed' and value != 'completed':
            raise serializers.ValidationError("Cannot change status of completed order")
        
        if current_status == 'cancelled' and value != 'cancelled':
            raise serializers.ValidationError("Cannot change status of cancelled order")
        
        return value
    
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # Update order
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Create status history entry if status changed
        if old_status != new_status:
            OrderStatusHistory.objects.create(
                order=instance,
                status=new_status,
                changed_by=self.context['request'].user,
                notes=f"Status changed from {old_status} to {new_status}"
            )
        
        return instance

class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_status(self, value):
        order = self.context.get('order')
        if not order:
            return value
        
        # Business logic for status transitions
        if order.status == 'completed' and value != 'completed':
            raise serializers.ValidationError("Cannot change status of completed order")
        
        if order.status == 'cancelled' and value != 'cancelled':
            raise serializers.ValidationError("Cannot change status of cancelled order")
        
        return value
        