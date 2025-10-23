from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Locations, Route, Bus, Trip, Seat
from .serializers import (
    LocationSerializer,
    RouteSerializer,
    BusSerializer,
    TripSerializer,
    SeatSerializer
)


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing locations.

    Endpoints:
    - GET /api/locations/ - List all locations
    - POST /api/locations/ - Create a new location
    - GET /api/locations/{id}/ - Retrieve location details
    - PUT /api/locations/{id}/ - Update location
    - DELETE /api/locations/{id}/ - Delete location
    """
    queryset = Locations.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city']
    ordering_fields = ['name', 'city']


class RouteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing routes.

    Endpoints:
    - GET /api/routes/ - List all routes
    - POST /api/routes/ - Create a new route
    - GET /api/routes/{id}/ - Retrieve route details
    - PUT /api/routes/{id}/ - Update route
    - DELETE /api/routes/{id}/ - Delete route
    """
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['start_location', 'end_location']
    ordering_fields = ['distance_km']

    def get_queryset(self):
        return Route.objects.select_related('start_location', 'end_location')


class BusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing buses.

    Endpoints:
    - GET /api/buses/ - List all buses
    - POST /api/buses/ - Create a new bus
    - GET /api/buses/{id}/ - Retrieve bus details
    - PUT /api/buses/{id}/ - Update bus
    - DELETE /api/buses/{id}/ - Delete bus
    """
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['license_plate', 'model']
    ordering_fields = ['manufacture_year', 'total_seats']


class SeatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing seats.

    Endpoints:
    - GET /api/seats/ - List all seats
    - POST /api/seats/ - Create a new seat
    - GET /api/seats/{id}/ - Retrieve seat details
    - PUT /api/seats/{id}/ - Update seat
    - DELETE /api/seats/{id}/ - Delete seat
    """
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['bus', 'is_available']
    ordering_fields = ['seat_number']

    def get_queryset(self):
        return Seat.objects.select_related('bus')


class TripViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trips.

    Endpoints:
    - GET /api/trips/ - List all trips
    - POST /api/trips/ - Create a new trip
    - GET /api/trips/{id}/ - Retrieve trip details
    - PUT /api/trips/{id}/ - Update trip
    - DELETE /api/trips/{id}/ - Delete trip
    - GET /api/trips/upcoming/ - List upcoming trips
    - GET /api/trips/{id}/available_seats/ - Get available seats for a trip
    """
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['route', 'bus']
    ordering_fields = ['departure_time', 'price_per_seat']

    def get_queryset(self):
        return Trip.objects.select_related('route', 'bus', 'route__start_location', 'route__end_location')

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get all upcoming trips"""
        from django.utils.timezone import now
        upcoming_trips = self.get_queryset().filter(departure_time__gt=now())
        serializer = self.get_serializer(upcoming_trips, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """Get available seats count for a specific trip"""
        trip = self.get_object()
        return Response({
            'trip_id': trip.id,
            'total_seats': trip.bus.total_seats,
            'available_seats': trip.available_seats(),
            'booked_seats': trip.bus.total_seats - trip.available_seats()
        })
