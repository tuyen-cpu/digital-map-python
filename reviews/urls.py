from django.urls import path
from .views import (
    AllReviewsView,
    LocationReviewListView,
    ReviewDeleteView,
    ReviewReplyCreateView,
    ReviewReplyDeleteView,
)

urlpatterns = [
    # Admin/manager — all reviews
    path('reviews/', AllReviewsView.as_view(), name='all-reviews'),

    # Nested under locations
    path('locations/<str:location_id>/reviews/', LocationReviewListView.as_view(), name='location-reviews'),

    # Standalone review actions
    path('reviews/<uuid:review_id>/', ReviewDeleteView.as_view(), name='review-delete'),
    path('reviews/<uuid:review_id>/replies/', ReviewReplyCreateView.as_view(), name='review-reply-create'),
    path('reviews/<uuid:review_id>/replies/<uuid:reply_id>/', ReviewReplyDeleteView.as_view(), name='review-reply-delete'),
]
