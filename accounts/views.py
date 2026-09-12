from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ManagerPermission
from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    SessionSerializer,
)

User = get_user_model()


def _make_tokens(user):
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['username'] = user.username
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def _session_data(user):
    return SessionSerializer(user).data


# ---------------------------------------------------------------------------
# POST /api/auth/register/
# ---------------------------------------------------------------------------
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        tokens = _make_tokens(user)
        return Response({
            **tokens,
            'user': _session_data(user),
        }, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# POST /api/auth/login/
# ---------------------------------------------------------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username'].strip()
        password = serializer.validated_data['password']

        # Check hardcoded admin account
        admin_username = getattr(settings, 'ADMIN_USERNAME', 'admin')
        admin_password = getattr(settings, 'ADMIN_PASSWORD', '')
        if username.lower() == admin_username.lower() and password == admin_password:
            # Return a synthetic admin session (no DB user)
            admin_display = getattr(settings, 'ADMIN_DISPLAY_NAME', 'Quản trị viên')
            # Create or get a DB user for admin (needed for JWT)
            admin_user, created = User.objects.get_or_create(
                username=admin_username,
                defaults={
                    'display_name': admin_display,
                    'phone': '0900000000',
                    'role': 'admin',
                    'must_change_password': False,
                }
            )
            if created:
                admin_user.set_unusable_password()
                admin_user.save()
            tokens = _make_tokens(admin_user)
            return Response({
                **tokens,
                'user': _session_data(admin_user),
            })

        # Regular user login
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Tên đăng nhập hoặc mật khẩu không đúng.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'Tên đăng nhập hoặc mật khẩu không đúng.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = _make_tokens(user)
        return Response({
            **tokens,
            'user': _session_data(user),
        })


# ---------------------------------------------------------------------------
# POST /api/auth/logout/
# ---------------------------------------------------------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass
        return Response({'success': True})


# ---------------------------------------------------------------------------
# GET /api/auth/me/
# ---------------------------------------------------------------------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_session_data(request.user))


# ---------------------------------------------------------------------------
# PUT /api/auth/profile/
# ---------------------------------------------------------------------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if request.user.role == 'admin':
            return Response(
                {'detail': 'Không thể cập nhật profile cho tài khoản admin.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProfileUpdateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        request.user.display_name = d['displayName']
        request.user.phone = d['phone']
        if 'avatar' in d:
            request.user.avatar = d['avatar']
        request.user.save()
        return Response(_session_data(request.user))


# ---------------------------------------------------------------------------
# POST /api/auth/change-password/
# ---------------------------------------------------------------------------
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role == 'admin':
            return Response(
                {'detail': 'Không thể đổi mật khẩu cho tài khoản admin.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        if not request.user.check_password(d['currentPassword']):
            return Response(
                {'detail': 'Mật khẩu hiện tại không đúng.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(d['newPassword']) < 8:
            return Response(
                {'detail': 'Mật khẩu mới phải có ít nhất 8 ký tự.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_password(d['newPassword'])
        request.user.must_change_password = False
        request.user.password_changed_at = timezone.now()
        request.user.save()
        return Response({'success': True})


# ---------------------------------------------------------------------------
# Admin: GET/PUT/DELETE /api/admin/users/{username}/
# ---------------------------------------------------------------------------
class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        admin_username = getattr(settings, 'ADMIN_USERNAME', 'admin')
        users = User.objects.exclude(username=admin_username).order_by('-created_at')
        return Response({
            'count': users.count(),
            'results': AdminUserSerializer(users, many=True).data,
        })


class AdminUserDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def put(self, request, username):
        user = self._get_user(username)
        if not user:
            return Response({'detail': 'Không tìm thấy tài khoản.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        new_username = d['username'].strip()
        admin_username = getattr(settings, 'ADMIN_USERNAME', 'admin')

        # Check username uniqueness (exclude self)
        if new_username.lower() == admin_username.lower():
            return Response({'detail': 'Tên đăng nhập này dành cho quản trị viên.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username__iexact=new_username).exclude(pk=user.pk).exists():
            return Response({'detail': 'Tên đăng nhập đã tồn tại.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(phone=d['phone']).exclude(pk=user.pk).exists():
            return Response({'detail': 'Số điện thoại đã thuộc về tài khoản khác.'}, status=status.HTTP_400_BAD_REQUEST)

        user.username = new_username
        user.display_name = d['displayName'].strip()
        user.phone = d['phone']
        user.role = d['role']
        user.save()

        # Update permissions
        perms_data = d.get('permissions', {})
        perm, _ = ManagerPermission.objects.get_or_create(user=user)
        perm.categories = perms_data.get('categories', [])
        perm.groups = perms_data.get('groups', [])
        perm.subgroups = perms_data.get('subgroups', [])
        perm.save()

        return Response(AdminUserSerializer(user).data)

    def delete(self, request, username):
        user = self._get_user(username)
        if not user:
            return Response({'detail': 'Không tìm thấy tài khoản.'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'success': True})


class AdminUserResetPasswordView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Không tìm thấy tài khoản.'}, status=status.HTTP_404_NOT_FOUND)

        default_password = getattr(settings, 'DEFAULT_RESET_PASSWORD', 'PhuongBinhDinh@123')
        user.set_password(default_password)
        user.must_change_password = True
        user.password_reset_at = timezone.now()
        user.save()
        return Response({'success': True, 'newPassword': default_password})
