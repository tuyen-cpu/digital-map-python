from django.db import models
from .category_models import Category  # noqa: F401 — re-export for convenience


class Location(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=300)
    # Free-form CharField — validated against Category.key at serializer level
    category = models.CharField(max_length=50, default='utility')
    group = models.CharField(max_length=200, blank=True, default='')
    subgroup = models.CharField(max_length=200, blank=True, default='')
    address = models.TextField(blank=True, default='')
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    zalo_url = models.CharField(max_length=500, null=True, blank=True)
    website = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    facebook = models.CharField(max_length=500, null=True, blank=True)
    hours = models.CharField(max_length=300, null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    heritage_status = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    image = models.TextField(null=True, blank=True)
    image_alt = models.CharField(max_length=300, null=True, blank=True)
    image_source_url = models.CharField(max_length=500, null=True, blank=True)
    image_source_name = models.CharField(max_length=300, null=True, blank=True)
    gallery = models.JSONField(default=list)
    panoramas = models.JSONField(default=list)
    videos = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'locations_location'
        ordering = ['name']

    def __str__(self):
        return self.name
