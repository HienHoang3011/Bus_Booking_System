# ReHearten API Testing Guide - Postman

Hướng dẫn chi tiết để test toàn bộ API của hệ thống quản lý đặt vé xe ReHearten sử dụng Postman.

## 📌 Thông tin cơ bản

### Base URL
```
http://localhost:8000
```

### Thông tin tài khoản test
```
Username: thaoLinh
Password: Hieudevdut277*
```

### Lưu ý quan trọng
- **KHÔNG tạo dữ liệu mẫu trực tiếp** - Tất cả dữ liệu phải được tạo thông qua API
- Thứ tự test API phải tuân thủ theo workflow: Locations → Routes → Buses → Seats → Trips → Bookings
- Đọc kỹ serializer và view của mỗi app để hiểu rõ request format
- Booking cần có Trip, Trip cần có Route và Bus, Route cần có Locations

---

## 🔐 1. AUTHENTICATION & USER MANAGEMENT

### 1.1 Đăng ký tài khoản (Register)

**Endpoint:** `POST /register/`

**Content-Type:** `application/x-www-form-urlencoded` (form submission)

**Request Body:**
```
username=thaoLinh
email=thaolinhtest@example.com
first_name=Linh
last_name=Thao
password1=Hieudevdut277*
password2=Hieudevdut277*
```

**Validation Rules (xem `accounts/forms.py:70-121`):**
- Username: ít nhất 3 ký tự, chỉ chữ, số và dấu gạch dưới
- Email: phải unique
- Password phải có:
  - Ít nhất 8 ký tự
  - Ít nhất 1 chữ cái viết hoa
  - Ít nhất 1 chữ cái viết thường
  - Ít nhất 1 chữ số
  - Ít nhất 1 ký tự đặc biệt (!@#$%^&*()_+{}[]:;<>,.?~\\/-)
- password1 và password2 phải giống nhau

**Response Success:**
- Redirect đến `/login/` với message thành công

---

### 1.2 Đăng nhập (Login)

**Endpoint:** `POST /login/`

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
username=thaoLinh
password=Hieudevdut277*
```

**Response Success:**
- Sets cookies: `sessionid`, `csrftoken`
- Redirect dựa trên role:
  - Admin → `/admin-dashboard/`
  - User → `/dashboard/`

**Lưu cookies để dùng cho các request sau:**
1. Trong Postman, sau khi login thành công, vào tab "Cookies"
2. Copy giá trị `sessionid` và `csrftoken`
3. Dùng cho các request cần authentication

---

### 1.3 Đăng xuất (Logout)

**Endpoint:** `GET /logout/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

---

### 1.4 Lấy thông tin profile

**Endpoint:** `GET /api/get-profile/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

**Response Example:**
```json
{
    "id": 1,
    "username": "thaoLinh",
    "email": "thaolinhtest@example.com",
    "first_name": "Linh",
    "last_name": "Thao",
    "role": "user",
    "is_active": true,
    "date_joined": "2025-01-15T10:30:00Z"
}
```

---

### 1.5 Cập nhật profile

**Endpoint:** `PATCH /api/profile/`

**Headers:**
```
Content-Type: application/json
X-CSRFToken: {{csrf_token}}
Cookie: sessionid={{session_id}}
```

**Request Body:**
```json
{
    "first_name": "Linh Updated",
    "last_name": "Thao Updated",
    "email": "newemail@example.com"
}
```

---

### 1.6 Đổi mật khẩu

**Endpoint:** `POST /api/change-password/`

**Headers:**
```
Content-Type: application/json
X-CSRFToken: {{csrf_token}}
Cookie: sessionid={{session_id}}
```

**Request Body:**
```json
{
    "current_password": "Hieudevdut277*",
    "new_password1": "NewPassword123!",
    "new_password2": "NewPassword123!"
}
```

**Validation (xem `accounts/forms.py:362-411`):**
- `current_password` phải đúng
- `new_password1` phải đáp ứng yêu cầu password mạnh
- `new_password1` phải khác `current_password`
- `new_password2` phải match `new_password1`

---

## 👥 2. USER MANAGEMENT APIs (Admin Only)

### 2.1 Danh sách tất cả users

**Endpoint:** `GET /api/users/`

**Headers:**
```
Cookie: sessionid={{admin_session_id}}
```

**Response Example:**
```json
[
    {
        "id": 1,
        "username": "thaoLinh",
        "email": "thaolinhtest@example.com",
        "first_name": "Linh",
        "last_name": "Thao",
        "role": "user",
        "is_active": true,
        "date_joined": "2025-01-15T10:30:00Z"
    }
]
```

---

### 2.2 Thay đổi role của user

**Endpoint:** `POST /api/change-user-role/`

**Headers:**
```
Content-Type: application/json
X-CSRFToken: {{csrf_token}}
Cookie: sessionid={{admin_session_id}}
```

**Request Body:**
```json
{
    "username": "thaoLinh",
    "role": "admin"
}
```

**Valid roles:** `admin`, `user`

**Validation (xem `accounts/views.py:226-293`):**
- Admin không thể thay đổi role của chính mình
- Role phải là một trong các giá trị hợp lệ

---

### 2.3 Toggle trạng thái active của user

**Endpoint:** `POST /api/toggle-user-status/`

**Headers:**
```
Content-Type: application/json
X-CSRFToken: {{csrf_token}}
Cookie: sessionid={{admin_session_id}}
```

**Request Body:**
```json
{
    "username": "thaoLinh"
}
```

---

## 🚍 3. TRANSPORT APIs - LOCATIONS

### 3.1 Tạo Location

**Endpoint:** `POST /api/locations/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body (theo `transport/serializers.py:5-11`):**
```json
{
    "name": "Bến xe Mỹ Đình",
    "city": "Hà Nội"
}
```

**Response Example:**
```json
{
    "id": 1,
    "name": "Bến xe Mỹ Đình",
    "city": "Hà Nội",
    "full_address": "Bến xe Mỹ Đình, Hà Nội"
}
```

**Lưu ý:** Tạo ít nhất 2 locations để làm điểm đầu và điểm cuối cho Route

---

### 3.2 Danh sách Locations

**Endpoint:** `GET /api/locations/`

**Query Parameters:**
- `?search=Hà Nội` - Tìm kiếm theo name hoặc city

**Response Example:**
```json
[
    {
        "id": 1,
        "name": "Bến xe Mỹ Đình",
        "city": "Hà Nội",
        "full_address": "Bến xe Mỹ Đình, Hà Nội"
    },
    {
        "id": 2,
        "name": "Bến xe Miền Đông",
        "city": "TP. Hồ Chí Minh",
        "full_address": "Bến xe Miền Đông, TP. Hồ Chí Minh"
    }
]
```

---

### 3.3 Chi tiết Location

**Endpoint:** `GET /api/locations/{id}/`

**Example:** `GET /api/locations/1/`

---

### 3.4 Cập nhật Location

**Endpoint:** `PUT /api/locations/{id}/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body:**
```json
{
    "name": "Bến xe Mỹ Đình Mới",
    "city": "Hà Nội"
}
```

---

### 3.5 Xóa Location

**Endpoint:** `DELETE /api/locations/{id}/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

---

## 🛣️ 4. TRANSPORT APIs - ROUTES

### 4.1 Tạo Route

**Endpoint:** `POST /api/routes/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body (theo `transport/serializers.py:14-22`):**
```json
{
    "start_location": 1,
    "end_location": 2,
    "distance_km": 1700.5
}
```

**Validation:**
- `start_location` và `end_location` phải tồn tại (Location IDs)
- Unique constraint: không được trùng cặp (start_location, end_location)

**Response Example:**
```json
{
    "id": 1,
    "start_location": 1,
    "start_location_name": "Bến xe Mỹ Đình",
    "end_location": 2,
    "end_location_name": "Bến xe Miền Đông",
    "distance_km": 1700.5,
    "route_info": "Bến xe Mỹ Đình → Bến xe Miền Đông (1700.5 km)"
}
```

---

### 4.2 Danh sách Routes

**Endpoint:** `GET /api/routes/`

**Query Parameters:**
- `?start_location=1` - Filter theo điểm đầu
- `?end_location=2` - Filter theo điểm cuối
- `?ordering=distance_km` - Sắp xếp theo khoảng cách

---

### 4.3 Chi tiết Route

**Endpoint:** `GET /api/routes/{id}/`

---

### 4.4 Cập nhật Route

**Endpoint:** `PUT /api/routes/{id}/`

**Request Body:**
```json
{
    "start_location": 1,
    "end_location": 2,
    "distance_km": 1705.0
}
```

---

### 4.5 Xóa Route

**Endpoint:** `DELETE /api/routes/{id}/`

---

## 🚌 5. TRANSPORT APIs - BUSES

### 5.1 Tạo Bus

**Endpoint:** `POST /api/buses/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body (theo `transport/serializers.py:25-30`):**
```json
{
    "license_plate": "29A-12345",
    "model": "Hyundai Universe",
    "total_seats": 45,
    "manufacture_year": 2023
}
```

**Validation:**
- `license_plate` phải unique

**Response Example:**
```json
{
    "id": 1,
    "license_plate": "29A-12345",
    "model": "Hyundai Universe",
    "total_seats": 45,
    "manufacture_year": 2023
}
```

**✅ TỰ ĐỘNG TẠO SEATS:**
- **Seats được TỰ ĐỘNG TẠO** khi tạo Bus mới
- Hệ thống tự động tạo đủ số ghế theo `total_seats`
- **Quy tắc đặt tên ghế:** A01, A02, ..., A10, B01, B02, ..., B10, C01, ...
  - Mỗi hàng (row) có tối đa 10 ghế
  - Hàng A: ghế 1-10 (A01-A10)
  - Hàng B: ghế 11-20 (B01-B10)
  - Hàng C: ghế 21-30 (C01-C10), v.v.
- Ví dụ: Bus 45 ghế → Tự động tạo A01-A10, B01-B10, C01-C10, D01-D10, E01-E05
- Tất cả ghế mặc định `is_available = true`

**Ví dụ kết quả:**
```http
POST /api/buses/
{"license_plate": "29A-12345", "model": "Hyundai", "total_seats": 15, "manufacture_year": 2023}

# Hệ thống tự động tạo 15 seats:
# A01, A02, A03, A04, A05, A06, A07, A08, A09, A10
# B01, B02, B03, B04, B05
```

---

### 5.2 Danh sách Buses

**Endpoint:** `GET /api/buses/`

**Query Parameters:**
- `?search=29A` - Tìm kiếm theo license_plate hoặc model
- `?ordering=manufacture_year` - Sắp xếp

---

### 5.3 Chi tiết Bus

**Endpoint:** `GET /api/buses/{id}/`

---

### 5.4 Cập nhật Bus

**Endpoint:** `PUT /api/buses/{id}/`

---

### 5.5 Xóa Bus

**Endpoint:** `DELETE /api/buses/{id}/`

---

## 💺 6. TRANSPORT APIs - SEATS

**✅ TỰ ĐỘNG TẠO SEATS:**
- Khi bạn tạo Bus, hệ thống **TỰ ĐỘNG** tạo tất cả seats theo `total_seats`
- Seats được đặt tên theo quy tắc: A01-A10, B01-B10, C01-C10, ...
- Bạn **KHÔNG CẦN** tạo seats thủ công nữa
- API tạo seat vẫn có sẵn cho trường hợp cần thêm ghế đặc biệt

### 6.1 Tạo Seat thủ công (Tùy chọn - nếu cần thêm ghế)

**Endpoint:** `POST /api/seats/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body (theo `transport/serializers.py:105-119`):**
```json
{
    "bus": 1,
    "seat_number": "VIP01",
    "is_available": true
}
```

**Validation:**
- `bus` phải tồn tại (Bus ID)
- Unique constraint: không được trùng cặp (bus, seat_number)
- `seat_number` phải unique trong cùng một bus

**Response Example:**
```json
{
    "id": 46,
    "seat_number": "VIP01",
    "bus": 1,
    "bus_license_plate": "29A-12345",
    "is_available": true
}
```

**💡 Khi nào cần tạo seat thủ công?**
- Thêm ghế VIP đặc biệt
- Thêm ghế nằm (sleeper)
- Ghế có tên đặc biệt khác với quy tắc A01-Z99

**Ví dụ: Thêm ghế VIP sau khi Bus đã tạo xong:**
```http
# Bus đã tự động tạo A01-E05 (45 ghế)
# Giờ thêm 2 ghế VIP:

POST /api/seats/
{"bus": 1, "seat_number": "VIP01", "is_available": true}

POST /api/seats/
{"bus": 1, "seat_number": "VIP02", "is_available": true}
```

**⚠️ Lưu ý:**
- Seats thông thường đã được tạo tự động khi tạo Bus
- Chỉ cần API này nếu muốn thêm ghế đặc biệt

---

### 6.2 Danh sách Seats

**Endpoint:** `GET /api/seats/`

**Query Parameters:**
- `?bus=1` - Filter theo bus
- `?is_available=true` - Filter theo trạng thái
- `?ordering=seat_number` - Sắp xếp

---

### 6.3 Chi tiết Seat

**Endpoint:** `GET /api/seats/{id}/`

---

### 6.4 Cập nhật Seat

**Endpoint:** `PUT /api/seats/{id}/`

---

### 6.5 Xóa Seat

**Endpoint:** `DELETE /api/seats/{id}/`

---

## 🚏 7. TRANSPORT APIs - TRIPS

### 7.1 Tạo Trip

**Endpoint:** `POST /api/trips/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body (theo `transport/serializers.py:42-56`):**
```json
{
    "route": 1,
    "bus": 1,
    "departure_time": "2025-12-11T08:00:00Z",
    "arrival_time": "2025-12-12T08:00:00Z",
    "price_per_seat": 350000
}
```

**Validation:**
- `route` phải tồn tại (Route ID)
- `bus` phải tồn tại (Bus ID)
- `departure_time` phải trước `arrival_time`
- Để trip là "upcoming", `departure_time` phải > hiện tại

**Response Example:**
```json
{
    "id": 1,
    "route": 1,
    "route_info": "Bến xe Mỹ Đình → Bến xe Miền Đông (1700.5 km)",
    "bus": 1,
    "bus_license_plate": "29A-12345",
    "departure_time": "2025-12-11T08:00:00Z",
    "arrival_time": "2025-12-12T08:00:00Z",
    "price_per_seat": 350000,
    "duration": "24 hours",
    "available_seats_count": 45,
    "is_upcoming": true
}
```

---

### 7.2 Danh sách Trips

**Endpoint:** `GET /api/trips/`

**Query Parameters:**
- `?route=1` - Filter theo route
- `?bus=1` - Filter theo bus
- `?ordering=departure_time` - Sắp xếp

---

### 7.3 Danh sách Upcoming Trips

**Endpoint:** `GET /api/trips/upcoming/`

**Chỉ trả về các trip có `departure_time` > hiện tại**

---

### 7.4 Kiểm tra số ghế còn trống

**Endpoint:** `GET /api/trips/{id}/available_seats/`

**Example:** `GET /api/trips/1/available_seats/`

**Response Example:**
```json
{
    "trip_id": 1,
    "total_seats": 45,
    "available_seats": 42,
    "booked_seats": 3
}
```

**Logic tính toán (xem `transport/models.py:115-118`):**
```python
available_seats = bus.total_seats - sum(booking.number_of_seats)
```

---

### 7.5 Chi tiết Trip

**Endpoint:** `GET /api/trips/{id}/`

---

### 7.6 Cập nhật Trip

**Endpoint:** `PUT /api/trips/{id}/`

---

### 7.7 Xóa Trip

**Endpoint:** `DELETE /api/trips/{id}/`

---

## 🎫 8. BOOKING APIs

### 8.1 Tạo Booking với Tickets

**Endpoint:** `POST /api/bookings/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body (theo `bookings/serializers.py:94-105`):**
```json
{
    "trip_id": 1,
    "number_of_seats": 2,
    "tickets": [
        {
            "seat_id": 1,
            "passenger_name": "Nguyễn Văn A"
        },
        {
            "seat_id": 2,
            "passenger_name": "Trần Thị B"
        }
    ]
}
```

**Validation (xem `bookings/serializers.py:106-153`):**
1. Trip phải tồn tại và là upcoming trip
2. Trip phải có đủ ghế trống (`available_seats >= number_of_seats`)
3. Số lượng tickets phải bằng `number_of_seats`
4. Không được trùng `seat_id` trong cùng 1 booking
5. Các seat phải thuộc bus của trip đó
6. Seat không được đã book cho trip này (unique constraint: trip + seat)

**Response Example:**
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user": 1,
    "user_name": "Thao Linh",
    "trip_id": 1,
    "trip_details": {
        "id": 1,
        "departure_location": "Bến xe Mỹ Đình",
        "arrival_location": "Bến xe Miền Đông",
        "departure_time": "2025-02-01T08:00:00Z",
        "arrival_time": "2025-02-02T08:00:00Z",
        "price_per_seat": 350000,
        "route_info": "Bến xe Mỹ Đình → Bến xe Miền Đông (1700.5 km)",
        "available_seats": 43,
        "duration": "24 hours"
    },
    "number_of_seats": 2,
    "total_amount": 700000,
    "booking_time": "2025-01-15T14:30:00Z",
    "status": "Pending",
    "status_display": "Đang chờ",
    "tickets": [
        {
            "id": 1,
            "seat_number": "A01",
            "price": 350000,
            "passenger_name": "Nguyễn Văn A"
        },
        {
            "id": 2,
            "seat_number": "A02",
            "price": 350000,
            "passenger_name": "Trần Thị B"
        }
    ]
}
```

**Lưu ý:**
- `total_amount` tự động tính: `number_of_seats × trip.price_per_seat`
- Tickets tự động được tạo với price từ trip
- Booking ID sử dụng UUID format

---

### 8.2 Danh sách Bookings

**Endpoint:** `GET /api/bookings/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

**Query Parameters:**
- `?status=Pending` - Filter theo status (Pending/Confirmed/Canceled)
- `?trip_id=1` - Filter theo trip

**Authorization:**
- User thường: chỉ thấy booking của mình
- Admin: thấy tất cả bookings

**Response Example:**
```json
[
    {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "user_name": "Thao Linh",
        "trip_info": "Bến xe Mỹ Đình → Bến xe Miền Đông",
        "number_of_seats": 2,
        "total_amount": 700000,
        "booking_time": "2025-01-15T14:30:00Z",
        "status": "Pending",
        "status_display": "Đang chờ"
    }
]
```

---

### 8.3 Chi tiết Booking

**Endpoint:** `GET /api/bookings/{booking_id}/`

**Example:** `GET /api/bookings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/`

**Response:** Full booking details với trip_details và tickets

---

### 8.4 Cập nhật Booking

**Endpoint:** `PUT /api/bookings/{id}/`

**Headers:**
```
Content-Type: application/json
Cookie: sessionid={{session_id}}
```

**Request Body:**
```json
{
    "number_of_seats": 3
}
```

**Validation (xem `bookings/views.py:73-90`):**
- Chỉ booking có status "Pending" mới được update
- Chỉ update được `number_of_seats`

---

### 8.5 Xác nhận Booking (Admin Only)

**Endpoint:** `POST /api/bookings/{id}/confirm/`

**Headers:**
```
Cookie: sessionid={{admin_session_id}}
```

**Validation (xem `bookings/views.py:108-127`):**
- Chỉ admin mới được confirm
- Booking phải có status "Pending"

**Response:**
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "Confirmed",
    "status_display": "Đã xác nhận",
    ...
}
```

---

### 8.6 Hủy Booking

**Endpoint:** `POST /api/bookings/{id}/cancel/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

**Validation:**
- Booking không được có status "Canceled"

**Response:**
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "Canceled",
    "status_display": "Đã hủy",
    ...
}
```

---

### 8.7 Xóa Booking (thực chất là Cancel)

**Endpoint:** `DELETE /api/bookings/{id}/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

**Lưu ý:** DELETE không xóa booking mà chỉ chuyển status thành "Canceled"

---

### 8.8 Lấy bookings của user hiện tại

**Endpoint:** `GET /api/bookings/my-bookings/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

---

### 8.9 Thống kê Bookings (Admin Only)

**Endpoint:** `GET /api/bookings/statistics/`

**Headers:**
```
Cookie: sessionid={{admin_session_id}}
```

**Response Example:**
```json
{
    "total_bookings": 150,
    "pending_bookings": 25,
    "confirmed_bookings": 100,
    "canceled_bookings": 25
}
```

---

### 8.10 Lấy danh sách Tickets của một Booking

**Endpoint:** `GET /api/bookings/{id}/tickets/`

**Example:** `GET /api/bookings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/tickets/`

**Response Example:**
```json
[
    {
        "id": 1,
        "seat_number": "A01",
        "price": 350000,
        "passenger_name": "Nguyễn Văn A"
    },
    {
        "id": 2,
        "seat_number": "A02",
        "price": 350000,
        "passenger_name": "Trần Thị B"
    }
]
```

---

## 🎟️ 9. TICKET APIs (Read-Only)

### 9.1 Danh sách Tickets

**Endpoint:** `GET /api/tickets/`

**Headers:**
```
Cookie: sessionid={{session_id}}
```

**Authorization:**
- User thường: chỉ thấy tickets từ bookings của mình
- Admin: thấy tất cả tickets

**Response Example:**
```json
[
    {
        "id": 1,
        "seat_number": "A01",
        "price": 350000,
        "passenger_name": "Nguyễn Văn A"
    }
]
```

**Lưu ý:** Tickets được tạo tự động khi tạo Booking, không có API tạo ticket riêng

---

### 9.2 Chi tiết Ticket

**Endpoint:** `GET /api/tickets/{id}/`

---

## 📋 10. WORKFLOW TEST ĐẦY ĐỦ

### Scenario 1: User đặt vé xe

**Bước 1: Đăng ký tài khoản**
```http
POST /register/
Content-Type: application/x-www-form-urlencoded

username=thaoLinh&email=thaolinhtest@example.com&first_name=Linh&last_name=Thao&password1=Hieudevdut277*&password2=Hieudevdut277*
```

**Bước 2: Đăng nhập**
```http
POST /login/
Content-Type: application/x-www-form-urlencoded

username=thaoLinh&password=Hieudevdut277*
```

**Bước 3: Tạo Locations (2 địa điểm)**
```http
POST /api/locations/
Content-Type: application/json

{"name": "Bến xe Mỹ Đình", "city": "Hà Nội"}
```

```http
POST /api/locations/
Content-Type: application/json

{"name": "Bến xe Miền Đông", "city": "TP. Hồ Chí Minh"}
```

**Bước 4: Tạo Route**
```http
POST /api/routes/
Content-Type: application/json

{
    "start_location": 1,
    "end_location": 2,
    "distance_km": 1700.5
}
```

**Bước 5: Tạo Bus**
```http
POST /api/buses/
Content-Type: application/json

{
    "license_plate": "29A-12345",
    "model": "Hyundai Universe",
    "total_seats": 45,
    "manufacture_year": 2023
}
```

**Bước 6: Kiểm tra Seats đã tự động tạo (✅ TỰ ĐỘNG)**
```http
# Seats đã được TỰ ĐỘNG TẠO khi tạo Bus ở Bước 5!
# Kiểm tra danh sách seats của bus:

GET /api/seats/?bus=1

# Response sẽ trả về 45 seats tự động:
# [
#   {"id": 1, "seat_number": "A01", "bus": 1, ...},
#   {"id": 2, "seat_number": "A02", "bus": 1, ...},
#   ...
#   {"id": 45, "seat_number": "E05", "bus": 1, ...}
# ]
```

**Pattern ghế tự động:**
- Bus 45 ghế → A01-A10, B01-B10, C01-C10, D01-D10, E01-E05
- Bus 15 ghế → A01-A10, B01-B05
- Bus 30 ghế → A01-A10, B01-B10, C01-C10

**Bước 7: Tạo Trip (upcoming)**
```http
POST /api/trips/
Content-Type: application/json

{
    "route": 1,
    "bus": 1,
    "departure_time": "2025-02-01T08:00:00Z",
    "arrival_time": "2025-02-02T08:00:00Z",
    "price_per_seat": 350000
}
```

**Bước 8: Kiểm tra ghế trống**
```http
GET /api/trips/1/available_seats/
```

**Bước 9: Tạo Booking**
```http
POST /api/bookings/
Content-Type: application/json

{
    "trip_id": 1,
    "number_of_seats": 2,
    "tickets": [
        {
            "seat_id": 1,
            "passenger_name": "Nguyễn Văn A"
        },
        {
            "seat_id": 2,
            "passenger_name": "Trần Thị B"
        }
    ]
}
```

**Bước 10: Xem bookings của mình**
```http
GET /api/bookings/my-bookings/
```

**Bước 11: Xem chi tiết booking**
```http
GET /api/bookings/{booking_id}/
```

**Bước 12: Xem tickets**
```http
GET /api/bookings/{booking_id}/tickets/
```

---

### Scenario 2: Admin quản lý hệ thống

**Bước 1: Login với admin account**
```http
POST /login/
username=admin&password=adminpass
```

**Bước 2: Xem tất cả users**
```http
GET /api/users/
```

**Bước 3: Thay đổi role user thành admin**
```http
POST /api/change-user-role/
{"username": "thaoLinh", "role": "admin"}
```

**Bước 4: Xem tất cả bookings**
```http
GET /api/bookings/
```

**Bước 5: Xác nhận booking**
```http
POST /api/bookings/{booking_id}/confirm/
```

**Bước 6: Xem thống kê**
```http
GET /api/bookings/statistics/
```

---

### Scenario 3: User hủy booking

**Bước 1: Xem bookings của mình**
```http
GET /api/bookings/my-bookings/
```

**Bước 2: Hủy booking**
```http
POST /api/bookings/{booking_id}/cancel/
```

**Bước 3: Verify status đã chuyển thành Canceled**
```http
GET /api/bookings/{booking_id}/
```

---

## 🛠️ 11. POSTMAN ENVIRONMENT SETUP

### Tạo Environment variables

```json
{
    "base_url": "http://localhost:8000",
    "csrf_token": "",
    "session_id": "",
    "location_id_1": "",
    "location_id_2": "",
    "route_id": "",
    "bus_id": "",
    "seat_id_1": "",
    "seat_id_2": "",
    "trip_id": "",
    "booking_id": ""
}
```

### Auto-extract tokens và IDs

**Thêm vào Tests tab của login request:**
```javascript
// Extract CSRF token
var csrfToken = pm.cookies.get('csrftoken');
pm.environment.set('csrf_token', csrfToken);

// Extract session ID
var sessionId = pm.cookies.get('sessionid');
pm.environment.set('session_id', sessionId);
```

**Thêm vào Tests tab của create location request:**
```javascript
var jsonData = pm.response.json();
pm.environment.set('location_id_1', jsonData.id);
```

**Tương tự cho các resource khác:**
```javascript
// Create Route response
pm.environment.set('route_id', jsonData.id);

// Create Bus response
pm.environment.set('bus_id', jsonData.id);

// Create Seat response
pm.environment.set('seat_id_1', jsonData.id);

// Create Trip response
pm.environment.set('trip_id', jsonData.id);

// Create Booking response
pm.environment.set('booking_id', jsonData.id);
```

---

## ⚠️ 12. LƯU Ý QUAN TRỌNG

### Authentication trong Development Mode

**Theo `CLAUDE.md` và code `bookings/views.py:41-43, 134-139, 214-215`:**
- Authentication hiện đang **partially disabled** để test
- Anonymous users có thể access bookings/tickets APIs
- **PHẢI enable full authentication trước khi deploy production**

### Unique Constraints

**Ticket (xem `bookings/models.py`):**
- Unique constraint: (trip, seat)
- Không thể book cùng 1 ghế 2 lần cho cùng 1 trip

**Seat (xem `transport/models.py`):**
- Unique constraint: (bus, seat_number)
- Mỗi bus không thể có 2 ghế cùng số

**Route (xem `transport/models.py`):**
- Unique constraint: (start_location, end_location)
- Không thể có 2 route giống nhau

### UUID Primary Keys

**Booking và Payment sử dụng UUID:**
- Format: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- Phải sử dụng UUID string đầy đủ trong request

### Datetime Format

**Tất cả datetime phải theo ISO 8601:**
```
2025-02-01T08:00:00Z
```

### Request Content-Type

**Form submission (login, register):**
```
Content-Type: application/x-www-form-urlencoded
```

**API JSON requests:**
```
Content-Type: application/json
```

---

## 🐛 13. TROUBLESHOOTING

### CSRF Token Error

**Triệu chứng:** `403 Forbidden - CSRF verification failed`

**Giải pháp:**
1. Đảm bảo đã include header: `X-CSRFToken: {{csrf_token}}`
2. Kiểm tra cookie `csrftoken` còn hợp lệ
3. Login lại để lấy token mới

### Session Expired

**Triệu chứng:** `401 Unauthorized`

**Giải pháp:**
1. Login lại
2. Update `session_id` trong environment

### Validation Error

**Triệu chứng:** `400 Bad Request` với error messages

**Giải pháp:**
1. Đọc kỹ error message
2. Kiểm tra serializer validation rules
3. Đảm bảo data format đúng

### Trip không upcoming

**Triệu chứng:** Không thể tạo booking - "Cannot book a trip that has already departed"

**Giải pháp:**
1. Tạo trip mới với `departure_time` > hiện tại
2. Sử dụng datetime trong tương lai (ví dụ: 2025-02-01)

### Ghế đã được book

**Triệu chứng:** "Seat X is already booked for this trip"

**Giải pháp:**
1. Chọn seat_id khác chưa được book
2. Check available seats: `GET /api/trips/{id}/available_seats/`

---

## 📊 14. HTTP RESPONSE CODES

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | GET/PUT thành công |
| 201 | Created | POST thành công |
| 204 | No Content | DELETE thành công |
| 400 | Bad Request | Validation error, dữ liệu không hợp lệ |
| 401 | Unauthorized | Chưa login hoặc session expired |
| 403 | Forbidden | Không có quyền, CSRF error |
| 404 | Not Found | Resource không tồn tại |
| 405 | Method Not Allowed | Sử dụng sai HTTP method |
| 500 | Server Error | Lỗi server (check Django logs) |

---

## 📝 15. TESTING CHECKLIST

### Trước khi test:
- [ ] Django server đang chạy (`python manage.py runserver`)
- [ ] PostgreSQL database đang chạy
- [ ] File `.env` đã được config đúng
- [ ] Đã migrate database (`python manage.py migrate`)

### Test Authentication:
- [ ] Register user mới với password mạnh
- [ ] Login thành công và lưu cookies
- [ ] Get profile
- [ ] Update profile
- [ ] Change password

### Test Transport (theo thứ tự):
- [ ] Create 2 Locations
- [ ] Create Route từ 2 locations
- [ ] Create Bus (✅ seats tự động tạo!)
- [ ] **Verify seats đã tự động tạo:** `GET /api/seats/?bus={bus_id}`
  - [ ] Kiểm tra số lượng seats khớp với `total_seats`
  - [ ] Kiểm tra pattern đặt tên: A01-A10, B01-B10, ...
  - [ ] Tất cả seats có `is_available = true`
- [ ] Create Trip với datetime trong tương lai
- [ ] Check available seats

### Test Booking:
- [ ] Create Booking với valid seat IDs
- [ ] Verify total_amount được tính đúng
- [ ] Verify tickets được tạo tự động
- [ ] Get my bookings
- [ ] Get booking details
- [ ] Cancel booking

### Test Admin (nếu có admin account):
- [ ] List all users
- [ ] Change user role
- [ ] View all bookings
- [ ] Confirm booking
- [ ] View statistics

---

## 🎯 16. KẾT LUẬN

Hướng dẫn này bao gồm:
- ✅ Tất cả API endpoints với request format chính xác
- ✅ Validation rules từ serializers và views
- ✅ Workflow đầy đủ từ đầu đến cuối
- ✅ Không tạo sample data - tất cả qua API
- ✅ Username: thaoLinh, Password: Hieudevdut277*

**Thứ tự test bắt buộc:**
1. Authentication (Register → Login)
2. Locations (tạo 2 locations)
3. Routes (tạo route từ 2 locations)
4. Buses (tạo bus - **✅ seats tự động tạo theo total_seats!**)
5. ~~Seats~~ (KHÔNG cần tạo thủ công - đã tự động!)
6. Trips (tạo trip từ route + bus)
7. Bookings (tạo booking với seats)

**Tham khảo code:**
- Serializers: `transport/serializers.py`, `bookings/serializers.py`
- Views: `transport/views.py`, `bookings/views.py`, `accounts/views.py`
- Models: `transport/models.py`, `bookings/models.py`, `accounts/models.py`
- Forms: `accounts/forms.py`

**Happy Testing! 🚀**
