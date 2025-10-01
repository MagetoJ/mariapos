from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dashboard_stats'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]