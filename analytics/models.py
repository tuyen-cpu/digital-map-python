import uuid

from django.db import models


class AnalyticsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50)          # page_view, location_view, route_start, ...
    visitor_id = models.CharField(max_length=100)
    session_id = models.CharField(max_length=100)
    account = models.CharField(max_length=40, blank=True, default='')   # username or ''
    role = models.CharField(max_length=10, default='guest')             # guest/user/manager/admin
    location_id = models.CharField(max_length=200, blank=True, null=True)
    location_name = models.CharField(max_length=300, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    path = models.CharField(max_length=500, blank=True, null=True)
    section = models.CharField(max_length=200, blank=True, null=True)
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_event'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['account']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.type} by {self.account or "guest"} @ {self.created_at}'
