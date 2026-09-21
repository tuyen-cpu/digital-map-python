from rest_framework import serializers
from .models import TravelHistory, TravelReminder


class TravelHistorySerializer(serializers.ModelSerializer):
    locationId = serializers.CharField(source='location_id', read_only=True)
    firstSeenAt = serializers.DateTimeField(source='first_seen_at', read_only=True)
    lastActivityAt = serializers.DateTimeField(source='last_activity_at', read_only=True)
    lastAction = serializers.CharField(source='last_action', read_only=True)
    viewCount = serializers.IntegerField(source='view_count', read_only=True)
    routeCount = serializers.IntegerField(source='route_count', read_only=True)
    visitedAt = serializers.DateTimeField(source='visited_at', read_only=True, allow_null=True)

    class Meta:
        model = TravelHistory
        fields = [
            'id', 'locationId', 'firstSeenAt', 'lastActivityAt',
            'lastAction', 'viewCount', 'routeCount', 'visitedAt',
        ]


class TravelHistoryRecordSerializer(serializers.Serializer):
    locationId = serializers.CharField()
    action = serializers.ChoiceField(choices=['view', 'route', 'visited', 'unvisit'])


class TravelReminderSerializer(serializers.ModelSerializer):
    locationId = serializers.CharField(source='location_id', read_only=True)
    scheduledAt = serializers.DateTimeField(source='scheduled_at')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    completedAt = serializers.DateTimeField(source='completed_at', read_only=True, allow_null=True)
    notifiedAt = serializers.DateTimeField(source='notified_at', read_only=True, allow_null=True)

    class Meta:
        model = TravelReminder
        fields = ['id', 'locationId', 'scheduledAt', 'note', 'createdAt', 'completedAt', 'notifiedAt']
        read_only_fields = ['id', 'createdAt', 'completedAt', 'notifiedAt']


class TravelReminderCreateSerializer(serializers.Serializer):
    locationId = serializers.CharField()
    scheduledAt = serializers.DateTimeField()
    note = serializers.CharField(max_length=300, allow_blank=True, default='')

    def validate_note(self, value):
        return value.strip()[:300]


class TravelReminderPatchSerializer(serializers.Serializer):
    completedAt = serializers.DateTimeField(allow_null=True, required=False)
    notifiedAt = serializers.DateTimeField(allow_null=True, required=False)
