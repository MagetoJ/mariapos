from django.urls import path
from . import views

app_name = 'tables'

urlpatterns = [
    # Tables
    path('', views.TableListView.as_view(), name='table-list'),
    path('<uuid:pk>/', views.TableDetailView.as_view(), name='table-detail'),
    path('<uuid:pk>/assign-waiter/', views.assign_waiter, name='assign-waiter'),
    path('<uuid:pk>/occupy/', views.occupy_table, name='occupy-table'),
    path('<uuid:pk>/free/', views.free_table, name='free-table'),
    
    # Table utilities
    path('available/', views.get_available_tables, name='available-tables'),
    path('sections/', views.get_table_sections, name='table-sections'),
    
    # Reservations
    path('reservations/', views.TableReservationListCreateView.as_view(), name='reservation-list-create'),
    path('reservations/<uuid:pk>/', views.TableReservationDetailView.as_view(), name='reservation-detail'),
    path('reservations/<uuid:pk>/confirm/', views.confirm_reservation, name='confirm-reservation'),
    
    # Layouts
    path('layouts/', views.TableLayoutListCreateView.as_view(), name='layout-list-create'),
    path('layouts/<uuid:pk>/', views.TableLayoutDetailView.as_view(), name='layout-detail'),
]