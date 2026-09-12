from django.conf import settings
from rest_framework.permissions import BasePermission


def _is_env_admin(request):
    """Check if request carries the hardcoded admin token (set during login)."""
    return getattr(request, '_is_admin', False)


class IsAdmin(BasePermission):
    """Only the hardcoded admin (from env) can access."""
    message = 'Chỉ quản trị viên hệ thống được thực hiện thao tác này.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    getattr(request.user, 'role', None) == 'admin')


class IsAdminOrManager(BasePermission):
    """Admin or any manager can access."""
    message = 'Bạn cần có quyền quản lý để thực hiện thao tác này.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('admin', 'manager')


class IsManagerOf(BasePermission):
    """
    Object-level: manager can only touch locations in their permitted
    categories / groups / subgroups.  Admin always passes.
    """
    message = 'Bạn không có quyền quản lý địa điểm trong nhóm này.'

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == 'admin':
            return True
        if user.role != 'manager':
            return False
        try:
            perms = user.manager_permission
        except Exception:
            return False
        # obj is a Location instance
        if obj.category and obj.category in (perms.categories or []):
            return True
        if obj.group and obj.group in (perms.groups or []):
            return True
        if obj.subgroup and obj.subgroup in (perms.subgroups or []):
            return True
        return False


def can_manage_location(user, location):
    """Helper used in views — returns True if user may write this location."""
    if not user or not user.is_authenticated:
        return False
    if user.role == 'admin':
        return True
    if user.role != 'manager':
        return False
    try:
        perms = user.manager_permission
    except Exception:
        return False
    if location.category in (perms.categories or []):
        return True
    if location.group and location.group in (perms.groups or []):
        return True
    if location.subgroup and location.subgroup in (perms.subgroups or []):
        return True
    return False


def can_manage_category(user, category):
    """Helper — returns True if user may create locations in this category."""
    if not user or not user.is_authenticated:
        return False
    if user.role == 'admin':
        return True
    if user.role != 'manager':
        return False
    try:
        perms = user.manager_permission
    except Exception:
        return False
    return category in (perms.categories or [])
