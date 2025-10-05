from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .forms import CustomUserCreationForm, LoginForm, UserUpdateForm, PasswordChangeForm
from .models import User, UserSession
from .utils import get_current_user, create_user_session, logout_user
from .decorators import login_required, admin_required
from datetime import datetime
import json
import logging
import re

logger = logging.getLogger(__name__)


def home_view(request):
    """Trang chủ - Home page"""
    user = get_current_user(request)
    
    context = {
        'user': user,
    }
    
    # Add stats for admin users
    if user and user.is_admin():
        try:
            context['total_users'] = User.objects.count()
            context['active_sessions'] = UserSession.objects.count()
        except Exception:
            context['total_users'] = 0
            context['active_sessions'] = 0
    
    return render(request, 'accounts/home.html', context)


def register_view(request):
    """Đăng ký tài khoản - User registration"""
    current_user = get_current_user(request)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(current_user, request.POST)
        try:
            if form.is_valid():
                user = form.save()
                messages.success(request, f'Đăng ký thành công! Chào mừng {user.first_name} với vai trò {user.get_role_display()}! Bạn có thể đăng nhập ngay bây giờ.')
                return redirect('login')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra (có thể do kết nối PostgreSQL): {str(e)}')
    else:
        form = CustomUserCreationForm(current_user)
    
    return render(request, 'accounts/register.html', {'form': form, 'user': current_user})


def login_view(request):
    """Đăng nhập - User login"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        try:
            if form.is_valid():
                user = form.cleaned_data['user']
                
                # Create session
                session_key = create_user_session(request, user)
                if session_key:
                    # Update last login
                    user.last_login = timezone.now()
                    user.save()
                    
                    messages.success(request, f'Chào mừng {user.first_name} {user.last_name} ({user.get_role_display()})!')
                    
                    # Redirect based on role - simplified to only admin and user
                    if user.is_admin():
                        return redirect('admin_dashboard')
                    else:
                        return redirect('dashboard')
                else:
                    messages.error(request, 'Có lỗi xảy ra khi tạo phiên đăng nhập.')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra (có thể do kết nối MongoDB): {str(e)}')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Đăng xuất - User logout"""
    logout_user(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('home')


@login_required
def dashboard_view(request):
    """Trang dashboard sau khi đăng nhập - User dashboard"""
    user = get_current_user(request)
    
    # Debug: Check if user is valid
    if not user:
        messages.error(request, 'Lỗi: Không thể xác thực người dùng. Vui lòng đăng nhập lại.')
        return redirect('login')
    
    # Debug: Check user role
    if not user.role:
        messages.error(request, 'Lỗi: Tài khoản của bạn chưa được gán vai trò. Vui lòng liên hệ quản trị viên.')
        return redirect('login')
    
    # Debug: Validate role
    valid_roles = [role[0] for role in User.ROLES]
    if user.role not in valid_roles:
        messages.error(request, f'Lỗi: Vai trò "{user.role}" không hợp lệ. Vui lòng liên hệ quản trị viên.')
        return redirect('login')
    
    try:
        # Get user statistics with error handling
        total_users = User.objects.count()
        active_sessions = UserSession.objects.count()
    except Exception as e:
        messages.error(request, f'Lỗi kết nối cơ sở dữ liệu: {str(e)}')
        total_users = 0
        active_sessions = 0
    
    context = {
        'user': user,
        'total_users': total_users,
        'active_sessions': active_sessions,
        'dashboard_type': 'user'
    }
    return render(request, 'accounts/dashboard.html', context)


@admin_required
def admin_dashboard_view(request):
    """Dashboard dành cho Admin"""
    user = get_current_user(request)
    
    try:
        # Get comprehensive statistics
        total_users = User.objects.count()
        active_sessions = UserSession.objects.count()
        
        # Role statistics - simplified for only admin and user
        role_stats = {}
        for role_key, role_name in User.ROLES:
            role_stats[role_name] = User.objects.filter(role=role_key).count()
        
        # Recent users
        recent_users = User.objects.order_by('-date_joined')[:5]
        
    except Exception:
        total_users = active_sessions = 0
        role_stats = {}
        recent_users = []
    
    context = {
        'user': user,
        'total_users': total_users,
        'active_sessions': active_sessions,
        'role_stats': role_stats,
        'recent_users': recent_users,
        'dashboard_type': 'admin'
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@admin_required
def users_management_view(request):
    """Quản lý người dùng - chỉ admin mới truy cập được"""
    user = get_current_user(request)
    
    try:
        # Get all users for management
        users = User.objects.order_by('-date_joined')
    except Exception:
        users = []
    
    context = {
        'user': user,
        'users': users,
        'available_roles': User.ROLES  # Now only admin and user
    }
    return render(request, 'accounts/users_management.html', context)


@admin_required
def edit_user_view(request, username):
    """Chỉnh sửa thông tin người dùng - chỉ admin"""
    current_user = get_current_user(request)
    
    try:
        target_user = User.objects.filter(username=username).first()
    except User.DoesNotExist:
        messages.error(request, 'Không tìm thấy người dùng.')
        return redirect('users_management')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('users_management')
    
    if request.method == 'POST':
        form = UserUpdateForm(instance=target_user, current_user=current_user, data=request.POST)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, f'Cập nhật thông tin người dùng {target_user.username} thành công!')
                return redirect('users_management')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra khi cập nhật: {str(e)}')
    else:
        form = UserUpdateForm(instance=target_user, current_user=current_user)
    
    context = {
        'user': current_user,
        'target_user': target_user,
        'form': form,
        'available_roles': User.ROLES  # Now only admin and user
    }
    return render(request, 'accounts/edit_user.html', context)


@csrf_exempt
@admin_required
def api_change_user_role(request):
    """API để thay đổi vai trò người dùng - chỉ admin"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        username = data.get('username')
        new_role = data.get('role')
        
        if not username or not new_role:
            return JsonResponse({'error': 'Username và role là bắt buộc'}, status=400)
        
        # Validate role
        valid_roles = [role[0] for role in User.ROLES]  # Now only admin and user
        if new_role not in valid_roles:
            return JsonResponse({'error': f'Vai trò không hợp lệ. Chỉ chấp nhận: {", ".join(valid_roles)}'}, status=400)
        
        # Check if admin is trying to change their own role
        current_user = get_current_user(request)
        if current_user.username == username:
            return JsonResponse({'error': 'Bạn không thể thay đổi vai trò của chính mình!'}, status=403)
        
        # Find user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy người dùng'}, status=404)
        
        # Check if user is already in that role
        if user.role == new_role:
            return JsonResponse({'error': f'Người dùng {username} đã có vai trò {user.get_role_display()}'}, status=400)
        
        # Store old role info for logging
        old_role = user.get_role_display()
        old_role_key = user.role
        
        # Update role
        user.role = new_role
        user.save()
        new_role_display = user.get_role_display()
        
        # Log the role change (you could save this to a log model)
        print(f"[ROLE CHANGE] Admin {current_user.username} changed {username} from {old_role} to {new_role_display}")
        
        return JsonResponse({
            'success': True,
            'message': f'Đã thay đổi vai trò của {username} từ {old_role} thành {new_role_display}',
            'user': {
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name(),
                'old_role': old_role_key,
                'old_role_display': old_role,
                'new_role': user.role,
                'new_role_display': new_role_display,
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%d/%m/%Y %H:%M') if user.date_joined else '',
                'changed_by': current_user.username,
                'changed_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Có lỗi xảy ra: {str(e)}'}, status=500)


@csrf_exempt
@admin_required
def api_toggle_user_status(request):
    """API để toggle trạng thái hoạt động của người dùng - chỉ admin"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        from datetime import datetime
        data = json.loads(request.body)
        username = data.get('username')
        
        if not username:
            return JsonResponse({'error': 'Username là bắt buộc'}, status=400)
        
        # Check if admin is trying to change their own status
        current_user = get_current_user(request)
        if current_user.username == username:
            return JsonResponse({'error': 'Bạn không thể thay đổi trạng thái hoạt động của chính mình!'}, status=403)
        
        # Find user
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'error': 'Không tìm thấy người dùng'}, status=404)
        
        # Store old status info for logging
        old_status = "Hoạt động" if user.is_active else "Không hoạt động"
        old_active = user.is_active
        
        # Toggle status
        user.is_active = not user.is_active
        user.save()
        
        new_status = "Hoạt động" if user.is_active else "Không hoạt động"
        action = "kích hoạt" if user.is_active else "vô hiệu hóa"
        
        # Log the status change
        print(f"[STATUS CHANGE] Admin {current_user.username} {action} user {username} - từ {old_status} thành {new_status}")
        
        return JsonResponse({
            'success': True,
            'message': f'Đã {action} tài khoản {username} thành công',
            'user': {
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name(),
                'old_status': old_active,
                'old_status_display': old_status,
                'new_status': user.is_active,
                'new_status_display': new_status,
                'role': user.role,
                'role_display': user.get_role_display(),
                'date_joined': user.date_joined.strftime('%d/%m/%Y %H:%M') if user.date_joined else '',
                'last_login': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else None,
                'changed_by': current_user.username,
                'changed_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
                'action': action
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Có lỗi xảy ra: {str(e)}'}, status=500)


@login_required
def profile_view(request):
    """Trang thông tin cá nhân"""
    user = get_current_user(request)
    
    if request.method == 'POST' :
        form = UserUpdateForm(instance=user, current_user=user, data=request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Thông tin cá nhân đã được cập nhật!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    else:
        form = UserUpdateForm(instance=user, current_user=user)
    
    return render(request, 'accounts/profile.html', {'form': form, 'user': user})

@csrf_exempt
@login_required
def api_profile_update(request):
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)
    
    logger.info(f"PATCH /api/profile/ - User: {request.session.get('username', 'Unknown')}")
    
    try:
        data = json.loads(request.body)
        logger.info(f"PATCH Request Data: {data}")

        user = get_current_user(request)
        if not user:
            logger.error("PATCH Request Failed: User not authenticated")
            return JsonResponse({'error': 'Người dùng không được xác thực'}, status=401)
        updated_fields = []
        if 'first_name' in data:
            new_first_name = data['first_name'].strip()
            if new_first_name != user.first_name:
                if not new_first_name:
                    return JsonResponse({'first_name': ['Tên không được để trống']}, status=400)
                user.first_name = new_first_name
                updated_fields.append('first_name')
        
        if 'last_name' in data:
            new_last_name = data['last_name'].strip()
            if new_last_name != user.last_name:
                if not new_last_name:
                    return JsonResponse({'last_name': ['Họ không được để trống']}, status=400)
                user.last_name = new_last_name
                updated_fields.append('last_name')
        
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                if not new_email:
                    return JsonResponse({'email': ['Email không được để trống']}, status=400)
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                    return JsonResponse({'email': ['Email không hợp lệ']}, status=400)

                try:
                    existing_user = User.objects.get(email=new_email)
                    if existing_user.id != user.id:
                        return JsonResponse({'email': ['Email này đã được sử dụng']}, status=400)
                except User.DoesNotExist:
                    pass  

                user.email = new_email
                updated_fields.append('email')
        if not updated_fields:
            logger.warning("PATCH Request: No fields to update")
            return JsonResponse({'message': 'Không có thông tin nào được thay đổi'}, status=200)
        user.save()
        logger.info(f"PATCH Request Successful: Updated fields {updated_fields} for user {user.username}")

        return JsonResponse({
            'message': 'Cập nhật thông tin thành công!',
            'updated_fields': updated_fields,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'role': user.get_role_display(),
                'is_active': user.is_active,
                'updated_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        }, status=200)
    except json.JSONDecodeError:
        logger.error("PATCH Request Failed: Invalid JSON")
        return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
    except Exception as e:
        logger.error(f"PATCH Request Failed: {str(e)}")
        return JsonResponse({'error': f'Có lỗi xảy ra: {str(e)}'}, status=500)

@csrf_exempt
@login_required
def api_user_list(request):
    """API để lấy danh sách người dùng"""
    user = get_current_user(request)
    
    try:
        # Only admin can see all users, regular users can't access this API
        if not user.is_admin():
            return JsonResponse({'error': 'Chỉ admin mới có thể truy cập danh sách người dùng'}, status=403)
        
        users = User.objects.all()
        
        user_list = []
        for u in users:
            user_list.append({
                'username': u.username,
                'email': u.email,
                'full_name': u.get_full_name(),
                'role': u.get_role_display(),
                'role_key': u.role,
                'date_joined': u.date_joined.strftime('%d/%m/%Y %H:%M') if u.date_joined else '',
                'last_login': u.last_login.strftime('%d/%m/%Y %H:%M') if u.last_login else 'Chưa đăng nhập',
                'is_active': u.is_active,
                'permissions': u.get_permissions_display()
            })
        
        return JsonResponse({
            'users': user_list,
            'total_count': len(user_list)
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Có lỗi xảy ra: {str(e)}'}, status=500)


@csrf_exempt
@login_required
def api_get_profile(request):
    """
    API endpoint để lấy thông tin cá nhân của người dùng đang đăng nhập.
    Chỉ chấp nhận phương thức GET.
    """
    # Chỉ cho phép phương thức GET
    if request.method != 'GET':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)

    # Lấy thông tin người dùng từ request (nhờ decorator @login_required)
    user = get_current_user(request)

    if not user:
        # Lỗi này xảy ra nếu cookie hợp lệ nhưng không tìm thấy user trong DB
        return JsonResponse({'error': 'Không tìm thấy người dùng hoặc phiên hết hạn.'}, status=401)
    
    user_data = {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.get_role_display(),
        'is_active': user.is_active,
        'date_joined': user.date_joined.strftime('%d/%m/%Y %H:%M:%S') if user.date_joined else None,
        'last_login': user.last_login.strftime('%d/%m/%Y %H:%M:%S') if user.last_login else None
    }

    # Trả về dữ liệu người dùng dưới dạng JSON
    return JsonResponse(user_data, status=200)


@login_required
def change_password_view(request):
    """Trang đổi mật khẩu"""
    user = get_current_user(request)
    
    if not user:
        messages.error(request, 'Vui lòng đăng nhập để đổi mật khẩu.')
        return redirect('login')
    
    if request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            try:
                success = form.save()
                if success:
                    # Log the user out to force re-login with new password
                    logout_user(request)
                    messages.success(request, 
                        'Đổi mật khẩu thành công! Vui lòng đăng nhập lại với mật khẩu mới.')
                    return redirect('login')
                else:
                    messages.error(request, 'Có lỗi xảy ra khi lưu mật khẩu mới.')
            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    else:
        form = PasswordChangeForm(user=user)
    
    context = {
        'user': user,
        'form': form,
        'page_title': 'Đổi mật khẩu'
    }
    
    return render(request, 'accounts/change_password.html', context)

@csrf_exempt
@login_required
def api_change_password(request):
    """API endpoint để đổi mật khẩu"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        user = get_current_user(request)
        if not user:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        data = json.loads(request.body)
        
        # Create form with data
        form = PasswordChangeForm(user=user, data=data)
        
        if form.is_valid():
            success = form.save()
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Đổi mật khẩu thành công! Vui lòng đăng nhập lại.',
                    'redirect_to_login': True
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Có lỗi xảy ra khi lưu mật khẩu mới'
                }, status=500)
        else:
            # Return form errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in api_change_password: {str(e)}")
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)