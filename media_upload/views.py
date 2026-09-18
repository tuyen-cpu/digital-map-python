import mimetypes
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrManager


def _get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name='auto',
    )


def _check_r2_configured():
    return all([
        settings.R2_ACCOUNT_ID,
        settings.R2_ACCESS_KEY_ID,
        settings.R2_SECRET_ACCESS_KEY,
        settings.R2_BUCKET_NAME,
        settings.R2_PUBLIC_URL,
    ])


# ---------------------------------------------------------------------------
# POST /api/media/upload/
# ---------------------------------------------------------------------------
class MediaUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _check_r2_configured():
            return Response(
                {'detail': 'Chưa cấu hình Cloudflare R2. Kiểm tra biến môi trường R2_*.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'Thiếu file upload.'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra folder — user thường chỉ được upload vào 'avatars/'
        folder = request.data.get('folder', 'locations').strip('/')
        restricted_folders = ('locations', 'slides')
        if folder in restricted_folders and request.user.role not in ('admin', 'manager'):
            return Response(
                {'detail': 'Bạn cần có quyền quản lý để upload vào thư mục này.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate MIME type
        content_type = file.content_type or ''
        # Double-check bằng tên file nếu content_type không rõ
        if not content_type or content_type == 'application/octet-stream':
            guessed, _ = mimetypes.guess_type(file.name)
            content_type = guessed or content_type

        allowed = settings.MEDIA_ALLOWED_TYPES
        if content_type not in allowed:
            return Response(
                {'detail': f'Loại file không được phép. Chỉ hỗ trợ: image/jpeg, image/png, image/webp, image/gif, video/mp4, video/webm, video/ogg.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate size — video có giới hạn riêng
        is_video = content_type.startswith('video/')
        if is_video:
            max_bytes = getattr(settings, 'MEDIA_UPLOAD_MAX_VIDEO_BYTES', 40 * 1024 * 1024)
            max_label = '40 MB'
        else:
            max_bytes = settings.MEDIA_UPLOAD_MAX_BYTES
            max_label = f'{max_bytes // (1024 * 1024)} MB'
        if file.size > max_bytes:
            return Response(
                {'detail': f'File vượt quá giới hạn {max_label}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Tạo key duy nhất trong bucket
        ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else 'jpg'
        key = f"{folder}/{uuid.uuid4().hex}.{ext}"

        try:
            client = _get_r2_client()
            client.upload_fileobj(
                file,
                settings.R2_BUCKET_NAME,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'public, max-age=31536000',
                },
            )
        except (BotoCoreError, ClientError) as exc:
            return Response(
                {'detail': f'Upload thất bại: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        public_url = f"{settings.R2_PUBLIC_URL}/{key}"
        return Response({'url': public_url, 'key': key}, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# DELETE /api/media/delete/
# ---------------------------------------------------------------------------
class MediaDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def post(self, request):
        """Dùng POST thay vì DELETE để dễ gửi body JSON từ frontend."""
        if not _check_r2_configured():
            return Response(
                {'detail': 'Chưa cấu hình Cloudflare R2.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        key = request.data.get('key', '').strip()
        if not key:
            # Thử parse key từ URL
            url = request.data.get('url', '').strip()
            base = settings.R2_PUBLIC_URL.rstrip('/')
            if url.startswith(base + '/'):
                key = url[len(base) + 1:]

        if not key:
            return Response({'detail': 'Thiếu key hoặc url của file.'}, status=status.HTTP_400_BAD_REQUEST)

        # Bảo vệ: không cho xóa file ngoài các folder cho phép
        allowed_prefixes = ('locations/', 'slides/', 'avatars/')
        if not any(key.startswith(p) for p in allowed_prefixes):
            return Response({'detail': 'Không được phép xóa file này.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            client = _get_r2_client()
            client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)
        except (BotoCoreError, ClientError) as exc:
            return Response({'detail': f'Xóa thất bại: {exc}'}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'success': True})
