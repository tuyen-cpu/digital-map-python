import uuid

from django.conf import settings
from django.db import models


class TravelHistory(models.Model):
    ACTION_VIEW = 'view'
    ACTION_ROUTE = 'route'
    ACTION_VISITED = 'visited'
    ACTION_CHOICES = [
        (ACTION_VIEW, 'Xem'),
        (ACTION_ROUTE, 'Dẫn đường'),
        (ACTION_VISITED, 'Đã đến'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='travel_history',
    )
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='travel_history',
    )
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    last_action = models.CharField(max_length=10, choices=ACTION_CHOICES, default=ACTION_VIEW)
    view_count = models.IntegerField(default=0)
    route_count = models.IntegerField(default=0)
    visited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'travel_history'
        unique_together = [('user', 'location')]
        ordering = ['-last_activity_at']

    def __str__(self):
        return f'{self.user.username} → {self.location_id} ({self.last_action})'


class TravelReminder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='travel_reminders',
    )
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='reminders',
    )
    scheduled_at = models.DateTimeField()
    note = models.TextField(max_length=300, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'travel_reminder'
        ordering = ['scheduled_at']

    def __str__(self):
        return f'{self.user.username} → {self.location_id} @ {self.scheduled_at}'
