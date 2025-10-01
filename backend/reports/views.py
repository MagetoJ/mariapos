from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

from .models import ShiftReport, DailyReport, WeeklyReport, MonthlyReport
from .serializers import (
    ShiftReportSerializer, DailyReportSerializer, WeeklyReportSerializer,
    MonthlyReportSerializer, ShiftReportSummarySerializer, ReportAnalyticsSerializer
)

class ShiftReportViewSet(viewsets.ModelViewSet):
    serializer_class = ShiftReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ShiftReport.objects.all()
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by shift type
        shift_type = self.request.query_params.get('shift_type')
        if shift_type in ['morning', 'night']:
            queryset = queryset.filter(shift_type=shift_type)
        
        # Filter by user (for admin)
        user_id = self.request.query_params.get('user_id')
        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-date', '-created_at')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get shift report summary for current user or all users (admin)"""
        queryset = self.get_queryset()
        
        # Calculate summary metrics
        total_shifts = queryset.count()
        completed_shifts = queryset.filter(is_completed=True).count()
        
        aggregated = queryset.aggregate(
            total_revenue=Sum('total_revenue'),
            total_orders=Sum('orders_handled')
        )
        
        total_revenue = aggregated['total_revenue'] or Decimal('0')
        total_orders = aggregated['total_orders'] or 0
        
        average_revenue_per_shift = Decimal('0')
        if completed_shifts > 0:
            average_revenue_per_shift = total_revenue / completed_shifts
        
        # Find top performer (admin only)
        top_performer = "N/A"
        if request.user.is_staff:
            top_performer_data = queryset.values('user__name').annotate(
                total_rev=Sum('total_revenue')
            ).order_by('-total_rev').first()
            
            if top_performer_data:
                top_performer = top_performer_data['user__name']
        
        summary_data = {
            'total_shifts': total_shifts,
            'completed_shifts': completed_shifts,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'average_revenue_per_shift': average_revenue_per_shift,
            'top_performer': top_performer
        }
        
        serializer = ShiftReportSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_shift(self, request, pk=None):
        """Mark a shift as completed and calculate metrics"""
        shift_report = self.get_object()
        
        # Only allow the user or admin to complete the shift
        if shift_report.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        shift_report.end_time = timezone.now().time()
        shift_report.is_completed = True
        shift_report.calculate_metrics()
        
        # Generate daily report
        DailyReport.generate_for_date(shift_report.date)
        
        serializer = self.get_serializer(shift_report)
        return Response(serializer.data)

class DailyReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate daily report for a specific date"""
        date_str = request.data.get('date')
        if not date_str:
            return Response(
                {'error': 'Date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report = DailyReport.generate_for_date(date)
        serializer = self.get_serializer(report)
        return Response(serializer.data)

class ReportAnalyticsViewSet(viewsets.ViewSet):
    """Analytics endpoints for reports"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics data"""
        # Date range (default to last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Override with query params if provided
        if request.query_params.get('start_date'):
            start_date = datetime.strptime(
                request.query_params.get('start_date'), '%Y-%m-%d'
            ).date()
        
        if request.query_params.get('end_date'):
            end_date = datetime.strptime(
                request.query_params.get('end_date'), '%Y-%m-%d'
            ).date()
        
        # Revenue trend
        daily_reports = DailyReport.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        revenue_trend = []
        orders_trend = []
        
        for report in daily_reports:
            revenue_trend.append({
                'date': report.date.isoformat(),
                'revenue': float(report.total_revenue)
            })
            orders_trend.append({
                'date': report.date.isoformat(),
                'orders': report.total_orders
            })
        
        # Shift comparison
        shift_reports = ShiftReport.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_completed=True
        )
        
        morning_stats = shift_reports.filter(shift_type='morning').aggregate(
            total_revenue=Sum('total_revenue'),
            total_orders=Sum('orders_handled'),
            avg_revenue=Avg('total_revenue')
        )
        
        night_stats = shift_reports.filter(shift_type='night').aggregate(
            total_revenue=Sum('total_revenue'),
            total_orders=Sum('orders_handled'),
            avg_revenue=Avg('total_revenue')
        )
        
        shift_comparison = {
            'morning': {
                'revenue': float(morning_stats['total_revenue'] or 0),
                'orders': morning_stats['total_orders'] or 0,
                'avg_revenue': float(morning_stats['avg_revenue'] or 0)
            },
            'night': {
                'revenue': float(night_stats['total_revenue'] or 0),
                'orders': night_stats['total_orders'] or 0,
                'avg_revenue': float(night_stats['avg_revenue'] or 0)
            }
        }
        
        # Top performing staff
        top_staff = shift_reports.values('user__name').annotate(
            total_revenue=Sum('total_revenue'),
            total_orders=Sum('orders_handled'),
            shift_count=Count('id')
        ).order_by('-total_revenue')[:5]
        
        top_staff_list = []
        for staff in top_staff:
            top_staff_list.append({
                'name': staff['user__name'],
                'revenue': float(staff['total_revenue']),
                'orders': staff['total_orders'],
                'shifts': staff['shift_count']
            })
        
        # Overall performance metrics
        total_revenue = daily_reports.aggregate(
            total=Sum('total_revenue')
        )['total'] or 0
        
        total_orders = daily_reports.aggregate(
            total=Sum('total_orders')
        )['total'] or 0
        
        avg_daily_revenue = float(total_revenue) / len(daily_reports) if daily_reports else 0
        
        performance_metrics = {
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'avg_daily_revenue': avg_daily_revenue,
            'total_days': len(daily_reports)
        }
        
        analytics_data = {
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'revenue_trend': revenue_trend,
            'orders_trend': orders_trend,
            'shift_comparison': shift_comparison,
            'top_staff': top_staff_list,
            'performance_metrics': performance_metrics
        }
        
        serializer = ReportAnalyticsSerializer(analytics_data)
        return Response(serializer.data)