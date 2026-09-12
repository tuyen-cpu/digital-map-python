from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsAdminOrManager
from .models import AnalyticsEvent
from .serializers import AnalyticsEventSerializer, AnalyticsEventCreateSerializer


# ---------------------------------------------------------------------------
# POST /api/analytics/events/   — public (no auth needed)
# GET  /api/analytics/events/   — admin/manager
# DELETE /api/analytics/events/ — admin only
# ---------------------------------------------------------------------------
class AnalyticsEventView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        return [IsAdminOrManager()]

    def post(self, request):
        serializer = AnalyticsEventCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        event = AnalyticsEvent.objects.create(
            type=d['type'],
            visitor_id=d['visitorId'],
            session_id=d['sessionId'],
            account=d.get('account', ''),
            role=d.get('role', 'guest'),
            location_id=d.get('locationId'),
            location_name=d.get('locationName'),
            category=d.get('category'),
            path=d.get('path'),
            section=d.get('section'),
            rating=d.get('rating'),
        )
        return Response({'id': str(event.id)}, status=status.HTTP_201_CREATED)

    def get(self, request):
        qs = AnalyticsEvent.objects.all()

        # Manager sees only events for their locations
        user = request.user
        if user.role == 'manager':
            from accounts.permissions import can_manage_location
            from locations.models import Location
            try:
                perms = user.manager_permission
                managed_ids = Location.objects.filter(
                    category__in=perms.categories or []
                ).values_list('id', flat=True)
                qs = qs.filter(location_id__in=list(managed_ids))
            except Exception:
                qs = qs.none()

        # Optional filters
        event_type = request.query_params.get('type')
        if event_type:
            qs = qs.filter(type=event_type)

        return Response({
            'count': qs.count(),
            'results': AnalyticsEventSerializer(qs[:5000], many=True).data,
        })

    def delete(self, request):
        count, _ = AnalyticsEvent.objects.all().delete()
        return Response({'success': True, 'deleted': count})
