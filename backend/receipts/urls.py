from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'receipts'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.ReceiptViewSet, basename='receipts')
router.register(r'templates', views.ReceiptTemplateViewSet, basename='receipt-templates')
router.register(r'print-queue', views.ReceiptPrintQueueViewSet, basename='receipt-print-queue')
router.register(r'email-logs', views.ReceiptEmailLogViewSet, basename='receipt-email-logs')

urlpatterns = [
    path('', include(router.urls)),
]