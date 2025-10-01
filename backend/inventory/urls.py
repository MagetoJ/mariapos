from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'items', views.InventoryItemViewSet, basename='items')
router.register(r'movements', views.StockMovementViewSet, basename='movements')
router.register(r'suppliers', views.SupplierViewSet, basename='suppliers')
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchase-orders')
router.register(r'waste', views.WasteLogViewSet, basename='waste')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('bulk-update/', views.BulkStockUpdateView.as_view(), name='bulk-update'),
    path('track-waste/', views.WasteTrackingView.as_view(), name='track-waste'),
]