from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShiftReportViewSet, DailyReportViewSet, ReportAnalyticsViewSet

router = DefaultRouter()
router.register(r'shifts', ShiftReportViewSet, basename='shift-reports')
router.register(r'daily', DailyReportViewSet, basename='daily-reports')
router.register(r'analytics', ReportAnalyticsViewSet, basename='report-analytics')

urlpatterns = [
    path('', include(router.urls)),
]