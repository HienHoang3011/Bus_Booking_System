"""
Transport models using raw SQL (No ORM)
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


class Locations:
    """Location model using raw SQL"""

    TABLE_NAME = 'locations'

    @classmethod
    def create(cls, name: str, city: str) -> Dict[str, Any]:
        """Create a new location"""
        query = f"""
            INSERT INTO {cls.TABLE_NAME} (name, city)
            VALUES (%s, %s)
            RETURNING id, name, city
        """
        result = execute_query(query, (name, city))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, location_id: int) -> Optional[Dict[str, Any]]:
        """Get location by ID"""
        query = f"SELECT id, name, city FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_query_one(query, (location_id,))

    @classmethod
    def get_all(cls, ordering: List[str] = None) -> List[Dict[str, Any]]:
        """Get all locations"""
        order_clause = build_order_clause(ordering or ['name'])
        query = f"SELECT id, name, city FROM {cls.TABLE_NAME} {order_clause}"
        return execute_query(query)

    @classmethod
    def search(cls, name: str = None, city: str = None) -> List[Dict[str, Any]]:
        """Search locations by name or city"""
        conditions = []
        params = []

        if name:
            conditions.append("name ILIKE %s")
            params.append(f"%{name}%")
        if city:
            conditions.append("city ILIKE %s")
            params.append(f"%{city}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT id, name, city FROM {cls.TABLE_NAME} {where_clause} ORDER BY name"

        return execute_query(query, tuple(params))

    @classmethod
    def update(cls, location_id: int, name: str = None, city: str = None) -> bool:
        """Update a location"""
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if city is not None:
            updates.append("city = %s")
            params.append(city)

        if not updates:
            return False

        params.append(location_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, location_id: int) -> bool:
        """Delete a location"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (location_id,)) > 0

    @classmethod
    def full_address(cls, location: Dict[str, Any]) -> str:
        """Get full address of location"""
        return f"{location['name']}, {location['city']}"


class Route:
    """Route model using raw SQL"""

    TABLE_NAME = 'routes'

    @classmethod
    def create(cls, start_location_id: int, end_location_id: int, distance_km: float) -> Dict[str, Any]:
        """Create a new route"""
        query = f"""
            INSERT INTO {cls.TABLE_NAME} (start_location_id, end_location_id, distance_km)
            VALUES (%s, %s, %s)
            RETURNING id, start_location_id, end_location_id, distance_km
        """
        result = execute_query(query, (start_location_id, end_location_id, distance_km))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, route_id: int) -> Optional[Dict[str, Any]]:
        """Get route by ID with location details"""
        query = f"""
            SELECT
                r.id, r.start_location_id, r.end_location_id, r.distance_km,
                sl.name as start_location_name, sl.city as start_location_city,
                el.name as end_location_name, el.city as end_location_city
            FROM {cls.TABLE_NAME} r
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            WHERE r.id = %s
        """
        return execute_query_one(query, (route_id,))

    @classmethod
    def get_all(cls, start_location_id: int = None, end_location_id: int = None,
                ordering: List[str] = None) -> List[Dict[str, Any]]:
        """Get all routes with optional filters"""
        conditions = []
        params = []

        if start_location_id:
            conditions.append("r.start_location_id = %s")
            params.append(start_location_id)
        if end_location_id:
            conditions.append("r.end_location_id = %s")
            params.append(end_location_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        order_clause = build_order_clause(ordering or ['distance_km'])

        query = f"""
            SELECT
                r.id, r.start_location_id, r.end_location_id, r.distance_km,
                sl.name as start_location_name, sl.city as start_location_city,
                el.name as end_location_name, el.city as end_location_city
            FROM {cls.TABLE_NAME} r
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            {where_clause}
            {order_clause}
        """

        return execute_query(query, tuple(params))

    @classmethod
    def update(cls, route_id: int, start_location_id: int = None,
               end_location_id: int = None, distance_km: float = None) -> bool:
        """Update a route"""
        updates = []
        params = []

        if start_location_id is not None:
            updates.append("start_location_id = %s")
            params.append(start_location_id)
        if end_location_id is not None:
            updates.append("end_location_id = %s")
            params.append(end_location_id)
        if distance_km is not None:
            updates.append("distance_km = %s")
            params.append(distance_km)

        if not updates:
            return False

        params.append(route_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, route_id: int) -> bool:
        """Delete a route"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (route_id,)) > 0

    @classmethod
    def route_info(cls, route: Dict[str, Any]) -> str:
        """Get route info string"""
        return f"Route from {route['start_location_name']}, {route['start_location_city']} to {route['end_location_name']}, {route['end_location_city']}, Distance: {route['distance_km']} km"


class Bus:
    """Bus model using raw SQL"""

    TABLE_NAME = 'buses'

    @classmethod
    def create(cls, license_plate: str, model: str, total_seats: int, manufacture_year: int) -> Dict[str, Any]:
        """Create a new bus"""
        query = f"""
            INSERT INTO {cls.TABLE_NAME} (license_plate, model, total_seats, manufacture_year)
            VALUES (%s, %s, %s, %s)
            RETURNING id, license_plate, model, total_seats, manufacture_year
        """
        result = execute_query(query, (license_plate, model, total_seats, manufacture_year))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, bus_id: int) -> Optional[Dict[str, Any]]:
        """Get bus by ID"""
        query = f"SELECT id, license_plate, model, total_seats, manufacture_year FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_query_one(query, (bus_id,))

    @classmethod
    def get_all(cls, ordering: List[str] = None) -> List[Dict[str, Any]]:
        """Get all buses"""
        order_clause = build_order_clause(ordering or ['license_plate'])
        query = f"SELECT id, license_plate, model, total_seats, manufacture_year FROM {cls.TABLE_NAME} {order_clause}"
        return execute_query(query)

    @classmethod
    def search(cls, license_plate: str = None, model: str = None) -> List[Dict[str, Any]]:
        """Search buses by license plate or model"""
        conditions = []
        params = []

        if license_plate:
            conditions.append("license_plate ILIKE %s")
            params.append(f"%{license_plate}%")
        if model:
            conditions.append("model ILIKE %s")
            params.append(f"%{model}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT id, license_plate, model, total_seats, manufacture_year FROM {cls.TABLE_NAME} {where_clause} ORDER BY license_plate"

        return execute_query(query, tuple(params))

    @classmethod
    def update(cls, bus_id: int, license_plate: str = None, model: str = None,
               total_seats: int = None, manufacture_year: int = None) -> bool:
        """Update a bus"""
        updates = []
        params = []

        if license_plate is not None:
            updates.append("license_plate = %s")
            params.append(license_plate)
        if model is not None:
            updates.append("model = %s")
            params.append(model)
        if total_seats is not None:
            updates.append("total_seats = %s")
            params.append(total_seats)
        if manufacture_year is not None:
            updates.append("manufacture_year = %s")
            params.append(manufacture_year)

        if not updates:
            return False

        params.append(bus_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, bus_id: int) -> bool:
        """Delete a bus"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (bus_id,)) > 0


class Seat:
    """Seat model using raw SQL"""

    TABLE_NAME = 'seats'

    @classmethod
    def create(cls, seat_number: str, bus_id: int, is_available: bool = True) -> Dict[str, Any]:
        """Create a new seat"""
        query = f"""
            INSERT INTO {cls.TABLE_NAME} (seat_number, bus_id, is_available)
            VALUES (%s, %s, %s)
            RETURNING id, seat_number, bus_id, is_available
        """
        result = execute_query(query, (seat_number, bus_id, is_available))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, seat_id: int) -> Optional[Dict[str, Any]]:
        """Get seat by ID with bus details"""
        query = f"""
            SELECT
                s.id, s.seat_number, s.bus_id, s.is_available,
                b.license_plate as bus_license_plate, b.model as bus_model
            FROM {cls.TABLE_NAME} s
            JOIN buses b ON s.bus_id = b.id
            WHERE s.id = %s
        """
        return execute_query_one(query, (seat_id,))

    @classmethod
    def get_all(cls, bus_id: int = None, is_available: bool = None,
                ordering: List[str] = None) -> List[Dict[str, Any]]:
        """Get all seats with optional filters"""
        conditions = []
        params = []

        if bus_id is not None:
            conditions.append("s.bus_id = %s")
            params.append(bus_id)
        if is_available is not None:
            conditions.append("s.is_available = %s")
            params.append(is_available)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        order_clause = build_order_clause(ordering or ['seat_number'])

        query = f"""
            SELECT
                s.id, s.seat_number, s.bus_id, s.is_available,
                b.license_plate as bus_license_plate, b.model as bus_model
            FROM {cls.TABLE_NAME} s
            JOIN buses b ON s.bus_id = b.id
            {where_clause}
            {order_clause}
        """

        return execute_query(query, tuple(params))

    @classmethod
    def update(cls, seat_id: int, seat_number: str = None, is_available: bool = None) -> bool:
        """Update a seat"""
        updates = []
        params = []

        if seat_number is not None:
            updates.append("seat_number = %s")
            params.append(seat_number)
        if is_available is not None:
            updates.append("is_available = %s")
            params.append(is_available)

        if not updates:
            return False

        params.append(seat_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, seat_id: int) -> bool:
        """Delete a seat"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (seat_id,)) > 0


class Trip:
    """Trip model using raw SQL"""

    TABLE_NAME = 'trips'

    @classmethod
    def create(cls, route_id: int, bus_id: int, departure_time: datetime,
               arrival_time: datetime, price_per_seat: Decimal) -> Dict[str, Any]:
        """Create a new trip"""
        query = f"""
            INSERT INTO {cls.TABLE_NAME} (route_id, bus_id, departure_time, arrival_time, price_per_seat)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, route_id, bus_id, departure_time, arrival_time, price_per_seat
        """
        result = execute_query(query, (route_id, bus_id, departure_time, arrival_time, price_per_seat))
        return result[0] if result else None

    @classmethod
    def get_by_id(cls, trip_id: int) -> Optional[Dict[str, Any]]:
        """Get trip by ID with route and bus details"""
        query = f"""
            SELECT
                t.id, t.route_id, t.bus_id, t.departure_time, t.arrival_time, t.price_per_seat,
                r.start_location_id, r.end_location_id, r.distance_km,
                sl.name as start_location_name, sl.city as start_location_city,
                el.name as end_location_name, el.city as end_location_city,
                b.license_plate as bus_license_plate, b.model as bus_model,
                b.total_seats as bus_total_seats, b.manufacture_year as bus_manufacture_year
            FROM {cls.TABLE_NAME} t
            JOIN routes r ON t.route_id = r.id
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            JOIN buses b ON t.bus_id = b.id
            WHERE t.id = %s
        """
        return execute_query_one(query, (trip_id,))

    @classmethod
    def get_all(cls, route_id: int = None, bus_id: int = None, upcoming_only: bool = False,
                ordering: List[str] = None) -> List[Dict[str, Any]]:
        """Get all trips with optional filters"""
        conditions = []
        params = []

        if route_id is not None:
            conditions.append("t.route_id = %s")
            params.append(route_id)
        if bus_id is not None:
            conditions.append("t.bus_id = %s")
            params.append(bus_id)
        if upcoming_only:
            conditions.append("t.departure_time > %s")
            params.append(now())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        order_clause = build_order_clause(ordering or ['-departure_time'])

        query = f"""
            SELECT
                t.id, t.route_id, t.bus_id, t.departure_time, t.arrival_time, t.price_per_seat,
                r.start_location_id, r.end_location_id, r.distance_km,
                sl.name as start_location_name, sl.city as start_location_city,
                el.name as end_location_name, el.city as end_location_city,
                b.license_plate as bus_license_plate, b.model as bus_model,
                b.total_seats as bus_total_seats, b.manufacture_year as bus_manufacture_year
            FROM {cls.TABLE_NAME} t
            JOIN routes r ON t.route_id = r.id
            JOIN locations sl ON r.start_location_id = sl.id
            JOIN locations el ON r.end_location_id = el.id
            JOIN buses b ON t.bus_id = b.id
            {where_clause}
            {order_clause}
        """

        return execute_query(query, tuple(params))

    @classmethod
    def update(cls, trip_id: int, route_id: int = None, bus_id: int = None,
               departure_time: datetime = None, arrival_time: datetime = None,
               price_per_seat: Decimal = None) -> bool:
        """Update a trip"""
        updates = []
        params = []

        if route_id is not None:
            updates.append("route_id = %s")
            params.append(route_id)
        if bus_id is not None:
            updates.append("bus_id = %s")
            params.append(bus_id)
        if departure_time is not None:
            updates.append("departure_time = %s")
            params.append(departure_time)
        if arrival_time is not None:
            updates.append("arrival_time = %s")
            params.append(arrival_time)
        if price_per_seat is not None:
            updates.append("price_per_seat = %s")
            params.append(price_per_seat)

        if not updates:
            return False

        params.append(trip_id)
        query = f"UPDATE {cls.TABLE_NAME} SET {', '.join(updates)} WHERE id = %s"
        return execute_update(query, tuple(params)) > 0

    @classmethod
    def delete(cls, trip_id: int) -> bool:
        """Delete a trip"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return execute_delete(query, (trip_id,)) > 0

    @classmethod
    def is_upcoming(cls, trip: Dict[str, Any]) -> bool:
        """Check if the trip is upcoming"""
        return trip['departure_time'] > now()

    @classmethod
    def get_duration(cls, trip: Dict[str, Any]) -> str:
        """Get the duration of the trip in hours and minutes"""
        duration = trip['arrival_time'] - trip['departure_time']
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"

    @classmethod
    def available_seats(cls, trip_id: int) -> int:
        """Get the number of available seats on the bus for this trip"""
        query = """
            SELECT
                b.total_seats - COALESCE(SUM(bk.number_of_seats), 0) as available
            FROM trips t
            JOIN buses b ON t.bus_id = b.id
            LEFT JOIN bookings bk ON t.id = bk.trip_id AND bk.status != 'Canceled'
            WHERE t.id = %s
            GROUP BY b.total_seats
        """
        result = execute_query_one(query, (trip_id,))
        return result['available'] if result else 0
