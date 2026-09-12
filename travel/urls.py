from django.urls import path
from .views import (
    TravelHistoryListView,
    TravelHistoryDeleteView,
    TravelReminderListView,
    TravelReminderDetailView,
)

urlpatterns = [
    path('travel/history/', TravelHistoryListView.as_view(), name='travel-history-list'),
    path('travel/history/<uuid:pk>/', TravelHistoryDeleteView.as_view(), name='travel-history-delete'),
    path('travel/reminders/', TravelReminderListView.as_view(), name='travel-reminder-list'),
    path('travel/reminders/<uuid:pk>/', TravelReminderDetailView.as_view(), name='travel-reminder-detail'),
]
