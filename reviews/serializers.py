from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Review, ReviewReply

User = get_user_model()


class ReviewReplySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    displayName = serializers.CharField(source='user.display_name', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = ReviewReply
        fields = ['id', 'username', 'displayName', 'role', 'avatar', 'comment', 'createdAt']
        read_only_fields = ['id', 'username', 'displayName', 'role', 'avatar', 'createdAt']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    displayName = serializers.CharField(source='user.display_name', read_only=True)
    locationId = serializers.CharField(source='location_id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    replies = ReviewReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'locationId', 'username', 'displayName',
            'rating', 'comment', 'replies', 'createdAt', 'updatedAt',
        ]
        read_only_fields = ['id', 'locationId', 'username', 'displayName',
                            'replies', 'createdAt', 'updatedAt']

    def validate_rating(self, value):
        if not isinstance(value, int) or value < 1 or value > 5:
            raise serializers.ValidationError('Hãy chọn số sao từ 1 đến 5.')
        return value


class ReviewCreateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(max_length=800, allow_blank=True, default='')


class ReviewReplyCreateSerializer(serializers.Serializer):
    comment = serializers.CharField(max_length=600)

    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError('Nội dung phản hồi không được để trống.')
        return value.strip()[:600]
