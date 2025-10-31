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
        ('Momo', 'Momo'),
        ('VNPay', 'VNPay'),
        ('ZaloPay', 'ZaloPay'),
        ('ViettelPay','ViettelPay'),
        ('MBbank','Ngân hàng Quân đội'),
        ('Techcombank', 'Ngân hàng TMCP Kỹ thương Việt Nam'),
        ('Agribank', 'Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam'),
        ('Vietcombank', 'Ngân hàng TMCP Ngoại thương Việt Nam'),
        ('Vietinbank', 'Ngân hàng TMCP Công thương Việt Nam')
    ]
    STATUS_CHOICES = [
        ('Pending', 'Chờ xử lý'),
        ('Completed', 'Hoàn thành'),
    ]
    
    @classmethod
    def create(cls, booking_id: str, amount: Decimal, payment_method: str,
               transaction_code: str, wallet_id: Optional[str] = None,
               status: str = 'Pending') -> Optional[Dict[str, Any]]:
        """Create a new payment"""
        payment_id = str(uuid.uuid4())
        payment_time = now()

        query = f"""
            INSERT INTO {cls.TABLE_NAME}
            (id, booking_id, amount, payment_method, status, payment_time, transaction_code, wallet_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, booking_id, amount, payment_method, status, payment_time, transaction_code, wallet_id
        """
        result = execute_query(query, (payment_id, booking_id, amount, payment_method,
                                      status, payment_time, transaction_code, wallet_id))
        return result[0] if result else None

    @classmethod
    def mark_as_completed(cls, payment_id: int) -> bool:
        query = f"UPDATE {cls.TABLE_NAME} SET status = %s WHERE id = %s"
        return execute_update(query, ('Completed', payment_id))

    @classmethod
    def check_payment_state(cls, payment_id: int) -> bool:
        query = f"SELECT status FROM {cls.TABLE_NAME} WHERE id = %s"
        result = execute_query_one(query, (payment_id,))
        return result and result.get('status') == 'Completed'

    @classmethod
    def get_payment(cls, payment_id: int) -> Optional[Dict[str, Any]]:
        """Display payment details by payment_id"""
        query = f"SELECT id, booking_id, amount, payment_method, status, payment_time, transaction_code, wallet_id FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_query_one(query, (payment_id,))

class Wallet:
    TABLE_NAME = 'wallets'
    TRANSACTION_TYPES = [
        ('deposit', 'Nạp tiền'),
        ('withdraw', 'Rút tiền'),
        ('payment', 'Thanh toán vé xe'),
        ('refund', 'Hoàn tiền'),
        ('receive', 'Nhận tiền'),
    ]
    @classmethod
    def create(cls, user_id: int, balance: Decimal = Decimal('0.00')) -> Optional[Dict[str, Any]]:
        """Create a new wallet for a user"""
        existing_wallet = cls.get_by_user_id(user_id)
        if existing_wallet:
            return existing_wallet

        wallet_id = str(uuid.uuid4())
        created_at = now()
        
        query = f"""
            INSERT INTO {cls.TABLE_NAME}
            (id, user_id, balance, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        success = execute_insert(query, (wallet_id, user_id, balance, created_at, created_at))
        
        if success:
            select_query = f"SELECT id, user_id, balance, created_at, updated_at FROM {cls.TABLE_NAME} WHERE id = %s"
            return execute_query_one(select_query, (wallet_id,))
        return None

    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a wallet by user ID."""
        query = f"SELECT id, user_id, balance, created_at, updated_at FROM {cls.TABLE_NAME} WHERE user_id = %s"
        return execute_query_one(query, (user_id,))

    @classmethod
    def get_balance(cls, user_id: int) -> Optional[Decimal]:
        """Get wallet balance by user ID"""
        query = f"SELECT balance FROM {cls.TABLE_NAME} WHERE user_id = %s"
        result = execute_query_one(query, (user_id,))
        return result['balance'] if result else None

    @classmethod
    def deposit(cls, user_id: int, amount: Decimal) -> bool:
        """Update wallet balance: depositing"""
        if amount < Decimal('0.00'):
            return False
        query = f"UPDATE {cls.TABLE_NAME} SET balance = %s, updated_at = %s WHERE user_id = %s"
        wallet = cls.get_by_user_id(user_id)
        new_balance = wallet['balance'] + amount
        return execute_update(query, (new_balance, now(), user_id))
    
    @classmethod
    def withdraw(cls, user_id: str, amount: Decimal) -> bool:
        """Update wallet balance: withdrawing"""
        wallet = cls.get_by_user_id(user_id)
        if amount == Decimal('0.00') or amount > wallet['balance']:
            return False
        query = f"UPDATE {cls.TABLE_NAME} SET balance = %s, updated_at = %s WHERE user_id = %s"
        new_balance = wallet['balance'] - amount
        return execute_update(query, (new_balance, now(), user_id))
    
    @classmethod
    def pay(cls, user_id: str, admin_id: str, amount: Decimal) -> bool:
        """Make a payment from user wallet to admin wallet"""
        user_wallet = cls.get_by_user_id(user_id)
        admin_wallet = cls.get_by_user_id(admin_id)
        
        if not user_wallet or not admin_wallet:
            return False
        if amount <= Decimal('0.00') or amount > user_wallet['balance']:
            return False
        
        # Withdraw from user and deposit to admin
        if cls.withdraw(user_id, amount):
            return cls.deposit(admin_id, amount)
        return False

    @classmethod
    def get_all_payments(cls, wallet_id: str) -> List[Dict[str, Any]]:
        """Get all payments for a wallet (order by latest time)"""
        query = f"""
            SELECT id, booking_id, wallet_id, amount, payment_method, status, payment_time, transaction_code 
            FROM {Payment.TABLE_NAME} 
            WHERE wallet_id = %s
            ORDER BY payment_time DESC
        """
        return execute_query(query, (wallet_id,))

    

        


