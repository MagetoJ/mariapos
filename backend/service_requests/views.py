from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta

from accounts.permissions import IsManagerOrAdmin, IsStaffMember, IsReceptionistOrAbove
from .models import (
    ServiceRequest, ServiceRequestUpdate, ServiceRequestTemplate, ServiceMetrics
)
from .serializers import (
    ServiceRequestListSerializer, ServiceRequestDetailSerializer,
    ServiceRequestCreateSerializer, ServiceRequestUpdateSerializer,
    ServiceRequestAssignmentSerializer, ServiceRequestStatusUpdateSerializer,
    ServiceRequestUpdateRecordSerializer, ServiceRequestUpdateCreateSerializer,
    ServiceRequestTemplateSerializer, ServiceRequestFromTemplateSerializer,
    ServiceMetricsSerializer, ServiceDashboardSerializer,
    ServiceRequestNotificationSerializer, GuestSatisfactionSerializer
)

class ServiceRequestViewSet(ModelViewSet):
    """
    ViewSet for managing service requests
    """
    queryset = ServiceRequest.objects.all().select_related(
        'guest', 'assigned_to'
    ).prefetch_related('updates')
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceRequestListSerializer
        elif self.action == 'create':
            return ServiceRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ServiceRequestUpdateSerializer
        elif self.action == 'assign':
            return ServiceRequestAssignmentSerializer
        elif self.action == 'update_status':
            return ServiceRequestStatusUpdateSerializer
        return ServiceRequestDetailSerializer
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'assign', 'update_status']:
            permission_classes = [permissions.IsAuthenticated, IsReceptionistOrAbove]
        elif self.action in ['destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by type
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by assigned staff
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter by guest
        guest_id = self.request.query_params.get('guest_id')
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)
        
        # Filter by room number
        room_number = self.request.query_params.get('room_number')
        if room_number:
            queryset = queryset.filter(room_number=room_number)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(requested_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(requested_at__date__lte=date_to)
        
        # Filter overdue requests
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            queryset = queryset.filter(
                estimated_completion__lt=timezone.now(),
                status__in=['pending', 'acknowledged', 'in_progress']
            )
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(request_number__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(guest__first_name__icontains=search) |
                Q(guest__last_name__icontains=search) |
                Q(room_number__icontains=search)
            )
        
        return queryset.order_by('-priority', '-requested_at')
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign service request to staff member"""
        service_request = self.get_object()
        serializer = self.get_serializer(service_request, data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                # Update assignment
                old_assigned = service_request.assigned_to
                serializer.save()
                
                # Create update record
                update_message = f"Assigned to {service_request.assigned_to.name}"
                if old_assigned:
                    update_message += f" (previously assigned to {old_assigned.name})"
                
                ServiceRequestUpdate.objects.create(
                    service_request=service_request,
                    update_type='assignment',
                    message=update_message,
                    created_by=request.user
                )
                
                # Acknowledge the request if it's still pending
                if service_request.status == 'pending':
                    service_request.acknowledge(service_request.assigned_to)
            
            return Response({
                'message': 'Service request assigned successfully',
                'request': ServiceRequestDetailSerializer(service_request).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update service request status"""
        service_request = self.get_object()
        serializer = self.get_serializer(
            data=request.data, 
            context={'request_obj': service_request}
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                old_status = service_request.status
                new_status = serializer.validated_data['status']
                notes = serializer.validated_data.get('notes', '')
                
                # Update status and related fields
                service_request.status = new_status
                
                if new_status == 'in_progress' and not service_request.started_at:
                    service_request.started_at = timezone.now()
                elif new_status == 'completed' and not service_request.completed_at:
                    service_request.completed_at = timezone.now()
                    if notes:
                        service_request.resolution_notes = notes
                
                # Update costs and satisfaction
                actual_cost = serializer.validated_data.get('actual_cost')
                if actual_cost is not None:
                    service_request.actual_cost = actual_cost
                
                guest_satisfaction = serializer.validated_data.get('guest_satisfaction')
                if guest_satisfaction is not None:
                    service_request.guest_satisfaction = guest_satisfaction
                
                service_request.save()
                
                # Create update record
                update_message = f"Status changed from {old_status} to {new_status}"
                if notes:
                    update_message += f"\nNotes: {notes}"
                
                ServiceRequestUpdate.objects.create(
                    service_request=service_request,
                    update_type='status_change',
                    message=update_message,
                    created_by=request.user
                )
            
            return Response({
                'message': f'Status updated to {new_status}',
                'request': ServiceRequestDetailSerializer(service_request).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post'])
    def updates(self, request, pk=None):
        """Get or create updates for a service request"""
        service_request = self.get_object()
        
        if request.method == 'GET':
            updates = service_request.updates.all().select_related('created_by')
            serializer = ServiceRequestUpdateRecordSerializer(updates, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ServiceRequestUpdateCreateSerializer(data=request.data)
            if serializer.is_valid():
                update = serializer.save(
                    service_request=service_request,
                    created_by=request.user
                )
                return Response(
                    ServiceRequestUpdateRecordSerializer(update).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get service request dashboard statistics"""
        # Basic counts
        total_requests = ServiceRequest.objects.count()
        pending_requests = ServiceRequest.objects.filter(status='pending').count()
        in_progress_requests = ServiceRequest.objects.filter(status='in_progress').count()
        
        # Today's completions
        today = timezone.now().date()
        completed_today = ServiceRequest.objects.filter(
            status='completed',
            completed_at__date=today
        ).count()
        
        # Overdue requests
        overdue_requests = ServiceRequest.objects.filter(
            estimated_completion__lt=timezone.now(),
            status__in=['pending', 'acknowledged', 'in_progress']
        ).count()
        
        # High priority pending
        high_priority_pending = ServiceRequest.objects.filter(
            priority__in=['high', 'urgent'],
            status__in=['pending', 'acknowledged']
        ).count()
        
        urgent_requests = ServiceRequest.objects.filter(
            priority='urgent',
            status__in=['pending', 'acknowledged', 'in_progress']
        ).count()
        
        # Calculate averages
        completed_requests = ServiceRequest.objects.filter(status='completed')
        avg_response_time = 0
        avg_satisfaction = 0
        
        if completed_requests.exists():
            # Calculate response times
            response_times = []
            satisfaction_scores = []
            
            for req in completed_requests:
                if req.response_time:
                    response_times.append(req.response_time)
                if req.guest_satisfaction:
                    satisfaction_scores.append(req.guest_satisfaction)
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
            if satisfaction_scores:
                avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
        
        # Department breakdown
        department_stats = list(
            ServiceRequest.objects.values('department')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Type distribution
        type_distribution = list(
            ServiceRequest.objects.values('type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        dashboard_data = {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'in_progress_requests': in_progress_requests,
            'completed_today': completed_today,
            'overdue_requests': overdue_requests,
            'avg_response_time': round(avg_response_time, 2),
            'avg_satisfaction': round(avg_satisfaction, 2),
            'high_priority_pending': high_priority_pending,
            'urgent_requests': urgent_requests,
            'department_stats': department_stats,
            'type_distribution': type_distribution
        }
        
        serializer = ServiceDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue service requests"""
        overdue_requests = self.get_queryset().filter(
            estimated_completion__lt=timezone.now(),
            status__in=['pending', 'acknowledged', 'in_progress']
        )
        
        serializer = ServiceRequestListSerializer(overdue_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get requests assigned to current user"""
        my_requests = self.get_queryset().filter(assigned_to=request.user)
        
        serializer = ServiceRequestListSerializer(my_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_satisfaction(self, request, pk=None):
        """Add guest satisfaction rating"""
        service_request = self.get_object()
        serializer = GuestSatisfactionSerializer(data=request.data)
        
        if serializer.is_valid():
            service_request.guest_satisfaction = serializer.validated_data['rating']
            service_request.save()
            
            # Add feedback as an update
            feedback = serializer.validated_data.get('feedback', '')
            if feedback:
                ServiceRequestUpdate.objects.create(
                    service_request=service_request,
                    update_type='guest_communication',
                    message=f"Guest feedback: {feedback}",
                    communicated_to_guest=True
                )
            
            return Response({
                'message': 'Satisfaction rating added successfully',
                'rating': service_request.guest_satisfaction
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceRequestTemplateViewSet(ModelViewSet):
    """ViewSet for service request templates"""
    
    queryset = ServiceRequestTemplate.objects.all()
    serializer_class = ServiceRequestTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by type
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by guest selectable
        guest_selectable = self.request.query_params.get('guest_selectable')
        if guest_selectable is not None:
            queryset = queryset.filter(is_guest_selectable=guest_selectable.lower() == 'true')
        
        # Filter active templates
        active_only = self.request.query_params.get('active_only')
        if active_only is None or active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('type', 'name')
    
    @action(detail=True, methods=['post'])
    def create_request(self, request, pk=None):
        """Create a service request from template"""
        template = self.get_object()
        serializer = ServiceRequestFromTemplateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Get template and form data
            guest_id = serializer.validated_data['guest']
            room_number = serializer.validated_data['room_number']
            custom_description = serializer.validated_data.get('custom_description', '')
            priority_override = serializer.validated_data.get('priority_override')
            
            # Create service request from template
            service_request_data = {
                'guest_id': guest_id,
                'type': template.type,
                'priority': priority_override or template.default_priority,
                'title': template.title_template,
                'description': custom_description or template.description_template,
                'room_number': room_number,
                'department': template.department,
                'estimated_cost': template.estimated_cost,
            }
            
            # Calculate estimated completion based on duration
            if template.estimated_duration_minutes:
                estimated_completion = timezone.now() + timedelta(
                    minutes=template.estimated_duration_minutes
                )
                service_request_data['estimated_completion'] = estimated_completion
            
            # Create the request
            service_request = ServiceRequest.objects.create(**service_request_data)
            
            return Response({
                'message': 'Service request created from template',
                'request': ServiceRequestDetailSerializer(service_request).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceMetricsViewSet(ModelViewSet):
    """ViewSet for service metrics (read-only)"""
    
    queryset = ServiceMetrics.objects.all()
    serializer_class = ServiceMetricsSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    http_method_names = ['get']  # Read-only
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        return queryset.order_by('-date')

class ServiceReportsView(APIView):
    """Service reports and analytics"""
    
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    
    def get(self, request):
        # Date range parameters
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Basic statistics
        total_requests = ServiceRequest.objects.filter(
            requested_at__date__range=[start_date, end_date]
        ).count()
        
        # Status distribution
        status_stats = ServiceRequest.objects.filter(
            requested_at__date__range=[start_date, end_date]
        ).values('status').annotate(count=Count('id')).order_by('status')
        
        # Priority distribution
        priority_stats = ServiceRequest.objects.filter(
            requested_at__date__range=[start_date, end_date]
        ).values('priority').annotate(count=Count('id')).order_by('priority')
        
        # Department performance
        department_stats = ServiceRequest.objects.filter(
            requested_at__date__range=[start_date, end_date]
        ).values('department').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            avg_satisfaction=Avg('guest_satisfaction')
        ).order_by('-total')
        
        # Daily trends
        from django.db.models.functions import TruncDate
        daily_trends = ServiceRequest.objects.filter(
            requested_at__date__range=[start_date, end_date]
        ).annotate(
            date=TruncDate('requested_at')
        ).values('date').annotate(
            requests=Count('id'),
            completed=Count('id', filter=Q(status='completed'))
        ).order_by('date')
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days
            },
            'total_requests': total_requests,
            'status_distribution': list(status_stats),
            'priority_distribution': list(priority_stats),
            'department_performance': list(department_stats),
            'daily_trends': list(daily_trends),
            'generated_at': timezone.now()
        })