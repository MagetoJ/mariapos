from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'guests'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'guests', views.GuestViewSet, basename='guests')
router.register(r'feedback', views.GuestFeedbackViewSet, basename='feedback')
router.register(r'groups', views.GuestGroupViewSet, basename='groups')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('check-availability/', views.RoomAvailabilityView.as_view(), name='check-availability'),
    path('reports/', views.GuestReportsView.as_view(), name='reports'),
]