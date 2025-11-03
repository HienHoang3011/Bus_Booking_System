"""
Payment serializers for dictionary data (No ORM)
"""
from rest_framework import serializers
from .models import Payment, Wallet
from decimal import Decimal


class PaymentSerializer(serializers.Serializer):
    """Serializer for Payment dictionary data"""
    id = serializers.UUIDField(read_only=True)
    booking_id = serializers.UUIDField(required=True)
    wallet_id = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=0, required=True)
    payment_method = serializers.ChoiceField(
        choices=[choice[0] for choice in Payment.PAYMENT_METHODS],
        required=True
    )
    payment_method_display = serializers.SerializerMethodField(read_only=True)
    status = serializers.ChoiceField(
        choices=[choice[0] for choice in Payment.STATUS_CHOICES],
        default='Pending'
    )
    status_display = serializers.SerializerMethodField(read_only=True)
    payment_time = serializers.DateTimeField(read_only=True)
    transaction_code = serializers.CharField(max_length=100, required=True)

    def get_payment_method_display(self, obj):
        """
        Get payment method display name
        Ex: MBbank -> Ngân hàng Quân Đội
        """
        payment_method = obj['payment_method']
        for choice in Payment.PAYMENT_METHODS:
            if choice[0] == payment_method:
                return choice[1]
        return ''

    def get_status_display(self, obj):
        """Get status display name of payment"""
        status = obj['status']
        for choice in Payment.STATUS_CHOICES:
            if choice[0] == status:
                return choice[1]
        return ''

    def validate_amount(self, value):
        """Validate payment amount is positive"""
        if value <= Decimal('0.00'):
            raise serializers.ValidationError('Payment amount must be greater than zero.')
        return value

    def create(self, validated_data):
        """Create a new payment"""
        wallet_id = validated_data.get('wallet_id')
        return Payment.create(
            booking_id=validated_data['booking_id'],
            amount=validated_data['amount'],
            payment_method=validated_data['payment_method'],
            transaction_code=validated_data['transaction_code'],
            wallet_id=str(wallet_id) if wallet_id else None,
            status=validated_data.get('status', 'Pending')
        )


class WalletSerializer(serializers.Serializer):
    """Serializer for Wallet dictionary data"""
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.IntegerField(required=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=0, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """Create a new wallet"""
        return Wallet.create(
            user_id=validated_data['user_id'],
            balance=validated_data.get('balance', Decimal('0.00'))
        )


class WalletTransactionSerializer(serializers.Serializer):
    """Serializer for wallet transactions (deposit/withdraw)"""
    user_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    transaction_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Wallet.TRANSACTION_TYPES],
        required=True
    )

    def validate_amount(self, value):
        """Validate transaction amount is positive"""
        if value <= Decimal('0.00'):
            raise serializers.ValidationError('Transaction amount must be greater than zero.')
        return value