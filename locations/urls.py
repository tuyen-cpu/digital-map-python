from django.urls import path
from .views import LocationListView, LocationDetailView, LocationImportView, LocationResetView

urlpatterns = [
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/import/', LocationImportView.as_view(), name='location-import'),
    path('locations/reset/', LocationResetView.as_view(), name='location-reset'),
    path('locations/<str:pk>/', LocationDetailView.as_view(), name='location-detail'),
]
