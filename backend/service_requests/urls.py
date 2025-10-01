from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'service_requests'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'requests', views.ServiceRequestViewSet, basename='requests')
router.register(r'templates', views.ServiceRequestTemplateViewSet, basename='templates')
router.register(r'metrics', views.ServiceMetricsViewSet, basename='metrics')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('reports/', views.ServiceReportsView.as_view(), name='reports'),
]