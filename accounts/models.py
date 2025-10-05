from django.db import models
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import re
# Create your models here.

class User(models.Model):
    # User roles constants - simplified to only admin and user
    ROLES = [
        ('admin', 'Quản trị viên'),
        ('user', 'Người dùng'),
    ]
    username = models.CharField(max_length=300, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=255)  # Hashed password
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    permissions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    # Django compatibility fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = 'username'

    # Các trường này sẽ được hỏi khi chạy lệnh createsuperuser
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    class Meta:
        ordering = ['-date_joined']
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        db_table = 'users'

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
    
    @classmethod
    def create_user(cls, username, email, first_name, last_name, password, role='user', **extra_fields):
        """Create and save a new user"""
        # Validate input
        if not username or not email or not password:
            raise ValueError("Username, email và password là bắt buộc")
        
        if cls.objects.filter(username=username).exists():
            raise ValueError("Tên đăng nhập đã tồn tại")

        if cls.objects.filter(email=email).exists():
            raise ValueError("Email đã được sử dụng")
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Email không hợp lệ")
        
        # Validate password strength
        if len(password) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        
        # Set Django compatibility fields based on role
        is_staff = role == 'admin'
        is_superuser = role == 'admin'
        
        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        # Use set_password to properly hash the password
        user.set_password(password)
        user.save()
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user with username and password"""
        try:
            user = cls.objects.get(username=username)
            if user.check_password(password):
                # Update last login
                user.last_login = timezone.now()
                user.save()
                return user
        except cls.DoesNotExist:
            pass
        return None

    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True

    @property
    def is_anonymous(self):
        """Always return False for real users"""  
        return False

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
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_regular_user(self):
        """Check if user is regular user"""
        return self.role == 'user'
    
    def can_manage_users(self):
        """Check if user can manage other users - only admin"""
        return self.role == 'admin'
    
    def can_access_admin_panel(self):
        """Check if user can access admin panel - only admin"""
        return self.role == 'admin'
    
    def add_permission(self, permission):
        """Add permission to user"""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.save()
    
    def remove_permission(self, permission):
        """Remove permission from user"""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.save()
    
    def get_permissions_display(self):
        """Get permissions as comma-separated string"""
        return ', '.join(self.permissions) if self.permissions else 'Không có quyền đặc biệt'

    def save(self, *args, **kwargs):
        """Override save to update Django compatibility fields"""
        # Auto-update is_staff and is_superuser based on role
        self.is_staff = self.role == 'admin'
        self.is_superuser = self.role == 'admin'
        super().save(*args, **kwargs)

class UserSession(models.Model):
    """User session management"""
    session_key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(
        User,
        related_name='sessions',
        on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-last_activity']
        db_table = 'user_sessions'

    def __str__(self):
        return f"Session for {self.user} from {self.ip_address}"
    