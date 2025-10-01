from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<uuid:pk>/upload-image/', views.upload_category_image, name='category-upload-image'),
    path('categories/with-items/', views.CategoryWithItemsView.as_view(), name='categories-with-items'),
    
    # Menu Items
    path('', views.MenuItemListCreateView.as_view(), name='menuitem-list-create'),
    path('<uuid:pk>/', views.MenuItemDetailView.as_view(), name='menuitem-detail'),
    path('<uuid:pk>/upload-image/', views.upload_menu_item_image, name='menuitem-upload-image'),
    path('<uuid:pk>/toggle-availability/', views.toggle_menu_item_availability, name='toggle-availability'),
    path('bulk/update-availability/', views.bulk_update_availability, name='bulk-update-availability'),
    
    # Special endpoints
    path('popular/', views.get_popular_items, name='popular-items'),
    path('by-category/', views.get_menu_by_category, name='menu-by-category'),
]