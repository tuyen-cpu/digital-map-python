from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from locations.models import Location
from .models import TravelHistory, TravelReminder
from .serializers import (
    TravelHistorySerializer,
    TravelHistoryRecordSerializer,
    TravelReminderSerializer,
    TravelReminderCreateSerializer,
    TravelReminderPatchSerializer,
)


# ---------------------------------------------------------------------------
# GET /api/travel/history/
# POST /api/travel/history/
# ---------------------------------------------------------------------------
class TravelHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = TravelHistory.objects.filter(user=request.user).select_related('location')
        return Response({
            'count': history.count(),
            'results': TravelHistorySerializer(history, many=True).data,
        })

    def post(self, request):
        user = request.user
        if user.role not in ('user', 'manager'):
            return Response({'detail': 'Chỉ user/manager mới ghi nhận hành trình.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TravelHistoryRecordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        location_id = d['locationId']
        action = d['action']

        try:
            location = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)

        entry, created = TravelHistory.objects.get_or_create(
            user=user,
            location=location,
            defaults={'last_action': action},
        )

        if not created:
            if action == 'unvisit':
                entry.visited_at = None
                entry.last_action = 'view' if entry.view_count > 0 else 'route' if entry.route_count > 0 else 'view'
                entry.save()
            else:
                entry.last_action = action
                if action == 'view':
                    entry.view_count += 1
                elif action == 'route':
                    entry.route_count += 1
                elif action == 'visited' and not entry.visited_at:
                    entry.visited_at = timezone.now()
                entry.save()
        else:
            if action == 'unvisit':
                pass  # nothing to unvisit on new entry
            elif action == 'view':
                entry.view_count = 1
            elif action == 'route':
                entry.route_count = 1
            elif action == 'visited':
                entry.visited_at = timezone.now()
            entry.save()

        return Response(
            TravelHistorySerializer(entry).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# DELETE /api/travel/history/{id}/
# ---------------------------------------------------------------------------
class TravelHistoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            entry = TravelHistory.objects.get(pk=pk, user=request.user)
        except TravelHistory.DoesNotExist:
            return Response({'detail': 'Không tìm thấy.'}, status=status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response({'success': True})


# ---------------------------------------------------------------------------
# GET /api/travel/reminders/
# POST /api/travel/reminders/
# ---------------------------------------------------------------------------
class TravelReminderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reminders = TravelReminder.objects.filter(user=request.user).select_related('location')
        return Response({
            'count': reminders.count(),
            'results': TravelReminderSerializer(reminders, many=True).data,
        })

    def post(self, request):
        user = request.user
        if user.role not in ('user', 'manager'):
            return Response({'detail': 'Hãy đăng nhập để tạo lịch nhắc.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TravelReminderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        try:
            location = Location.objects.get(pk=d['locationId'])
        except Location.DoesNotExist:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)

        reminder = TravelReminder.objects.create(
            user=user,
            location=location,
            scheduled_at=d['scheduledAt'],
            note=d['note'],
        )
        return Response(TravelReminderSerializer(reminder).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# PATCH/DELETE /api/travel/reminders/{id}/
# ---------------------------------------------------------------------------
class TravelReminderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, pk, user):
        try:
            return TravelReminder.objects.get(pk=pk, user=user)
        except TravelReminder.DoesNotExist:
            return None

    def patch(self, request, pk):
        reminder = self._get(pk, request.user)
        if not reminder:
            return Response({'detail': 'Không tìm thấy lịch nhắc.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TravelReminderPatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        if 'completedAt' in d:
            reminder.completed_at = d['completedAt']
        if 'notifiedAt' in d:
            reminder.notified_at = d['notifiedAt']
        reminder.save()
        return Response(TravelReminderSerializer(reminder).data)

    def delete(self, request, pk):
        reminder = self._get(pk, request.user)
        if not reminder:
            return Response({'detail': 'Không tìm thấy lịch nhắc.'}, status=status.HTTP_404_NOT_FOUND)
        reminder.delete()
        return Response({'success': True})
