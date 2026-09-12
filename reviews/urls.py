from django.urls import path
from .views import (
    LocationReviewListView,
    ReviewDeleteView,
    ReviewReplyCreateView,
    ReviewReplyDeleteView,
)

urlpatterns = [
    # Nested under locations
    path('locations/<str:location_id>/reviews/', LocationReviewListView.as_view(), name='location-reviews'),

    # Standalone review actions
    path('reviews/<uuid:review_id>/', ReviewDeleteView.as_view(), name='review-delete'),
    path('reviews/<uuid:review_id>/replies/', ReviewReplyCreateView.as_view(), name='review-reply-create'),
    path('reviews/<uuid:review_id>/replies/<uuid:reply_id>/', ReviewReplyDeleteView.as_view(), name='review-reply-delete'),
]
