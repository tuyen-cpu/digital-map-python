import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


def validate_vietnam_phone(value):
    pattern = r'^(\+84|0)(3|5|7|8|9)\d{8}$'
    if value and not re.match(pattern, value.replace(' ', '').replace('-', '').replace('.', '')):
        raise ValidationError('Số điện thoại không đúng định dạng di động Việt Nam.')


def validate_username(value):
    pattern = r'^[a-zA-Z0-9._-]{3,40}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Tên đăng nhập chỉ dùng chữ, số, dấu chấm, gạch dưới hoặc gạch ngang; dài 3–40 ký tự.'
        )


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_USER = 'user'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_USER, 'User'),
    ]

    # Override username to add custom validator
    username = models.CharField(
        max_length=40,
        unique=True,
        validators=[validate_username],
        error_messages={'unique': 'Tên đăng nhập đã tồn tại.'},
    )
    display_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_vietnam_phone],
        error_messages={'unique': 'Số điện thoại này đã được dùng cho một tài khoản khác.'},
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    avatar = models.TextField(blank=True, null=True)
    must_change_password = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    password_reset_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Remove unused AbstractUser fields
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    REQUIRED_FIELDS = ['phone']

    class Meta:
        db_table = 'accounts_user'
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    @property
    def effective_display_name(self):
        return self.display_name or self.username


class ManagerPermission(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='manager_permission',
    )
    categories = models.JSONField(default=list)
    groups = models.JSONField(default=list)
    subgroups = models.JSONField(default=list)

    class Meta:
        db_table = 'accounts_manager_permission'

    def __str__(self):
        return f'Permissions for {self.user.username}'
