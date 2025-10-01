from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Orders
    path('', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:pk>/status/', views.update_order_status, name='update-status'),
    path('<uuid:pk>/cancel/', views.cancel_order, name='cancel-order'),
    
    # Special views
    path('kitchen/', views.get_kitchen_orders, name='kitchen-orders'),
    path('waiter/<uuid:waiter_id>/', views.get_waiter_orders, name='waiter-orders'),
    path('waiter/', views.get_waiter_orders, name='current-waiter-orders'),
    path('room-service/', views.get_room_service_orders, name='room-service-orders'),
    
    # Statistics
    path('statistics/', views.get_order_statistics, name='order-statistics'),
]