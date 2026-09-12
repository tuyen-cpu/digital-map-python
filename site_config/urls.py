from django.urls import path
from .views import SiteSettingsView, SiteSettingsResetView

urlpatterns = [
    path('site-config/', SiteSettingsView.as_view(), name='site-config'),
    path('site-config/reset/', SiteSettingsResetView.as_view(), name='site-config-reset'),
]
