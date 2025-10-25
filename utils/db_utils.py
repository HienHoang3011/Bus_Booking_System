"""
Database utility functions for raw SQL operations
"""
from django.db import connection
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import uuid


def dictfetchall(cursor) -> List[Dict[str, Any]]:
    """Return all rows from a cursor as a list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dictfetchone(cursor) -> Optional[Dict[str, Any]]:
    """Return one row from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None


def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return results as list of dicts
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or ())
        return dictfetchall(cursor)


def execute_query_one(query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
    """
    Execute a SELECT query and return one result as dict
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or ())
        return dictfetchone(cursor)


def execute_insert(query: str, params: tuple = None) -> int:
    """
    Execute an INSERT query and return the inserted ID
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or ())
        # For PostgreSQL, use RETURNING id clause in query
        result = cursor.fetchone()
        return result[0] if result else None


def execute_update(query: str, params: tuple = None) -> int:
    """
    Execute an UPDATE query and return number of affected rows
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount


def execute_delete(query: str, params: tuple = None) -> int:
    """
    Execute a DELETE query and return number of affected rows
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount


def convert_to_db_value(value: Any) -> Any:
    """
    Convert Python values to database-compatible values
    """
    if isinstance(value, datetime):
        return value
    elif isinstance(value, Decimal):
        return value
    elif isinstance(value, bool):
        return value
    elif isinstance(value, uuid.UUID):
        return str(value)
    return value


def build_where_clause(filters: Dict[str, Any]) -> tuple:
    """
    Build WHERE clause from filters dict
    Returns (where_clause_string, params_tuple)
    """
    if not filters:
        return "", ()

    conditions = []
    params = []

    for key, value in filters.items():
        if value is not None:
            conditions.append(f"{key} = %s")
            params.append(convert_to_db_value(value))

    where_clause = " AND ".join(conditions)
    return f"WHERE {where_clause}" if where_clause else "", tuple(params)


def build_order_clause(ordering: List[str]) -> str:
    """
    Build ORDER BY clause from ordering list
    """
    if not ordering:
        return ""

    order_parts = []
    for field in ordering:
        if field.startswith('-'):
            order_parts.append(f"{field[1:]} DESC")
        else:
            order_parts.append(f"{field} ASC")

    return f"ORDER BY {', '.join(order_parts)}"


def paginate_query(query: str, page: int = 1, page_size: int = 100) -> str:
    """
    Add pagination to query
    """
    offset = (page - 1) * page_size
    return f"{query} LIMIT {page_size} OFFSET {offset}"
