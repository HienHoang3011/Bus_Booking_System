from accounts.models import User
from accounts.utils import create_user_session

# Hàm xử lý sau khi đăng nhập Google: tạo user MongoDB nếu chưa có và đồng bộ session custom

def process_login_gg(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('email')
    fullname = details.get('fullname') or ''
    first_name = details.get('first_name') or (fullname.split(' ')[0] if fullname else '')
    last_name = details.get('last_name') or (' '.join(fullname.split(' ')[1:]) if fullname else '')
    username = email.split('@')[0] if email else ''
    password = 'google_oauth2_default_password'

    user = User.objects.filter(email=email).first() if email else None
    if not user and email:
        user = User(
            username=username,
            email=email,
            first_name=first_name or username,
            last_name=last_name or '',
            is_active=True,
            is_verified=True,
        )
        user.set_password(password)
        user.save()

    # Tạo session custom cho user Google
    if user:
        request = strategy.request
        create_user_session(request, user)

# Middleware đồng bộ session custom sau khi đăng nhập Google
class SyncCustomSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('username') and hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False) and getattr(request.user, 'email', None):
            user = User.objects.filter(email=request.user.email).first()
            if user:
                create_user_session(request, user)
        return self.get_response(request)
