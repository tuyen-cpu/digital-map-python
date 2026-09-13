# Du lịch Phường Bình Định — Backend API

Django REST Framework backend cho website du lịch Phường Bình Định, thị xã An Nhơn, tỉnh Bình Định.

---

## Yêu cầu

- Python 3.11+
- PostgreSQL 14+ (hoặc SQLite cho dev)
- pip

---

## Cài đặt & Chạy

### 1. Tạo và kích hoạt virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Cài dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

```bash
cp .env.example .env
```

Mở `.env` và điền các giá trị thực tế (xem phần [Biến môi trường](#biến-môi-trường) bên dưới).

### 4. Migrate database

```bash
python manage.py migrate
```

### 5. Seed dữ liệu địa điểm (tuỳ chọn)

```bash
python manage.py seed_locations
```

### 6. Chạy server

```bash
python manage.py runserver
```

Server chạy tại: `http://127.0.0.1:8000`

---

## Biến môi trường

Sao chép `.env.example` thành `.env` và điền đầy đủ:

| Biến | Mặc định | Mô tả |
|---|---|---|
| `SECRET_KEY` | _(bắt buộc)_ | Django secret key |
| `DEBUG` | `True` | Bật/tắt debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Danh sách host được phép |
| `USE_POSTGRES` | `False` | `True` để dùng PostgreSQL, `False` dùng SQLite |
| `DB_NAME` | `binh_dinh_tourism` | Tên database PostgreSQL |
| `DB_USER` | `postgres` | User PostgreSQL |
| `DB_PASSWORD` | _(bắt buộc nếu dùng PG)_ | Mật khẩu PostgreSQL |
| `DB_HOST` | `localhost` | Host PostgreSQL |
| `DB_PORT` | `5432` | Port PostgreSQL |
| `ADMIN_USERNAME` | `admin` | Tên đăng nhập admin |
| `ADMIN_PASSWORD` | `BinhDinh@2026` | Mật khẩu admin |
| `ADMIN_DISPLAY_NAME` | `Quản trị viên Bình Định` | Tên hiển thị admin |
| `DEFAULT_RESET_PASSWORD` | `PhuongBinhDinh@123` | Mật khẩu mặc định khi reset |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | URL frontend được phép CORS |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | Thời gian sống access token (phút) |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `7` | Thời gian sống refresh token (ngày) |

---

## Cấu trúc thư mục

```
digital-map-python1/
├── BE/                  # Django project config (settings, urls, wsgi)
├── accounts/            # Auth, user management, phân quyền
├── locations/           # Địa điểm du lịch
├── reviews/             # Đánh giá và phản hồi
├── favorites/           # Địa điểm yêu thích
├── travel/              # Lịch sử hành trình & lịch nhắc
├── analytics/           # Sự kiện analytics
├── site_config/         # Cấu hình trang (slideshow, settings)
├── manage.py
├── requirements.txt
└── .env.example
```

---

## API Endpoints

Base URL: `http://127.0.0.1:8000/api`

### Auth & Tài khoản

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `POST` | `/auth/register/` | Đăng ký tài khoản | Public |
| `POST` | `/auth/login/` | Đăng nhập, trả về JWT | Public |
| `POST` | `/auth/logout/` | Đăng xuất (blacklist token) | User |
| `GET` | `/auth/me/` | Thông tin user hiện tại | User |
| `PUT/PATCH` | `/auth/profile/` | Cập nhật hồ sơ | User |
| `POST` | `/auth/change-password/` | Đổi mật khẩu | User |

### Quản lý User (Admin)

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `GET` | `/admin/users/` | Danh sách tất cả user | Admin |
| `GET/PUT/DELETE` | `/admin/users/<username>/` | Chi tiết / sửa / xoá user | Admin |
| `POST` | `/admin/users/<username>/reset-password/` | Reset mật khẩu user | Admin |

### Địa điểm

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `GET` | `/locations/` | Danh sách địa điểm (có filter) | Public |
| `POST` | `/locations/` | Tạo địa điểm mới | Admin/Manager |
| `GET` | `/locations/<id>/` | Chi tiết địa điểm | Public |
| `PUT/PATCH` | `/locations/<id>/` | Cập nhật địa điểm | Admin/Manager |
| `DELETE` | `/locations/<id>/` | Xoá địa điểm | Admin |
| `POST` | `/locations/import/` | Import hàng loạt (JSON) | Admin |
| `POST` | `/locations/reset/` | Xoá toàn bộ & seed lại | Admin |

Query params cho `GET /locations/`:
- `category` — lọc theo danh mục (`tourism`, `food`, `accommodation`, ...)
- `group` — lọc theo nhóm
- `subgroup` — lọc theo nhóm con
- `search` — tìm kiếm theo tên / địa chỉ / từ khoá
- `is_active` — `true`/`false`

### Đánh giá

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `GET` | `/locations/<id>/reviews/` | Danh sách đánh giá của địa điểm | Public |
| `POST` | `/locations/<id>/reviews/` | Tạo đánh giá mới | User |
| `DELETE` | `/reviews/<uuid>/` | Xoá đánh giá | Owner/Admin |
| `POST` | `/reviews/<uuid>/replies/` | Thêm phản hồi | User |
| `DELETE` | `/reviews/<uuid>/replies/<uuid>/` | Xoá phản hồi | Owner/Admin |

### Yêu thích

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `GET` | `/favorites/` | Danh sách địa điểm yêu thích | User |
| `POST` | `/favorites/toggle/` | Thêm/bỏ yêu thích | User |

### Hành trình & Lịch nhắc

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `GET/POST` | `/travel/history/` | Lịch sử hành trình | User |
| `DELETE` | `/travel/history/<uuid>/` | Xoá một mục lịch sử | User |
| `GET/POST` | `/travel/reminders/` | Danh sách / tạo lịch nhắc | User |
| `GET/PUT/DELETE` | `/travel/reminders/<uuid>/` | Chi tiết / sửa / xoá lịch nhắc | User |

### Analytics

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `POST` | `/analytics/events/` | Ghi nhận sự kiện (view, click...) | Public |

### Cấu hình trang

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `GET` | `/site-config/` | Lấy cấu hình trang (slideshow...) | Public |
| `PUT/PATCH` | `/site-config/` | Cập nhật cấu hình | Admin |
| `POST` | `/site-config/reset/` | Reset về mặc định | Admin |

---

## Phân quyền

| Role | Mô tả |
|---|---|
| `user` | Đăng nhập, đánh giá, yêu thích, hành trình |
| `manager` | Quản lý địa điểm theo phạm vi được admin cấp (category/group/subgroup) |
| `admin` | Toàn quyền — quản lý user, địa điểm, cấu hình, thống kê |

JWT được truyền qua header:
```
Authorization: Bearer <access_token>
```

---

## Stack kỹ thuật

| Thành phần | Phiên bản |
|---|---|
| Python | 3.11+ |
| Django | 5.2.1 |
| Django REST Framework | 3.15.2 |
| djangorestframework-simplejwt | 5.3.1 |
| django-cors-headers | 4.4.0 |
| django-environ | 0.11.2 |
| psycopg2-binary | 2.9.9 |
| Pillow | 10.4.0 |

---

## Chạy trên PyCharm

1. Mở thư mục gốc (chứa `manage.py`) trong PyCharm
2. `File → Settings → Project → Python Interpreter` → chọn `.venv\Scripts\python.exe`
3. Mở Terminal trong PyCharm, chạy:
   ```
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```
