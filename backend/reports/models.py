from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Avg
from django.utils import timezone
import uuid

User = get_user_model()

class ShiftReport(models.Model):
    """Daily shift reports for tracking staff performance"""
    SHIFT_CHOICES = [
        ('morning', 'Morning Shift'),
        ('night', 'Night Shift'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shift_type = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    
    # Performance metrics
    orders_handled = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    customer_count = models.IntegerField(default=0)
    
    # Status and notes
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date', 'shift_type']
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date', 'shift_type']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['is_completed']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.shift_type} - {self.date}"
    
    def calculate_metrics(self):
        """Calculate performance metrics from orders"""
        from orders.models import Order
        
        orders = Order.objects.filter(
            staff_member=self.user,
            created_at__date=self.date,
            created_at__time__gte=self.start_time
        )
        
        if self.end_time:
            orders = orders.filter(created_at__time__lte=self.end_time)
        
        self.orders_handled = orders.count()
        self.total_revenue = orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        if self.orders_handled > 0:
            self.average_order_value = self.total_revenue / self.orders_handled
        
        # Count unique customers (assuming orders have customer field)
        self.customer_count = orders.values('customer').distinct().count()
        
        self.save()

class DailyReport(models.Model):
    """Daily summary reports for the entire restaurant"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    morning_shift_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    night_shift_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Order metrics
    total_orders = models.IntegerField(default=0)
    morning_shift_orders = models.IntegerField(default=0)
    night_shift_orders = models.IntegerField(default=0)
    
    # Customer metrics
    total_customers = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Staff metrics
    staff_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Daily Report - {self.date}"
    
    @classmethod
    def generate_for_date(cls, date):
        """Generate daily report for a specific date"""
        from orders.models import Order
        
        report, created = cls.objects.get_or_create(date=date)
        
        # Get all orders for the date
        orders = Order.objects.filter(created_at__date=date)
        
        # Calculate totals
        report.total_orders = orders.count()
        report.total_revenue = orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        if report.total_orders > 0:
            report.average_order_value = report.total_revenue / report.total_orders
        
        # Calculate shift-specific metrics
        shift_reports = ShiftReport.objects.filter(date=date)
        
        morning_reports = shift_reports.filter(shift_type='morning')
        night_reports = shift_reports.filter(shift_type='night')
        
        report.morning_shift_revenue = morning_reports.aggregate(
            total=Sum('total_revenue')
        )['total'] or 0
        
        report.night_shift_revenue = night_reports.aggregate(
            total=Sum('total_revenue')
        )['total'] or 0
        
        report.morning_shift_orders = morning_reports.aggregate(
            total=Sum('orders_handled')
        )['total'] or 0
        
        report.night_shift_orders = night_reports.aggregate(
            total=Sum('orders_handled')
        )['total'] or 0
        
        # Count unique customers
        report.total_customers = orders.values('customer').distinct().count()
        
        # Count staff who worked
        report.staff_count = shift_reports.values('user').distinct().count()
        
        report.save()
        return report

class WeeklyReport(models.Model):
    """Weekly summary reports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    week_start = models.DateField()
    week_end = models.DateField()
    
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    total_customers = models.IntegerField(default=0)
    average_daily_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Best performing metrics
    best_day_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    best_day_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-week_start']
        unique_together = ['week_start', 'week_end']
    
    def __str__(self):
        return f"Weekly Report - {self.week_start} to {self.week_end}"

class MonthlyReport(models.Model):
    """Monthly summary reports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    total_customers = models.IntegerField(default=0)
    average_daily_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Growth metrics
    revenue_growth_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    order_growth_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"Monthly Report - {self.month}/{self.year}"