from django.urls import include, path

urlpatterns = [
    path('api/', include('accounts.urls')),
    path('api/', include('locations.urls')),
    path('api/', include('reviews.urls')),
    path('api/', include('favorites.urls')),
    path('api/', include('travel.urls')),
    path('api/', include('analytics.urls')),
    path('api/', include('site_config.urls')),
    path('api/media/', include('media_upload.urls')),
]
