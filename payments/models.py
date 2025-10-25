"""
Payments models using raw SQL (No ORM)
"""
from utils.db_utils import (
    execute_query, execute_query_one,
    execute_insert, execute_update, execute_delete,
    build_where_clause, build_order_clause
)
from typing import List, Dict, Any, Optional
from datetime import datetime
from django.utils.timezone import now
from decimal import Decimal
import uuid


class Payment:
    """Payment model using raw SQL"""

    TABLE_NAME = 'payments'
    PAYMENT_METHODS = [
        ('Credit Card', 'Thẻ tín dụng'),
        ('PayPal', 'PayPal'),
        ('Bank Transfer', 'Chuyển khoản ngân hàng'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Chờ xử lý'),
        ('Completed', 'Hoàn thành'),
        ('Failed', 'Thất bại'),
    ]

    @classmethod
    def create(cls, booking_id: str, amount: Decimal, payment_method: str,
               transaction_code: str, status: str = 'Pending') -> Dict[str, Any]:
        """Create a new payment"""
        payment_id = str(uuid.uuid4())
        payment_time = now()

        query = f"""
            INSERT INTO {cls.TABLE_NAME}
            (id, booking_id, amount, payment_method, transaction_code, status, payment_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, booking_id, amount, payment_method, transaction_code, status, payment_time
        """
        result = execute_query(query, (payment_id, booking_id, amount, payment_method,
                                      transaction_code, status, payment_time))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by ID with booking details"""
        query = f"""
            SELECT
                p.id, p.booking_id, p.amount, p.payment_method, p.transaction_code,
                p.status, p.payment_time,
                b.user_id, b.trip_id, b.number_of_seats, b.total_amount as booking_amount,
                b.booking_time, b.status as booking_status
            FROM {cls.TABLE_NAME} p
            JOIN bookings b ON p.booking_id = b.id
            WHERE p.id = %s
        """
        return execute_query_one(query, (payment_id,))

    @classmethod
    def get_all(cls, booking_id: str = None, status: str = None,
                payment_method: str = None, ordering: List[str] = None) -> List[Dict[str, Any]]:
        """Get all payments with optional filters"""
        conditions = []
        params = []

        if booking_id is not None:
            conditions.append("p.booking_id = %s")
            params.append(booking_id)
        if status:
            conditions.append("p.status = %s")
            params.append(status)
        if payment_method:
            conditions.append("p.payment_method = %s")
            params.append(payment_method)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        order_clause = build_order_clause(ordering or ['-payment_time'])

        query = f"""
            SELECT
                p.id, p.booking_id, p.amount, p.payment_method, p.transaction_code,
                p.status, p.payment_time,
                b.user_id, b.trip_id, b.number_of_seats, b.total_amount as booking_amount,
                b.booking_time, b.status as booking_status
            FROM {cls.TABLE_NAME} p
            JOIN bookings b ON p.booking_id = b.id
            {where_clause}
            {order_clause}
        """

        return execute_query(query, tuple(params))

    @classmethod
    def get_by_booking_id(cls, booking_id: str) -> List[Dict[str, Any]]:
        """Get all payments for a booking"""
        return cls.get_all(booking_id=booking_id)

    @classmethod
    def update(cls, payment_id: str, amount: Decimal = None, payment_method: str = None,
               status: str = None, transaction_code: str = None) -> bool:
        """Update a payment"""
        updates = []
        params = []

        if amount is not None:
            updates.append("amount = %s")
            params.append(amount)
        if payment_method is not None:
            updates.append("payment_method = %s")
            params.append(payment_method)
        if status is not None:
            updates.append("status = %s")
            params.append(status)
        if transaction_code is not None:
            updates.append("transaction_code = %s")
            params.append(transaction_code)

        if not updates:
            return False

        params.append(payment_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, payment_id: str) -> bool:
        """Delete a payment"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (payment_id,)) > 0

    @classmethod
    def mark_as_completed(cls, payment_id: str) -> bool:
        """Mark the payment as completed"""
        return cls.update(payment_id, status='Completed')

    @classmethod
    def mark_as_failed(cls, payment_id: str) -> bool:
        """Mark the payment as failed"""
        return cls.update(payment_id, status='Failed')

    @classmethod
    def is_successful(cls, payment: Dict[str, Any]) -> bool:
        """Check if the payment was successful"""
        return payment['status'] == 'Completed'

    @classmethod
    def create_payment_summary(cls, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the payment details"""
        return {
            'payment_id': payment['id'],
            'booking_id': payment['booking_id'],
            'amount': float(payment['amount']),
            'payment_method': cls.get_payment_method_display(payment['payment_method']),
            'status': cls.get_status_display(payment['status']),
            'payment_time': payment['payment_time'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(payment['payment_time'], datetime) else str(payment['payment_time']),
            'transaction_code': payment['transaction_code'],
        }

    @classmethod
    def get_payment_method_display(cls, payment_method: str) -> str:
        """Get display text for payment method"""
        for choice in cls.PAYMENT_METHODS:
            if choice[0] == payment_method:
                return choice[1]
        return payment_method

    @classmethod
    def get_status_display(cls, status: str) -> str:
        """Get display text for status"""
        for choice in cls.STATUS_CHOICES:
            if choice[0] == status:
                return choice[1]
        return status

    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Get payment statistics"""
        query = f"""
            SELECT
                COUNT(*) as total_payments,
                COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_payments,
                COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_payments,
                COUNT(CASE WHEN status = 'Failed' THEN 1 END) as failed_payments,
                COALESCE(SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END), 0) as total_revenue
            FROM {cls.TABLE_NAME}
        """
        result = execute_query_one(query)
        return result if result else {
            'total_payments': 0,
            'pending_payments': 0,
            'completed_payments': 0,
            'failed_payments': 0,
            'total_revenue': 0
        }
