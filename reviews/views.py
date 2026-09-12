from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import can_manage_location
from locations.models import Location
from .models import Review, ReviewReply
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewReplyCreateSerializer


def _can_moderate(user, location):
    """Admin or manager within scope can moderate reviews."""
    return can_manage_location(user, location)


# ---------------------------------------------------------------------------
# GET/POST /api/locations/{location_id}/reviews/
# ---------------------------------------------------------------------------
class LocationReviewListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, location_id):
        try:
            location = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(location=location).prefetch_related('replies__user').select_related('user')
        return Response({'count': reviews.count(), 'results': ReviewSerializer(reviews, many=True).data})

    def post(self, request, location_id):
        user = request.user
        if not user.is_authenticated or user.role not in ('user', 'manager'):
            return Response({'detail': 'Bạn phải đăng nhập tài khoản người dùng để đánh giá.'}, status=status.HTTP_403_FORBIDDEN)

        # Require valid VN phone
        import re
        phone_re = re.compile(r'^(\+84|0)(3|5|7|8|9)\d{8}$')
        clean_phone = (user.phone or '').replace(' ', '').replace('-', '').replace('.', '')
        if not phone_re.match(clean_phone):
            return Response({'detail': 'Tài khoản cần có số điện thoại hợp lệ trước khi đánh giá.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        review, created = Review.objects.update_or_create(
            location=location,
            user=user,
            defaults={'rating': d['rating'], 'comment': d['comment']},
        )
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# DELETE /api/reviews/{id}/
# ---------------------------------------------------------------------------
class ReviewDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id):
        try:
            review = Review.objects.select_related('location', 'user').get(pk=review_id)
        except Review.DoesNotExist:
            return Response({'detail': 'Không tìm thấy đánh giá.'}, status=status.HTTP_404_NOT_FOUND)

        if not _can_moderate(request.user, review.location):
            return Response({'detail': 'Bạn không có quyền xóa đánh giá của địa điểm này.'}, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response({'success': True})


# ---------------------------------------------------------------------------
# POST /api/reviews/{id}/replies/
# ---------------------------------------------------------------------------
class ReviewReplyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return Response({'detail': 'Không tìm thấy đánh giá.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewReplyCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reply = ReviewReply.objects.create(
            review=review,
            user=request.user,
            comment=serializer.validated_data['comment'],
        )
        from .serializers import ReviewReplySerializer
        return Response(ReviewReplySerializer(reply).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# DELETE /api/reviews/{review_id}/replies/{reply_id}/
# ---------------------------------------------------------------------------
class ReviewReplyDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id, reply_id):
        try:
            reply = ReviewReply.objects.select_related('review__location', 'user').get(
                pk=reply_id, review_id=review_id
            )
        except ReviewReply.DoesNotExist:
            return Response({'detail': 'Không tìm thấy phản hồi.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_own = reply.user_id == user.pk
        can_mod = _can_moderate(user, reply.review.location)

        if not is_own and not can_mod:
            return Response({'detail': 'Bạn không có quyền xóa phản hồi này.'}, status=status.HTTP_403_FORBIDDEN)

        reply.delete()
        return Response({'success': True})
