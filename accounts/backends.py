from django.contrib.auth.backends import BaseBackend
from .models import User

class AuthUserBackend(BaseBackend):
    """Custom authentication backend using raw SQL instead of Django ORM"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate user with username and password using raw SQL"""
        try:
            # User.authenticate uses raw SQL via db_utils.py
            user = User.authenticate(username, password)
            if user:
                return user
        except Exception as e:
            # Log exception if needed
            return None
        return None

    def get_user(self, user_id):
        """Get user by ID using raw SQL"""
        try:
            # User.objects().get() uses raw SQL via db_utils.py
            return User.objects().get(id=user_id)
        except User.DoesNotExist:
            return None
        except Exception:
            return None
