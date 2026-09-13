from django.urls import path
from .views import MediaUploadView, MediaDeleteView

urlpatterns = [
    path('upload/', MediaUploadView.as_view(), name='media-upload'),
    path('delete/', MediaDeleteView.as_view(), name='media-delete'),
]
