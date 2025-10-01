from django.contrib import admin
from .models import ShiftReport, DailyReport, WeeklyReport, MonthlyReport

@admin.register(ShiftReport)
class ShiftReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'shift_type', 'date', 'orders_handled', 'total_revenue', 'is_completed']
    list_filter = ['shift_type', 'date', 'is_completed', 'user']
    search_fields = ['user__name', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'shift_type', 'date', 'start_time', 'end_time', 'is_completed')
        }),
        ('Performance Metrics', {
            'fields': ('orders_handled', 'total_revenue', 'average_order_value', 'customer_count'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_revenue', 'total_orders', 'total_customers', 'staff_count']
    list_filter = ['date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('date',)
        }),
        ('Revenue Metrics', {
            'fields': ('total_revenue', 'morning_shift_revenue', 'night_shift_revenue', 'average_order_value')
        }),
        ('Order Metrics', {
            'fields': ('total_orders', 'morning_shift_orders', 'night_shift_orders', 'total_customers')
        }),
        ('Staff Metrics', {
            'fields': ('staff_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ['week_start', 'week_end', 'total_revenue', 'total_orders', 'average_daily_revenue']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['month', 'year', 'total_revenue', 'total_orders', 'revenue_growth_percent']
    list_filter = ['year', 'month']
    readonly_fields = ['id', 'created_at', 'updated_at']