from django.db import models

CATEGORY_CHOICES = [
    ('tourism', 'Du lịch'),
    ('food', 'Ẩm thực'),
    ('accommodation', 'Lưu trú'),
    ('administration', 'Hành chính'),
    ('utility', 'Tiện ích'),
    ('heritage', 'Di sản'),
    ('education', 'Giáo dục'),
    ('health', 'Y tế'),
    ('religion', 'Tôn giáo'),
    ('shopping', 'Mua sắm'),
    ('sport', 'Thể thao'),
    ('other', 'Khác'),
]


class Location(models.Model):
    # Slug-based primary key (e.g. "dinh-tan-an-123abc")
    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='utility')
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
    # JSONField: [{url, alt, name}]
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
