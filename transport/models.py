from django.db import models

class Locations(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        db_table = 'locations'

    def __str__(self):
        return self.name
    
class Route(models.Model):
    start_location = models.ForeignKey(
        Locations,
        related_name='start_routes',
        on_delete=models.CASCADE
    )
    end_location = models.ForeignKey(
        Locations,
        related_name='end_routes',
        on_delete=models.CASCADE
    )
    distance_km = models.FloatField()
    
    class Meta:
        ordering = ['start_location', 'end_location']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        db_table = 'routes'
        unique_together = ('start_location', 'end_location')

    def __str__(self):
        return f"{self.start_location} to {self.end_location}"
    
class Bus(models.Model):
    license_plate = models.CharField(max_length=30, unique=True)
    model = models.CharField(max_length=100)
    total_seats = models.PositiveIntegerField()
    manufacture_year = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['license_plate']
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'
        db_table = 'buses'

    def __str__(self):
        return self.license_plate
    
class Seat(models.Model):
    seat_number = models.CharField(max_length=10)
    bus = models.ForeignKey(
        Bus,
        related_name='seats',
        on_delete=models.CASCADE
    )
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['bus', 'seat_number']
        verbose_name = 'Seat'
        verbose_name_plural = 'Seats'
        db_table = 'seats'
        unique_together = ('bus', 'seat_number')

    def __str__(self):
        return f"Seat {self.seat_number} on {self.bus}"
    
class Trip(models.Model):
    route = models.ForeignKey(
        Route,
        related_name='trips',
        on_delete=models.CASCADE
    )
    bus = models.ForeignKey(
        Bus,
        related_name='trips',
        on_delete=models.CASCADE
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-departure_time']
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        db_table = 'trips'
    
    def __str__(self):
        return f"Trip {self.id} from {self.route.start_location} to {self.route.end_location}"
    
    def is_upcoming(self):
        """Check if the trip is upcoming"""
        from django.utils.timezone import now
        return self.departure_time > now()
    
    def get_duration(self):
        """Get the duration of the trip in hours and minutes"""
        duration = self.arrival_time - self.departure_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"
    
    def available_seats(self):
        """Get the number of available seats on the bus for this trip"""
        booked_seats = self.bookings.aggregate(total=models.Sum('number_of_seats'))['total'] or 0
        return self.bus.total_seats - booked_seats
