from django.contrib import admin
from .models import User, UserSession

# Register your models here.
# Note: Since we're using raw SQL instead of Django ORM,
# these admin registrations are for compatibility only
# The actual database operations are handled by db_utils.py

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user', 'ip_address', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session_key', 'user__username', 'ip_address')
