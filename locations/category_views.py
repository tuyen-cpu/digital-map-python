"""
Category CRUD API

GET    /api/categories/              — public, list active categories
POST   /api/categories/              — admin only, create
GET    /api/categories/{key}/        — public, single category
PUT    /api/categories/{key}/        — admin only, update
DELETE /api/categories/{key}/        — admin only, delete
POST   /api/categories/seed/         — admin only, seed defaults if empty
"""
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from .category_models import Category

DEFAULT_CATEGORIES = [
    {
        'key': 'tourism', 'label': 'Khu/điểm du lịch', 'short_label': 'Du lịch',
        'emoji': '🏛️', 'marker': '#1d4ed8', 'order': 1,
        'description': 'Di tích, danh thắng, không gian văn hóa, tâm linh và các điểm tham quan.',
        'suggested_groups': ['Di tích lịch sử / khảo cổ', 'Văn hóa / du lịch / tâm linh', 'Điểm tham quan', 'Làng nghề / trải nghiệm'],
        'suggested_subgroups': ['Di tích lịch sử', 'Lịch sử - kiến trúc', 'Chùa', 'Đình làng', 'Miếu', 'Tâm linh', 'Làng nghề / trải nghiệm', 'Làng võ / trải nghiệm', 'Nhà văn hóa', 'Điểm tham quan đô thị'],
        'suggested_keywords': ['lịch sử', 'kiến trúc', 'di tích', 'tâm linh', 'văn hóa', 'tham quan', 'làng nghề', 'võ cổ truyền'],
    },
    {
        'key': 'lodging', 'label': 'Lưu trú du lịch', 'short_label': 'Lưu trú',
        'emoji': '🛏️', 'marker': '#2563eb', 'order': 2,
        'description': 'Khách sạn, nhà nghỉ và cơ sở lưu trú phục vụ du khách.',
        'suggested_groups': ['Lưu trú du lịch'],
        'suggested_subgroups': ['Khách sạn', 'Nhà nghỉ', 'Khách sạn / nhà nghỉ', 'Homestay'],
        'suggested_keywords': ['lưu trú', 'khách sạn', 'nhà nghỉ', 'homestay'],
    },
    {
        'key': 'food', 'label': 'Ẩm thực', 'short_label': 'Ẩm thực',
        'emoji': '🍜', 'marker': '#0284c7', 'order': 3,
        'description': 'Nhà hàng, quán ăn, cà phê, trà sữa và các địa chỉ ẩm thực địa phương.',
        'suggested_groups': ['Ẩm thực / nhà hàng / cafe', 'Ẩm thực / đồ uống'],
        'suggested_subgroups': ['Nhà hàng', 'Quán ăn', 'Cafe', 'Trà sữa', 'Bánh xèo', 'Bún bò', 'Phở', 'Cơm gia đình', 'Hải sản / ốc', 'Lẩu nướng', 'Đặc sản / cơ sở sản xuất'],
        'suggested_keywords': ['ẩm thực', 'quán ăn', 'nhà hàng', 'cafe', 'trà sữa', 'đặc sản', 'ăn sáng', 'ăn tối'],
    },
    {
        'key': 'entertainment', 'label': 'Giải trí', 'short_label': 'Giải trí',
        'emoji': '🎯', 'marker': '#0369a1', 'order': 4,
        'description': 'Công viên, thể thao, karaoke và các điểm vui chơi giải trí.',
        'suggested_groups': ['Vui chơi / thể thao', 'Giải trí'],
        'suggested_subgroups': ['Công viên', 'Karaoke', 'Gym', 'Billiards', 'Sân bóng / cafe', 'Sân vận động', 'Công viên giải trí', 'Trẻ em'],
        'suggested_keywords': ['giải trí', 'thể thao', 'công viên', 'karaoke', 'gym', 'trẻ em'],
    },
    {
        'key': 'health', 'label': 'Chăm sóc sức khỏe', 'short_label': 'Sức khỏe',
        'emoji': '💙', 'marker': '#0e7490', 'order': 5,
        'description': 'Trạm y tế, phòng khám, nhà thuốc và dịch vụ chăm sóc sức khỏe.',
        'suggested_groups': ['Y tế / chăm sóc sức khỏe'],
        'suggested_subgroups': ['Trạm y tế', 'Phòng khám', 'Nhà thuốc', 'Nha khoa'],
        'suggested_keywords': ['y tế', 'sức khỏe', 'phòng khám', 'nhà thuốc', 'nha khoa'],
    },
    {
        'key': 'administration', 'label': 'Cơ quan hành chính', 'short_label': 'Hành chính',
        'emoji': '🏢', 'marker': '#1e40af', 'order': 6,
        'description': 'UBND, Công an, Trung tâm hành chính công, Đảng ủy và các cơ quan phường.',
        'suggested_groups': ['Cơ quan hành chính', 'Cơ quan hành chính / dịch vụ công', 'Cơ quan hành chính / an ninh', 'Cơ quan hành chính / quốc phòng', 'Cơ quan chuyên môn', 'Đơn vị sự nghiệp công'],
        'suggested_subgroups': ['Ủy ban nhân dân phường', 'Công an phường', 'Trung tâm Phục vụ hành chính công', 'Đảng', 'Ban Chỉ huy Quân sự', 'Văn phòng HĐND và UBND', 'Văn hóa - Xã hội', 'Dịch vụ sự nghiệp công'],
        'suggested_keywords': ['UBND', 'Công an', 'hành chính', 'dịch vụ công', 'an ninh', 'quốc phòng', 'chính quyền'],
    },
    {
        'key': 'utility', 'label': 'Tiện ích', 'short_label': 'Tiện ích',
        'emoji': '📍', 'marker': '#1e3a8a', 'order': 7,
        'description': 'Ngân hàng, chợ, trường học, bưu chính, điện và các dịch vụ thiết yếu.',
        'suggested_groups': ['Ngân hàng / ATM', 'Mua sắm / chợ / siêu thị', 'Bưu chính / viễn thông / điện / nhiên liệu', 'Giáo dục'],
        'suggested_subgroups': ['Ngân hàng', 'ATM', 'Chợ', 'Siêu thị', 'Siêu thị mini', 'Cửa hàng tiện lợi', 'Bưu chính', 'Xăng dầu', 'Điện lực', 'Viễn thông', 'Mầm non công lập', 'Tiểu học công lập', 'THCS công lập', 'THPT'],
        'suggested_keywords': ['ngân hàng', 'ATM', 'chợ', 'siêu thị', 'bưu chính', 'điện lực', 'viễn thông', 'giáo dục', 'trường học'],
    },
]


def _serialize(cat):
    return {
        'key': cat.key,
        'label': cat.label,
        'shortLabel': cat.short_label,
        'emoji': cat.emoji,
        'description': cat.description,
        'marker': cat.marker,
        'order': cat.order,
        'isActive': cat.is_active,
        'suggestedGroups': cat.suggested_groups or [],
        'suggestedSubgroups': cat.suggested_subgroups or [],
        'suggestedKeywords': cat.suggested_keywords or [],
    }


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cats = Category.objects.filter(is_active=True).order_by('order', 'key')
        return Response({'count': cats.count(), 'results': [_serialize(c) for c in cats]})

    def post(self, request):
        if not request.user.is_authenticated or getattr(request.user, 'role', '') != 'admin':
            return Response({'detail': 'Chỉ quản trị viên được thêm danh mục.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        key = str(data.get('key', '')).strip().lower().replace(' ', '_').replace('-', '_')
        if not key:
            return Response({'detail': 'Thiếu key danh mục.'}, status=status.HTTP_400_BAD_REQUEST)
        if Category.objects.filter(key=key).exists():
            return Response({'detail': f'Key "{key}" đã tồn tại.'}, status=status.HTTP_400_BAD_REQUEST)
        cat = Category.objects.create(
            key=key,
            label=str(data.get('label', key)).strip(),
            short_label=str(data.get('shortLabel', key)).strip(),
            emoji=str(data.get('emoji', '📍')).strip(),
            description=str(data.get('description', '')).strip(),
            marker=str(data.get('marker', '#1d4ed8')).strip(),
            order=int(data.get('order', 99)),
            is_active=bool(data.get('isActive', True)),
            suggested_groups=data.get('suggestedGroups', []) or [],
            suggested_subgroups=data.get('suggestedSubgroups', []) or [],
            suggested_keywords=data.get('suggestedKeywords', []) or [],
        )
        return Response(_serialize(cat), status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdmin()]

    def get(self, request, key):
        try:
            cat = Category.objects.get(key=key)
        except Category.DoesNotExist:
            return Response({'detail': 'Không tìm thấy danh mục.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(_serialize(cat))

    def put(self, request, key):
        try:
            cat = Category.objects.get(key=key)
        except Category.DoesNotExist:
            return Response({'detail': 'Không tìm thấy danh mục.'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if 'label' in data:              cat.label = str(data['label']).strip()
        if 'shortLabel' in data:         cat.short_label = str(data['shortLabel']).strip()
        if 'emoji' in data:              cat.emoji = str(data['emoji']).strip()
        if 'description' in data:        cat.description = str(data['description']).strip()
        if 'marker' in data:             cat.marker = str(data['marker']).strip()
        if 'order' in data:              cat.order = int(data['order'])
        if 'isActive' in data:           cat.is_active = bool(data['isActive'])
        if 'suggestedGroups' in data:    cat.suggested_groups = data['suggestedGroups'] or []
        if 'suggestedSubgroups' in data: cat.suggested_subgroups = data['suggestedSubgroups'] or []
        if 'suggestedKeywords' in data:  cat.suggested_keywords = data['suggestedKeywords'] or []
        cat.save()
        return Response(_serialize(cat))

    def delete(self, request, key):
        try:
            cat = Category.objects.get(key=key)
        except Category.DoesNotExist:
            return Response({'detail': 'Không tìm thấy danh mục.'}, status=status.HTTP_404_NOT_FOUND)
        from locations.models import Location
        in_use = Location.objects.filter(category=key).count()
        if in_use:
            return Response(
                {'detail': f'Không thể xóa — có {in_use} địa điểm đang dùng danh mục này. Hãy chuyển địa điểm sang danh mục khác trước.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cat.delete()
        return Response({'success': True})


class CategorySeedView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        created = 0
        for item in DEFAULT_CATEGORIES:
            key = item['key']
            defaults = {k: v for k, v in item.items() if k != 'key'}
            obj, was_created = Category.objects.get_or_create(key=key, defaults=defaults)
            if not was_created:
                # Update suggested lists even for existing categories
                obj.suggested_groups = item.get('suggested_groups', [])
                obj.suggested_subgroups = item.get('suggested_subgroups', [])
                obj.suggested_keywords = item.get('suggested_keywords', [])
                obj.save(update_fields=['suggested_groups', 'suggested_subgroups', 'suggested_keywords'])
            else:
                created += 1
        return Response({'success': True, 'created': created, 'total': Category.objects.count()})
