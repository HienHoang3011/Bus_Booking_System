"""
Bookings serializers for dictionary data (No ORM)
"""
from rest_framework import serializers
from .models import Booking, Ticket
from transport.models import Trip, Seat
from decimal import Decimal


class TripDetailsSerializer(serializers.Serializer):
    """Serializer for Trip details in booking"""
    id = serializers.IntegerField(read_only=True)
    departure_location = serializers.CharField(source='start_location_name', read_only=True)
    arrival_location = serializers.CharField(source='end_location_name', read_only=True)
    departure_time = serializers.DateTimeField(read_only=True)
    arrival_time = serializers.DateTimeField(read_only=True)
    price_per_seat = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    available_seats = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField(read_only=True)
    route_info = serializers.SerializerMethodField(read_only=True)

    def get_route_info(self, obj):
        """Get route info"""
        if isinstance(obj, dict):
            return f"{obj.get('start_location_name', '')} to {obj.get('end_location_name', '')}"
        return ''

    def get_duration(self, obj):
        """Get trip duration"""
        if isinstance(obj, dict):
            return Trip.get_duration(obj)
        return ''

    def get_available_seats(self, obj):
        """Get available seats"""
        if isinstance(obj, dict) and 'trip_id' in obj:
            return Trip.available_seats(obj['trip_id'])
        return 0


class SeatDetailsSerializer(serializers.Serializer):
    """Serializer for Seat details"""
    id = serializers.IntegerField(read_only=True)
    seat_number = serializers.CharField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)


class TicketSerializer(serializers.Serializer):
    """Serializer for Ticket"""
    id = serializers.IntegerField(read_only=True)
    seat_number = serializers.CharField(read_only=True)
    seat_id = serializers.IntegerField(write_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    passenger_name = serializers.CharField(max_length=100, required=True)


class BookingSerializer(serializers.Serializer):
    """Serializer for Booking with full details"""
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    user_name = serializers.SerializerMethodField(read_only=True)
    trip_id = serializers.IntegerField(write_only=True)
    trip_details = serializers.SerializerMethodField(read_only=True)
    number_of_seats = serializers.IntegerField(min_value=1, required=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    booking_time = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    tickets = serializers.SerializerMethodField(read_only=True)

    def get_user_name(self, obj):
        """Get user name"""
        if isinstance(obj, dict) and 'user_id' in obj:
            from accounts.models import User
            user = User.get_by_id(obj['user_id'])
            if user:
                return user.get('username', 'Unknown')
        return 'Unknown'

    def get_trip_details(self, obj):
        """Get trip details"""
        if isinstance(obj, dict):
            return TripDetailsSerializer(obj).data
        return {}

    def get_status_display(self, obj):
        """Get status display"""
        if isinstance(obj, dict) and 'status' in obj:
            return Booking.get_status_display(obj['status'])
        return ''

    def get_tickets(self, obj):
        """Get tickets for booking"""
        if isinstance(obj, dict) and 'id' in obj:
            tickets = Ticket.get_by_booking_id(str(obj['id']))
            return TicketSerializer(tickets, many=True).data
        return []


class BookingCreateSerializer(serializers.Serializer):
    """Serializer for creating bookings with tickets"""
    trip_id = serializers.IntegerField(required=True)
    number_of_seats = serializers.IntegerField(min_value=1, required=True)
    tickets = TicketSerializer(many=True, required=True)

    def validate(self, data):
        """Validate booking creation data"""
        trip_id = data.get('trip_id')
        number_of_seats = data.get('number_of_seats')
        tickets = data.get('tickets', [])

        # Get trip details
        trip = Trip.get_by_id(trip_id)
        if not trip:
            raise serializers.ValidationError({
                'trip_id': 'Trip not found.'
            })

        # Validate number of tickets matches number of seats
        if len(tickets) != number_of_seats:
            raise serializers.ValidationError({
                'tickets': f'Number of tickets ({len(tickets)}) must match number of seats ({number_of_seats}).'
            })

        # Check if trip has enough available seats
        available_seats = Trip.available_seats(trip_id)
        if available_seats < number_of_seats:
            raise serializers.ValidationError({
                'number_of_seats': f'Only {available_seats} seats available for this trip.'
            })

        # Check if trip is upcoming
        if not Trip.is_upcoming(trip):
            raise serializers.ValidationError({
                'trip_id': 'Cannot book a trip that has already departed.'
            })

        # Validate seat availability for each ticket
        seat_ids = []
        for ticket in tickets:
            seat_id = ticket.get('seat_id')
            if seat_id is None:
                raise serializers.ValidationError({
                    'tickets': 'Each ticket must have a seat_id.'
                })
            seat_ids.append(seat_id)

        # Check for duplicate seats in the request
        if len(seat_ids) != len(set(seat_ids)):
            raise serializers.ValidationError({
                'tickets': 'Cannot book the same seat multiple times.'
            })

        # Check if seats belong to the trip's bus and are not already booked
        for seat_id in seat_ids:
            seat = Seat.get_by_id(seat_id)
            if not seat:
                raise serializers.ValidationError({
                    'tickets': f'Seat with ID {seat_id} not found.'
                })

            if seat['bus_id'] != trip['bus_id']:
                raise serializers.ValidationError({
                    'tickets': f'Seat {seat["seat_number"]} does not belong to this trip\'s bus.'
                })

            # Check if seat is already booked for this trip
            if Ticket.check_seat_booked(trip_id, seat_id):
                raise serializers.ValidationError({
                    'tickets': f'Seat {seat["seat_number"]} is already booked for this trip.'
                })

        return data

    def create(self, validated_data):
        """Create booking with tickets"""
        tickets_data = validated_data.pop('tickets')
        user = self.context['request'].user
        trip_id = validated_data['trip_id']

        # Get user_id
        if hasattr(user, 'id') and user.id is not None:
            user_id = user.id
        else:
            # For testing with anonymous users, use a default user_id
            user_id = 1

        # Get trip to calculate total_amount
        trip = Trip.get_by_id(trip_id)

        # Create booking
        booking = Booking.create(
            user_id=user_id,
            trip_id=trip_id,
            number_of_seats=validated_data['number_of_seats']
        )

        # Create tickets
        for ticket_data in tickets_data:
            Ticket.create(
                booking_id=booking['id'],
                seat_id=ticket_data['seat_id'],
                trip_id=trip_id,
                price=trip['price_per_seat'],
                passenger_name=ticket_data['passenger_name']
            )

        # Fetch full booking details
        return Booking.get_by_id(booking['id'])


class BookingListSerializer(serializers.Serializer):
    """Simplified serializer for listing bookings"""
    id = serializers.UUIDField(read_only=True)
    user_name = serializers.SerializerMethodField(read_only=True)
    trip_info = serializers.SerializerMethodField(read_only=True)
    number_of_seats = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    booking_time = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)

    def get_user_name(self, obj):
        """Get user name"""
        if isinstance(obj, dict) and 'user_id' in obj:
            from accounts.models import User
            user = User.get_by_id(obj['user_id'])
            if user:
                return user.get('username', 'Unknown')
        return 'Unknown'

    def get_trip_info(self, obj):
        """Get trip info"""
        if isinstance(obj, dict):
            return f"{obj.get('start_location_name', '')} → {obj.get('end_location_name', '')}"
        return ''

    def get_status_display(self, obj):
        """Get status display"""
        if isinstance(obj, dict) and 'status' in obj:
            return Booking.get_status_display(obj['status'])
        return ''
