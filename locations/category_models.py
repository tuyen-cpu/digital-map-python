from django.db import models


class Category(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    label = models.CharField(max_length=100)
    short_label = models.CharField(max_length=50)
    emoji = models.CharField(max_length=10, default='📍')
    description = models.TextField(blank=True, default='')
    marker = models.CharField(max_length=20, default='#1d4ed8')
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # Suggested groups/subgroups/keywords for this category (admin can edit)
    suggested_groups = models.JSONField(default=list)      # ['Group A', 'Group B']
    suggested_subgroups = models.JSONField(default=list)   # ['Sub A', 'Sub B']
    suggested_keywords = models.JSONField(default=list)    # ['keyword1', 'keyword2']

    class Meta:
        db_table = 'locations_category'
        ordering = ['order', 'key']

    def __str__(self):
        return f'{self.emoji} {self.label} ({self.key})'
