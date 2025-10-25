"""
Bookings models using raw SQL (No ORM)
"""
from utils.db_utils import (
    execute_query, execute_query_one,
    execute_insert, execute_update, execute_delete,
    build_where_clause, build_order_clause
)
from typing import List, Dict, Any, Optional
from datetime import datetime
from django.utils.timezone import now
from decimal import Decimal
import uuid


class Booking:
    """Booking model using raw SQL"""

    TABLE_NAME = 'bookings'
    STATUS_CHOICES = [
        ('Pending', 'Chờ xử lý'),
        ('Confirmed', 'Đã xác nhận'),
        ('Canceled', 'Đã hủy'),
    ]

    @classmethod
    def create(cls, user_id: int, trip_id: int, number_of_seats: int,
               total_amount: Decimal = None, status: str = 'Pending') -> Dict[str, Any]:
        """Create a new booking"""
        booking_id = str(uuid.uuid4())
        booking_time = now()

        # Auto-calculate total_amount if not provided
        if total_amount is None:
            from transport.models import Trip
            trip = Trip.get_by_id(trip_id)
            if trip:
                total_amount = number_of_seats * trip['price_per_seat']

        query = f"""
            INSERT INTO {cls.TABLE_NAME}
            (id, number_of_seats, total_amount, booking_time, status, trip_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, trip_id, number_of_seats, total_amount, booking_time, status
        """
        result = execute_query(query, (booking_id, number_of_seats, total_amount,
                                      booking_time, status, trip_id, user_id))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, booking_id: str) -> Optional[Dict[str, Any]]:
        """Get booking by ID with full details"""
        query = f"""
            SELECT
                b.id, b.user_id, b.trip_id, b.number_of_seats, b.total_amount,
                b.booking_time, b.status,
                t.route_id, t.bus_id, t.departure_time, t.arrival_time, t.price_per_seat,
                r.start_location_id, r.end_location_id, r.distance_km,
                sl.name as start_location_name, sl.city as start_location_city,
                el.name as end_location_name, el.city as end_location_city,
                bus.license_plate as bus_license_plate, bus.model as bus_model,
                bus.total_seats as bus_total_seats, bus.manufacture_year as bus_manufacture_year
            FROM {cls.TABLE_NAME} b
            JOIN trips t ON b.trip_id = t.id
            JOIN routes r ON t.route_id = r.id
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            JOIN buses bus ON t.bus_id = bus.id
            WHERE b.id = %s
        """
        return execute_query_one(query, (booking_id,))

    @classmethod
    def get_all(cls, user_id: int = None, trip_id: int = None, status: str = None,
                ordering: List[str] = None) -> List[Dict[str, Any]]:
        """Get all bookings with optional filters"""
        conditions = []
        params = []

        if user_id is not None:
            conditions.append("b.user_id = %s")
            params.append(user_id)
        if trip_id is not None:
            conditions.append("b.trip_id = %s")
            params.append(trip_id)
        if status:
            conditions.append("b.status = %s")
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        order_clause = build_order_clause(ordering or ['-booking_time'])

        query = f"""
            SELECT
                b.id, b.user_id, b.trip_id, b.number_of_seats, b.total_amount,
                b.booking_time, b.status,
                t.route_id, t.bus_id, t.departure_time, t.arrival_time, t.price_per_seat,
                r.start_location_id, r.end_location_id, r.distance_km,
                sl.name as start_location_name, sl.city as start_location_city,
                el.name as end_location_name, el.city as end_location_city,
                bus.license_plate as bus_license_plate, bus.model as bus_model,
                bus.total_seats as bus_total_seats, bus.manufacture_year as bus_manufacture_year
            FROM {cls.TABLE_NAME} b
            JOIN trips t ON b.trip_id = t.id
            JOIN routes r ON t.route_id = r.id
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            JOIN buses bus ON t.bus_id = bus.id
            {where_clause}
            {order_clause}
        """

        return execute_query(query, tuple(params))

    @classmethod
    def update(cls, booking_id: str, number_of_seats: int = None,
               total_amount: Decimal = None, status: str = None) -> bool:
        """Update a booking"""
        updates = []
        params = []

        if number_of_seats is not None:
            updates.append("number_of_seats = %s")
            params.append(number_of_seats)
        if total_amount is not None:
            updates.append("total_amount = %s")
            params.append(total_amount)
        if status is not None:
            updates.append("status = %s")
            params.append(status)

        if not updates:
            return False

        params.append(booking_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, booking_id: str) -> bool:
        """Delete a booking"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (booking_id,)) > 0

    @classmethod
    def cancel_booking(cls, booking_id: str) -> bool:
        """Cancel the booking if it's not already canceled"""
        return cls.update(booking_id, status='Canceled')

    @classmethod
    def confirm_booking(cls, booking_id: str) -> bool:
        """Confirm the booking if it's pending"""
        booking = cls.get_by_id(booking_id)
        if booking and booking['status'] == 'Pending':
            return cls.update(booking_id, status='Confirmed')
        return False

    @classmethod
    def is_active(cls, booking: Dict[str, Any]) -> bool:
        """Check if the booking is active (not canceled)"""
        return booking['status'] != 'Canceled'

    @classmethod
    def is_past_booking(cls, booking: Dict[str, Any]) -> bool:
        """Check if the booking is for a trip that has already departed"""
        return booking['departure_time'] < datetime.now()

    @classmethod
    def can_modify(cls, booking: Dict[str, Any]) -> bool:
        """Check if the booking can be modified (only if pending and trip not departed)"""
        return booking['status'] == 'Pending' and not cls.is_past_booking(booking)

    @classmethod
    def get_statistics(cls) -> Dict[str, int]:
        """Get booking statistics"""
        query = f"""
            SELECT
                COUNT(*) as total_bookings,
                COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_bookings,
                COUNT(CASE WHEN status = 'Confirmed' THEN 1 END) as confirmed_bookings,
                COUNT(CASE WHEN status = 'Canceled' THEN 1 END) as canceled_bookings
            FROM {cls.TABLE_NAME}
        """
        result = execute_query_one(query)
        return result if result else {
            'total_bookings': 0,
            'pending_bookings': 0,
            'confirmed_bookings': 0,
            'canceled_bookings': 0
        }

    @classmethod
    def get_status_display(cls, status: str) -> str:
        """Get display text for status"""
        for choice in cls.STATUS_CHOICES:
            if choice[0] == status:
                return choice[1]
        return status


class Ticket:
    """Ticket model using raw SQL"""

    TABLE_NAME = 'tickets'

    @classmethod
    def create(cls, booking_id: str, seat_id: int, trip_id: int,
               price: Decimal, passenger_name: str) -> Dict[str, Any]:
        """Create a new ticket"""
        query = f"""
            INSERT INTO {cls.TABLE_NAME}
            (booking_id, seat_id, trip_id, price, passenger_name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, booking_id, seat_id, trip_id, price, passenger_name
        """
        result = execute_query(query, (booking_id, seat_id, trip_id, price, passenger_name))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Get ticket by ID with full details"""
        query = f"""
            SELECT
                tk.id, tk.booking_id, tk.seat_id, tk.trip_id, tk.price, tk.passenger_name,
                s.seat_number, s.is_available as seat_is_available,
                b.license_plate as bus_license_plate, b.model as bus_model,
                t.departure_time, t.arrival_time, t.price_per_seat as trip_price_per_seat,
                r.start_location_id, r.end_location_id,
                sl.name as start_location_name, el.name as end_location_name
            FROM {cls.TABLE_NAME} tk
            JOIN seats s ON tk.seat_id = s.id
            JOIN buses b ON s.bus_id = b.id
            JOIN trips t ON tk.trip_id = t.id
            JOIN routes r ON t.route_id = r.id
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            WHERE tk.id = %s
        """
        return execute_query_one(query, (ticket_id,))

    @classmethod
    def get_all(cls, booking_id: str = None, trip_id: int = None,
                user_id: int = None) -> List[Dict[str, Any]]:
        """Get all tickets with optional filters"""
        conditions = []
        params = []

        if booking_id is not None:
            conditions.append("tk.booking_id = %s")
            params.append(booking_id)
        if trip_id is not None:
            conditions.append("tk.trip_id = %s")
            params.append(trip_id)
        if user_id is not None:
            conditions.append("bk.user_id = %s")
            params.append(user_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT
                tk.id, tk.booking_id, tk.seat_id, tk.trip_id, tk.price, tk.passenger_name,
                s.seat_number, s.is_available as seat_is_available,
                b.license_plate as bus_license_plate, b.model as bus_model,
                t.departure_time, t.arrival_time, t.price_per_seat as trip_price_per_seat,
                r.start_location_id, r.end_location_id,
                sl.name as start_location_name, el.name as end_location_name
            FROM {cls.TABLE_NAME} tk
            JOIN seats s ON tk.seat_id = s.id
            JOIN buses b ON s.bus_id = b.id
            JOIN trips t ON tk.trip_id = t.id
            JOIN routes r ON t.route_id = r.id
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            LEFT JOIN bookings bk ON tk.booking_id = bk.id
            {where_clause}
            ORDER BY tk.id
        """

        return execute_query(query, tuple(params))

    @classmethod
    def get_by_booking_id(cls, booking_id: str) -> List[Dict[str, Any]]:
        """Get all tickets for a booking"""
        return cls.get_all(booking_id=booking_id)

    @classmethod
    def update(cls, ticket_id: int, passenger_name: str = None,
               price: Decimal = None) -> bool:
        """Update a ticket"""
        updates = []
        params = []

        if passenger_name is not None:
            updates.append("passenger_name = %s")
            params.append(passenger_name)
        if price is not None:
            updates.append("price = %s")
            params.append(price)

        if not updates:
            return False

        params.append(ticket_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, ticket_id: int) -> bool:
        """Delete a ticket"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (ticket_id,)) > 0

    @classmethod
    def check_seat_booked(cls, trip_id: int, seat_id: int) -> bool:
        """Check if a seat is already booked for a trip"""
        query = f"""
            SELECT COUNT(*) as count
            FROM {cls.TABLE_NAME}
            WHERE trip_id = %s AND seat_id = %s
        """
        result = execute_query_one(query, (trip_id, seat_id))
        return result['count'] > 0 if result else False
