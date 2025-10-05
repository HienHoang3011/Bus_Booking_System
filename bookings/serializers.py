from rest_framework import serializers
from .models import Booking, Ticket
from transport.models import Trip, Seat
from accounts.models import User


class TripSerializer(serializers.ModelSerializer):
    """Serializer for Trip details in booking"""
    route_info = serializers.SerializerMethodField()
    departure_location = serializers.CharField(source='route.start_location.name', read_only=True)
    arrival_location = serializers.CharField(source='route.end_location.name', read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'departure_location', 'arrival_location',
            'departure_time', 'arrival_time', 'price_per_seat',
            'route_info', 'available_seats', 'duration'
        ]

    def get_route_info(self, obj):
        return str(obj.route)

    def get_duration(self, obj):
        return obj.get_duration()


class SeatSerializer(serializers.ModelSerializer):
    """Serializer for Seat details"""
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_available']


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for Ticket"""
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    seat_id = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(),
        source='seat',
        write_only=True
    )

    class Meta:
        model = Ticket
        fields = ['id', 'seat_number', 'seat_id', 'price', 'passenger_name']
        read_only_fields = ['id', 'price']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking with full details"""
    trip_details = TripSerializer(source='trip', read_only=True)
    trip_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.all(),
        source='trip',
        write_only=True
    )
    tickets = TicketSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_name', 'trip_id', 'trip_details',
            'number_of_seats', 'total_amount', 'booking_time',
            'status', 'status_display', 'tickets'
        ]
        read_only_fields = ['id', 'user', 'total_amount', 'booking_time', 'status']

    def validate(self, data):
        """Validate booking data"""
        trip = data.get('trip')
        number_of_seats = data.get('number_of_seats')

        if trip and number_of_seats:
            # Check if enough seats are available
            if trip.available_seats() < number_of_seats:
                raise serializers.ValidationError({
                    'number_of_seats': f'Only {trip.available_seats()} seats available for this trip.'
                })

            # Check if trip is upcoming
            if not trip.is_upcoming():
                raise serializers.ValidationError({
                    'trip': 'Cannot book a trip that has already departed.'
                })

        return data


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings with tickets"""
    tickets = TicketSerializer(many=True, required=True)
    trip_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.all(),
        source='trip'
    )

    class Meta:
        model = Booking
        fields = ['trip_id', 'number_of_seats', 'tickets']

    def validate(self, data):
        """Validate booking creation data"""
        trip = data.get('trip')
        number_of_seats = data.get('number_of_seats')
        tickets = data.get('tickets', [])

        # Validate number of tickets matches number of seats
        if len(tickets) != number_of_seats:
            raise serializers.ValidationError({
                'tickets': f'Number of tickets ({len(tickets)}) must match number of seats ({number_of_seats}).'
            })

        # Check if trip has enough available seats
        if trip.available_seats() < number_of_seats:
            raise serializers.ValidationError({
                'number_of_seats': f'Only {trip.available_seats()} seats available for this trip.'
            })

        # Check if trip is upcoming
        if not trip.is_upcoming():
            raise serializers.ValidationError({
                'trip': 'Cannot book a trip that has already departed.'
            })

        # Validate seat availability for each ticket
        seat_ids = [ticket['seat'].id for ticket in tickets]

        # Check for duplicate seats in the request
        if len(seat_ids) != len(set(seat_ids)):
            raise serializers.ValidationError({
                'tickets': 'Cannot book the same seat multiple times.'
            })

        # Check if seats belong to the trip's bus
        for ticket in tickets:
            seat = ticket['seat']
            if seat.bus.id != trip.bus.id:
                raise serializers.ValidationError({
                    'tickets': f'Seat {seat.seat_number} does not belong to this trip\'s bus.'
                })

            # Check if seat is already booked for this trip
            if Ticket.objects.filter(trip=trip, seat=seat).exists():
                raise serializers.ValidationError({
                    'tickets': f'Seat {seat.seat_number} is already booked for this trip.'
                })

        return data

    def create(self, validated_data):
        """Create booking with tickets"""
        tickets_data = validated_data.pop('tickets')
        user = self.context['request'].user
        trip = validated_data['trip']

        # Create booking
        booking = Booking.objects.create(
            user=user,
            **validated_data
        )

        # Create tickets
        for ticket_data in tickets_data:
            Ticket.objects.create(
                booking=booking,
                trip=trip,
                price=trip.price_per_seat,
                **ticket_data
            )

        return booking


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing bookings"""
    trip_info = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user_name', 'trip_info', 'number_of_seats',
            'total_amount', 'booking_time', 'status', 'status_display'
        ]

    def get_trip_info(self, obj):
        return f"{obj.trip.route.start_location.name} → {obj.trip.route.end_location.name}"
