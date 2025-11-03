"""
Frontend views for trip booking
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Trip, Seat, Bus
from bookings.models import Booking, Ticket
from payments.models import Payment
from accounts.decorators import admin_required
from decimal import Decimal
import json
import uuid


def trip_list(request):
    """Display all available trips for booking"""
    # Get filter parameters
    start_location = request.GET.get('start_location', '')
    end_location = request.GET.get('end_location', '')
    date = request.GET.get('date', '')

    # Build filter conditions
    filters = {'upcoming_only': True}

    context = {
        'start_location': start_location,
        'end_location': end_location,
        'date': date,
    }

    return render(request, 'transport/trip_list.html', context)


def trip_detail(request, trip_id):
    """Display trip details and seat selection"""
    trip = Trip.get_by_id(int(trip_id))

    if not trip:
        messages.error(request, 'Chuyến xe không tồn tại.')
        return redirect('trip_list')

    # Get available seats count
    available_seats = Trip.available_seats(int(trip_id))

    context = {
        'trip': trip,
        'available_seats': available_seats,
        'trip_id': trip_id,
    }

    return render(request, 'transport/trip_detail.html', context)


def booking_create(request, trip_id):
    """Create a booking for selected trip - allows guest users"""
    if request.method == 'POST':
        try:
            trip = Trip.get_by_id(int(trip_id))
            if not trip:
                return JsonResponse({'error': 'Chuyến xe không tồn tại'}, status=404)

            # Get selected seats from request
            data = json.loads(request.body)
            selected_seat_ids = data.get('seat_ids', [])
            passenger_names = data.get('passenger_names', [])

            if not selected_seat_ids:
                return JsonResponse({'error': 'Vui lòng chọn ít nhất một ghế'}, status=400)

            # Check if seats are available
            for seat_id in selected_seat_ids:
                if Ticket.check_seat_booked(int(trip_id), int(seat_id)):
                    return JsonResponse({'error': f'Ghế đã được đặt trước'}, status=400)

            # Calculate total amount
            number_of_seats = len(selected_seat_ids)
            total_amount = Decimal(trip['price_per_seat']) * number_of_seats

            # Get user ID (None for guest users)
            from accounts.utils import get_current_user
            current_user = get_current_user(request)
            user_id = current_user.id if current_user else None

            # Create booking (can be for guest or logged-in user)
            booking = Booking.create(
                user_id=user_id,
                trip_id=int(trip_id),
                number_of_seats=number_of_seats,
                total_amount=total_amount,
                status='Pending'
            )

            if not booking:
                return JsonResponse({'error': 'Không thể tạo booking'}, status=500)

            # Get passenger name for guest users
            default_passenger_name = current_user.get_full_name() if current_user else 'Khách'

            # Create tickets for each seat
            for i, seat_id in enumerate(selected_seat_ids):
                passenger_name = passenger_names[i] if i < len(passenger_names) else ''
                Ticket.create(
                    booking_id=booking['id'],
                    seat_id=int(seat_id),
                    trip_id=int(trip_id),
                    price=Decimal(trip['price_per_seat']),
                    passenger_name=passenger_name or default_passenger_name
                )

            # Automatically create a payment for this booking
            transaction_code = f"TXN-{uuid.uuid4().hex[:8].upper()}"
            payment = Payment.create(
                booking_id=booking['id'],
                amount=total_amount,
                payment_method='Pending',  # Will be selected by user later
                transaction_code=transaction_code,
                status='Pending'
            )

            if not payment:
                return JsonResponse({'error': 'Không thể tạo payment'}, status=500)

            # Store booking info in session for guest users
            if not current_user:
                request.session['guest_booking_id'] = booking['id']
                request.session['guest_payment_id'] = payment['id']

            return JsonResponse({
                'success': True,
                'booking_id': booking['id'],
                'payment_id': payment['id'],
                'transaction_code': transaction_code,
                'redirect_url': f'/booking/{booking["id"]}/confirmation/'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def booking_confirmation(request, booking_id):
    """Display booking confirmation page - allows guest users"""
    booking = Booking.get_by_id(booking_id)

    if not booking:
        messages.error(request, 'Booking không tồn tại.')
        return redirect('trip_list')

    # Get current user
    from accounts.utils import get_current_user
    current_user = get_current_user(request)

    # Check access permissions
    # Allow if: user owns booking, user is admin, or guest with session
    is_owner = current_user and booking['user_id'] == current_user.id
    is_admin = current_user and current_user.is_admin()
    is_guest_session = not current_user and request.session.get('guest_booking_id') == booking_id

    if not (is_owner or is_admin or is_guest_session):
        messages.error(request, 'Bạn không có quyền truy cập booking này.')
        return redirect('trip_list')

    # Get tickets for this booking
    tickets = Ticket.get_by_booking_id(booking_id)

    # Get payment information for this booking
    payment = Payment.get_by_booking_id(booking_id)

    context = {
        'booking': booking,
        'tickets': tickets,
        'payment': payment,
        'payment_methods': Payment.PAYMENT_METHODS,
        'is_guest': not current_user,
    }

    return render(request, 'transport/booking_confirmation.html', context)


def get_trip_seats(request, trip_id):
    """API endpoint to get seats for a trip with booking status"""
    try:
        trip = Trip.get_by_id(int(trip_id))
        if not trip:
            return JsonResponse({'error': 'Trip not found'}, status=404)

        # Get all seats for the bus
        seats = Seat.get_all(bus_id=trip['bus_id'])

        # Get booked seats for this trip (excluding canceled bookings)
        booked_tickets = Ticket.get_active_tickets_for_trip(int(trip_id))
        booked_seat_ids = [ticket['seat_id'] for ticket in booked_tickets]

        # Add booking status to seats
        seats_with_status = []
        for seat in seats:
            seat_data = {
                'id': seat['id'],
                'seat_number': seat['seat_number'],
                'is_booked': seat['id'] in booked_seat_ids,
            }
            seats_with_status.append(seat_data)

        return JsonResponse({
            'seats': seats_with_status,
            'bus_model': trip['bus_model'],
            'total_seats': trip['bus_total_seats']
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@admin_required
def admin_trips(request):
    """Admin page for managing trips"""
    return render(request, 'transport/admin_trips.html')


def my_bookings(request):
    """Display user's bookings and tickets"""
    from accounts.utils import get_current_user
    current_user = get_current_user(request)

    if not current_user:
        messages.info(request, 'Vui lòng đăng nhập để xem vé của bạn.')
        return redirect('login')

    # Get all bookings for the current user
    bookings = Booking.get_all(user_id=current_user.id)

    # Get tickets for each booking
    for booking in bookings:
        booking['tickets'] = Ticket.get_by_booking_id(booking['id'])

    context = {
        'bookings': bookings,
    }

    return render(request, 'transport/my_bookings.html', context)
