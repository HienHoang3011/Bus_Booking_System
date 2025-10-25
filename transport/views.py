"""
Transport views using raw SQL (No ORM)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Locations, Route, Bus, Trip, Seat
from .serializers import (
    LocationSerializer,
    RouteSerializer,
    BusSerializer,
    TripSerializer,
    SeatSerializer
)


class LocationViewSet(viewsets.ViewSet):
    """
    ViewSet for managing locations using raw SQL.

    Endpoints:
    - GET /api/locations/ - List all locations
    - POST /api/locations/ - Create a new location
    - GET /api/locations/{id}/ - Retrieve location details
    - PUT /api/locations/{id}/ - Update location
    - DELETE /api/locations/{id}/ - Delete location
    """

    def list(self, request):
        """List all locations"""
        search_name = request.query_params.get('search', None)
        search_city = request.query_params.get('city', None)

        if search_name or search_city:
            locations = Locations.search(name=search_name, city=search_city)
        else:
            ordering = request.query_params.get('ordering', 'name')
            locations = Locations.get_all(ordering=[ordering])

        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new location"""
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Retrieve a location by ID"""
        location = Locations.get_by_id(int(pk))
        if not location:
            raise NotFound('Location not found')
        serializer = LocationSerializer(location)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Update a location"""
        location = Locations.get_by_id(int(pk))
        if not location:
            raise NotFound('Location not found')

        serializer = LocationSerializer(location, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_location = serializer.save()
        return Response(LocationSerializer(updated_location).data)

    def partial_update(self, request, pk=None):
        """Partially update a location"""
        location = Locations.get_by_id(int(pk))
        if not location:
            raise NotFound('Location not found')

        serializer = LocationSerializer(location, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_location = serializer.save()
        return Response(LocationSerializer(updated_location).data)

    def destroy(self, request, pk=None):
        """Delete a location"""
        if not Locations.delete(int(pk)):
            raise NotFound('Location not found')
        return Response(status=status.HTTP_204_NO_CONTENT)


class RouteViewSet(viewsets.ViewSet):
    """
    ViewSet for managing routes using raw SQL.

    Endpoints:
    - GET /api/routes/ - List all routes
    - POST /api/routes/ - Create a new route
    - GET /api/routes/{id}/ - Retrieve route details
    - PUT /api/routes/{id}/ - Update route
    - DELETE /api/routes/{id}/ - Delete route
    """

    def list(self, request):
        """List all routes"""
        start_location_id = request.query_params.get('start_location', None)
        end_location_id = request.query_params.get('end_location', None)
        ordering = request.query_params.get('ordering', 'distance_km')

        routes = Route.get_all(
            start_location_id=int(start_location_id) if start_location_id else None,
            end_location_id=int(end_location_id) if end_location_id else None,
            ordering=[ordering]
        )

        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new route"""
        serializer = RouteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        route = serializer.save()
        # Fetch full route details with location names
        full_route = Route.get_by_id(route['id'])
        return Response(RouteSerializer(full_route).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Retrieve a route by ID"""
        route = Route.get_by_id(int(pk))
        if not route:
            raise NotFound('Route not found')
        serializer = RouteSerializer(route)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Update a route"""
        route = Route.get_by_id(int(pk))
        if not route:
            raise NotFound('Route not found')

        serializer = RouteSerializer(route, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_route = serializer.save()
        return Response(RouteSerializer(updated_route).data)

    def partial_update(self, request, pk=None):
        """Partially update a route"""
        route = Route.get_by_id(int(pk))
        if not route:
            raise NotFound('Route not found')

        serializer = RouteSerializer(route, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_route = serializer.save()
        return Response(RouteSerializer(updated_route).data)

    def destroy(self, request, pk=None):
        """Delete a route"""
        if not Route.delete(int(pk)):
            raise NotFound('Route not found')
        return Response(status=status.HTTP_204_NO_CONTENT)


class BusViewSet(viewsets.ViewSet):
    """
    ViewSet for managing buses using raw SQL.

    Endpoints:
    - GET /api/buses/ - List all buses
    - POST /api/buses/ - Create a new bus
    - GET /api/buses/{id}/ - Retrieve bus details
    - PUT /api/buses/{id}/ - Update bus
    - DELETE /api/buses/{id}/ - Delete bus
    """

    def list(self, request):
        """List all buses"""
        search_license = request.query_params.get('search', None)
        search_model = request.query_params.get('model', None)

        if search_license or search_model:
            buses = Bus.search(license_plate=search_license, model=search_model)
        else:
            ordering = request.query_params.get('ordering', 'license_plate')
            buses = Bus.get_all(ordering=[ordering])

        serializer = BusSerializer(buses, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new bus"""
        serializer = BusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bus = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Retrieve a bus by ID"""
        bus = Bus.get_by_id(int(pk))
        if not bus:
            raise NotFound('Bus not found')
        serializer = BusSerializer(bus)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Update a bus"""
        bus = Bus.get_by_id(int(pk))
        if not bus:
            raise NotFound('Bus not found')

        serializer = BusSerializer(bus, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_bus = serializer.save()
        return Response(BusSerializer(updated_bus).data)

    def partial_update(self, request, pk=None):
        """Partially update a bus"""
        bus = Bus.get_by_id(int(pk))
        if not bus:
            raise NotFound('Bus not found')

        serializer = BusSerializer(bus, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_bus = serializer.save()
        return Response(BusSerializer(updated_bus).data)

    def destroy(self, request, pk=None):
        """Delete a bus"""
        if not Bus.delete(int(pk)):
            raise NotFound('Bus not found')
        return Response(status=status.HTTP_204_NO_CONTENT)


class SeatViewSet(viewsets.ViewSet):
    """
    ViewSet for managing seats using raw SQL.

    Endpoints:
    - GET /api/seats/ - List all seats
    - POST /api/seats/ - Create a new seat
    - GET /api/seats/{id}/ - Retrieve seat details
    - PUT /api/seats/{id}/ - Update seat
    - DELETE /api/seats/{id}/ - Delete seat
    """

    def list(self, request):
        """List all seats"""
        bus_id = request.query_params.get('bus', None)
        is_available = request.query_params.get('is_available', None)
        ordering = request.query_params.get('ordering', 'seat_number')

        # Convert is_available to boolean
        if is_available is not None:
            is_available = is_available.lower() == 'true'

        seats = Seat.get_all(
            bus_id=int(bus_id) if bus_id else None,
            is_available=is_available,
            ordering=[ordering]
        )

        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new seat"""
        serializer = SeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seat = serializer.save()
        # Fetch full seat details with bus info
        full_seat = Seat.get_by_id(seat['id'])
        return Response(SeatSerializer(full_seat).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Retrieve a seat by ID"""
        seat = Seat.get_by_id(int(pk))
        if not seat:
            raise NotFound('Seat not found')
        serializer = SeatSerializer(seat)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Update a seat"""
        seat = Seat.get_by_id(int(pk))
        if not seat:
            raise NotFound('Seat not found')

        serializer = SeatSerializer(seat, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_seat = serializer.save()
        return Response(SeatSerializer(updated_seat).data)

    def partial_update(self, request, pk=None):
        """Partially update a seat"""
        seat = Seat.get_by_id(int(pk))
        if not seat:
            raise NotFound('Seat not found')

        serializer = SeatSerializer(seat, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_seat = serializer.save()
        return Response(SeatSerializer(updated_seat).data)

    def destroy(self, request, pk=None):
        """Delete a seat"""
        if not Seat.delete(int(pk)):
            raise NotFound('Seat not found')
        return Response(status=status.HTTP_204_NO_CONTENT)


class TripViewSet(viewsets.ViewSet):
    """
    ViewSet for managing trips using raw SQL.

    Endpoints:
    - GET /api/trips/ - List all trips
    - POST /api/trips/ - Create a new trip
    - GET /api/trips/{id}/ - Retrieve trip details
    - PUT /api/trips/{id}/ - Update trip
    - DELETE /api/trips/{id}/ - Delete trip
    - GET /api/trips/upcoming/ - List upcoming trips
    - GET /api/trips/{id}/available_seats/ - Get available seats for a trip
    """

    def list(self, request):
        """List all trips"""
        route_id = request.query_params.get('route', None)
        bus_id = request.query_params.get('bus', None)
        ordering = request.query_params.get('ordering', '-departure_time')

        trips = Trip.get_all(
            route_id=int(route_id) if route_id else None,
            bus_id=int(bus_id) if bus_id else None,
            ordering=[ordering]
        )

        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new trip"""
        serializer = TripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trip = serializer.save()
        # Fetch full trip details with route and bus info
        full_trip = Trip.get_by_id(trip['id'])
        return Response(TripSerializer(full_trip).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Retrieve a trip by ID"""
        trip = Trip.get_by_id(int(pk))
        if not trip:
            raise NotFound('Trip not found')
        serializer = TripSerializer(trip)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Update a trip"""
        trip = Trip.get_by_id(int(pk))
        if not trip:
            raise NotFound('Trip not found')

        serializer = TripSerializer(trip, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_trip = serializer.save()
        return Response(TripSerializer(updated_trip).data)

    def partial_update(self, request, pk=None):
        """Partially update a trip"""
        trip = Trip.get_by_id(int(pk))
        if not trip:
            raise NotFound('Trip not found')

        serializer = TripSerializer(trip, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_trip = serializer.save()
        return Response(TripSerializer(updated_trip).data)

    def destroy(self, request, pk=None):
        """Delete a trip"""
        if not Trip.delete(int(pk)):
            raise NotFound('Trip not found')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get all upcoming trips"""
        ordering = request.query_params.get('ordering', '-departure_time')
        trips = Trip.get_all(upcoming_only=True, ordering=[ordering])
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """Get available seats count for a specific trip"""
        trip = Trip.get_by_id(int(pk))
        if not trip:
            raise NotFound('Trip not found')

        available = Trip.available_seats(int(pk))
        total_seats = trip['bus_total_seats']

        return Response({
            'trip_id': trip['id'],
            'total_seats': total_seats,
            'available_seats': available,
            'booked_seats': total_seats - available
        })
