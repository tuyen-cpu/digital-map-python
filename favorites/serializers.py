from rest_framework import serializers
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    locationId = serializers.CharField(source='location_id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'locationId', 'createdAt']


class FavoriteToggleSerializer(serializers.Serializer):
    locationId = serializers.CharField()
