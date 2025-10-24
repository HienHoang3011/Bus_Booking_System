# Import raw SQL models instead of Django ORM models
from .user_model import User
from .session_model import UserSession

# Keep the original models for backward compatibility if needed
# but use the raw SQL versions as the primary models
    