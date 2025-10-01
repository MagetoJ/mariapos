from rest_framework import serializers
from django.utils import timezone
from .models import Guest, GuestGroup, GuestPreference, GuestFeedback
from accounts.serializers import UserListSerializer

class GuestListSerializer(serializers.ModelSerializer):
    """Simplified guest serializer for list views"""
    
    full_name = serializers.CharField(read_only=True)
    stay_duration = serializers.IntegerField(read_only=True)
    assigned_staff_name = serializers.CharField(source='assigned_staff.name', read_only=True)
    
    class Meta:
        model = Guest
        fields = [
            'id', 'guest_number', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'room_number', 'status', 'guest_type',
            'expected_checkin', 'actual_checkin', 'expected_checkout',
            'actual_checkout', 'stay_duration', 'is_vip',
            'assigned_staff_name', 'created_at'
        ]
        read_only_fields = ['id', 'guest_number', 'created_at']

class GuestDetailSerializer(serializers.ModelSerializer):
    """Full guest serializer with all details"""
    
    full_name = serializers.CharField(read_only=True)
    stay_duration = serializers.IntegerField(read_only=True)
    assigned_staff_data = UserListSerializer(source='assigned_staff', read_only=True)
    
    class Meta:
        model = Guest
        fields = [
            'id', 'guest_number', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'address', 'city', 'country', 'postal_code',
            'id_type', 'id_number', 'guest_type', 'company', 'room_number',
            'status', 'expected_checkin', 'actual_checkin', 'expected_checkout',
            'actual_checkout', 'stay_duration', 'dietary_preferences',
            'special_requests', 'preferred_language', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'billing_address', 'payment_method', 'housekeeping_preferences',
            'minibar_access', 'marketing_consent', 'newsletter_subscription',
            'is_vip', 'loyalty_number', 'previous_stays', 'assigned_staff',
            'assigned_staff_data', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'guest_number', 'stay_duration', 'actual_checkin', 
            'actual_checkout', 'created_at', 'updated_at'
        ]

class GuestCreateSerializer(serializers.ModelSerializer):
    """Guest serializer for creation"""
    
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'city', 'country', 'postal_code', 'id_type', 'id_number',
            'guest_type', 'company', 'room_number', 'expected_checkin',
            'expected_checkout', 'dietary_preferences', 'special_requests',
            'preferred_language', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'billing_address', 'payment_method',
            'housekeeping_preferences', 'minibar_access', 'marketing_consent',
            'newsletter_subscription', 'is_vip', 'loyalty_number',
            'previous_stays', 'assigned_staff', 'notes'
        ]
    
    def validate_room_number(self, value):
        """Ensure room is not already occupied for the same period"""
        expected_checkin = self.initial_data.get('expected_checkin')
        expected_checkout = self.initial_data.get('expected_checkout')
        
        if expected_checkin and expected_checkout:
            # Check for overlapping bookings
            overlapping = Guest.objects.filter(
                room_number=value,
                status__in=['pending', 'checked_in'],
                expected_checkin__lt=expected_checkout,
                expected_checkout__gt=expected_checkin
            )
            
            # Exclude current instance if updating
            if self.instance:
                overlapping = overlapping.exclude(id=self.instance.id)
            
            if overlapping.exists():
                raise serializers.ValidationError(
                    f"Room {value} is not available for the selected dates"
                )
        
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        expected_checkin = data.get('expected_checkin')
        expected_checkout = data.get('expected_checkout')
        
        if expected_checkin and expected_checkout:
            if expected_checkout <= expected_checkin:
                raise serializers.ValidationError(
                    "Checkout date must be after checkin date"
                )
            
            # Don't allow checkin in the past
            if expected_checkin < timezone.now():
                raise serializers.ValidationError(
                    "Checkin date cannot be in the past"
                )
        
        return data

class GuestUpdateSerializer(serializers.ModelSerializer):
    """Guest serializer for updates (excluding some fields)"""
    
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'city', 'country', 'postal_code', 'guest_type', 'company',
            'dietary_preferences', 'special_requests', 'preferred_language',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'billing_address', 'payment_method',
            'housekeeping_preferences', 'minibar_access', 'marketing_consent',
            'newsletter_subscription', 'is_vip', 'loyalty_number',
            'previous_stays', 'assigned_staff', 'notes'
        ]

class CheckInSerializer(serializers.Serializer):
    """Serializer for guest check-in"""
    
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    create_user_account = serializers.BooleanField(default=True)
    
    def validate(self, data):
        guest = self.context['guest']
        
        if guest.status == 'checked_in':
            raise serializers.ValidationError("Guest is already checked in")
        
        if guest.status not in ['pending']:
            raise serializers.ValidationError(
                f"Cannot check in guest with status: {guest.status}"
            )
        
        return data

class CheckOutSerializer(serializers.Serializer):
    """Serializer for guest check-out"""
    
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    final_bill_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    
    def validate(self, data):
        guest = self.context['guest']
        
        if guest.status == 'checked_out':
            raise serializers.ValidationError("Guest is already checked out")
        
        if guest.status != 'checked_in':
            raise serializers.ValidationError(
                f"Cannot check out guest with status: {guest.status}"
            )
        
        return data

class GuestPreferenceSerializer(serializers.ModelSerializer):
    """Guest preference serializer"""
    
    class Meta:
        model = GuestPreference
        fields = [
            'id', 'category', 'preference_key', 'preference_value',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class GuestFeedbackSerializer(serializers.ModelSerializer):
    """Guest feedback serializer"""
    
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    guest_room = serializers.CharField(source='guest.room_number', read_only=True)
    responded_by_name = serializers.CharField(source='responded_by.name', read_only=True)
    
    class Meta:
        model = GuestFeedback
        fields = [
            'id', 'guest', 'guest_name', 'guest_room', 'category',
            'rating', 'comments', 'is_anonymous', 'is_public',
            'management_response', 'responded_by', 'responded_by_name',
            'responded_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'responded_by', 'responded_at', 'created_at'
        ]

class GuestFeedbackCreateSerializer(serializers.ModelSerializer):
    """Guest feedback creation serializer"""
    
    class Meta:
        model = GuestFeedback
        fields = [
            'guest', 'category', 'rating', 'comments',
            'is_anonymous', 'is_public'
        ]
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class GuestFeedbackResponseSerializer(serializers.ModelSerializer):
    """Serializer for management response to feedback"""
    
    class Meta:
        model = GuestFeedback
        fields = ['management_response']
    
    def validate_management_response(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Response cannot be empty")
        return value

class GuestGroupSerializer(serializers.ModelSerializer):
    """Guest group serializer"""
    
    group_leader_name = serializers.CharField(source='group_leader.full_name', read_only=True)
    group_leader_room = serializers.CharField(source='group_leader.room_number', read_only=True)
    
    class Meta:
        model = GuestGroup
        fields = [
            'id', 'group_name', 'group_leader', 'group_leader_name',
            'group_leader_room', 'total_guests', 'group_type',
            'group_rate_applied', 'group_discount_percent',
            'special_arrangements', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class GuestStatsSerializer(serializers.Serializer):
    """Serializer for guest statistics"""
    
    total_guests = serializers.IntegerField()
    checked_in_guests = serializers.IntegerField()
    pending_checkins = serializers.IntegerField()
    pending_checkouts = serializers.IntegerField()
    vip_guests = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    total_rooms = serializers.IntegerField()
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)

class RoomAvailabilitySerializer(serializers.Serializer):
    """Serializer for room availability check"""
    
    room_number = serializers.CharField(max_length=10)
    checkin_date = serializers.DateTimeField()
    checkout_date = serializers.DateTimeField()
    
    def validate(self, data):
        if data['checkout_date'] <= data['checkin_date']:
            raise serializers.ValidationError(
                "Checkout date must be after checkin date"
            )
        
        if data['checkin_date'] < timezone.now():
            raise serializers.ValidationError(
                "Checkin date cannot be in the past"
            )
        
        return data