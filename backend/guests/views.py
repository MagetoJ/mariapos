from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q, Count, F
from django.utils import timezone
from decimal import Decimal

from accounts.permissions import IsManagerOrAdmin, IsStaffMember, IsReceptionistOrAbove
from .models import Guest, GuestGroup, GuestPreference, GuestFeedback
from .serializers import (
    GuestListSerializer, GuestDetailSerializer, GuestCreateSerializer,
    GuestUpdateSerializer, CheckInSerializer, CheckOutSerializer,
    GuestPreferenceSerializer, GuestFeedbackSerializer,
    GuestFeedbackCreateSerializer, GuestFeedbackResponseSerializer,
    GuestGroupSerializer, GuestStatsSerializer, RoomAvailabilitySerializer
)

class GuestViewSet(ModelViewSet):
    """
    ViewSet for managing hotel guests
    """
    queryset = Guest.objects.all().select_related('assigned_staff')
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GuestListSerializer
        elif self.action == 'create':
            return GuestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GuestUpdateSerializer
        elif self.action == 'check_in':
            return CheckInSerializer
        elif self.action == 'check_out':
            return CheckOutSerializer
        return GuestDetailSerializer
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'check_in', 'check_out']:
            permission_classes = [permissions.IsAuthenticated, IsReceptionistOrAbove]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by room number
        room_number = self.request.query_params.get('room_number')
        if room_number:
            queryset = queryset.filter(room_number=room_number)
        
        # Filter by guest type
        guest_type = self.request.query_params.get('guest_type')
        if guest_type:
            queryset = queryset.filter(guest_type=guest_type)
        
        # Filter by VIP status
        is_vip = self.request.query_params.get('is_vip')
        if is_vip is not None:
            queryset = queryset.filter(is_vip=is_vip.lower() == 'true')
        
        # Filter by assigned staff
        assigned_staff = self.request.query_params.get('assigned_staff')
        if assigned_staff:
            queryset = queryset.filter(assigned_staff_id=assigned_staff)
        
        # Filter by date range
        checkin_from = self.request.query_params.get('checkin_from')
        checkin_to = self.request.query_params.get('checkin_to')
        
        if checkin_from:
            queryset = queryset.filter(expected_checkin__date__gte=checkin_from)
        if checkin_to:
            queryset = queryset.filter(expected_checkin__date__lte=checkin_to)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(guest_number__icontains=search) |
                Q(room_number__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a guest"""
        guest = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'guest': guest})
        
        if serializer.is_valid():
            with transaction.atomic():
                # Create user account if requested
                guest_user = None
                if serializer.validated_data.get('create_user_account', True):
                    guest_user = guest.check_in()
                else:
                    guest.check_in()
                
                # Add notes if provided
                notes = serializer.validated_data.get('notes')
                if notes:
                    if guest.notes:
                        guest.notes += f"\n\nCheck-in notes: {notes}"
                    else:
                        guest.notes = f"Check-in notes: {notes}"
                    guest.save()
            
            response_data = {
                'message': 'Guest checked in successfully',
                'guest': GuestDetailSerializer(guest).data
            }
            
            if guest_user:
                response_data['user_account_created'] = True
                response_data['temporary_password'] = 'temp123'
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Check out a guest"""
        guest = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'guest': guest})
        
        if serializer.is_valid():
            with transaction.atomic():
                guest.check_out()
                
                # Add notes if provided
                notes = serializer.validated_data.get('notes')
                if notes:
                    if guest.notes:
                        guest.notes += f"\n\nCheck-out notes: {notes}"
                    else:
                        guest.notes = f"Check-out notes: {notes}"
                    guest.save()
            
            return Response({
                'message': 'Guest checked out successfully',
                'guest': GuestDetailSerializer(guest).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get guest statistics"""
        total_guests = Guest.objects.count()
        checked_in_guests = Guest.objects.filter(status='checked_in').count()
        pending_checkins = Guest.objects.filter(status='pending').count()
        pending_checkouts = Guest.objects.filter(
            status='checked_in',
            expected_checkout__date=timezone.now().date()
        ).count()
        vip_guests = Guest.objects.filter(is_vip=True, status='checked_in').count()
        
        # Calculate occupancy
        occupied_rooms = Guest.objects.filter(status='checked_in').values('room_number').distinct().count()
        # Note: In a real system, you'd have a Rooms model to get total rooms
        total_rooms = 100  # Placeholder - should come from rooms configuration
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        stats_data = {
            'total_guests': total_guests,
            'checked_in_guests': checked_in_guests,
            'pending_checkins': pending_checkins,
            'pending_checkouts': pending_checkouts,
            'vip_guests': vip_guests,
            'occupied_rooms': occupied_rooms,
            'total_rooms': total_rooms,
            'occupancy_rate': round(occupancy_rate, 2)
        }
        
        serializer = GuestStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def arriving_today(self, request):
        """Get guests arriving today"""
        today = timezone.now().date()
        arriving_guests = self.get_queryset().filter(
            expected_checkin__date=today,
            status='pending'
        )
        
        serializer = GuestListSerializer(arriving_guests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def departing_today(self, request):
        """Get guests departing today"""
        today = timezone.now().date()
        departing_guests = self.get_queryset().filter(
            expected_checkout__date=today,
            status='checked_in'
        )
        
        serializer = GuestListSerializer(departing_guests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vip_guests(self, request):
        """Get VIP guests"""
        vip_guests = self.get_queryset().filter(is_vip=True)
        
        serializer = GuestListSerializer(vip_guests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def preferences(self, request, pk=None):
        """Manage guest preferences"""
        guest = self.get_object()
        
        if request.method == 'GET':
            preferences = guest.preferences.filter(is_active=True)
            serializer = GuestPreferenceSerializer(preferences, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = GuestPreferenceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(guest=guest)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post'])
    def feedback(self, request, pk=None):
        """Manage guest feedback"""
        guest = self.get_object()
        
        if request.method == 'GET':
            feedback = guest.feedback.all()
            serializer = GuestFeedbackSerializer(feedback, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = GuestFeedbackCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(guest=guest)
                return Response(
                    GuestFeedbackSerializer(serializer.instance).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestFeedbackViewSet(ModelViewSet):
    """ViewSet for guest feedback management"""
    
    queryset = GuestFeedback.objects.all().select_related('guest', 'responded_by')
    serializer_class = GuestFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'respond']:
            permission_classes = [permissions.IsAuthenticated, IsReceptionistOrAbove]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Filter by guest
        guest = self.request.query_params.get('guest')
        if guest:
            queryset = queryset.filter(guest_id=guest)
        
        # Filter by response status
        has_response = self.request.query_params.get('has_response')
        if has_response is not None:
            if has_response.lower() == 'true':
                queryset = queryset.exclude(management_response='')
            else:
                queryset = queryset.filter(management_response='')
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Add management response to feedback"""
        feedback = self.get_object()
        serializer = GuestFeedbackResponseSerializer(feedback, data=request.data)
        
        if serializer.is_valid():
            serializer.save(
                responded_by=request.user,
                responded_at=timezone.now()
            )
            return Response(GuestFeedbackSerializer(feedback).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestGroupViewSet(ModelViewSet):
    """ViewSet for guest groups"""
    
    queryset = GuestGroup.objects.all().select_related('group_leader')
    serializer_class = GuestGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsReceptionistOrAbove]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by group type
        group_type = self.request.query_params.get('group_type')
        if group_type:
            queryset = queryset.filter(group_type=group_type)
        
        return queryset.order_by('-created_at')

class RoomAvailabilityView(APIView):
    """Check room availability"""
    
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def post(self, request):
        serializer = RoomAvailabilitySerializer(data=request.data)
        
        if serializer.is_valid():
            room_number = serializer.validated_data['room_number']
            checkin_date = serializer.validated_data['checkin_date']
            checkout_date = serializer.validated_data['checkout_date']
            
            # Check for overlapping bookings
            overlapping = Guest.objects.filter(
                room_number=room_number,
                status__in=['pending', 'checked_in'],
                expected_checkin__lt=checkout_date,
                expected_checkout__gt=checkin_date
            )
            
            is_available = not overlapping.exists()
            
            response_data = {
                'room_number': room_number,
                'is_available': is_available,
                'checkin_date': checkin_date,
                'checkout_date': checkout_date
            }
            
            if not is_available:
                conflicting_bookings = []
                for booking in overlapping:
                    conflicting_bookings.append({
                        'guest_name': booking.full_name,
                        'guest_number': booking.guest_number,
                        'checkin': booking.expected_checkin,
                        'checkout': booking.expected_checkout,
                        'status': booking.status
                    })
                response_data['conflicting_bookings'] = conflicting_bookings
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestReportsView(APIView):
    """Guest reports and analytics"""
    
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    
    def get(self, request):
        # Guest statistics by status
        status_stats = Guest.objects.values('status').annotate(count=Count('id')).order_by('status')
        
        # Guest type distribution
        type_stats = Guest.objects.values('guest_type').annotate(count=Count('id')).order_by('guest_type')
        
        # Monthly guest trends (last 12 months)
        from datetime import datetime, timedelta
        from django.db.models import Q
        from django.db.models.functions import TruncMonth
        
        twelve_months_ago = timezone.now() - timedelta(days=365)
        monthly_guests = Guest.objects.filter(
            created_at__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Average stay duration
        checked_out_guests = Guest.objects.filter(
            status='checked_out',
            actual_checkin__isnull=False,
            actual_checkout__isnull=False
        )
        
        avg_stay_duration = 0
        if checked_out_guests.exists():
            total_days = sum(guest.stay_duration for guest in checked_out_guests)
            avg_stay_duration = total_days / checked_out_guests.count()
        
        # Feedback summary
        feedback_stats = GuestFeedback.objects.values('rating').annotate(
            count=Count('id')
        ).order_by('rating')
        
        avg_rating = GuestFeedback.objects.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating'] or 0
        
        return Response({
            'status_distribution': list(status_stats),
            'guest_type_distribution': list(type_stats),
            'monthly_trends': list(monthly_guests),
            'average_stay_duration': round(avg_stay_duration, 1),
            'feedback_stats': list(feedback_stats),
            'average_rating': round(avg_rating, 2),
            'generated_at': timezone.now()
        })