import json
import re
import time

from django.conf import settings
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsAdminOrManager, can_manage_category, can_manage_location
from .models import Location
from .serializers import LocationListSerializer, LocationSerializer


def _make_location_id(name='dia-diem'):
    """Generate slug-based ID matching frontend pattern."""
    slug = re.sub(r'[^a-z0-9\s-]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug).strip('-')
    suffix = hex(int(time.time() * 1000))[-6:]
    return f"{slug or 'dia-diem'}-{suffix}"


# ---------------------------------------------------------------------------
# GET/POST /api/locations/
# ---------------------------------------------------------------------------
class LocationListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = Location.objects.filter(is_active=True)
        category = request.query_params.get('category', '').strip()
        q = request.query_params.get('q', '').strip()
        if category:
            qs = qs.filter(category=category)
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(address__icontains=q) |
                Q(phone__icontains=q) |
                Q(keywords__icontains=q) |
                Q(group__icontains=q) |
                Q(subgroup__icontains=q)
            )
        serializer = LocationListSerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})

    def post(self, request):
        user = request.user
        if not user.is_authenticated or user.role not in ('admin', 'manager'):
            return Response({'detail': 'Tài khoản không có quyền quản lý địa điểm.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = LocationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        category = request.data.get('category', 'utility')
        if user.role == 'manager' and not can_manage_category(user, category):
            return Response({'detail': 'Bạn không có quyền thêm địa điểm vào nhóm này.'}, status=status.HTTP_403_FORBIDDEN)

        # Generate ID if not provided
        location_id = str(request.data.get('id', '')).strip()
        if not location_id:
            location_id = _make_location_id(request.data.get('name', ''))

        location = serializer.save(id=location_id)
        return Response(LocationSerializer(location).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# GET/PUT/DELETE /api/locations/{id}/
# ---------------------------------------------------------------------------
class LocationDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _get(self, pk):
        try:
            return Location.objects.get(pk=pk, is_active=True)
        except Location.DoesNotExist:
            return None

    def get(self, request, pk):
        location = self._get(pk)
        if not location:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(LocationSerializer(location).data)

    def put(self, request, pk):
        location = self._get(pk)
        if not location:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not can_manage_location(user, location):
            return Response({'detail': 'Bạn không có quyền sửa địa điểm này.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = LocationSerializer(location, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Manager cannot move location to a category outside their permission
        new_category = request.data.get('category', location.category)
        if user.role == 'manager' and new_category != location.category:
            if not can_manage_category(user, new_category):
                return Response({'detail': 'Bạn không có quyền chuyển địa điểm sang nhóm này.'}, status=status.HTTP_403_FORBIDDEN)

        location = serializer.save()
        return Response(LocationSerializer(location).data)

    def delete(self, request, pk):
        location = self._get(pk)
        if not location:
            return Response({'detail': 'Không tìm thấy địa điểm.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not can_manage_location(user, location):
            return Response({'detail': 'Bạn không có quyền xóa địa điểm này.'}, status=status.HTTP_403_FORBIDDEN)

        location.delete()
        return Response({'success': True})


# ---------------------------------------------------------------------------
# POST /api/locations/import/  — admin only
# ---------------------------------------------------------------------------
class LocationImportView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({'detail': 'Dữ liệu nhập phải là một mảng địa điểm.'}, status=status.HTTP_400_BAD_REQUEST)

        created, updated, errors = 0, 0, []
        for i, item in enumerate(data):
            if not item.get('name'):
                errors.append(f'Dòng {i+1}: thiếu tên địa điểm.')
                continue
            location_id = str(item.get('id', '')).strip() or _make_location_id(item['name'])
            serializer = LocationSerializer(data={**item, 'id': location_id})
            if not serializer.is_valid():
                errors.append(f'Dòng {i+1} ({item.get("name")}): {serializer.errors}')
                continue
            _, was_created = Location.objects.update_or_create(
                id=location_id,
                defaults=serializer.validated_data,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        return Response({'created': created, 'updated': updated, 'errors': errors})


# ---------------------------------------------------------------------------
# POST /api/locations/reset/  — admin only, seed from locations.json
# ---------------------------------------------------------------------------
class LocationResetView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        import os
        from pathlib import Path

        json_path = Path(settings.BASE_DIR).parent / 'binh-dinh-tourism-react' / 'src' / 'data' / 'locations.json'
        if not json_path.exists():
            return Response({'detail': f'Không tìm thấy file seed: {json_path}'}, status=status.HTTP_404_NOT_FOUND)

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        Location.objects.all().delete()
        created = 0
        for item in data:
            if not item.get('name'):
                continue
            location_id = str(item.get('id', '')).strip() or _make_location_id(item['name'])
            serializer = LocationSerializer(data={**item, 'id': location_id})
            if serializer.is_valid():
                serializer.save(id=location_id)
                created += 1

        return Response({'success': True, 'created': created})
