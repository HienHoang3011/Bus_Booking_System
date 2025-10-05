from django.db import models
from datetime import datetime
from accounts.models import User
from transport.models import Trip, Seat
from django.utils.timezone import now
import uuid
class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Chờ xử lý'),
        ('Confirmed', 'Đã xác nhận'),
        ('Canceled', 'Đã hủy'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        related_name='bookings',
        on_delete=models.CASCADE
    )
    trip = models.ForeignKey(
        Trip,
        related_name='bookings',
        on_delete=models.CASCADE
    )
    number_of_seats = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_time = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    
    class Meta:
        ordering = ['-booking_time']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        db_table = 'bookings'
    
    def __str__(self):
        return f"Booking {self.id} by {self.user.username} for Trip {self.trip.id}"
    
    def cancel_booking(self):
        """Cancel the booking if it's not already canceled"""
        if self.status != 'Canceled':
            self.status = 'Canceled'
            self.save()
            
    def confirm_booking(self):
        """Confirm the booking if it's pending"""
        if self.status == 'Pending':
            self.status = 'Confirmed'
            self.save()
            
    def is_active(self):
        """Check if the booking is active (not canceled)"""
        return self.status != 'Canceled'
    
    def create_booking_summary(self):
        """Create a summary of the booking details"""
        return {
            'booking_id': self.id,
            'user': self.user.get_full_name(),
            'trip': str(self.trip),
            'number_of_seats': self.number_of_seats,
            'total_amount': float(self.total_amount),
            'booking_time': self.booking_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.get_status_display(),
        }
        
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.number_of_seats * self.trip.price_per_seat
        super().save(*args, **kwargs)
        
    def get_trip_details(self):
        """Get details of the associated trip"""
        return {
            'departure': self.trip.departure_location,
            'arrival': self.trip.arrival_location,
            'departure_time': self.trip.departure_time.strftime('%Y-%m-%d %H:%M:%S'),
            'arrival_time': self.trip.arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
    def get_user_contact(self):
        """Get contact details of the user who made the booking"""
        return {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
    
    def update_seats(self, new_seat_count):
        if new_seat_count > 0:
            self.number_of_seats = new_seat_count
            self.total_amount = self.number_of_seats * self.trip.price_per_seat
            self.save()
            
    def is_past_booking(self):
        """Check if the booking is for a trip that has already departed"""
        return self.trip.departure_time < datetime.now()
    
    def can_modify(self):
        """Check if the booking can be modified (only if pending and trip not departed)"""
        return self.status == 'Pending' and not self.is_past_booking()
    
class Ticket(models.Model):
    booking = models.ForeignKey(Booking, related_name='tickets', on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, related_name='tickets', on_delete=models.PROTECT, verbose_name="Ghế")
    trip = models.ForeignKey(Trip, related_name='tickets', on_delete=models.CASCADE, verbose_name="Chuyến đi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá vé")
    passenger_name = models.CharField(max_length=100, verbose_name="Tên hành khách")

    class Meta:
        unique_together = ('trip', 'seat')
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        db_table = 'tickets'

    def save(self, *args, **kwargs):
        # Tự động gán chuyến đi từ đơn đặt vé
        if not self.trip_id:
            self.trip = self.booking.trip
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vé ghế {self.seat.seat_number} - Chuyến {self.trip.id}"
    