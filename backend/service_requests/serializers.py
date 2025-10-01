from rest_framework import serializers
from django.utils import timezone
from .models import (
    ServiceRequest, ServiceRequestUpdate, ServiceRequestTemplate, ServiceMetrics
)
from accounts.serializers import UserListSerializer
from guests.serializers import GuestListSerializer

class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Simplified service request serializer for list views"""
    
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    response_time = serializers.IntegerField(read_only=True)
    resolution_time = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'request_number', 'guest', 'guest_name', 'type',
            'priority', 'status', 'title', 'room_number', 'assigned_to',
            'assigned_to_name', 'department', 'requested_at',
            'estimated_completion', 'response_time', 'resolution_time',
            'is_overdue', 'guest_satisfaction'
        ]
        read_only_fields = ['id', 'request_number', 'requested_at']

class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    """Full service request serializer with all details"""
    
    guest_data = GuestListSerializer(source='guest', read_only=True)
    assigned_to_data = UserListSerializer(source='assigned_to', read_only=True)
    response_time = serializers.IntegerField(read_only=True)
    resolution_time = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'request_number', 'guest', 'guest_data', 'type',
            'priority', 'status', 'title', 'description', 'room_number',
            'assigned_to', 'assigned_to_data', 'department', 'requested_at',
            'acknowledged_at', 'started_at', 'completed_at',
            'estimated_completion', 'estimated_cost', 'actual_cost',
            'guest_notified', 'guest_phone', 'resolution_notes',
            'guest_satisfaction', 'requires_followup', 'followup_date',
            'followup_notes', 'response_time', 'resolution_time',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'request_number', 'requested_at', 'acknowledged_at',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        ]

class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """Service request serializer for creation"""
    
    class Meta:
        model = ServiceRequest
        fields = [
            'guest', 'type', 'priority', 'title', 'description',
            'room_number', 'department', 'estimated_completion',
            'estimated_cost', 'guest_phone', 'requires_followup',
            'followup_date', 'followup_notes'
        ]
    
    def validate_room_number(self, value):
        """Validate room number matches guest's room"""
        guest = self.initial_data.get('guest')
        if guest:
            # In a real system, you'd verify the room number matches the guest
            pass
        return value
    
    def validate_estimated_completion(self, value):
        """Ensure estimated completion is in the future"""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Estimated completion must be in the future"
            )
        return value

class ServiceRequestUpdateSerializer(serializers.ModelSerializer):
    """Service request serializer for updates"""
    
    class Meta:
        model = ServiceRequest
        fields = [
            'priority', 'title', 'description', 'assigned_to',
            'department', 'estimated_completion', 'estimated_cost',
            'actual_cost', 'guest_notified', 'guest_phone',
            'resolution_notes', 'guest_satisfaction', 'requires_followup',
            'followup_date', 'followup_notes'
        ]

class ServiceRequestAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for assigning service requests"""
    
    class Meta:
        model = ServiceRequest
        fields = ['assigned_to', 'department', 'estimated_completion']
    
    def validate_assigned_to(self, value):
        """Ensure assigned staff member has appropriate role"""
        if value and value.role not in ['admin', 'manager', 'receptionist', 'waiter', 'kitchen']:
            raise serializers.ValidationError(
                "Assigned staff member must have appropriate role"
            )
        return value

class ServiceRequestStatusUpdateSerializer(serializers.Serializer):
    """Serializer for status updates"""
    
    status = serializers.ChoiceField(choices=ServiceRequest.STATUS_CHOICES)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    actual_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    guest_satisfaction = serializers.IntegerField(
        min_value=1, max_value=5, required=False
    )
    
    def validate_status(self, value):
        """Validate status transition"""
        request = self.context.get('request_obj')
        if not request:
            return value
        
        current_status = request.status
        valid_transitions = {
            'pending': ['acknowledged', 'cancelled'],
            'acknowledged': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}"
            )
        
        return value

class ServiceRequestUpdateRecordSerializer(serializers.ModelSerializer):
    """Service request update record serializer"""
    
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    service_request_number = serializers.CharField(
        source='service_request.request_number', read_only=True
    )
    
    class Meta:
        model = ServiceRequestUpdate
        fields = [
            'id', 'service_request', 'service_request_number',
            'update_type', 'message', 'created_by', 'created_by_name',
            'communicated_to_guest', 'guest_response', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ServiceRequestUpdateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating service request updates"""
    
    class Meta:
        model = ServiceRequestUpdate
        fields = [
            'update_type', 'message', 'communicated_to_guest', 'guest_response'
        ]

class ServiceRequestTemplateSerializer(serializers.ModelSerializer):
    """Service request template serializer"""
    
    class Meta:
        model = ServiceRequestTemplate
        fields = [
            'id', 'name', 'type', 'department', 'title_template',
            'description_template', 'default_priority',
            'estimated_duration_minutes', 'estimated_cost',
            'is_active', 'is_guest_selectable', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ServiceRequestFromTemplateSerializer(serializers.Serializer):
    """Serializer for creating service requests from templates"""
    
    template = serializers.UUIDField()
    guest = serializers.UUIDField()
    room_number = serializers.CharField(max_length=10)
    custom_description = serializers.CharField(
        max_length=1000, required=False, allow_blank=True
    )
    priority_override = serializers.ChoiceField(
        choices=ServiceRequest.PRIORITY_CHOICES, required=False
    )
    
    def validate_template(self, value):
        """Validate template exists and is active"""
        try:
            template = ServiceRequestTemplate.objects.get(id=value, is_active=True)
        except ServiceRequestTemplate.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive template")
        return value

class ServiceMetricsSerializer(serializers.ModelSerializer):
    """Service metrics serializer"""
    
    completion_rate = serializers.SerializerMethodField()
    cancellation_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceMetrics
        fields = [
            'id', 'date', 'department', 'total_requests',
            'completed_requests', 'cancelled_requests', 'overdue_requests',
            'completion_rate', 'cancellation_rate', 'avg_response_time',
            'avg_resolution_time', 'avg_satisfaction',
            'total_satisfaction_responses', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_completion_rate(self, obj):
        """Calculate completion rate percentage"""
        if obj.total_requests > 0:
            return round((obj.completed_requests / obj.total_requests) * 100, 2)
        return 0
    
    def get_cancellation_rate(self, obj):
        """Calculate cancellation rate percentage"""
        if obj.total_requests > 0:
            return round((obj.cancelled_requests / obj.total_requests) * 100, 2)
        return 0

class ServiceDashboardSerializer(serializers.Serializer):
    """Serializer for service dashboard statistics"""
    
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    in_progress_requests = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    overdue_requests = serializers.IntegerField()
    avg_response_time = serializers.DecimalField(max_digits=8, decimal_places=2)
    avg_satisfaction = serializers.DecimalField(max_digits=3, decimal_places=2)
    high_priority_pending = serializers.IntegerField()
    urgent_requests = serializers.IntegerField()
    
    # Department breakdown
    department_stats = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    
    # Request type distribution
    type_distribution = serializers.ListField(
        child=serializers.DictField(), required=False
    )

class ServiceRequestNotificationSerializer(serializers.Serializer):
    """Serializer for service request notifications"""
    
    request_id = serializers.UUIDField()
    guest_id = serializers.UUIDField()
    message = serializers.CharField(max_length=500)
    notification_type = serializers.ChoiceField(
        choices=[
            ('sms', 'SMS'),
            ('email', 'Email'),
            ('in_app', 'In-App'),
            ('phone', 'Phone Call'),
        ]
    )
    send_immediately = serializers.BooleanField(default=True)

class GuestSatisfactionSerializer(serializers.Serializer):
    """Serializer for guest satisfaction feedback"""
    
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    would_recommend = serializers.BooleanField(required=False)
    
    def validate_rating(self, value):
        """Ensure rating is within valid range"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value