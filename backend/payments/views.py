from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from accounts.permissions import IsManagerOrAdmin, IsStaffMember, IsCashierOrAbove
from .models import (
    Payment, PaymentRefund, PaymentGateway, PaymentAttempt, 
    PaymentSplit, PaymentReport
)
from .serializers import (
    PaymentListSerializer, PaymentDetailSerializer, PaymentCreateSerializer,
    PaymentUpdateSerializer, PaymentProcessingSerializer, PaymentRefundSerializer,
    PaymentRefundCreateSerializer, PaymentGatewaySerializer,
    PaymentGatewayConfigSerializer, PaymentAttemptSerializer,
    PaymentSplitSerializer, PaymentReportSerializer, PaymentStatsSerializer,
    PaymentMethodStatsSerializer, PaymentReceiptSerializer,
    MobileMoneyPaymentSerializer, CardPaymentSerializer
)

class PaymentViewSet(ModelViewSet):
    """
    ViewSet for managing payments
    """
    queryset = Payment.objects.all().select_related(
        'order', 'customer', 'processed_by'
    ).prefetch_related('refunds', 'attempts')
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PaymentUpdateSerializer
        elif self.action == 'process':
            return PaymentProcessingSerializer
        return PaymentDetailSerializer
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'process', 'refund']:
            permission_classes = [permissions.IsAuthenticated, IsCashierOrAbove]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by method
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(method=method)
        
        # Filter by customer
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer_id=customer)
        
        # Filter by processed by
        processed_by = self.request.query_params.get('processed_by')
        if processed_by:
            queryset = queryset.filter(processed_by_id=processed_by)
        
        # Filter by order
        order = self.request.query_params.get('order')
        if order:
            queryset = queryset.filter(order_id=order)
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(payment_number__icontains=search) |
                Q(transaction_reference__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__email__icontains=search) |
                Q(order__order_number__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set default values when creating payment"""
        payment = serializer.save()
        
        # Auto-process cash payments
        if payment.method == 'cash':
            payment.processed_by = self.request.user
            payment.processed_at = timezone.now()
            payment.process_payment()
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a pending payment"""
        payment = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'payment': payment})
        
        if serializer.is_valid():
            with transaction.atomic():
                # Update payment with processing details
                gateway_reference = serializer.validated_data.get('gateway_reference')
                authorization_code = serializer.validated_data.get('authorization_code')
                notes = serializer.validated_data.get('notes')
                
                if gateway_reference:
                    payment.gateway_reference = gateway_reference
                if authorization_code:
                    payment.authorization_code = authorization_code
                if notes:
                    payment.notes = notes
                
                payment.processed_by = request.user
                payment.processed_at = timezone.now()
                payment.process_payment()
            
            return Response({
                'message': 'Payment processed successfully',
                'payment': PaymentDetailSerializer(payment).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process a refund for this payment"""
        payment = self.get_object()
        serializer = PaymentRefundCreateSerializer(
            data=request.data, 
            context={'payment': payment}
        )
        
        if serializer.is_valid():
            amount = serializer.validated_data.get('amount')
            reason = serializer.validated_data['reason']
            
            try:
                with transaction.atomic():
                    payment.refund(amount=amount, reason=reason)
                    
                    # Get the latest refund record
                    refund = payment.refunds.latest('created_at')
                    refund.processed_by = request.user
                    refund.processed_at = timezone.now()
                    refund.save()
                
                return Response({
                    'message': 'Refund processed successfully',
                    'refund': PaymentRefundSerializer(refund).data,
                    'payment': PaymentDetailSerializer(payment).data
                })
            
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a payment"""
        payment = self.get_object()
        
        if payment.status not in ['pending', 'processing']:
            return Response(
                {'error': f'Cannot cancel payment with status: {payment.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'cancelled'
        payment.notes = request.data.get('reason', 'Payment cancelled by staff')
        payment.save()
        
        return Response({
            'message': 'Payment cancelled successfully',
            'payment': PaymentDetailSerializer(payment).data
        })
    
    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """Generate payment receipt data"""
        payment = self.get_object()
        
        # Prepare receipt data
        receipt_data = {
            'payment_number': payment.payment_number,
            'order_number': payment.order.order_number,
            'amount': payment.amount,
            'method': payment.get_method_display(),
            'status': payment.get_status_display(),
            'customer_name': payment.customer.name,
            'customer_email': payment.customer.email,
            'processed_by': payment.processed_by.name if payment.processed_by else '',
            'processed_at': payment.processed_at,
            'transaction_reference': payment.transaction_reference,
        }
        
        # Add order items if available
        if payment.order:
            order_items = []
            for item in payment.order.items.all():
                order_items.append({
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'total': item.total_price
                })
            receipt_data['order_items'] = order_items
        
        serializer = PaymentReceiptSerializer(receipt_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payment statistics"""
        # Date range
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        payments_in_range = self.get_queryset().filter(
            created_at__date__range=[start_date, end_date]
        )
        
        # Basic stats
        total_payments = payments_in_range.count()
        total_amount = payments_in_range.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        completed_payments = payments_in_range.filter(status='completed').count()
        pending_payments = payments_in_range.filter(status='pending').count()
        failed_payments = payments_in_range.filter(status='failed').count()
        
        total_refunds = payments_in_range.aggregate(
            total=Sum('refunded_amount')
        )['total'] or Decimal('0.00')
        
        net_revenue = total_amount - total_refunds
        
        avg_payment_amount = total_amount / total_payments if total_payments > 0 else Decimal('0.00')
        
        # Method breakdown
        method_breakdown = list(
            payments_in_range.values('method')
            .annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
            .order_by('-total_amount')
        )
        
        # Calculate percentages
        for method_stat in method_breakdown:
            if total_amount > 0:
                method_stat['percentage'] = float(
                    (method_stat['total_amount'] / total_amount) * 100
                )
            else:
                method_stat['percentage'] = 0
        
        # Daily trends
        from django.db.models.functions import TruncDate
        daily_trends = list(
            payments_in_range.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id'),
                total_amount=Sum('amount'),
                completed=Count('id', filter=Q(status='completed'))
            ).order_by('date')
        )
        
        stats_data = {
            'total_payments': total_payments,
            'total_amount': total_amount,
            'completed_payments': completed_payments,
            'pending_payments': pending_payments,
            'failed_payments': failed_payments,
            'total_refunds': total_refunds,
            'net_revenue': net_revenue,
            'avg_payment_amount': avg_payment_amount,
            'method_breakdown': method_breakdown,
            'daily_trends': daily_trends
        }
        
        serializer = PaymentStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending payments"""
        pending_payments = self.get_queryset().filter(status='pending')
        
        serializer = PaymentListSerializer(pending_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily payment summary"""
        today = timezone.now().date()
        
        today_payments = self.get_queryset().filter(created_at__date=today)
        
        summary = {
            'date': today,
            'total_payments': today_payments.count(),
            'completed_payments': today_payments.filter(status='completed').count(),
            'pending_payments': today_payments.filter(status='pending').count(),
            'failed_payments': today_payments.filter(status='failed').count(),
            'total_amount': today_payments.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00'),
            'completed_amount': today_payments.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
        }
        
        # Method breakdown for today
        method_stats = list(
            today_payments.values('method')
            .annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
            .order_by('-total_amount')
        )
        summary['method_breakdown'] = method_stats
        
        return Response(summary)

class PaymentRefundViewSet(ReadOnlyModelViewSet):
    """ViewSet for payment refunds (read-only)"""
    
    queryset = PaymentRefund.objects.all().select_related('payment', 'processed_by')
    serializer_class = PaymentRefundSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffMember]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by payment
        payment = self.request.query_params.get('payment')
        if payment:
            queryset = queryset.filter(payment_id=payment)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')

class PaymentGatewayViewSet(ModelViewSet):
    """ViewSet for payment gateways"""
    
    queryset = PaymentGateway.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentGatewayConfigSerializer
        return PaymentGatewaySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter active gateways
        active_only = self.request.query_params.get('active_only')
        if active_only is None or active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        # Filter by gateway type
        gateway_type = self.request.query_params.get('gateway_type')
        if gateway_type:
            queryset = queryset.filter(gateway_type=gateway_type)
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test gateway connection"""
        gateway = self.get_object()
        
        # Placeholder for actual gateway testing logic
        # In a real implementation, this would test the connection to each gateway
        
        return Response({
            'gateway': gateway.name,
            'status': 'connected' if gateway.is_active else 'disconnected',
            'test_mode': gateway.is_test_mode,
            'message': f'Gateway {gateway.name} is ready for processing'
        })

class MobileMoneyPaymentView(APIView):
    """Handle mobile money payment initialization"""
    
    permission_classes = [permissions.IsAuthenticated, IsCashierOrAbove]
    
    def post(self, request):
        serializer = MobileMoneyPaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            provider = serializer.validated_data['provider']
            amount = serializer.validated_data['amount']
            
            # Placeholder for actual mobile money integration
            # In a real implementation, this would integrate with M-Pesa, Airtel Money, etc.
            
            # Simulate payment initialization
            transaction_reference = f"MM{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            response_data = {
                'status': 'initiated',
                'message': f'Payment request sent to {phone_number}',
                'transaction_reference': transaction_reference,
                'provider': provider,
                'amount': amount,
                'instructions': f'Check your {provider} app or dial *XXX# to complete payment'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CardPaymentView(APIView):
    """Handle card payment processing"""
    
    permission_classes = [permissions.IsAuthenticated, IsCashierOrAbove]
    
    def post(self, request):
        serializer = CardPaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            # Placeholder for actual card processing
            # In a real implementation, this would integrate with Stripe, Flutterwave, etc.
            
            card_number = serializer.validated_data['card_number']
            amount = serializer.validated_data['amount']
            
            # Simulate card processing
            transaction_reference = f"CD{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            response_data = {
                'status': 'processing',
                'message': 'Card payment is being processed',
                'transaction_reference': transaction_reference,
                'card_last_four': card_number[-4:],
                'amount': amount,
                'estimated_completion': timezone.now() + timedelta(seconds=30)
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentReportsView(APIView):
    """Payment reports and analytics"""
    
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    
    def get(self, request):
        # Date range parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        payments = Payment.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        
        # Overall statistics
        total_payments = payments.count()
        total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        completed_amount = payments.filter(status='completed').aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        
        # Status breakdown
        status_breakdown = list(
            payments.values('status')
            .annotate(count=Count('id'), total_amount=Sum('amount'))
            .order_by('-total_amount')
        )
        
        # Payment method analysis
        method_breakdown = list(
            payments.values('method')
            .annotate(count=Count('id'), total_amount=Sum('amount'))
            .order_by('-total_amount')
        )
        
        # Daily trends
        from django.db.models.functions import TruncDate
        daily_trends = list(
            payments.annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                total_payments=Count('id'),
                total_amount=Sum('amount'),
                completed_amount=Sum(
                    'amount', 
                    filter=Q(status='completed')
                )
            )
            .order_by('date')
        )
        
        # Top customers by payment amount
        top_customers = list(
            payments.values(
                'customer__name', 'customer__email'
            ).annotate(
                total_spent=Sum('amount'),
                payment_count=Count('id')
            ).order_by('-total_spent')[:10]
        )
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_payments': total_payments,
                'total_amount': total_amount,
                'completed_amount': completed_amount,
                'completion_rate': (
                    payments.filter(status='completed').count() / total_payments * 100
                    if total_payments > 0 else 0
                )
            },
            'status_breakdown': status_breakdown,
            'method_breakdown': method_breakdown,
            'daily_trends': daily_trends,
            'top_customers': top_customers,
            'generated_at': timezone.now()
        })