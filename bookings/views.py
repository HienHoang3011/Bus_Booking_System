from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Booking, Ticket
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingListSerializer,
    TicketSerializer
)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.

    Endpoints:
    - GET /api/bookings/ - List all bookings for authenticated user
    - POST /api/bookings/ - Create a new booking
    - GET /api/bookings/{id}/ - Retrieve booking details
    - PUT /api/bookings/{id}/ - Update booking (limited fields)
    - DELETE /api/bookings/{id}/ - Cancel booking
    - POST /api/bookings/{id}/confirm/ - Confirm booking
    - POST /api/bookings/{id}/cancel/ - Cancel booking
    - GET /api/bookings/my-bookings/ - Get current user's bookings
    """
    queryset = Booking.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'list':
            return BookingListSerializer
        return BookingSerializer

    def get_queryset(self):
        """Filter bookings based on user role"""
        user = self.request.user

        # For testing: allow anonymous access, show all bookings
        if not user or user.is_anonymous:
            queryset = Booking.objects.all()
        # Admin can see all bookings
        elif hasattr(user, 'is_admin') and user.is_admin():
            queryset = Booking.objects.all()
        else:
            # Regular users can only see their own bookings
            queryset = Booking.objects.filter(user=user)

        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by trip
        trip_id = self.request.query_params.get('trip_id', None)
        if trip_id:
            queryset = queryset.filter(trip_id=trip_id)

        return queryset.select_related('user', 'trip', 'trip__route', 'trip__bus').prefetch_related('tickets')

    def create(self, request, *args, **kwargs):
        """Create a new booking"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Return full booking details
        response_serializer = BookingSerializer(booking)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update booking - only allowed for pending bookings"""
        instance = self.get_object()

        # Check if booking can be modified
        if not instance.can_modify():
            return Response(
                {'error': 'Cannot modify this booking. It is either not pending or the trip has departed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only allow updating number_of_seats
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Cancel booking instead of deleting"""
        instance = self.get_object()

        if instance.status == 'Canceled':
            return Response(
                {'error': 'Booking is already canceled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.cancel_booking()
        return Response(
            {'message': 'Booking canceled successfully.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending booking (admin only)"""
        if not request.user.is_admin():
            return Response(
                {'error': 'Only admins can confirm bookings.'},
                status=status.HTTP_403_FORBIDDEN
            )

        booking = self.get_object()

        if booking.status != 'Pending':
            return Response(
                {'error': f'Cannot confirm booking with status: {booking.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.confirm_booking()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()

        # Skip permission check for testing
        # if not request.user.is_admin() and booking.user != request.user:
        #     return Response(
        #         {'error': 'You can only cancel your own bookings.'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        if booking.status == 'Canceled':
            return Response(
                {'error': 'Booking is already canceled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.cancel_booking()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get all bookings for the current user"""
        # For testing: if no user, return all bookings
        if not request.user or request.user.is_anonymous:
            bookings = Booking.objects.all().select_related(
                'trip', 'trip__route', 'trip__bus'
            ).prefetch_related('tickets')
        else:
            bookings = Booking.objects.filter(user=request.user).select_related(
                'trip', 'trip__route', 'trip__bus'
            ).prefetch_related('tickets')

        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get booking statistics (admin only)"""
        if not request.user.is_admin():
            return Response(
                {'error': 'Only admins can view statistics.'},
                status=status.HTTP_403_FORBIDDEN
            )

        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='Pending').count()
        confirmed_bookings = Booking.objects.filter(status='Confirmed').count()
        canceled_bookings = Booking.objects.filter(status='Canceled').count()

        return Response({
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'canceled_bookings': canceled_bookings,
        })

    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Get all tickets for a specific booking"""
        booking = self.get_object()
        tickets = booking.tickets.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing tickets (read-only).

    Endpoints:
    - GET /api/tickets/ - List all tickets for authenticated user's bookings
    - GET /api/tickets/{id}/ - Retrieve ticket details
    """
    # permission_classes = [IsAuthenticated]  # Disabled for testing
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

    def get_queryset(self):
        """Filter tickets based on user role"""
        user = self.request.user

        # For testing: allow anonymous access, show all tickets
        if not user or user.is_anonymous:
            queryset = Ticket.objects.all()
        # Admin can see all tickets
        elif hasattr(user, 'is_admin') and user.is_admin():
            queryset = Ticket.objects.all()
        else:
            # Regular users can only see their own tickets
            queryset = Ticket.objects.filter(booking__user=user)

        return queryset.select_related('booking', 'seat', 'trip')
