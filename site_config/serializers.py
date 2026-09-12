from rest_framework import serializers
from .models import SiteSettings


class HeroSlideSerializer(serializers.Serializer):
    id = serializers.CharField()
    image = serializers.CharField(allow_blank=True)
    title = serializers.CharField(allow_blank=True)
    caption = serializers.CharField(allow_blank=True)


class SiteSettingsSerializer(serializers.ModelSerializer):
    heroSlides = serializers.JSONField(source='hero_slides')
    heroIntervalMs = serializers.IntegerField(source='hero_interval_ms')

    class Meta:
        model = SiteSettings
        fields = ['heroSlides', 'heroIntervalMs']


class SiteSettingsUpdateSerializer(serializers.Serializer):
    heroSlides = serializers.ListField(child=serializers.DictField(), required=False)
    heroIntervalMs = serializers.IntegerField(required=False, min_value=1000)
