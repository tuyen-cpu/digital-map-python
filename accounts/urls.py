from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    ProfileView, ChangePasswordView,
    AdminUserListView, AdminUserDetailView, AdminUserResetPasswordView,
)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/profile/', ProfileView.as_view(), name='auth-profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),

    # Admin user management
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<str:username>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<str:username>/reset-password/', AdminUserResetPasswordView.as_view(), name='admin-user-reset-password'),
]
