from django.db import models
from bookings.models import Booking
import uuid
# Create your models here.
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    booking = models.ForeignKey(
        Booking,
        related_name='payments',
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_code = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_time']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        db_table = 'payments'
    
    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id}"
    
    def mark_as_completed(self):
        """Mark the payment as completed"""
        if self.status != 'Completed':
            self.status = 'Completed'
            self.save()
            
    def mark_as_failed(self):
        """Mark the payment as failed"""
        if self.status != 'Failed':
            self.status = 'Failed'
            self.save()
            
    def is_successful(self):
        """Check if the payment was successful"""
        return self.status == 'Completed'
    
    def create_payment_summary(self):
        """Create a summary of the payment details"""
        return {
            'payment_id': self.id,
            'booking_id': self.booking.id,
            'amount': float(self.amount),
            'payment_method': self.get_payment_method_display(),
            'status': self.get_status_display(),
            'payment_time': self.payment_time.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_code': self.transaction_code,
        }