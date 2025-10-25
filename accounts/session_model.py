"""
UserSession model using raw SQL instead of Django ORM
"""
from django.utils import timezone
from .db_utils import (
    create_user_session as db_create_user_session,
    get_user_session as db_get_user_session,
    update_user_session_activity as db_update_user_session_activity,
    delete_user_session as db_delete_user_session,
    delete_user_sessions_by_user as db_delete_user_sessions_by_user,
    count_active_sessions as db_count_active_sessions
)


class UserSession:
    """User session class using raw SQL instead of Django ORM"""

    def __init__(self, **kwargs):
        """Initialize user session object"""
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.session_key = kwargs.get('session_key')
        self.created_at = kwargs.get('created_at')
        self.last_activity = kwargs.get('last_activity')
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
        self.is_active = kwargs.get('is_active', True)
        self.user = kwargs.get('user')  # User object if loaded
        self.pk = self.id  # Django compatibility

    def __str__(self):
        if self.user:
            return f"Session for {self.user.username} from {self.ip_address}"
        return f"Session {self.session_key} from {self.ip_address}"

    def save(self, *args, **kwargs):
        """Save session to database"""
        if self.id:
            # Update existing session
            return db_update_user_session_activity(self.id)
        else:
            # Create new session
            session_id = db_create_user_session(
                user_id=self.user_id,
                session_key=self.session_key,
                ip_address=self.ip_address,
                user_agent=self.user_agent
            )
            if session_id:
                self.id = session_id
                self.pk = session_id
                return True
            return False

    def delete(self):
        """Delete session from database"""
        if self.session_key and self.user:
            return db_delete_user_session(self.user.username, self.session_key)
        return False


class UserSessionQuerySet:
    """QuerySet-like wrapper for session results"""

    def __init__(self, sessions):
        self.sessions = sessions

    def first(self):
        """Return first session or None"""
        return self.sessions[0] if self.sessions else None

    def delete(self):
        """Delete all sessions in the queryset"""
        for session in self.sessions:
            session.delete()
        return len(self.sessions)


class UserSessionManager:
    """Manager class to provide ORM-like interface for UserSession"""

    def filter(self, **kwargs):
        """Filter sessions by criteria - simplified implementation"""
        if 'user__username' in kwargs and 'session_key' in kwargs:
            session_data = db_get_user_session(kwargs['user__username'], kwargs['session_key'])
            sessions = [UserSession(**session_data)] if session_data else []
            return UserSessionQuerySet(sessions)
        return UserSessionQuerySet([])

    def get(self, **kwargs):
        """Get single session by criteria"""
        result = self.filter(**kwargs)
        session = result.first()
        if not session:
            raise UserSession.DoesNotExist("Session not found")
        return session

    def all(self):
        """Get all sessions"""
        return UserSessionQuerySet([])

    def count(self):
        """Count active sessions"""
        return db_count_active_sessions()

    def delete(self, **kwargs):
        """Delete sessions by criteria"""
        if 'user__username' in kwargs and 'session_key' in kwargs:
            return db_delete_user_session(kwargs['user__username'], kwargs['session_key'])
        elif 'user_id' in kwargs:
            return db_delete_user_sessions_by_user(kwargs['user_id'])
        return False


# Add DoesNotExist exception for compatibility
class DoesNotExist(Exception):
    pass

UserSession.DoesNotExist = DoesNotExist

# Add objects manager as class attribute
UserSession.objects = UserSessionManager()
