import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import ManagerPermission

User = get_user_model()

PHONE_RE = re.compile(r'^(\+84|0)(3|5|7|8|9)\d{8}$')


def _validate_phone(value):
    clean = value.replace(' ', '').replace('-', '').replace('.', '')
    if not PHONE_RE.match(clean):
        raise serializers.ValidationError('Số điện thoại không đúng định dạng di động Việt Nam.')
    return clean


# ---------------------------------------------------------------------------
# ManagerPermission
# ---------------------------------------------------------------------------
class ManagerPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPermission
        fields = ['categories', 'groups', 'subgroups']


# ---------------------------------------------------------------------------
# Session / Me response
# ---------------------------------------------------------------------------
class SessionSerializer(serializers.ModelSerializer):
    displayName = serializers.CharField(source='display_name')
    mustChangePassword = serializers.BooleanField(source='must_change_password')
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'displayName', 'phone', 'role', 'avatar',
                  'mustChangePassword', 'permissions']

    def get_permissions(self, obj):
        if obj.role == 'admin':
            return {'categories': [], 'groups': [], 'subgroups': []}
        try:
            p = obj.manager_permission
            return {'categories': p.categories, 'groups': p.groups, 'subgroups': p.subgroups}
        except ManagerPermission.DoesNotExist:
            return {'categories': [], 'groups': [], 'subgroups': []}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------
class RegisterSerializer(serializers.Serializer):
    displayName = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=40)
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_username(self, value):
        value = value.strip()
        if not re.match(r'^[a-zA-Z0-9._-]{3,40}$', value):
            raise serializers.ValidationError(
                'Tên đăng nhập chỉ dùng chữ, số, dấu chấm, gạch dưới hoặc gạch ngang; dài 3–40 ký tự.'
            )
        admin_username = getattr(settings, 'ADMIN_USERNAME', 'admin')
        if value.lower() == admin_username.lower():
            raise serializers.ValidationError('Tên đăng nhập này được dành cho quản trị viên.')
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Tên đăng nhập đã tồn tại.')
        return value

    def validate_phone(self, value):
        clean = _validate_phone(value)
        if User.objects.filter(phone=clean).exists():
            raise serializers.ValidationError('Số điện thoại này đã được dùng cho một tài khoản khác.')
        return clean

    def validate_displayName(self, value):
        if not value.strip():
            raise serializers.ValidationError('Hãy nhập tên hiển thị.')
        return value.strip()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            display_name=validated_data['displayName'],
            phone=validated_data['phone'],
            role='user',
        )
        return user


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# ---------------------------------------------------------------------------
# Profile update
# ---------------------------------------------------------------------------
class ProfileUpdateSerializer(serializers.Serializer):
    displayName = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)
    avatar = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    def validate_displayName(self, value):
        if not value.strip():
            raise serializers.ValidationError('Tên hiển thị không được để trống.')
        return value.strip()

    def validate_phone(self, value):
        clean = _validate_phone(value)
        request = self.context.get('request')
        qs = User.objects.filter(phone=clean)
        if request and request.user:
            qs = qs.exclude(pk=request.user.pk)
        if qs.exists():
            raise serializers.ValidationError('Số điện thoại này đã được dùng cho tài khoản khác.')
        return clean


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------
class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(min_length=8, write_only=True)


# ---------------------------------------------------------------------------
# Admin: full user view
# ---------------------------------------------------------------------------
class AdminUserSerializer(serializers.ModelSerializer):
    displayName = serializers.CharField(source='display_name')
    mustChangePassword = serializers.BooleanField(source='must_change_password')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'displayName', 'phone', 'role', 'avatar',
                  'mustChangePassword', 'createdAt', 'permissions']

    def get_permissions(self, obj):
        try:
            p = obj.manager_permission
            return {'categories': p.categories, 'groups': p.groups, 'subgroups': p.subgroups}
        except ManagerPermission.DoesNotExist:
            return {'categories': [], 'groups': [], 'subgroups': []}


# ---------------------------------------------------------------------------
# Admin: update user + permissions
# ---------------------------------------------------------------------------
class AdminUserUpdateSerializer(serializers.Serializer):
    displayName = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=40)
    phone = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=['manager', 'user'])
    permissions = serializers.DictField(child=serializers.ListField(child=serializers.CharField()), required=False)

    def validate_username(self, value):
        value = value.strip()
        if not re.match(r'^[a-zA-Z0-9._-]{3,40}$', value):
            raise serializers.ValidationError(
                'Tên đăng nhập chỉ dùng chữ, số, dấu chấm, gạch dưới hoặc gạch ngang; dài 3–40 ký tự.'
            )
        admin_username = getattr(settings, 'ADMIN_USERNAME', 'admin')
        if value.lower() == admin_username.lower():
            raise serializers.ValidationError('Tên đăng nhập này được dành cho quản trị viên.')
        return value

    def validate_phone(self, value):
        return _validate_phone(value)
