"""
Payments views using raw SQL (No ORM)
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from decimal import Decimal
from utils.db_utils import execute_query, execute_query_one, execute_update
from .models import Payment, Wallet
from .serializers import PaymentSerializer, WalletSerializer
from accounts.decorators import login_required
import json


class PaymentViewSet(viewsets.ViewSet):
    """ViewSet for managing payments using raw SQL"""
    lookup_value_regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    @action(detail=False, methods=['get'], url_path='listing')
    def listing(self, request):
        """List all payments, can be based on filters"""
        query = "SELECT * FROM payments WHERE 1=1"
        params = []
        if status_param := request.query_params.get('status'):
            query += " AND status = %s"
            params.append(status_param)
        if booking_id := request.query_params.get('booking_id'):
            query += " AND booking_id = %s"
            params.append(booking_id)
        query += " ORDER BY payment_time DESC"
        payments = execute_query(query, tuple(params))
        return Response(PaymentSerializer(payments, many=True).data)
    
    def create(self, request):
        """Create a new payment"""
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED if payment else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def get_and_validate_wallet(self, payment):
        """Get wallet and check sufficient balance for payment"""
        wallet = execute_query_one("SELECT * FROM wallets " \
        "                           WHERE id = %s", 
                                    (payment['wallet_id'],))
        if wallet['balance'] < payment['amount']:
            return Response({
                'error': 'Insufficient balance',
                'required': str(payment['amount']),
                'available': str(wallet['balance'])
            }, status=status.HTTP_400_BAD_REQUEST)
        return wallet

    @action(detail=True, methods=['get'], url_path='check-status')
    def check_status(self, request, pk=None):
        """Check if payment is successful"""
        payment = Payment.get_payment(pk)
        return Response({
            'payment_id': pk,
            'status': payment['status']
        })

    @action(detail=True, methods=['put', 'patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """update from pending to completed"""
        payment = Payment.get_payment(pk)
        if not payment:
            raise NotFound('Payment not found')

        if payment['status'] == 'Completed':
            return Response({'error': 'Payment is already completed.'},
                        status=status.HTTP_400_BAD_REQUEST)

        success = Payment.mark_as_completed(pk)

        if not success:
            return Response({'error': 'Failed to update payment status'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        updated_payment = Payment.get_payment(pk)
        return Response(PaymentSerializer(updated_payment).data)


class WalletViewSet(viewsets.ViewSet):
    """ViewSet for managing wallets"""
    lookup_value_regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    def create(self, request):
        """Create a new wallet"""
        serializer = WalletSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet = serializer.save()
        return Response(
            WalletSerializer(wallet).data,
            status=status.HTTP_201_CREATED if wallet else status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def retrieve(self, request, pk=None):
        """Retrieve wallet by ID"""
        wallet = self._get_wallet_by_id(pk)
        if not wallet:
            raise NotFound('Wallet not found')
        return Response(WalletSerializer(wallet).data)

    @action(detail=False, methods=['get'], url_path='my-wallet')
    def my_wallet(self, request):
        """Get or create current user's wallet"""
        user_id = request.query_params.get('user_id', 2)
        wallet = Wallet.create(int(user_id))
        return Response(WalletSerializer(wallet).data if wallet
                       else {'error': 'Failed to create wallet'},
                       status=status.HTTP_200_OK if wallet else status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get current user's wallet balance"""
        user_id = request.query_params.get('user_id', 2)
        balance = Wallet.get_balance(int(user_id))
        if balance is None:
            Wallet.create(user_id=int(user_id))
            balance = Decimal('0.00')

        return Response({'user_id': int(user_id), 'balance': str(balance)})

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        """Deposit money to user's wallet"""
        user_id = request.data.get('user_id')
        amount_data = request.data.get('amount')
        amount, error = self._validate_amount(amount_data)
        if error:
            return error
        if not Wallet.deposit(int(user_id), amount):
            return Response({'error': 'Failed to deposit'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            'message': 'Deposit successful',
            'wallet': WalletSerializer(self._get_wallet_by_user_id(int(user_id))).data
        })

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """Withdraw money from current user's wallet"""
        user_id = request.data.get('user_id')
        amount_data = request.data.get('amount')
        amount, error = self._validate_amount(amount_data)
        if error:
            return error
        wallet = self._get_wallet_by_user_id(int(user_id))
        if amount > wallet['balance']:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        if not Wallet.withdraw(int(user_id), amount):
            return Response({'error': 'Failed to withdraw'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'Withdrawal successful',
            'wallet': WalletSerializer(self._get_wallet_by_user_id(int(user_id))).data
        })

    def _validate_amount(self, amount_data):
        """Validate transaction amount"""
        amount = Decimal(str(amount_data or 0))
        if amount <= Decimal('0.00'):
            return None, Response({'error': 'Amount must be greater than zero'},
                                status=status.HTTP_400_BAD_REQUEST)
        return amount, None

    def _get_wallet_by_id(self, wallet_id):
        return execute_query_one("SELECT * FROM wallets WHERE id = %s", (wallet_id,))

    def _get_wallet_by_user_id(self, user_id):
        return execute_query_one("SELECT * FROM wallets WHERE user_id = %s", (user_id,))


@require_http_methods(["POST"])
def update_payment_method(request, payment_id):
    """Update payment method for a payment - allows guest users"""
    try:
        # Get payment
        payment = Payment.get_payment(payment_id)
        if not payment:
            return JsonResponse({'error': 'Payment not found'}, status=404)

        # Check if guest user has session or logged-in user
        from accounts.utils import get_current_user
        current_user = get_current_user(request)
        is_guest_session = request.session.get('guest_payment_id') == payment_id

        if not current_user and not is_guest_session:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Parse request body
        data = json.loads(request.body)
        payment_method = data.get('payment_method')

        if not payment_method:
            return JsonResponse({'error': 'Payment method is required'}, status=400)

        # Validate payment method
        valid_methods = [method[0] for method in Payment.PAYMENT_METHODS]
        if payment_method not in valid_methods:
            return JsonResponse({'error': 'Invalid payment method'}, status=400)

        # Update payment method
        query = "UPDATE payments SET payment_method = %s WHERE id = %s"
        success = execute_update(query, (payment_method, payment_id))

        if success:
            return JsonResponse({
                'success': True,
                'message': 'Payment method updated successfully',
                'payment_method': payment_method
            })
        else:
            return JsonResponse({'error': 'Failed to update payment method'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    