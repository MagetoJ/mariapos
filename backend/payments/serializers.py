from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import (
    Payment, PaymentRefund, PaymentGateway, PaymentAttempt, 
    PaymentSplit, PaymentReport
)
from accounts.serializers import UserListSerializer
from orders.serializers import OrderListSerializer

class PaymentListSerializer(serializers.ModelSerializer):
    """Simplified payment serializer for list views"""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'order', 'order_number', 'amount',
            'net_amount', 'method', 'status', 'customer', 'customer_name',
            'processed_by', 'processed_by_name', 'processed_at',
            'completed_at', 'refunded_amount', 'created_at'
        ]
        read_only_fields = [
            'id', 'payment_number', 'processed_at', 'completed_at', 'created_at'
        ]

class PaymentDetailSerializer(serializers.ModelSerializer):
    """Full payment serializer with all details"""
    
    customer_data = UserListSerializer(source='customer', read_only=True)
    processed_by_data = UserListSerializer(source='processed_by', read_only=True)
    order_data = OrderListSerializer(source='order', read_only=True)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)
    remaining_refundable_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'order', 'order_data', 'amount',
            'net_amount', 'method', 'status', 'customer', 'customer_data',
            'transaction_reference', 'gateway_reference', 'authorization_code',
            'card_last_four', 'card_brand', 'card_type', 'mobile_money_number',
            'mobile_money_provider', 'processed_by', 'processed_by_data',
            'processed_at', 'completed_at', 'gateway_fee', 'processing_fee',
            'refunded_amount', 'refund_reason', 'can_be_refunded',
            'remaining_refundable_amount', 'notes', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'payment_number', 'net_amount', 'processed_at',
            'completed_at', 'created_at', 'updated_at'
        ]

class PaymentCreateSerializer(serializers.ModelSerializer):
    """Payment serializer for creation"""
    
    class Meta:
        model = Payment
        fields = [
            'order', 'amount', 'method', 'customer', 'transaction_reference',
            'card_last_four', 'card_brand', 'card_type', 'mobile_money_number',
            'mobile_money_provider', 'gateway_fee', 'processing_fee', 'notes', 'metadata'
        ]
    
    def validate_amount(self, value):
        """Ensure amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be positive")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        order = data.get('order')
        amount = data.get('amount')
        
        if order and amount:
            # Check if payment amount doesn't exceed order total
            total_paid = sum(p.amount for p in order.payments.filter(status='completed'))
            remaining_amount = order.total_amount - total_paid
            
            if amount > remaining_amount:
                raise serializers.ValidationError(
                    f"Payment amount (KSh {amount}) exceeds remaining order amount (KSh {remaining_amount})"
                )
        
        return data

class PaymentUpdateSerializer(serializers.ModelSerializer):
    """Payment serializer for updates"""
    
    class Meta:
        model = Payment
        fields = [
            'status', 'transaction_reference', 'gateway_reference',
            'authorization_code', 'processed_by', 'gateway_fee',
            'processing_fee', 'notes', 'metadata'
        ]

class PaymentProcessingSerializer(serializers.Serializer):
    """Serializer for payment processing"""
    
    gateway_reference = serializers.CharField(max_length=100, required=False)
    authorization_code = serializers.CharField(max_length=50, required=False)
    notes = serializers.CharField(max_length=500, required=False)
    
    def validate(self, data):
        payment = self.context.get('payment')
        if not payment:
            return data
        
        if payment.status not in ['pending', 'processing']:
            raise serializers.ValidationError(
                f"Cannot process payment with status: {payment.status}"
            )
        
        return data

class PaymentRefundSerializer(serializers.ModelSerializer):
    """Payment refund serializer"""
    
    payment_number = serializers.CharField(source='payment.payment_number', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.name', read_only=True)
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'refund_number', 'payment', 'payment_number', 'amount',
            'reason', 'status', 'processed_by', 'processed_by_name',
            'gateway_reference', 'gateway_fee', 'processed_at',
            'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'refund_number', 'processed_at', 'completed_at',
            'created_at', 'updated_at'
        ]

class PaymentRefundCreateSerializer(serializers.Serializer):
    """Serializer for creating refunds"""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField(max_length=500)
    
    def validate_amount(self, value):
        """Validate refund amount"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Refund amount must be positive")
        return value
    
    def validate(self, data):
        payment = self.context.get('payment')
        if not payment:
            return data
        
        if not payment.can_be_refunded:
            raise serializers.ValidationError("Payment cannot be refunded")
        
        amount = data.get('amount')
        if amount and amount > payment.remaining_refundable_amount:
            raise serializers.ValidationError(
                f"Refund amount (KSh {amount}) exceeds refundable amount (KSh {payment.remaining_refundable_amount})"
            )
        
        return data

class PaymentGatewaySerializer(serializers.ModelSerializer):
    """Payment gateway serializer"""
    
    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'name', 'gateway_type', 'is_active', 'is_test_mode',
            'supports_cards', 'supports_mobile_money', 'supports_bank_transfers',
            'transaction_fee_fixed', 'transaction_fee_percent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    """Payment gateway configuration serializer (includes settings)"""
    
    calculated_fee = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'name', 'gateway_type', 'is_active', 'is_test_mode',
            'settings', 'supports_cards', 'supports_mobile_money',
            'supports_bank_transfers', 'transaction_fee_fixed',
            'transaction_fee_percent', 'calculated_fee', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'settings': {'write_only': True}
        }
    
    def get_calculated_fee(self, obj):
        """Calculate fee for a sample amount"""
        sample_amount = Decimal('1000.00')  # KSh 1,000
        return obj.calculate_fee(sample_amount)

class PaymentAttemptSerializer(serializers.ModelSerializer):
    """Payment attempt serializer"""
    
    payment_number = serializers.CharField(source='payment.payment_number', read_only=True)
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    
    class Meta:
        model = PaymentAttempt
        fields = [
            'id', 'payment', 'payment_number', 'attempt_number',
            'status', 'gateway', 'gateway_name', 'gateway_response',
            'error_message', 'error_code', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']

class PaymentSplitSerializer(serializers.ModelSerializer):
    """Payment split serializer"""
    
    payment_number = serializers.CharField(source='payment.payment_number', read_only=True)
    
    class Meta:
        model = PaymentSplit
        fields = [
            'id', 'payment', 'payment_number', 'recipient_name',
            'recipient_account', 'amount', 'percentage',
            'is_processed', 'processed_at', 'created_at'
        ]
        read_only_fields = ['id', 'processed_at', 'created_at']

class PaymentReportSerializer(serializers.ModelSerializer):
    """Payment report serializer"""
    
    class Meta:
        model = PaymentReport
        fields = [
            'id', 'report_type', 'start_date', 'end_date', 'total_payments',
            'total_amount', 'total_fees', 'total_refunds', 'net_amount',
            'completed_payments', 'failed_payments', 'pending_payments',
            'generated_by_name', 'report_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PaymentStatsSerializer(serializers.Serializer):
    """Payment statistics serializer"""
    
    total_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    completed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    total_refunds = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Method breakdown
    method_breakdown = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    
    # Daily trends
    daily_trends = serializers.ListField(
        child=serializers.DictField(), required=False
    )

class PaymentMethodStatsSerializer(serializers.Serializer):
    """Payment method statistics"""
    
    method = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

class PaymentReceiptSerializer(serializers.Serializer):
    """Payment receipt data serializer"""
    
    payment_number = serializers.CharField()
    order_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    method = serializers.CharField()
    status = serializers.CharField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    processed_by = serializers.CharField()
    processed_at = serializers.DateTimeField()
    transaction_reference = serializers.CharField(required=False)
    
    # Order details
    order_items = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    
    # Business details
    business_name = serializers.CharField(default="Maria Havens Hotel & Restaurant")
    business_address = serializers.CharField(required=False)
    business_phone = serializers.CharField(required=False)

class MobileMoneyPaymentSerializer(serializers.Serializer):
    """Mobile money payment initialization"""
    
    phone_number = serializers.CharField(max_length=17)
    provider = serializers.ChoiceField(
        choices=[
            ('mpesa', 'M-Pesa'),
            ('airtel_money', 'Airtel Money'),
            ('tkash', 'T-Kash'),
        ]
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        import re
        if not re.match(r'^\+?254[0-9]{9}$|^07[0-9]{8}$', value):
            raise serializers.ValidationError(
                "Please enter a valid Kenyan phone number"
            )
        return value
    
    def validate_amount(self, value):
        """Validate payment amount"""
        if value < 1:
            raise serializers.ValidationError("Minimum amount is KSh 1")
        if value > 150000:
            raise serializers.ValidationError("Maximum amount is KSh 150,000")
        return value

class CardPaymentSerializer(serializers.Serializer):
    """Card payment processing"""
    
    card_number = serializers.CharField(max_length=19)
    expiry_month = serializers.IntegerField(min_value=1, max_value=12)
    expiry_year = serializers.IntegerField(min_value=2024)
    cvv = serializers.CharField(max_length=4)
    cardholder_name = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_card_number(self, value):
        """Basic card number validation"""
        # Remove spaces and dashes
        card_number = value.replace(' ', '').replace('-', '')
        
        if not card_number.isdigit():
            raise serializers.ValidationError("Card number must contain only digits")
        
        if len(card_number) < 13 or len(card_number) > 19:
            raise serializers.ValidationError("Invalid card number length")
        
        return card_number
    
    def validate_cvv(self, value):
        """Validate CVV"""
        if not value.isdigit() or len(value) not in [3, 4]:
            raise serializers.ValidationError("CVV must be 3 or 4 digits")
        return value
    
    def validate(self, data):
        """Validate expiry date"""
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        expiry_year = data.get('expiry_year')
        expiry_month = data.get('expiry_month')
        
        if expiry_year < current_year:
            raise serializers.ValidationError("Card has expired")
        
        if expiry_year == current_year and expiry_month < current_month:
            raise serializers.ValidationError("Card has expired")
        
        return data