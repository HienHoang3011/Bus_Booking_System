"""
Database utility functions for raw SQL operations
Replaces Django ORM with direct PostgreSQL queries
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        """Get database connection from Django settings (loaded from .env)"""
        if not self.connection or self.connection.closed:
            try:
                # Django DATABASES settings automatically loaded from .env via os.getenv()
                self.connection = psycopg2.connect(
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT'],
                    database=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD']
                )
            except Exception as e:
                logger.error(f"Database connection error: {e}")
                raise
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()


# Global database connection instance
db_conn = DatabaseConnection()


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute SQL query and return results"""
    connection = db_conn.get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
            return dict(result) if result else None
        elif fetch_all:
            results = cursor.fetchall()
            return [dict(row) for row in results]
        else:
            connection.commit()
            return cursor.rowcount
            
    except Exception as e:
        connection.rollback()
        logger.error(f"Query execution error: {e}")
        raise
    finally:
        cursor.close()


def get_user_by_id(user_id):
    """Get user by ID"""
    query = """
        SELECT id, username, email, first_name, last_name, password, role, 
               permissions, is_active, is_verified, is_staff, is_superuser,
               date_joined, last_login
        FROM users 
        WHERE id = %s
    """
    return execute_query(query, (user_id,), fetch_one=True)


def get_user_by_username(username):
    """Get user by username"""
    query = """
        SELECT id, username, email, first_name, last_name, password, role, 
               permissions, is_active, is_verified, is_staff, is_superuser,
               date_joined, last_login
        FROM users 
        WHERE username = %s
    """
    return execute_query(query, (username,), fetch_one=True)


def get_user_by_email(email):
    """Get user by email"""
    query = """
        SELECT id, username, email, first_name, last_name, password, role, 
               permissions, is_active, is_verified, is_staff, is_superuser,
               date_joined, last_login
        FROM users 
        WHERE email = %s
    """
    return execute_query(query, (email,), fetch_one=True)


def create_user(username, email, first_name, last_name, password, role='user', **extra_fields):
    """Create new user"""
    # Hash password
    hashed_password = make_password(password)
    
    # Set Django compatibility fields based on role
    is_staff = role == 'admin'
    is_superuser = role == 'admin'
    
    # Prepare permissions
    permissions = extra_fields.get('permissions', [])
    permissions_json = json.dumps(permissions) if permissions else '[]'
    
    query = """
        INSERT INTO users (username, email, first_name, last_name, password, role,
                          permissions, is_active, is_verified, is_staff, is_superuser,
                          date_joined)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    
    result = execute_query(query, (
        username, email, first_name, last_name, hashed_password, role,
        permissions_json, True, False, is_staff, is_superuser, timezone.now()
    ), fetch_one=True)
    
    return result['id'] if result else None


def update_user(user_id, **updates):
    """Update user fields"""
    if not updates:
        return True
    
    # Build dynamic update query
    set_clauses = []
    values = []
    
    for field, value in updates.items():
        if field == 'permissions':
            value = json.dumps(value) if isinstance(value, list) else value
        set_clauses.append(f"{field} = %s")
        values.append(value)
    
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
    
    return execute_query(query, values) > 0


def delete_user(user_id):
    """Delete user"""
    query = "DELETE FROM users WHERE id = %s"
    return execute_query(query, (user_id,)) > 0


def get_all_users():
    """Get all users"""
    query = """
        SELECT id, username, email, first_name, last_name, password, role, 
               permissions, is_active, is_verified, is_staff, is_superuser,
               date_joined, last_login
        FROM users 
        ORDER BY date_joined DESC
    """
    return execute_query(query, fetch_all=True)



def count_users():
    """Count total users"""
    query = "SELECT COUNT(*) as count FROM users"
    result = execute_query(query, fetch_one=True)
    return result['count'] if result else 0


def count_users_by_role(role):
    """Count users by role"""
    query = "SELECT COUNT(*) as count FROM users WHERE role = %s"
    result = execute_query(query, (role,), fetch_one=True)
    return result['count'] if result else 0


def check_username_exists(username):
    """Check if username exists"""
    query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
    result = execute_query(query, (username,), fetch_one=True)
    return result['count'] > 0 if result else False


def check_email_exists(email):
    """Check if email exists"""
    query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
    result = execute_query(query, (email,), fetch_one=True)
    return result['count'] > 0 if result else False


def authenticate_user(username, password):
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if not user:
        return None
    
    if not check_password(password, user['password']):
        return None
    
    # Update last login
    update_user(user['id'], last_login=timezone.now())
    
    return user


def create_user_session(user_id, session_key, ip_address, user_agent):
    """Create user session"""
    query = """
        INSERT INTO user_sessions (user_id, session_key, ip_address, user_agent, 
                                 created_at, last_activity, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    
    result = execute_query(query, (
        user_id, session_key, ip_address, user_agent,
        timezone.now(), timezone.now(), True
    ), fetch_one=True)
    
    return result['id'] if result else None


def get_user_session(username, session_key):
    """Get user session by username and session key"""
    query = """
        SELECT s.id, s.user_id, s.session_key, s.ip_address, s.user_agent,
               s.created_at, s.last_activity, s.is_active,
               u.username, u.email, u.first_name, u.last_name, u.role,
               u.permissions, u.is_active as user_is_active, u.is_staff, u.is_superuser,
               u.date_joined, u.last_login
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE u.username = %s AND s.session_key = %s AND s.is_active = %s
    """
    return execute_query(query, (username, session_key, True), fetch_one=True)


def update_user_session_activity(session_id):
    """Update user session last activity"""
    query = "UPDATE user_sessions SET last_activity = %s WHERE id = %s"
    return execute_query(query, (timezone.now(), session_id)) > 0


def delete_user_session(username, session_key):
    """Delete user session"""
    query = """
        DELETE FROM user_sessions
        WHERE user_id = (SELECT id FROM users WHERE username = %s)
        AND session_key = %s
    """
    return execute_query(query, (username, session_key)) > 0


def delete_user_sessions_by_user(user_id):
    """Delete all sessions for a user"""
    query = "DELETE FROM user_sessions WHERE user_id = %s"
    return execute_query(query, (user_id,)) > 0


def count_active_sessions():
    """Count active sessions"""
    query = "SELECT COUNT(*) as count FROM user_sessions WHERE is_active = %s"
    result = execute_query(query, (True,), fetch_one=True)
    return result['count'] if result else 0


