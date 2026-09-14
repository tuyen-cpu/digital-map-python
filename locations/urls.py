from django.urls import path
from .views import LocationListView, LocationDetailView, LocationImportView, LocationResetView
from .category_views import CategoryListView, CategoryDetailView, CategorySeedView

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/seed/', CategorySeedView.as_view(), name='category-seed'),
    path('categories/<str:key>/', CategoryDetailView.as_view(), name='category-detail'),

    # Locations
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/import/', LocationImportView.as_view(), name='location-import'),
    path('locations/reset/', LocationResetView.as_view(), name='location-reset'),
    path('locations/<str:pk>/', LocationDetailView.as_view(), name='location-detail'),
]
