from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Table, TableReservation, TableLayout
from .serializers import (
    TableSerializer, TableListSerializer, TableStatusUpdateSerializer,
    TableReservationSerializer, TableLayoutSerializer,
    TableAssignmentSerializer, TableOccupancySerializer
)

User = get_user_model()

class TableListView(generics.ListAPIView):
    """List all tables"""
    queryset = Table.objects.all()
    serializer_class = TableListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Table.objects.select_related('waiter', 'current_order')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by section
        section = self.request.query_params.get('section')
        if section:
            queryset = queryset.filter(section=section)
        
        # Filter by waiter
        waiter_id = self.request.query_params.get('waiter')
        if waiter_id:
            queryset = queryset.filter(waiter_id=waiter_id)
        
        # For waiters, show their assigned tables by default
        if self.request.user.role == 'waiter':
            show_all = self.request.query_params.get('showAll', 'false').lower() == 'true'
            if not show_all:
                queryset = queryset.filter(waiter=self.request.user)
        
        return queryset.order_by('section', 'table_number')

class TableDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update a table"""
    queryset = Table.objects.select_related('waiter', 'current_order')
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TableStatusUpdateSerializer
        return TableSerializer
    
    def perform_update(self, serializer):
        # Only allow admin, manager, and waiters to update tables
        if self.request.user.role not in ['admin', 'manager', 'waiter']:
            raise permissions.PermissionDenied("Only admin, manager, and waiters can update tables")
        serializer.save()

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def assign_waiter(request, pk):
    """Assign a waiter to a table"""
    if request.user.role not in ['admin', 'manager']:
        return Response(
            {"error": "Only admin and manager can assign waiters"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        table = Table.objects.get(pk=pk)
        serializer = TableAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            waiter_id = serializer.validated_data['waiter']
            waiter = User.objects.get(id=waiter_id)
            
            table.waiter = waiter
            table.save()
            
            return Response(TableSerializer(table).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Table.DoesNotExist:
        return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def occupy_table(request, pk):
    """Mark table as occupied"""
    if request.user.role not in ['admin', 'manager', 'waiter', 'receptionist']:
        return Response(
            {"error": "Access denied"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        table = Table.objects.get(pk=pk)
        
        if table.status != 'available':
            return Response(
                {"error": f"Table is {table.status}, cannot occupy"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TableOccupancySerializer(data=request.data, context={'table': table})
        
        if serializer.is_valid():
            guest_count = serializer.validated_data['guest_count']
            waiter_id = serializer.validated_data.get('waiter')
            
            table.status = 'occupied'
            
            # Assign waiter if provided
            if waiter_id:
                try:
                    waiter = User.objects.get(id=waiter_id, role='waiter')
                    table.waiter = waiter
                except User.DoesNotExist:
                    return Response(
                        {"error": "Waiter not found"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            table.save()
            
            return Response({
                "message": f"Table {table.table_number} occupied by {guest_count} guests",
                "table": TableSerializer(table).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Table.DoesNotExist:
        return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def free_table(request, pk):
    """Mark table as available"""
    if request.user.role not in ['admin', 'manager', 'waiter']:
        return Response(
            {"error": "Only admin, manager, and waiters can free tables"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        table = Table.objects.get(pk=pk)
        
        # Check if table has active orders
        if table.current_order and table.current_order.status not in ['completed', 'cancelled']:
            return Response(
                {"error": "Cannot free table with active order"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        table.status = 'available'
        table.current_order = None
        table.save()
        
        return Response({
            "message": f"Table {table.table_number} is now available",
            "table": TableSerializer(table).data
        })
    
    except Table.DoesNotExist:
        return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_available_tables(request):
    """Get available tables"""
    capacity = request.query_params.get('capacity')
    section = request.query_params.get('section')
    
    tables = Table.objects.filter(status='available')
    
    if capacity:
        try:
            capacity = int(capacity)
            tables = tables.filter(capacity__gte=capacity)
        except ValueError:
            pass
    
    if section:
        tables = tables.filter(section=section)
    
    tables = tables.order_by('capacity', 'table_number')
    serializer = TableListSerializer(tables, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_table_sections(request):
    """Get all table sections"""
    sections = Table.objects.values_list('section', flat=True).distinct().order_by('section')
    return Response(list(sections))

# Table Reservations
class TableReservationListCreateView(generics.ListCreateAPIView):
    """List and create table reservations"""
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = TableReservation.objects.select_related('table', 'guest')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date
        date_filter = self.request.query_params.get('date')
        if date_filter:
            try:
                date = timezone.datetime.fromisoformat(date_filter).date()
                queryset = queryset.filter(reservation_time__date=date)
            except ValueError:
                pass
        
        # Filter by guest for guest users
        if self.request.user.role == 'guest':
            queryset = queryset.filter(guest=self.request.user)
        
        return queryset.order_by('reservation_time')
    
    def perform_create(self, serializer):
        # Guests can only create reservations for themselves
        if self.request.user.role == 'guest':
            serializer.save(guest=self.request.user)
        else:
            serializer.save()

class TableReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a table reservation"""
    queryset = TableReservation.objects.select_related('table', 'guest')
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Guests can only access their own reservations
        if self.request.user.role == 'guest':
            return super().get_queryset().filter(guest=self.request.user)
        return super().get_queryset()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_reservation(request, pk):
    """Confirm a table reservation"""
    if request.user.role not in ['admin', 'manager', 'receptionist']:
        return Response(
            {"error": "Only admin, manager, and receptionist can confirm reservations"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        reservation = TableReservation.objects.get(pk=pk)
        
        if reservation.status != 'pending':
            return Response(
                {"error": f"Cannot confirm {reservation.status} reservation"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'confirmed'
        reservation.save()
        
        return Response({
            "message": "Reservation confirmed",
            "reservation": TableReservationSerializer(reservation).data
        })
    
    except TableReservation.DoesNotExist:
        return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

# Table Layouts
class TableLayoutListCreateView(generics.ListCreateAPIView):
    """List and create table layouts"""
    queryset = TableLayout.objects.all()
    serializer_class = TableLayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = TableLayout.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('isActive')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-is_active', 'name')
    
    def perform_create(self, serializer):
        # Only allow admin and manager to create layouts
        if self.request.user.role not in ['admin', 'manager']:
            raise permissions.PermissionDenied("Only admin and manager can create layouts")
        serializer.save()

class TableLayoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a table layout"""
    queryset = TableLayout.objects.all()
    serializer_class = TableLayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        # Only allow admin and manager to update layouts
        if self.request.user.role not in ['admin', 'manager']:
            raise permissions.PermissionDenied("Only admin and manager can update layouts")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow admin to delete layouts
        if self.request.user.role != 'admin':
            raise permissions.PermissionDenied("Only admin can delete layouts")
        instance.delete()