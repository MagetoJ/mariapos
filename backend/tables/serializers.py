from rest_framework import serializers
from django.utils import timezone
from .models import Table, TableReservation, TableLayout
from accounts.serializers import UserListSerializer

class TableSerializer(serializers.ModelSerializer):
    """Table serializer"""
    
    current_order_id = serializers.UUIDField(source='current_order.id', read_only=True)
    current_order_number = serializers.CharField(source='current_order.order_number', read_only=True)
    waiter_name = serializers.CharField(source='assigned_waiter.name', read_only=True)
    
    class Meta:
        model = Table
        fields = [
            'id', 'number', 'capacity', 'status', 'section',
            'assigned_waiter', 'waiter_name', 'current_order_id', 'current_order_number',
            'position_x', 'position_y', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TableListSerializer(serializers.ModelSerializer):
    """Simplified table serializer for list views"""
    
    waiter_name = serializers.CharField(source='assigned_waiter.name', read_only=True)
    has_active_order = serializers.SerializerMethodField()
    
    class Meta:
        model = Table
        fields = [
            'id', 'number', 'capacity', 'status', 'section',
            'assigned_waiter', 'waiter_name', 'has_active_order'
        ]
        read_only_fields = ['id']
    
    def get_has_active_order(self, obj):
        return obj.current_order is not None

class TableStatusUpdateSerializer(serializers.ModelSerializer):
    """Table serializer for status updates"""
    
    class Meta:
        model = Table
        fields = ['status', 'assigned_waiter']
    
    def validate_status(self, value):
        # Business logic for status transitions
        if self.instance and self.instance.status == 'occupied' and value != 'occupied':
            if self.instance.current_order and self.instance.current_order.status not in ['completed', 'cancelled']:
                raise serializers.ValidationError("Cannot change status while table has an active order")
        return value

class TableReservationSerializer(serializers.ModelSerializer):
    """Table reservation serializer"""
    
    guest_name = serializers.CharField(source='guest.name', read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    
    class Meta:
        model = TableReservation
        fields = [
            'id', 'table', 'table_number', 'guest', 'guest_name',
            'reservation_time', 'party_size', 'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_reservation_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Reservation time cannot be in the past")
        return value
    
    def validate(self, attrs):
        table = attrs.get('table')
        party_size = attrs.get('party_size')
        
        if table and party_size and party_size > table.capacity:
            raise serializers.ValidationError(f"Party size ({party_size}) exceeds table capacity ({table.capacity})")
        
        return attrs

class TableLayoutSerializer(serializers.ModelSerializer):
    """Table layout serializer"""
    
    class Meta:
        model = TableLayout
        fields = [
            'id', 'name', 'description', 'is_active',
            'layout_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TableAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning waiter to table"""
    
    waiter = serializers.UUIDField()
    
    def validate_waiter(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=value)
            if user.role != 'waiter':
                raise serializers.ValidationError("Only waiter users can be assigned to tables")
            if not user.is_active:
                raise serializers.ValidationError("Cannot assign inactive waiter")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Waiter not found")

class TableOccupancySerializer(serializers.Serializer):
    """Serializer for table occupancy operations"""
    
    guest_count = serializers.IntegerField(min_value=1)
    waiter = serializers.UUIDField(required=False)
    
    def validate_guest_count(self, value):
        table = self.context.get('table')
        if table and value > table.capacity:
            raise serializers.ValidationError(f"Guest count ({value}) exceeds table capacity ({table.capacity})")
        return value