from rest_framework import serializers
from .models import Location
from .category_models import Category


def _valid_category_keys():
    """Fetch active category keys from DB — cached per request cycle."""
    return set(Category.objects.filter(is_active=True).values_list('key', flat=True))


class NullableFloatField(serializers.FloatField):
    """FloatField that treats empty string as null instead of raising a validation error."""

    def to_internal_value(self, data):
        if data == '' or data is None:
            return None
        return super().to_internal_value(data)


class LocationSerializer(serializers.ModelSerializer):
    # camelCase aliases for FE compatibility
    imageAlt = serializers.CharField(source='image_alt', allow_null=True, allow_blank=True, required=False)
    imageSourceUrl = serializers.CharField(source='image_source_url', allow_null=True, allow_blank=True, required=False)
    imageSourceName = serializers.CharField(source='image_source_name', allow_null=True, allow_blank=True, required=False)
    heritageStatus = serializers.CharField(source='heritage_status', allow_null=True, allow_blank=True, required=False)
    zaloUrl = serializers.CharField(source='zalo_url', allow_null=True, allow_blank=True, required=False)
    isActive = serializers.BooleanField(source='is_active', required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    lat = NullableFloatField(allow_null=True, required=False)
    lng = NullableFloatField(allow_null=True, required=False)

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'category', 'group', 'subgroup',
            'address', 'lat', 'lng',
            'phone', 'zaloUrl', 'website', 'email', 'facebook', 'hours',
            'keywords', 'heritageStatus',
            'description', 'notes',
            'image', 'imageAlt', 'imageSourceUrl', 'imageSourceName',
            'gallery', 'panoramas', 'videos',
            'isActive', 'createdAt', 'updatedAt',
        ]

    def validate_gallery(self, value):
        return self._validate_media_list(value, 'gallery')

    def validate_panoramas(self, value):
        return self._validate_media_list(value, 'panoramas')

    def validate_videos(self, value):
        return self._validate_media_list(value, 'videos')

    def validate_category(self, value):
        valid = _valid_category_keys()
        # Fallback: if DB empty (first run), allow any non-empty string
        if valid and value not in valid:
            raise serializers.ValidationError(
                f'"{value}" không phải danh mục hợp lệ. Các danh mục hiện có: {", ".join(sorted(valid))}'
            )
        return value

    def _validate_media_list(self, value, field_name):
        if not isinstance(value, list):
            raise serializers.ValidationError(f'{field_name} phải là danh sách.')
        result = []
        for item in value:
            if isinstance(item, str):
                result.append({'url': item, 'alt': '', 'name': ''})
            elif isinstance(item, dict):
                if not item.get('url'):
                    continue
                result.append({
                    'url': str(item.get('url', '')).strip(),
                    'alt': str(item.get('alt', '')).strip(),
                    'name': str(item.get('name', '')).strip(),
                })
        return result


class LocationListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view — omit heavy text fields."""
    imageAlt = serializers.CharField(source='image_alt', allow_null=True, allow_blank=True, required=False)
    heritageStatus = serializers.CharField(source='heritage_status', allow_null=True, allow_blank=True, required=False)
    zaloUrl = serializers.CharField(source='zalo_url', allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'category', 'group', 'subgroup',
            'address', 'lat', 'lng',
            'phone', 'zaloUrl', 'website', 'email', 'facebook', 'hours',
            'keywords', 'heritageStatus',
            'description', 'notes',
            'image', 'imageAlt',
            'gallery', 'panoramas', 'videos',
        ]
