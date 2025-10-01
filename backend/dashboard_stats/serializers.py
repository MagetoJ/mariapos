from rest_framework import serializers
from datetime import datetime
from decimal import Decimal

class DashboardStatsSerializer(serializers.Serializer):
    """Main dashboard statistics"""
    
    # Today's Stats
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_orders = serializers.IntegerField()
    today_guests = serializers.IntegerField()
    today_checkins = serializers.IntegerField()
    
    # Current Status
    active_orders = serializers.IntegerField()
    pending_service_requests = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    occupied_tables = serializers.IntegerField()
    
    # Performance Metrics
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    guest_satisfaction_score = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    staff_productivity = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    
    # Inventory Alerts
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    pending_purchase_orders = serializers.IntegerField()

class SalesDataSerializer(serializers.Serializer):
    """Sales data for charts"""
    
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Breakdown by type
    dine_in_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    takeaway_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_service_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

class CategorySalesSerializer(serializers.Serializer):
    """Sales by menu category"""
    
    category = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders = serializers.IntegerField()
    items_sold = serializers.IntegerField()
    percentage_of_total = serializers.DecimalField(max_digits=5, decimal_places=2)

class PaymentMethodStatsSerializer(serializers.Serializer):
    """Payment method statistics"""
    
    payment_method = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

class TopItemsSerializer(serializers.Serializer):
    """Top selling menu items"""
    
    item_name = serializers.CharField()
    category = serializers.CharField()
    quantity_sold = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)

class StaffPerformanceSerializer(serializers.Serializer):
    """Staff performance metrics"""
    
    staff_name = serializers.CharField()
    role = serializers.CharField()
    orders_served = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=8, decimal_places=2)
    customer_rating = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    service_requests_handled = serializers.IntegerField(default=0)

class GuestStatsSerializer(serializers.Serializer):
    """Guest and room statistics"""
    
    total_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    checkins_today = serializers.IntegerField()
    checkouts_today = serializers.IntegerField()
    expected_arrivals = serializers.IntegerField()
    expected_departures = serializers.IntegerField()
    
    # Guest satisfaction
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    total_feedback = serializers.IntegerField(default=0)

class ServiceRequestStatsSerializer(serializers.Serializer):
    """Service request statistics"""
    
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    in_progress_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    
    # Performance metrics
    average_response_time = serializers.IntegerField()  # minutes
    average_completion_time = serializers.IntegerField()  # minutes
    satisfaction_rating = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    
    # By type
    by_type = serializers.ListField(
        child=serializers.DictField(), required=False
    )

class InventoryStatsSerializer(serializers.Serializer):
    """Inventory statistics"""
    
    total_items = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    overstocked_items = serializers.IntegerField()
    
    total_inventory_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_stock_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Recent movements
    items_received_today = serializers.IntegerField()
    items_used_today = serializers.IntegerField()
    waste_items_today = serializers.IntegerField()
    waste_value_today = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Purchase orders
    pending_po_count = serializers.IntegerField()
    pending_po_value = serializers.DecimalField(max_digits=12, decimal_places=2)

class ComprehensiveReportSerializer(serializers.Serializer):
    """Comprehensive business report"""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    # Revenue Summary
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Breakdown by source
    restaurant_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    room_service_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    other_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Guest metrics
    total_guests = serializers.IntegerField()
    total_nights = serializers.IntegerField()
    average_stay_duration = serializers.DecimalField(max_digits=4, decimal_places=1)
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Service metrics
    service_requests_handled = serializers.IntegerField()
    average_response_time = serializers.IntegerField()
    guest_satisfaction = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    
    # Staff metrics
    total_staff_hours = serializers.DecimalField(max_digits=8, decimal_places=1)
    revenue_per_staff_hour = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    # Inventory metrics
    inventory_turnover = serializers.DecimalField(max_digits=5, decimal_places=2)
    waste_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    food_cost_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

class RealtimeStatsSerializer(serializers.Serializer):
    """Real-time dashboard statistics"""
    
    current_time = serializers.DateTimeField()
    
    # Active metrics
    active_orders = serializers.IntegerField()
    orders_in_kitchen = serializers.IntegerField()
    orders_ready = serializers.IntegerField()
    pending_service_requests = serializers.IntegerField()
    
    # Today's progress
    hours_into_day = serializers.IntegerField()
    revenue_so_far = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders_so_far = serializers.IntegerField()
    guests_checked_in = serializers.IntegerField()
    
    # Capacity utilization
    table_occupancy = serializers.DecimalField(max_digits=5, decimal_places=2)
    room_occupancy = serializers.DecimalField(max_digits=5, decimal_places=2)
    staff_utilization = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    
    # Alerts
    urgent_service_requests = serializers.IntegerField()
    overdue_orders = serializers.IntegerField()
    low_stock_alerts = serializers.IntegerField()

class TrendAnalysisSerializer(serializers.Serializer):
    """Trend analysis data"""
    
    metric_name = serializers.CharField()
    period = serializers.CharField()  # 'daily', 'weekly', 'monthly'
    
    # Trend data points
    data_points = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Trend indicators
    trend_direction = serializers.CharField()  # 'up', 'down', 'stable'
    trend_percentage = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    # Statistical measures
    average_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    median_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    highest_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    lowest_value = serializers.DecimalField(max_digits=12, decimal_places=2)

class BusinessInsightsSerializer(serializers.Serializer):
    """Business insights and recommendations"""
    
    # Revenue insights
    peak_hours = serializers.ListField(child=serializers.IntegerField())
    slow_periods = serializers.ListField(child=serializers.IntegerField())
    best_performing_categories = serializers.ListField(child=serializers.CharField())
    underperforming_items = serializers.ListField(child=serializers.CharField())
    
    # Operational insights
    average_table_turnover = serializers.DecimalField(max_digits=4, decimal_places=1)
    peak_service_request_times = serializers.ListField(child=serializers.IntegerField())
    staff_efficiency_score = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    
    # Guest behavior insights
    popular_room_types = serializers.ListField(child=serializers.CharField())
    average_guest_spending = serializers.DecimalField(max_digits=10, decimal_places=2)
    repeat_guest_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Recommendations
    recommendations = serializers.ListField(
        child=serializers.DictField()
    )

class AlertsSerializer(serializers.Serializer):
    """System alerts and notifications"""
    
    alert_type = serializers.CharField()
    priority = serializers.CharField()  # 'low', 'medium', 'high', 'critical'
    title = serializers.CharField()
    message = serializers.CharField()
    created_at = serializers.DateTimeField()
    is_read = serializers.BooleanField(default=False)
    
    # Related data
    related_entity_type = serializers.CharField(required=False)
    related_entity_id = serializers.CharField(required=False)
    
    # Action required
    action_required = serializers.BooleanField(default=False)
    action_url = serializers.CharField(required=False)