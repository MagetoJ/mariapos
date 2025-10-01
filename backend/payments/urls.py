from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payments')
router.register(r'refunds', views.PaymentRefundViewSet, basename='refunds')
router.register(r'gateways', views.PaymentGatewayViewSet, basename='gateways')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional payment processing endpoints
    path('mobile-money/', views.MobileMoneyPaymentView.as_view(), name='mobile-money'),
    path('card-payment/', views.CardPaymentView.as_view(), name='card-payment'),
    path('reports/', views.PaymentReportsView.as_view(), name='reports'),
]