from rest_framework import serializers
from .models import Locations, Route, Bus, Trip, Seat


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Locations
        fields = ['id', 'name', 'city', 'full_address']


class RouteSerializer(serializers.ModelSerializer):
    """Serializer for Route model"""
    start_location_name = serializers.CharField(source='start_location.name', read_only=True)
    end_location_name = serializers.CharField(source='end_location.name', read_only=True)
    route_info = serializers.ReadOnlyField()

    class Meta:
        model = Route
        fields = ['id', 'start_location', 'start_location_name', 'end_location', 'end_location_name', 'distance_km', 'route_info']


class BusSerializer(serializers.ModelSerializer):
    """Serializer for Bus model"""

    class Meta:
        model = Bus
        fields = ['id', 'license_plate', 'model', 'total_seats', 'manufacture_year']


class SeatSerializer(serializers.ModelSerializer):
    """Serializer for Seat model"""
    bus_license_plate = serializers.CharField(source='bus.license_plate', read_only=True)

    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'bus', 'bus_license_plate', 'is_available']


class TripSerializer(serializers.ModelSerializer):
    """Serializer for Trip model"""
    route_info = serializers.CharField(source='route.__str__', read_only=True)
    bus_license_plate = serializers.CharField(source='bus.license_plate', read_only=True)
    duration = serializers.ReadOnlyField(source='get_duration')
    available_seats_count = serializers.ReadOnlyField(source='available_seats')
    is_upcoming = serializers.ReadOnlyField()

    class Meta:
        model = Trip
        fields = [
            'id', 'route', 'route_info', 'bus', 'bus_license_plate',
            'departure_time', 'arrival_time', 'price_per_seat',
            'duration', 'available_seats_count', 'is_upcoming'
        ]