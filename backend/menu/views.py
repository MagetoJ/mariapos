from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
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

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_update(self, serializer):
        # Only allow admin and manager to update categories
        if self.request.user.role not in ['admin', 'manager']:
            raise permissions.PermissionDenied("Only admin and manager can update categories")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow admin to delete categories
        if self.request.user.role != 'admin':
            raise permissions.PermissionDenied("Only admin can delete categories")
        
        # Check if category has menu items
        if instance.menu_items.exists():
            raise permissions.PermissionDenied("Cannot delete category with existing menu items")
        
        instance.delete()

class CategoryWithItemsView(generics.ListAPIView):
    """List categories with their menu items"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategoryWithItemsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).prefetch_related(
            'menu_items__ingredients',
            'menu_items__modifiers'
        ).order_by('display_order', 'name')

class MenuItemListCreateView(generics.ListCreateAPIView):
    """List and create menu items"""
    queryset = MenuItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MenuItemCreateUpdateSerializer
        return MenuItemListSerializer
    
    def get_queryset(self):
        queryset = MenuItem.objects.select_related('category').prefetch_related(
            'ingredients', 'modifiers'
        )
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by availability
        is_available = self.request.query_params.get('isAvailable')
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        # Search by name or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Filter by dietary preferences  
        is_vegetarian = self.request.query_params.get('isVegetarian')
        if is_vegetarian is not None:
            queryset = queryset.filter(is_vegetarian=is_vegetarian.lower() == 'true')
            
        is_vegan = self.request.query_params.get('isVegan')
        if is_vegan is not None:
            queryset = queryset.filter(is_vegan=is_vegan.lower() == 'true')
            
        is_gluten_free = self.request.query_params.get('isGlutenFree')
        if is_gluten_free is not None:
            queryset = queryset.filter(is_gluten_free=is_gluten_free.lower() == 'true')
        
        # Filter by spice level
        spice_level = self.request.query_params.get('spiceLevel')
        if spice_level:
            queryset = queryset.filter(spice_level=spice_level)
        
        return queryset.order_by('category__display_order', 'display_order', 'name')
    
    def perform_create(self, serializer):
        # Only allow admin, manager, and kitchen staff to create menu items
        if self.request.user.role not in ['admin', 'manager', 'kitchen']:
            raise permissions.PermissionDenied("Only admin, manager, and kitchen staff can create menu items")
        serializer.save()

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a menu item"""
    queryset = MenuItem.objects.select_related('category').prefetch_related(
        'ingredients', 'modifiers'
    )
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MenuItemCreateUpdateSerializer
        return MenuItemSerializer
    
    def perform_update(self, serializer):
        # Only allow admin, manager, and kitchen staff to update menu items
        if self.request.user.role not in ['admin', 'manager', 'kitchen']:
            raise permissions.PermissionDenied("Only admin, manager, and kitchen staff can update menu items")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow admin to delete menu items
        if self.request.user.role != 'admin':
            raise permissions.PermissionDenied("Only admin can delete menu items")
        
        # Check if menu item is used in any active orders
        from orders.models import OrderItem
        if OrderItem.objects.filter(menu_item=instance, order__status__in=['pending', 'preparing', 'ready']).exists():
            raise permissions.PermissionDenied("Cannot delete menu item with active orders")
        
        instance.delete()

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def toggle_menu_item_availability(request, pk):
    """Toggle menu item availability"""
    if request.user.role not in ['admin', 'manager', 'kitchen']:
        return Response(
            {"error": "Only admin, manager, and kitchen staff can toggle availability"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        menu_item = MenuItem.objects.get(pk=pk)
        serializer = MenuItemAvailabilitySerializer(menu_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(MenuItemListSerializer(menu_item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except MenuItem.DoesNotExist:
        return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_popular_items(request):
    """Get popular menu items based on order frequency"""
    from django.db.models import Count
    from orders.models import OrderItem
    
    # Get items ordered most frequently in the last 30 days
    popular_items = MenuItem.objects.filter(
        orderitem__order__created_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).annotate(
        order_count=Count('orderitem')
    ).filter(
        order_count__gt=0,
        is_available=True
    ).order_by('-order_count')[:10]
    
    serializer = MenuItemListSerializer(popular_items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_menu_by_category(request):
    """Get menu organized by categories"""
    categories = Category.objects.filter(is_active=True).prefetch_related(
        'menu_items__ingredients',
        'menu_items__modifiers'
    ).order_by('display_order', 'name')
    
    # Filter items by availability if requested
    show_unavailable = request.query_params.get('showUnavailable', 'false').lower() == 'true'
    
    menu_data = []
    for category in categories:
        items = category.menu_items.all()
        if not show_unavailable:
            items = items.filter(is_available=True)
        
        if items.exists() or show_unavailable:
            category_data = CategorySerializer(category).data
            category_data['items'] = MenuItemListSerializer(items, many=True).data
            menu_data.append(category_data)
    
    return Response(menu_data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_availability(request):
    """Bulk update menu item availability"""
    if request.user.role not in ['admin', 'manager', 'kitchen']:
        return Response(
            {"error": "Only admin, manager, and kitchen staff can update availability"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    item_ids = request.data.get('item_ids', [])
    is_available = request.data.get('is_available', True)
    
    if not item_ids:
        return Response({"error": "No item IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    updated_count = MenuItem.objects.filter(id__in=item_ids).update(is_available=is_available)
    
    return Response({
        "message": f"Updated {updated_count} menu items",
        "updated_count": updated_count
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_category_image(request, pk):
    """Upload image for a category"""
    if request.user.role not in ['admin', 'manager']:
        return Response(
            {"error": "Only admin and manager can upload category images"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if 'image' not in request.FILES:
        return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    category.image = request.FILES['image']
    category.save()
    
    serializer = CategorySerializer(category)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_menu_item_image(request, pk):
    """Upload image for a menu item"""
    if request.user.role not in ['admin', 'manager', 'kitchen']:
        return Response(
            {"error": "Only admin, manager, and kitchen staff can upload menu item images"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        menu_item = MenuItem.objects.get(pk=pk)
    except MenuItem.DoesNotExist:
        return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if 'image' not in request.FILES:
        return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    menu_item.image = request.FILES['image']
    menu_item.save()
    
    serializer = MenuItemListSerializer(menu_item)
    return Response(serializer.data)