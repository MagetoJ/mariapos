import os
from django.urls import path
from . import views

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    # FIX: Using the correct generic view for detail/update/delete
    path('categories/<uuid:pk>/', views.CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    # NOTE: Old direct image upload views removed as generics handle files now.
    
    # Custom Endpoint for Guest Menu Display
    # CRITICAL FIX: Renamed CategoryWithItemsView to CategoryWithItemsListView (typo fix)
    path('categories/with-items/', views.CategoryWithItemsListView.as_view(), name='categories-with-items'),


    # Menu Item URLs
    path('', views.MenuItemListCreateView.as_view(), name='menuitem-list-create'),
    # FIX: Using the correct generic view for detail/update/delete
    path('<uuid:pk>/', views.MenuItemRetrieveUpdateDestroyView.as_view(), name='menuitem-detail'),
    # NOTE: Old direct image upload views removed as generics handle files now.

    
    # Custom actions/endpoints
    # FIX: Replaced toggle_menu_item_availability with the class-based view
    path('<uuid:pk>/toggle-availability/', views.MenuItemAvailabilityUpdateView.as_view(), name='toggle-availability'),
    
    # CRITICAL FIX: Removed the non-existent 'views.bulk_update_availability'
    # path('bulk/update-availability/', views.bulk_update_availability, name='bulk-update-availability'), 
    
    # Special endpoints - CRITICAL FIX: Removed non-existent functions
    # path('popular/', views.get_popular_items, name='popular-items'),
    # path('by-category/', views.get_menu_by_category, name='menu-by-category'),
]
