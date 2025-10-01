from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid

class DashboardStats(models.Model):
    """Daily dashboard statistics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    
    # Sales metrics
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Order type breakdown
    dine_in_orders = models.PositiveIntegerField(default=0)
    room_service_orders = models.PositiveIntegerField(default=0)
    takeaway_orders = models.PositiveIntegerField(default=0)
    
    # Revenue breakdown
    food_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    beverage_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    service_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taxes_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Guest metrics
    total_guests = models.PositiveIntegerField(default=0)
    new_checkins = models.PositiveIntegerField(default=0)
    checkouts = models.PositiveIntegerField(default=0)
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Service metrics
    service_requests = models.PositiveIntegerField(default=0)
    completed_requests = models.PositiveIntegerField(default=0)
    avg_response_time = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Staff metrics
    active_staff = models.PositiveIntegerField(default=0)
    
    # Inventory alerts
    low_stock_items = models.PositiveIntegerField(default=0)
    out_of_stock_items = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_stats'
        ordering = ['-date']
        verbose_name = 'Dashboard Stats'
        verbose_name_plural = 'Dashboard Stats'
    
    def __str__(self):
        return f"Dashboard Stats - {self.date}"
    
    @classmethod
    def get_or_create_today(cls):
        """Get or create today's dashboard stats"""
        today = timezone.now().date()
        stats, created = cls.objects.get_or_create(date=today)
        if created or stats.updated_at.date() < today:
            stats.calculate_stats()
        return stats
    
    def calculate_stats(self):
        """Calculate all dashboard statistics for the date"""
        from orders.models import Order
        from guests.models import Guest
        from service_requests.models import ServiceRequest
        from inventory.models import InventoryItem
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Date range for calculations
        start_date = timezone.datetime.combine(self.date, timezone.datetime.min.time())
        end_date = timezone.datetime.combine(self.date, timezone.datetime.max.time())
        
        # Orders for the day
        daily_orders = Order.objects.filter(
            created_at__range=[start_date, end_date],
            status__in=['completed', 'served']
        )
        
        # Sales metrics
        self.total_orders = daily_orders.count()
        self.total_sales = sum(order.total_amount for order in daily_orders)
        self.average_order_value = self.total_sales / self.total_orders if self.total_orders > 0 else 0
        
        # Order type breakdown
        self.dine_in_orders = daily_orders.filter(type='dine_in').count()
        self.room_service_orders = daily_orders.filter(type='room_service').count()
        self.takeaway_orders = daily_orders.filter(type='takeaway').count()
        
        # Revenue breakdown calculations would go here
        # For now, simplified calculations
        self.food_revenue = self.total_sales * Decimal('0.7')  # Assume 70% food
        self.beverage_revenue = self.total_sales * Decimal('0.3')  # Assume 30% beverage
        self.service_charges = sum(order.service_charge for order in daily_orders)
        self.taxes_collected = sum(order.tax_amount for order in daily_orders)
        
        # Guest metrics
        guests_today = Guest.objects.filter(actual_checkin__date=self.date)
        self.total_guests = Guest.objects.filter(status='checked_in').count()
        self.new_checkins = guests_today.count()
        self.checkouts = Guest.objects.filter(actual_checkout__date=self.date).count()
        
        # Service request metrics
        requests_today = ServiceRequest.objects.filter(requested_at__date=self.date)
        self.service_requests = requests_today.count()
        self.completed_requests = requests_today.filter(status='completed').count()
        
        # Calculate average response time
        completed_requests = requests_today.filter(
            status='completed',
            acknowledged_at__isnull=False
        )
        if completed_requests.exists():
            total_response_time = sum(
                (req.acknowledged_at - req.requested_at).total_seconds() / 60
                for req in completed_requests
            )
            self.avg_response_time = total_response_time / completed_requests.count()
        
        # Staff metrics
        self.active_staff = User.objects.filter(
            is_active=True,
            role__in=['admin', 'manager', 'waiter', 'kitchen', 'cashier', 'receptionist']
        ).count()
        
        # Inventory alerts
        self.low_stock_items = InventoryItem.objects.filter(
            is_active=True,
            current_stock__lte=models.F('reorder_point')
        ).count()
        
        self.out_of_stock_items = InventoryItem.objects.filter(
            is_active=True,
            current_stock__lte=0
        ).count()
        
        self.save()


class SalesData(models.Model):
    """Daily sales data for charts and analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    
    # Sales breakdown
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mobile_money_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Order counts
    total_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    
    # Time-based sales (for hourly breakdown)
    morning_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 6-12
    afternoon_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 12-18
    evening_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 18-24
    night_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 0-6
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_data'
        ordering = ['-date']
        unique_together = ['date']
        verbose_name = 'Sales Data'
        verbose_name_plural = 'Sales Data'
    
    def __str__(self):
        return f"Sales Data - {self.date}"


class CategorySales(models.Model):
    """Sales data by menu category"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    category = models.ForeignKey('menu.Category', on_delete=models.CASCADE, related_name='sales_data')
    
    # Sales metrics
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_sold = models.PositiveIntegerField(default=0)
    average_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Performance metrics
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'category_sales'
        ordering = ['-date', '-total_sales']
        unique_together = ['date', 'category']
        verbose_name = 'Category Sales'
        verbose_name_plural = 'Category Sales'
    
    def __str__(self):
        return f"{self.category.name} - {self.date}"


class HourlySales(models.Model):
    """Hourly sales data for detailed analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    hour = models.PositiveIntegerField()  # 0-23
    
    # Sales data
    sales_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_count = models.PositiveIntegerField(default=0)
    customer_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hourly_sales'
        ordering = ['-date', '-hour']
        unique_together = ['date', 'hour']
        verbose_name = 'Hourly Sales'
        verbose_name_plural = 'Hourly Sales'
    
    def __str__(self):
        return f"{self.date} {self.hour:02d}:00 - KSh {self.sales_amount}"


class PopularItems(models.Model):
    """Track popular menu items"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE, related_name='popularity_data')
    
    # Popularity metrics
    times_ordered = models.PositiveIntegerField(default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Rankings
    popularity_rank = models.PositiveIntegerField(default=0)
    revenue_rank = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'popular_items'
        ordering = ['-date', 'popularity_rank']
        unique_together = ['date', 'menu_item']
        verbose_name = 'Popular Item'
        verbose_name_plural = 'Popular Items'
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.date} (Rank #{self.popularity_rank})"


class RevenueReport(models.Model):
    """Comprehensive revenue reports"""
    
    REPORT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Revenue metrics
    gross_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_discounts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_refunds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Order metrics
    total_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Department breakdown
    food_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    beverage_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    room_service_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Costs (if tracked)
    cost_of_goods_sold = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labor_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    operational_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Report generation
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='generated_reports'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'revenue_reports'
        ordering = ['-created_at']
        verbose_name = 'Revenue Report'
        verbose_name_plural = 'Revenue Reports'
    
    def __str__(self):
        return f"{self.report_type.title()} Report - {self.start_date} to {self.end_date}"
    
    @property
    def gross_profit(self):
        return self.gross_revenue - self.cost_of_goods_sold
    
    @property
    def profit_margin(self):
        if self.gross_revenue > 0:
            return (self.gross_profit / self.gross_revenue) * 100
        return 0