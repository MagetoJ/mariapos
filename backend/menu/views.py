from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from .models import MenuItem, Category
from .serializers import (
    MenuItemSerializer, 
    MenuItemCreateUpdateSerializer, 
    CategorySerializer
)
# from accounts.permissions import IsStaffMember  # Uncomment if using

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated, IsStaffMember] # Uncomment if using

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated, IsStaffMember] # Uncomment if using

class MenuItemListCreateView(generics.ListCreateAPIView):
    """
    Handles GET and POST requests for menu items.
    """
    queryset = MenuItem.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    # permission_classes = [IsAuthenticated, IsStaffMember] # Uncomment if using

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MenuItemSerializer
        return MenuItemCreateUpdateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        is_available = self.request.query_params.get('is_available')

        if category:
            queryset = queryset.filter(category__name=category)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() in ['true', '1'])
            
        return queryset

    def perform_create(self, serializer):
        # NOTE: This assumes the user sending the request is a staff member
        serializer.save()

class MenuItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles GET, PUT, PATCH, and DELETE requests for a single menu item.
    """
    queryset = MenuItem.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    # permission_classes = [IsAuthenticated, IsStaffMember] # Uncomment if using

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MenuItemSerializer
        return MenuItemCreateUpdateSerializer

    def perform_update(self, serializer):
        serializer.save()

class MenuItemToggleAvailabilityView(generics.UpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemCreateUpdateSerializer
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = not instance.is_available
        instance.is_available = new_status
        instance.save(update_fields=['is_available'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)