import os
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<uuid:pk>/', views.CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),

    # Menu Item URLs
    path('menu-items/', views.MenuItemListCreateView.as_view(), name='menuitem-list-create'),
    path('menu-items/<uuid:pk>/', views.MenuItemRetrieveUpdateDestroyView.as_view(), name='menuitem-detail'),
    
    # Custom Endpoint for Guest Menu Display - This view is not implemented, so it's removed to fix the error.
    # path('categories/with-items/', views.CategoryWithItemsListView.as_view(), name='categories-with-items'),
    
    # Custom actions/endpoints - This view is not implemented, so it's removed to fix the error.
    # path('menu-items/<uuid:pk>/toggle-availability/', views.MenuItemAvailabilityUpdateView.as_view(), name='toggle-availability'),
]