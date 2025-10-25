"""
Transport serializers for dictionary data (No ORM)
"""
from rest_framework import serializers
from .models import Locations, Route, Bus, Trip, Seat


class LocationSerializer(serializers.Serializer):
    """Serializer for Location dictionary data"""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=True)
    city = serializers.CharField(max_length=100, required=True)
    full_address = serializers.SerializerMethodField(read_only=True)

    def get_full_address(self, obj):
        """Get full address"""
        if isinstance(obj, dict):
            return Locations.full_address(obj)
        return f"{obj.get('name', '')}, {obj.get('city', '')}"

    def create(self, validated_data):
        """Create a new location"""
        return Locations.create(
            name=validated_data['name'],
            city=validated_data['city']
        )

    def update(self, instance, validated_data):
        """Update a location"""
        location_id = instance['id'] if isinstance(instance, dict) else instance
        Locations.update(
            location_id=location_id,
            name=validated_data.get('name'),
            city=validated_data.get('city')
        )
        return Locations.get_by_id(location_id)


class RouteSerializer(serializers.Serializer):
    """Serializer for Route dictionary data"""
    id = serializers.IntegerField(read_only=True)
    start_location = serializers.IntegerField(source='start_location_id', required=True)
    start_location_name = serializers.CharField(read_only=True)
    end_location = serializers.IntegerField(source='end_location_id', required=True)
    end_location_name = serializers.CharField(read_only=True)
    distance_km = serializers.FloatField(required=True)
    route_info = serializers.SerializerMethodField(read_only=True)

    def get_route_info(self, obj):
        """Get route info"""
        if isinstance(obj, dict) and 'start_location_name' in obj:
            return Route.route_info(obj)
        return ''

    def create(self, validated_data):
        """Create a new route"""
        return Route.create(
            start_location_id=validated_data['start_location_id'],
            end_location_id=validated_data['end_location_id'],
            distance_km=validated_data['distance_km']
        )

    def update(self, instance, validated_data):
        """Update a route"""
        route_id = instance['id'] if isinstance(instance, dict) else instance
        Route.update(
            route_id=route_id,
            start_location_id=validated_data.get('start_location_id'),
            end_location_id=validated_data.get('end_location_id'),
            distance_km=validated_data.get('distance_km')
        )
        return Route.get_by_id(route_id)


class BusSerializer(serializers.Serializer):
    """Serializer for Bus dictionary data"""
    id = serializers.IntegerField(read_only=True)
    license_plate = serializers.CharField(max_length=30, required=True)
    model = serializers.CharField(max_length=100, required=True)
    total_seats = serializers.IntegerField(required=True, min_value=1)
    manufacture_year = serializers.IntegerField(required=True, min_value=1900)

    def _generate_seat_number(self, seat_index, seats_per_row=10):
        """
        Generate seat number in format: A01, A02, ..., B01, B02, etc.
        Args:
            seat_index: Zero-based seat index (0, 1, 2, ...)
            seats_per_row: Number of seats per row (default: 10)
        Returns:
            Seat number string (e.g., "A01", "B05")
        """
        row_letter = chr(65 + (seat_index // seats_per_row))  # A, B, C, ...
        seat_in_row = (seat_index % seats_per_row) + 1
        return f"{row_letter}{seat_in_row:02d}"

    def create(self, validated_data):
        """Create a new bus and automatically create seats"""
        # Create the bus first
        bus = Bus.create(
            license_plate=validated_data['license_plate'],
            model=validated_data['model'],
            total_seats=validated_data['total_seats'],
            manufacture_year=validated_data['manufacture_year']
        )

        if bus:
            # Automatically create seats for the bus
            total_seats = validated_data['total_seats']
            bus_id = bus['id']

            for seat_index in range(total_seats):
                seat_number = self._generate_seat_number(seat_index)
                try:
                    Seat.create(
                        seat_number=seat_number,
                        bus_id=bus_id,
                        is_available=True
                    )
                except Exception as e:
                    # Log error but continue creating other seats
                    print(f"Warning: Failed to create seat {seat_number} for bus {bus_id}: {e}")

        return bus

    def update(self, instance, validated_data):
        """Update a bus"""
        bus_id = instance['id'] if isinstance(instance, dict) else instance
        Bus.update(
            bus_id=bus_id,
            license_plate=validated_data.get('license_plate'),
            model=validated_data.get('model'),
            total_seats=validated_data.get('total_seats'),
            manufacture_year=validated_data.get('manufacture_year')
        )
        return Bus.get_by_id(bus_id)


class SeatSerializer(serializers.Serializer):
    """Serializer for Seat dictionary data"""
    id = serializers.IntegerField(read_only=True)
    seat_number = serializers.CharField(max_length=10, required=True)
    bus = serializers.IntegerField(source='bus_id', required=True)
    bus_license_plate = serializers.CharField(read_only=True)
    is_available = serializers.BooleanField(default=True)

    def create(self, validated_data):
        """Create a new seat"""
        return Seat.create(
            seat_number=validated_data['seat_number'],
            bus_id=validated_data['bus_id'],
            is_available=validated_data.get('is_available', True)
        )

    def update(self, instance, validated_data):
        """Update a seat"""
        seat_id = instance['id'] if isinstance(instance, dict) else instance
        Seat.update(
            seat_id=seat_id,
            seat_number=validated_data.get('seat_number'),
            is_available=validated_data.get('is_available')
        )
        return Seat.get_by_id(seat_id)


class TripSerializer(serializers.Serializer):
    """Serializer for Trip dictionary data"""
    id = serializers.IntegerField(read_only=True)
    route = serializers.IntegerField(source='route_id', required=True)
    route_info = serializers.SerializerMethodField(read_only=True)
    bus = serializers.IntegerField(source='bus_id', required=True)
    bus_license_plate = serializers.CharField(read_only=True)
    departure_time = serializers.DateTimeField(required=True)
    arrival_time = serializers.DateTimeField(required=True)
    price_per_seat = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    duration = serializers.SerializerMethodField(read_only=True)
    available_seats_count = serializers.SerializerMethodField(read_only=True)
    is_upcoming = serializers.SerializerMethodField(read_only=True)

    def get_route_info(self, obj):
        """Get route info"""
        if isinstance(obj, dict) and 'start_location_name' in obj:
            return f"{obj['start_location_name']} to {obj['end_location_name']}"
        return ''

    def get_duration(self, obj):
        """Get trip duration"""
        if isinstance(obj, dict):
            return Trip.get_duration(obj)
        return ''

    def get_available_seats_count(self, obj):
        """Get available seats count"""
        if isinstance(obj, dict) and 'id' in obj:
            return Trip.available_seats(obj['id'])
        return 0

    def get_is_upcoming(self, obj):
        """Check if trip is upcoming"""
        if isinstance(obj, dict):
            return Trip.is_upcoming(obj)
        return False

    def validate(self, data):
        """Validate trip data"""
        if data.get('arrival_time') and data.get('departure_time'):
            if data['arrival_time'] <= data['departure_time']:
                raise serializers.ValidationError({
                    'arrival_time': 'Arrival time must be after departure time.'
                })
        return data

    def create(self, validated_data):
        """Create a new trip"""
        return Trip.create(
            route_id=validated_data['route_id'],
            bus_id=validated_data['bus_id'],
            departure_time=validated_data['departure_time'],
            arrival_time=validated_data['arrival_time'],
            price_per_seat=validated_data['price_per_seat']
        )

    def update(self, instance, validated_data):
        """Update a trip"""
        trip_id = instance['id'] if isinstance(instance, dict) else instance
        Trip.update(
            trip_id=trip_id,
            route_id=validated_data.get('route_id'),
            bus_id=validated_data.get('bus_id'),
            departure_time=validated_data.get('departure_time'),
            arrival_time=validated_data.get('arrival_time'),
            price_per_seat=validated_data.get('price_per_seat')
        )
        return Trip.get_by_id(trip_id)
