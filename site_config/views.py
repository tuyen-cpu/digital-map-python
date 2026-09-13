from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from .models import SiteSettings, DEFAULT_HERO_SLIDES
from .serializers import SiteSettingsSerializer, SiteSettingsUpdateSerializer


# ---------------------------------------------------------------------------
# GET /api/site-config/         — public
# PUT /api/site-config/         — admin only
# POST /api/site-config/reset/  — admin only
# ---------------------------------------------------------------------------
class SiteSettingsView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdmin()]

    def get(self, request):
        obj = SiteSettings.get_solo()
        response = Response(SiteSettingsSerializer(obj).data)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response['Pragma'] = 'no-cache'
        return response

    def put(self, request):
        serializer = SiteSettingsUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = SiteSettings.get_solo()
        d = serializer.validated_data
        if 'heroSlides' in d:
            obj.hero_slides = d['heroSlides']
        if 'heroIntervalMs' in d:
            obj.hero_interval_ms = d['heroIntervalMs']
        obj.save()
        return Response(SiteSettingsSerializer(obj).data)


class SiteSettingsResetView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        obj = SiteSettings.get_solo()
        obj.hero_slides = DEFAULT_HERO_SLIDES
        obj.hero_interval_ms = 5200
        obj.save()
        return Response(SiteSettingsSerializer(obj).data)
