from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from locations.models import Location
from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteToggleSerializer


# ---------------------------------------------------------------------------
# GET /api/favorites/
# ---------------------------------------------------------------------------
class FavoriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related('location')
        return Response({
            'count': favorites.count(),
            'results': FavoriteSerializer(favorites, many=True).data,
        })


# ---------------------------------------------------------------------------
# POST /api/favorites/toggle/
# ---------------------------------------------------------------------------
class FavoriteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FavoriteToggleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        location_id = serializer.validated_data['locationId']
        try:
            location = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)

        fav, created = Favorite.objects.get_or_create(user=request.user, location=location)
        if not created:
            fav.delete()
            return Response({'favorited': False, 'locationId': location_id})

        return Response({'favorited': True, 'locationId': location_id}, status=status.HTTP_201_CREATED)
