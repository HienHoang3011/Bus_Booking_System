"""
User model using raw SQL instead of Django ORM
"""
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .db_utils import (
    get_user_by_id, get_user_by_username, get_user_by_email,
    create_user as db_create_user, update_user as db_update_user,
    delete_user as db_delete_user, authenticate_user as db_authenticate_user,
    check_username_exists, check_email_exists
)
import re
import json


class User:
    """User class using raw SQL instead of Django ORM"""
    
    # User roles constants
    ROLES = [
        ('admin', 'Quản trị viên'),
        ('user', 'Người dùng'),
    ]
    
    def __init__(self, **kwargs):
        """Initialize user object"""
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.password = kwargs.get('password')
        self.role = kwargs.get('role', 'user')
        self.permissions = kwargs.get('permissions', [])
        self.is_active = kwargs.get('is_active', True)
        self.is_verified = kwargs.get('is_verified', False)
        self.is_staff = kwargs.get('is_staff', False)
        self.is_superuser = kwargs.get('is_superuser', False)
        self.date_joined = kwargs.get('date_joined')
        self.last_login = kwargs.get('last_login')
        
        # Parse permissions if it's a string
        if isinstance(self.permissions, str):
            try:
                self.permissions = json.loads(self.permissions)
            except (json.JSONDecodeError, TypeError):
                self.permissions = []
        
        # Django compatibility fields
        self.USERNAME_FIELD = 'username'
        self.REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        """Check if provided password is correct"""
        return check_password(raw_password, self.password)
    
    def get_full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return first name"""
        return self.first_name
    
    def get_role_display(self):
        """Get role display name in Vietnamese"""
        role_dict = dict(self.ROLES)
        return role_dict.get(self.role, self.role)
    
    def get_permissions_display(self):
        """Get permissions as comma-separated string"""
        return ', '.join(self.permissions) if self.permissions else 'Không có quyền đặc biệt'
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        if self.role == 'admin':
            return True  # Admin has all permissions
        return permission in self.permissions
    
    def has_perm(self, perm, obj=None):
        """Django compatibility method"""
        if self.is_superuser:
            return True
        return self.has_permission(perm)
    
    def has_module_perms(self, app_label):
        """Django compatibility method"""
        if self.is_superuser:
            return True
        return self.role == 'admin'
    
    
    def save(self, *args, **kwargs):
        """Save user to database"""
        if self.id:
            # Update existing user
            updates = {
                'username': self.username,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'password': self.password,
                'role': self.role,
                'permissions': self.permissions,
                'is_active': self.is_active,
                'is_verified': self.is_verified,
                'is_staff': self.is_staff,
                'is_superuser': self.is_superuser,
                'last_login': self.last_login
            }
            return db_update_user(self.id, **updates)
        else:
            # Create new user
            user_id = db_create_user(
                username=self.username,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                password=self.password,
                role=self.role,
                permissions=self.permissions,
                is_active=self.is_active,
                is_verified=self.is_verified
            )
            if user_id:
                self.id = user_id
                return True
            return False
    
    def delete(self):
        """Delete user from database"""
        if self.id:
            return db_delete_user(self.id)
        return False
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for real users"""  
        return False
    
    @classmethod
    def create_user(cls, username, email, first_name, last_name, password, role='user', **extra_fields):
        """Create and save a new user"""
        # Validate input
        if not username or not email or not password:
            raise ValueError("Username, email và password là bắt buộc")
        
        if check_username_exists(username):
            raise ValueError("Tên đăng nhập đã tồn tại")

        if check_email_exists(email):
            raise ValueError("Email đã được sử dụng")
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Email không hợp lệ")
        
        # Validate password strength
        if len(password) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        
        # Create user in database
        user_id = db_create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=role,
            **extra_fields
        )
        
        if not user_id:
            raise ValueError("Không thể tạo người dùng")
        
        # Return user object
        user_data = get_user_by_id(user_id)
        return cls(**user_data) if user_data else None
    
    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user with username and password"""
        user_data = db_authenticate_user(username, password)
        return cls(**user_data) if user_data else None
    
    @classmethod
    def objects(cls):
        """Return UserManager for ORM-like interface"""
        return UserManager()


class UserManager:
    """Manager class to provide ORM-like interface"""
    
    def get(self, **kwargs):
        """Get single user by criteria"""
        if 'id' in kwargs:
            user_data = get_user_by_id(kwargs['id'])
        elif 'username' in kwargs:
            user_data = get_user_by_username(kwargs['username'])
        elif 'email' in kwargs:
            user_data = get_user_by_email(kwargs['email'])
        else:
            raise ValueError("Must specify id, username, or email")
        
        if not user_data:
            raise User.DoesNotExist("User not found")
        
        return User(**user_data)
    
    def filter(self, **kwargs):
        """Filter users by criteria - simplified implementation"""
        if 'username' in kwargs:
            user_data = get_user_by_username(kwargs['username'])
            return [User(**user_data)] if user_data else []
        elif 'email' in kwargs:
            user_data = get_user_by_email(kwargs['email'])
            return [User(**user_data)] if user_data else []
        else:
            # Return all users
            from .db_utils import get_all_users
            users_data = get_all_users()
            return [User(**user_data) for user_data in users_data]
    
    def all(self):
        """Get all users"""
        from .db_utils import get_all_users
        users_data = get_all_users()
        return [User(**user_data) for user_data in users_data]
    
    def count(self):
        """Count total users"""
        from .db_utils import count_users
        return count_users()
    
    def exists(self, **kwargs):
        """Check if user exists"""
        if 'username' in kwargs:
            return check_username_exists(kwargs['username'])
        elif 'email' in kwargs:
            return check_email_exists(kwargs['email'])
        return False


# Add DoesNotExist exception for compatibility
class DoesNotExist(Exception):
    pass

User.DoesNotExist = DoesNotExist
