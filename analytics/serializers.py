from rest_framework import serializers
from .models import AnalyticsEvent


class AnalyticsEventSerializer(serializers.ModelSerializer):
    visitorId = serializers.CharField(source='visitor_id')
    sessionId = serializers.CharField(source='session_id')
    locationId = serializers.CharField(source='location_id', allow_null=True, allow_blank=True, required=False)
    locationName = serializers.CharField(source='location_name', allow_null=True, allow_blank=True, required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'type', 'visitorId', 'sessionId',
            'account', 'role',
            'locationId', 'locationName',
            'category', 'path', 'section', 'rating',
            'createdAt',
        ]
        read_only_fields = ['id', 'createdAt']


class AnalyticsEventCreateSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=50)
    visitorId = serializers.CharField(max_length=100)
    sessionId = serializers.CharField(max_length=100)
    account = serializers.CharField(max_length=40, allow_blank=True, default='')
    role = serializers.CharField(max_length=10, default='guest')
    locationId = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, required=False)
    locationName = serializers.CharField(max_length=300, allow_blank=True, allow_null=True, required=False)
    category = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)
    path = serializers.CharField(max_length=500, allow_blank=True, allow_null=True, required=False)
    section = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, required=False)
    rating = serializers.IntegerField(allow_null=True, required=False)
