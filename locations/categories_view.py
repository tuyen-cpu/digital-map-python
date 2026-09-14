"""
GET  /api/categories/        — public, trả danh sách categories
"""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CATEGORY_CHOICES


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = [
            {'key': key, 'label': label}
            for key, label in CATEGORY_CHOICES
        ]
        return Response({'count': len(categories), 'results': categories})
