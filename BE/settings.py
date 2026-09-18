from datetime import timedelta
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:5173', 'http://localhost:3000']),
    JWT_ACCESS_TOKEN_LIFETIME_MINUTES=(int, 60),
    JWT_REFRESH_TOKEN_LIFETIME_DAYS=(int, 7),
)

environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # Local apps
    'accounts',
    'locations',
    'reviews',
    'favorites',
    'travel',
    'analytics',
    'site_config',
    'media_upload',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BE.wsgi.application'

# ---------------------------------------------------------------------------
# Database – SQLite (dev) hoặc PostgreSQL (production)
# Đặt USE_POSTGRES=True trong .env để dùng PostgreSQL
# ---------------------------------------------------------------------------
USE_POSTGRES = env.bool('USE_POSTGRES', default=False)

if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='binh_dinh_tourism'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env('JWT_ACCESS_TOKEN_LIFETIME_MINUTES')),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env('JWT_REFRESH_TOKEN_LIFETIME_DAYS')),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Admin env vars (không lưu DB)
# ---------------------------------------------------------------------------
ADMIN_USERNAME = env('ADMIN_USERNAME', default='admin')
ADMIN_PASSWORD = env('ADMIN_PASSWORD', default='BinhDinh@2026')
ADMIN_DISPLAY_NAME = env('ADMIN_DISPLAY_NAME', default='Quản trị viên Bình Định')
DEFAULT_RESET_PASSWORD = env('DEFAULT_RESET_PASSWORD', default='PhuongBinhDinh@123')

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ---------------------------------------------------------------------------
# Cloudflare R2 — media upload
# ---------------------------------------------------------------------------
R2_ACCOUNT_ID = env('R2_ACCOUNT_ID', default='')
R2_ACCESS_KEY_ID = env('R2_ACCESS_KEY_ID', default='')
R2_SECRET_ACCESS_KEY = env('R2_SECRET_ACCESS_KEY', default='')
R2_BUCKET_NAME = env('R2_BUCKET_NAME', default='binh-dinh-tourism')
R2_PUBLIC_URL = env('R2_PUBLIC_URL', default='').rstrip('/')
# Endpoint S3-compatible của R2
R2_ENDPOINT_URL = f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com' if R2_ACCOUNT_ID else ''

# Giới hạn upload
MEDIA_UPLOAD_MAX_BYTES = 10 * 1024 * 1024   # 10 MB cho ảnh
MEDIA_UPLOAD_MAX_VIDEO_BYTES = 40 * 1024 * 1024  # 40 MB cho video
MEDIA_ALLOWED_TYPES = [
    'image/jpeg', 'image/png', 'image/webp', 'image/gif',
    'video/mp4', 'video/webm', 'video/ogg',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
