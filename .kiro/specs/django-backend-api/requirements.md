# Tài liệu Yêu Cầu

## Giới thiệu

Xây dựng Django REST Framework API Backend với PostgreSQL để thay thế toàn bộ cơ chế lưu trữ localStorage/IndexedDB của ứng dụng React "Du lịch Phường Bình Định" (`binh-dinh-tourism-react`). Backend sẽ cung cấp các endpoint RESTful quản lý người dùng, địa điểm du lịch, đánh giá, yêu thích, lịch sử di chuyển, lịch nhắc, sự kiện thống kê, và cấu hình trang web. Project Django đã có sẵn tại `c:\project-canhan\digital-binhdinh\BE` và cần được mở rộng (không tạo project mới).

## Bảng chú giải

- **API**: Django REST Framework API Backend
- **Client**: Ứng dụng React frontend (`binh-dinh-tourism-react`)
- **Admin**: Tài khoản quản trị tối cao được cấu hình qua biến môi trường, không lưu trong DB
- **Manager**: Tài khoản quản lý có quyền hạn chế theo `category`, `group`, `subgroup`
- **User**: Tài khoản người dùng thường, chỉ quản lý dữ liệu cá nhân
- **Guest**: Người dùng chưa đăng nhập
- **JWT_Token**: JSON Web Token dùng cho xác thực (access + refresh)
- **Location**: Địa điểm du lịch với đầy đủ thông tin địa lý và media
- **Review**: Đánh giá địa điểm của người dùng (rating 1–5, comment)
- **ReviewReply**: Phản hồi của manager/admin dưới một Review
- **Favorite**: Danh sách địa điểm yêu thích của người dùng
- **TravelHistory**: Lịch sử tương tác (xem, dẫn đường, đã đến) của người dùng với địa điểm
- **TravelReminder**: Lịch nhắc đến địa điểm vào thời điểm cụ thể
- **AnalyticsEvent**: Sự kiện thống kê hành vi (page_view, location_view, login, …)
- **SiteSettings**: Cấu hình giao diện trang chủ (hero slideshow)
- **MediaItem**: Đối tượng media gồm `url`, `alt`, `name`
- **Permissions**: Đối tượng `{ categories: [], groups: [], subgroups: [] }` phân quyền Manager
- **VN_Phone**: Số điện thoại di động Việt Nam hợp lệ (10 chữ số, đầu 03x/05x/07x/08x/09x)

---

## Yêu Cầu

### Yêu Cầu 1: Cấu hình và khởi tạo Project Django

**User Story:** Là một developer, tôi muốn project Django được cấu hình đúng với các thư viện cần thiết, để có thể phát triển và chạy API ngay lập tức.

#### Tiêu chí Chấp nhận

1. THE API SHALL sử dụng `django-environ` để đọc toàn bộ cấu hình nhạy cảm (SECRET_KEY, DB credentials, ADMIN credentials, JWT secret) từ file `.env`.
2. THE API SHALL cấu hình kết nối PostgreSQL qua `psycopg2-binary` thay thế SQLite mặc định.
3. THE API SHALL bao gồm `rest_framework`, `corsheaders`, `rest_framework_simplejwt` trong `INSTALLED_APPS`.
4. WHEN `CORS_ALLOWED_ORIGINS` được cấu hình, THE API SHALL cho phép request từ `http://localhost:5173` và các origin được khai báo trong `.env`.
5. THE API SHALL đặt `TIME_ZONE = 'Asia/Ho_Chi_Minh'` và `USE_TZ = True` để xử lý thời gian đúng múi giờ Việt Nam.
6. THE API SHALL cung cấp file `.env.example` với tất cả các biến môi trường cần thiết và giá trị mặc định an toàn.
7. IF file `.env` không tồn tại khi khởi động, THEN THE API SHALL raise `ImproperlyConfigured` với thông báo rõ ràng.

---

### Yêu Cầu 2: Xác thực và Phân quyền JWT

**User Story:** Là một người dùng, tôi muốn đăng nhập bằng username/password và nhận JWT token, để truy cập các tính năng được bảo vệ mà không cần gửi lại thông tin xác thực mỗi lần.

#### Tiêu chí Chấp nhận

1. WHEN Client gửi `POST /api/auth/login/` với `username` và `password` hợp lệ, THE API SHALL trả về `access_token`, `refresh_token`, và thông tin phiên người dùng (`id`, `username`, `displayName`, `role`, `permissions`, `mustChangePassword`).
2. WHEN Client gửi `POST /api/auth/login/` với credentials của Admin account (đọc từ env), THE API SHALL xác thực thành công và trả về session với `role: "admin"` mà không cần tra cứu database.
3. WHEN Client gửi `POST /api/auth/login/` với credentials không hợp lệ, THE API SHALL trả về HTTP 401 với thông báo lỗi bằng tiếng Việt.
4. WHEN Client gửi `POST /api/auth/refresh/` với `refresh_token` hợp lệ, THE API SHALL trả về `access_token` mới.
5. WHEN Client gửi `POST /api/auth/refresh/` với `refresh_token` hết hạn hoặc không hợp lệ, THE API SHALL trả về HTTP 401.
6. WHEN Client gửi `POST /api/auth/logout/` với `refresh_token` hợp lệ, THE API SHALL đưa token vào blacklist và trả về HTTP 200.
7. THE API SHALL cấu hình `ACCESS_TOKEN_LIFETIME` là 60 phút và `REFRESH_TOKEN_LIFETIME` là 7 ngày.
8. WHEN một endpoint yêu cầu xác thực nhận request không có `Authorization: Bearer <token>`, THE API SHALL trả về HTTP 401.
9. WHEN một endpoint yêu cầu quyền Admin nhận request từ User/Manager, THE API SHALL trả về HTTP 403.

---

### Yêu Cầu 3: Quản lý Tài khoản Người dùng

**User Story:** Là một người dùng, tôi muốn đăng ký và quản lý tài khoản cá nhân; là Admin, tôi muốn quản lý toàn bộ tài khoản trong hệ thống.

#### Tiêu chí Chấp nhận

1. WHEN Client gửi `POST /api/auth/register/` với `username`, `password`, `displayName`, `phone` hợp lệ, THE API SHALL tạo tài khoản mới với `role: "user"` và trả về thông tin session cùng JWT tokens.
2. WHEN Client gửi `POST /api/auth/register/` với `username` đã tồn tại (case-insensitive), THE API SHALL trả về HTTP 400 với thông báo lỗi bằng tiếng Việt.
3. WHEN Client gửi `POST /api/auth/register/` với `phone` không phải VN_Phone hợp lệ, THE API SHALL trả về HTTP 400 với thông báo lỗi bằng tiếng Việt.
4. WHEN Client gửi `POST /api/auth/register/` với `phone` đã được dùng bởi tài khoản khác, THE API SHALL trả về HTTP 400 với thông báo lỗi bằng tiếng Việt.
5. WHEN Client gửi `POST /api/auth/register/` với `username` trùng với Admin account username (case-insensitive), THE API SHALL trả về HTTP 400.
6. THE API SHALL lưu `password` dưới dạng hash (không lưu plaintext) sử dụng Django password hashing.
7. WHEN Client (đã xác thực, role user/manager) gửi `PATCH /api/users/me/`, THE API SHALL cập nhật `displayName`, `phone`, `avatar` và trả về thông tin cập nhật.
8. WHEN Client (đã xác thực, role user/manager) gửi `POST /api/users/me/change-password/` với `currentPassword` đúng và `newPassword` ≥ 8 ký tự, THE API SHALL cập nhật mật khẩu và đặt `mustChangePassword = false`.
9. WHEN Client (đã xác thực, role user/manager) gửi `POST /api/users/me/change-password/` với `currentPassword` sai, THE API SHALL trả về HTTP 400 với thông báo lỗi bằng tiếng Việt.
10. WHEN Client (Admin) gửi `GET /api/admin/users/`, THE API SHALL trả về danh sách toàn bộ tài khoản (phân trang, mặc định 50/trang).
11. WHEN Client (Admin) gửi `PATCH /api/admin/users/{username}/`, THE API SHALL cập nhật `username`, `displayName`, `phone`, `role`, `permissions` của tài khoản chỉ định.
12. WHEN Client (Admin) gửi `POST /api/admin/users/{username}/reset-password/`, THE API SHALL đặt lại mật khẩu về `DEFAULT_RESET_PASSWORD` (đọc từ env) và đặt `mustChangePassword = true`.
13. WHEN Client (Admin) gửi `DELETE /api/admin/users/{username}/`, THE API SHALL xóa tài khoản và tất cả dữ liệu liên quan (reviews, replies, travel history, reminders).
14. THE API SHALL kiểm tra `username` hợp lệ theo pattern `^[a-zA-Z0-9._-]{3,40}$` trước khi tạo hoặc cập nhật.

---

### Yêu Cầu 4: Quản lý Địa điểm Du lịch

**User Story:** Là Admin/Manager, tôi muốn thêm, sửa, xóa địa điểm du lịch; là người dùng công cộng, tôi muốn xem danh sách và chi tiết địa điểm.

#### Tiêu chí Chấp nhận

1. WHEN Client gửi `GET /api/locations/`, THE API SHALL trả về danh sách địa điểm với phân trang (mặc định 100/trang) và hỗ trợ filter theo `category`, `group`, `subgroup`.
2. WHEN Client gửi `GET /api/locations/{id}/`, THE API SHALL trả về đầy đủ thông tin địa điểm bao gồm các trường: `id`, `name`, `category`, `group`, `subgroup`, `lat`, `lng`, `address`, `description`, `notes`, `phone`, `zaloUrl`, `website`, `email`, `facebook`, `hours`, `keywords`, `heritageStatus`, `image`, `imageAlt`, `imageSourceUrl`, `imageSourceName`, `gallery`, `panoramas`, `videos`.
3. WHEN Client gửi `GET /api/locations/{id}/` cho id không tồn tại, THE API SHALL trả về HTTP 404.
4. WHEN Client (Admin hoặc Manager có quyền) gửi `POST /api/locations/`, THE API SHALL tạo địa điểm mới với `id` tự sinh và trả về HTTP 201.
5. WHEN Client (Admin hoặc Manager) gửi `POST /api/locations/` với `name` trống, THE API SHALL trả về HTTP 400.
6. WHEN Client (Manager) gửi `POST /api/locations/` với `category` nằm ngoài `permissions.categories` và không thuộc `permissions.groups`/`permissions.subgroups`, THE API SHALL trả về HTTP 403.
7. WHEN Client (Admin hoặc Manager có quyền) gửi `PATCH /api/locations/{id}/`, THE API SHALL cập nhật các trường được gửi và trả về địa điểm đã cập nhật.
8. WHEN Client (Manager) gửi `PATCH /api/locations/{id}/` cho địa điểm ngoài phạm vi permissions, THE API SHALL trả về HTTP 403.
9. WHEN Client (Admin hoặc Manager có quyền) gửi `DELETE /api/locations/{id}/`, THE API SHALL xóa địa điểm và cascade xóa reviews, travel history, reminders liên quan.
10. THE API SHALL lưu `gallery`, `panoramas`, `videos` dưới dạng JSON array của MediaItem (`url`, `alt`, `name`).
11. WHEN Client (Admin) gửi `POST /api/admin/locations/bulk-replace/` với array địa điểm hợp lệ, THE API SHALL thay thế toàn bộ dữ liệu địa điểm.
12. WHEN Client gửi `GET /api/locations/` với query param `search=<từ khóa>`, THE API SHALL trả về các địa điểm có `name`, `keywords`, `address`, `description` khớp (case-insensitive).

---

### Yêu Cầu 5: Quản lý Đánh giá và Phản hồi

**User Story:** Là người dùng đã đăng nhập, tôi muốn đánh giá địa điểm; là Manager/Admin, tôi muốn phản hồi và kiểm duyệt đánh giá.

#### Tiêu chí Chấp nhận

1. WHEN Client (User/Manager đã xác thực) gửi `POST /api/locations/{id}/reviews/` với `rating` (1–5) và `comment`, THE API SHALL tạo hoặc cập nhật đánh giá của người dùng đó cho địa điểm (mỗi user chỉ có một review/location).
2. WHEN Client gửi `POST /api/locations/{id}/reviews/` với `rating` ngoài phạm vi 1–5, THE API SHALL trả về HTTP 400.
3. WHEN Client (User/Manager) gửi `POST /api/locations/{id}/reviews/` nhưng tài khoản không có VN_Phone hợp lệ, THE API SHALL trả về HTTP 400 với thông báo yêu cầu cập nhật số điện thoại.
4. WHEN Client gửi `GET /api/locations/{id}/reviews/`, THE API SHALL trả về danh sách reviews kèm replies của địa điểm, sắp xếp theo `updatedAt` giảm dần.
5. WHEN Client (Admin/Manager có quyền) gửi `POST /api/reviews/{reviewId}/replies/` với `comment` hợp lệ, THE API SHALL thêm reply vào review và trả về reply đã tạo.
6. WHEN Client (Admin/Manager có quyền) gửi `DELETE /api/reviews/{reviewId}/`, THE API SHALL xóa review và toàn bộ replies.
7. WHEN Client (Admin/Manager có quyền, hoặc chính tác giả reply) gửi `DELETE /api/reviews/{reviewId}/replies/{replyId}/`, THE API SHALL xóa reply chỉ định.
8. THE API SHALL giới hạn `comment` của Review tối đa 800 ký tự và `comment` của Reply tối đa 600 ký tự.

---

### Yêu Cầu 6: Quản lý Yêu thích

**User Story:** Là người dùng đã đăng nhập, tôi muốn đánh dấu/bỏ đánh dấu địa điểm yêu thích và xem lại danh sách đó.

#### Tiêu chí Chấp nhận

1. WHEN Client (đã xác thực) gửi `GET /api/users/me/favorites/`, THE API SHALL trả về danh sách `locationId` yêu thích của người dùng hiện tại.
2. WHEN Client (đã xác thực) gửi `POST /api/users/me/favorites/{locationId}/`, THE API SHALL thêm địa điểm vào danh sách yêu thích nếu chưa có.
3. WHEN Client (đã xác thực) gửi `POST /api/users/me/favorites/{locationId}/` với `locationId` đã trong danh sách, THE API SHALL giữ nguyên (idempotent) và trả về HTTP 200.
4. WHEN Client (đã xác thực) gửi `DELETE /api/users/me/favorites/{locationId}/`, THE API SHALL xóa địa điểm khỏi danh sách yêu thích.
5. WHEN Client (đã xác thực) gửi `DELETE /api/users/me/favorites/{locationId}/` với `locationId` không trong danh sách, THE API SHALL trả về HTTP 200 (idempotent).

---

### Yêu Cầu 7: Lịch sử Di chuyển

**User Story:** Là người dùng đã đăng nhập, tôi muốn hệ thống ghi lại lịch sử xem, dẫn đường, và đã đến địa điểm của tôi.

#### Tiêu chí Chấp nhận

1. WHEN Client (User/Manager đã xác thực) gửi `POST /api/users/me/travel-history/` với `locationId` và `action` (view/route/visited), THE API SHALL tạo hoặc cập nhật bản ghi lịch sử tương ứng.
2. WHEN `action` là `view`, THE API SHALL tăng `viewCount` thêm 1 và cập nhật `lastActivityAt`.
3. WHEN `action` là `route`, THE API SHALL tăng `routeCount` thêm 1 và cập nhật `lastActivityAt`.
4. WHEN `action` là `visited`, THE API SHALL đặt `visitedAt` là thời điểm hiện tại (nếu chưa có) và cập nhật `lastActivityAt`.
5. WHEN Client (đã xác thực) gửi `GET /api/users/me/travel-history/`, THE API SHALL trả về danh sách lịch sử của người dùng hiện tại.
6. WHEN Client (đã xác thực) gửi `DELETE /api/users/me/travel-history/{id}/`, THE API SHALL xóa bản ghi chỉ định nếu thuộc về người dùng hiện tại.
7. IF Client gửi `DELETE /api/users/me/travel-history/{id}/` cho bản ghi không thuộc về người dùng hiện tại, THEN THE API SHALL trả về HTTP 404.

---

### Yêu Cầu 8: Lịch nhắc Du lịch

**User Story:** Là người dùng đã đăng nhập, tôi muốn tạo lịch nhắc đến địa điểm vào thời điểm cụ thể và quản lý chúng.

#### Tiêu chí Chấp nhận

1. WHEN Client (User/Manager đã xác thực) gửi `POST /api/users/me/reminders/` với `locationId`, `scheduledAt` (ISO 8601), `note` tùy chọn (≤ 300 ký tự), THE API SHALL tạo lịch nhắc mới và trả về HTTP 201.
2. WHEN Client gửi `POST /api/users/me/reminders/` với `scheduledAt` không phải ISO 8601 hợp lệ, THE API SHALL trả về HTTP 400.
3. WHEN Client gửi `GET /api/users/me/reminders/`, THE API SHALL trả về danh sách lịch nhắc của người dùng hiện tại.
4. WHEN Client (đã xác thực) gửi `DELETE /api/users/me/reminders/{id}/`, THE API SHALL xóa lịch nhắc nếu thuộc về người dùng hiện tại.
5. WHEN Client (đã xác thực) gửi `POST /api/users/me/reminders/{id}/complete/`, THE API SHALL đặt `completedAt` là thời điểm hiện tại.
6. WHEN Client (đã xác thực) gửi `POST /api/users/me/reminders/{id}/notify/`, THE API SHALL đặt `notifiedAt` là thời điểm hiện tại.
7. IF Client gửi request thao tác trên lịch nhắc không thuộc về người dùng hiện tại, THEN THE API SHALL trả về HTTP 404.

---

### Yêu Cầu 9: Thống kê và Sự kiện Analytics

**User Story:** Là Admin, tôi muốn xem báo cáo thống kê hành vi người dùng; là hệ thống, tôi cần ghi nhận các sự kiện hành vi.

#### Tiêu chí Chấp nhận

1. WHEN Client gửi `POST /api/analytics/events/` với `type`, `visitorId`, `sessionId` và các trường payload tùy chọn, THE API SHALL ghi nhận sự kiện và trả về HTTP 201.
2. THE API SHALL chấp nhận các `type` sự kiện: `page_view`, `location_view`, `route_start`, `login`, `logout`, `register`, `review_submit`, `review_reply`, `reminder_create`, `profile_update`, `password_change`, `admin_location_create`, `admin_location_update`, `admin_location_delete`, `admin_user_update`, `admin_user_password_reset`.
3. WHEN Client (Admin) gửi `GET /api/admin/analytics/`, THE API SHALL trả về tổng hợp số lượng event theo `type` và theo ngày (30 ngày gần nhất).
4. WHEN Client (Admin) gửi `DELETE /api/admin/analytics/`, THE API SHALL xóa toàn bộ sự kiện analytics và trả về HTTP 200.
5. THE API SHALL lưu trường `account`, `role`, `path`, `locationId`, `category` kèm theo mỗi sự kiện.
6. THE API SHALL lưu trường `createdAt` tự động theo thời điểm nhận request.

---

### Yêu Cầu 10: Cấu hình Trang web (SiteSettings)

**User Story:** Là Admin, tôi muốn cấu hình slideshow trang chủ và các thông số giao diện, để có thể thay đổi nội dung hiển thị mà không cần deploy lại frontend.

#### Tiêu chí Chấp nhận

1. WHEN Client gửi `GET /api/settings/`, THE API SHALL trả về cấu hình trang web hiện tại bao gồm `heroSlides` (array) và `heroIntervalMs` (số nguyên dương).
2. WHEN Client (Admin) gửi `PATCH /api/admin/settings/` với dữ liệu hợp lệ, THE API SHALL cập nhật cấu hình và trả về cấu hình đã cập nhật.
3. WHEN Client (Admin) gửi `POST /api/admin/settings/reset/`, THE API SHALL khôi phục cấu hình về giá trị mặc định.
4. THE API SHALL lưu SiteSettings dưới dạng singleton record trong database (chỉ có một row).
5. IF `heroSlides` được cập nhật với phần tử thiếu trường `id` hoặc `image`, THEN THE API SHALL trả về HTTP 400.
6. IF `heroIntervalMs` được cập nhật với giá trị nhỏ hơn 1000, THEN THE API SHALL trả về HTTP 400.

---

### Yêu Cầu 11: Thông báo Đánh giá mới (Review Notifications)

**User Story:** Là Admin/Manager, tôi muốn được thông báo khi có đánh giá mới để kiểm duyệt kịp thời.

#### Tiêu chí Chấp nhận

1. WHEN Client (Admin/Manager đã xác thực) gửi `GET /api/notifications/reviews/`, THE API SHALL trả về danh sách reviews chưa được đọc trong phạm vi quyền của người dùng, sắp xếp theo `updatedAt` giảm dần.
2. WHEN Client (Admin/Manager) gửi `POST /api/notifications/reviews/mark-read/` với danh sách `ids`, THE API SHALL đánh dấu các notification tương ứng là đã đọc.
3. WHEN Client (Manager) gọi `GET /api/notifications/reviews/`, THE API SHALL chỉ trả về notifications của các địa điểm thuộc phạm vi `permissions` của Manager đó.
4. THE API SHALL trả về trường `unreadCount` trong response của `GET /api/notifications/reviews/`.

---

### Yêu Cầu 12: Xử lý Lỗi và Định dạng Response

**User Story:** Là developer frontend, tôi muốn API trả về response nhất quán và thông báo lỗi rõ ràng bằng tiếng Việt, để dễ dàng xử lý ở phía Client.

#### Tiêu chí Chấp nhận

1. THE API SHALL trả về toàn bộ response dưới định dạng JSON.
2. WHEN xử lý thành công, THE API SHALL trả về HTTP 200 (GET/PATCH/DELETE) hoặc HTTP 201 (POST tạo mới) kèm data.
3. WHEN xảy ra lỗi validation, THE API SHALL trả về HTTP 400 với object `{ "error": "<thông báo lỗi tiếng Việt>", "field": "<tên field lỗi nếu có>" }`.
4. WHEN xảy ra lỗi xác thực (unauthenticated), THE API SHALL trả về HTTP 401 với `{ "error": "Phiên đăng nhập hết hạn. Hãy đăng nhập lại." }`.
5. WHEN xảy ra lỗi phân quyền, THE API SHALL trả về HTTP 403 với `{ "error": "Bạn không có quyền thực hiện thao tác này." }`.
6. WHEN resource không tồn tại, THE API SHALL trả về HTTP 404 với `{ "error": "Không tìm thấy dữ liệu." }`.
7. WHEN xảy ra lỗi server nội bộ, THE API SHALL trả về HTTP 500 với `{ "error": "Lỗi máy chủ. Vui lòng thử lại sau." }` và log chi tiết lỗi ra server log.
8. THE API SHALL bao gồm header `Content-Type: application/json` trong mọi response.
