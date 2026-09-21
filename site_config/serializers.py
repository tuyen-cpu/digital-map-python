from rest_framework import serializers
from .models import SiteSettings, DEFAULT_FOOTER_CONFIG


class HeroSlideSerializer(serializers.Serializer):
    id = serializers.CharField()
    image = serializers.CharField(allow_blank=True)
    title = serializers.CharField(allow_blank=True)
    caption = serializers.CharField(allow_blank=True)


class FooterConfigSerializer(serializers.Serializer):
    """Validates and deserializes footer config fields."""
    orgName      = serializers.CharField(max_length=500, required=False, allow_blank=True)
    description  = serializers.CharField(max_length=500, required=False, allow_blank=True)
    address      = serializers.CharField(max_length=500, required=False, allow_blank=True)
    phone        = serializers.CharField(max_length=500, required=False, allow_blank=True)
    email        = serializers.CharField(max_length=500, required=False, allow_blank=True)
    workingHours = serializers.CharField(max_length=500, required=False, allow_blank=True)
    copyright    = serializers.CharField(max_length=500, required=False, allow_blank=True)
    logoUrl      = serializers.CharField(max_length=500, required=False, allow_blank=True)


class SiteSettingsSerializer(serializers.ModelSerializer):
    heroSlides = serializers.JSONField(source='hero_slides')
    heroIntervalMs = serializers.IntegerField(source='hero_interval_ms')
    footer = serializers.SerializerMethodField()

    def get_footer(self, obj):
        """Merge stored footer with DEFAULT_FOOTER_CONFIG to fill any missing keys."""
        return {**DEFAULT_FOOTER_CONFIG, **(obj.footer or {})}

    class Meta:
        model = SiteSettings
        fields = ['heroSlides', 'heroIntervalMs', 'footer']


class SiteSettingsUpdateSerializer(serializers.Serializer):
    heroSlides     = serializers.ListField(child=serializers.DictField(), required=False)
    heroIntervalMs = serializers.IntegerField(required=False, min_value=1000)
    footer         = FooterConfigSerializer(required=False)
