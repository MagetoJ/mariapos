from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
# Import MultiPartParser and FormParser to handle file uploads
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.utils import timezone
from .models import Category, MenuItem
from .serializers import (
    CategorySerializer, CategoryWithItemsSerializer,
    MenuItemSerializer, MenuItemListSerializer, 
    MenuItemCreateUpdateSerializer, MenuItemAvailabilitySerializer
)

class CategoryListCreateView(generics.ListCreateAPIView):
    """List and create categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    # ADDED PARSER CLASSES
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        queryset = Category.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('isActive')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('display_order', 'name')
    
    def perform_create(self, serializer):
        # Only allow admin and manager to create categories
        if self.request.user.role not in ['admin', 'manager']:
            raise permissions.PermissionDenied("Only admin and manager can create categories")
        serializer.save()

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and destroy categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    # ADDED PARSER CLASSES
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        # Only allow admin and manager to update categories
        if self.request.user.role not in ['admin', 'manager']:
            raise permissions.PermissionDenied("Only admin and manager can update categories")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow admin to delete categories
        if self.request.user.role not in ['admin']:
            raise permissions.PermissionDenied("Only admin can delete categories")
        instance.delete()

class CategoryWithItemsListView(generics.ListAPIView):
    """List categories with their menu items"""
    queryset = Category.objects.filter(is_active=True).prefetch_related('menu_items')
    serializer_class = CategoryWithItemsSerializer
    permission_classes = [permissions.IsAuthenticated]

class MenuItemListCreateView(generics.ListCreateAPIView):
    """List and create menu items"""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemListSerializer
    permission_classes = [permissions.IsAuthenticated]
    # ADDED PARSER CLASSES: CRITICAL for file uploads
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MenuItemCreateUpdateSerializer
        return MenuItemListSerializer

    def get_queryset(self):
        queryset = MenuItem.objects.select_related('category').all()
        
        # Filter by category
        category_id = self.request.query_params.get('categoryId')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        
        # Filter by availability
        is_available = self.request.query_params.get('isAvailable')
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
            
        return queryset.order_by('name')

    def perform_create(self, serializer):
        # Only allow admin, manager, and kitchen to create menu items
        if self.request.user.role not in ['admin', 'manager', 'kitchen']:
            raise permissions.PermissionDenied("Only admin, manager, and kitchen staff can create menu items")
        serializer.save()

class MenuItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and destroy menu items"""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    # ADDED PARSER CLASSES: CRITICAL for file uploads
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MenuItemCreateUpdateSerializer
        return MenuItemSerializer

    def perform_update(self, serializer):
        # Only allow admin, manager, and kitchen to update menu items
        if self.request.user.role not in ['admin', 'manager', 'kitchen']:
            raise permissions.PermissionDenied("Only admin, manager, and kitchen staff can update menu items")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow admin to delete menu items
        if self.request.user.role not in ['admin']:
            raise permissions.PermissionDenied("Only admin can delete menu items")
        instance.delete()

class MenuItemAvailabilityUpdateView(generics.UpdateAPIView):
    """Toggle menu item availability"""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        # Only allow admin, manager, and kitchen to update availability
        if self.request.user.role not in ['admin', 'manager', 'kitchen']:
            raise permissions.PermissionDenied("Only authorized staff can update item availability")
        serializer.save()

# NOTE: The redundant custom upload views were correctly omitted here as the generic
# ListCreateAPIView and RetrieveUpdateDestroyAPIView now handle files automatically.
