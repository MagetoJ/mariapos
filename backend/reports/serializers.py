from rest_framework import serializers
from .models import ShiftReport, DailyReport, WeeklyReport, MonthlyReport

class ShiftReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    shift_type_display = serializers.CharField(source='get_shift_type_display', read_only=True)
    
    class Meta:
        model = ShiftReport
        fields = [
            'id', 'user', 'user_name', 'shift_type', 'shift_type_display',
            'date', 'start_time', 'end_time', 'orders_handled', 'total_revenue',
            'average_order_value', 'customer_count', 'is_completed', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        fields = [
            'id', 'date', 'total_revenue', 'morning_shift_revenue', 'night_shift_revenue',
            'total_orders', 'morning_shift_orders', 'night_shift_orders',
            'total_customers', 'average_order_value', 'staff_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class WeeklyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReport
        fields = [
            'id', 'week_start', 'week_end', 'total_revenue', 'total_orders',
            'total_customers', 'average_daily_revenue', 'best_day_revenue',
            'best_day_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class MonthlyReportSerializer(serializers.ModelSerializer):
    month_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyReport
        fields = [
            'id', 'month', 'month_name', 'year', 'total_revenue', 'total_orders',
            'total_customers', 'average_daily_revenue', 'revenue_growth_percent',
            'order_growth_percent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_month_name(self, obj):
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[obj.month - 1] if 1 <= obj.month <= 12 else 'Unknown'

class ShiftReportSummarySerializer(serializers.Serializer):
    """Serializer for shift report summaries"""
    total_shifts = serializers.IntegerField()
    completed_shifts = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    average_revenue_per_shift = serializers.DecimalField(max_digits=10, decimal_places=2)
    top_performer = serializers.CharField()
    
class ReportAnalyticsSerializer(serializers.Serializer):
    """Serializer for analytics data"""
    date_range = serializers.DictField()
    revenue_trend = serializers.ListField()
    orders_trend = serializers.ListField()
    shift_comparison = serializers.DictField()
    top_staff = serializers.ListField()
    performance_metrics = serializers.DictField()