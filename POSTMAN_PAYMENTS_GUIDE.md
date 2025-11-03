# 💳 HƯỚNG DẪN TEST API PAYMENTS VỚI POSTMAN

## 📋 Mục lục
1. [API Wallets](#1-api-wallets)
2. [API Payments](#2-api-payments)
3. [Workflow hoàn chỉnh](#3-workflow-hoàn-chỉnh)

---

## Chuẩn bị trước khi test

### Cấu hình Postman

#### Headers cần thiết:
```
Content-Type: application/json
Cookie: sessionid={{session_id}}; csrftoken={{csrf_token}}
```

---

## 1. API WALLETS

### 1.1. Tạo Wallet mới

**Endpoint:** `POST /api/wallets/`

**Request:**
```json
{
  "user_id": 2
}
```

**Response (Success - 201):**
```json
{
    "id": "c12d69ee-31c0-46a6-833d-d5e85b407636",
    "user_id": 2,
    "balance": "0",
    "created_at": "2025-10-31T00:38:52.210514+07:00",
    "updated_at": "2025-10-31T00:43:36.785580+07:00"
}
```

**💡 Lưu ý:**
- Lưu lại `id` (wallet_id) để dùng cho các request tiếp theo
- Balance mặc định là 0
- Mỗi user chỉ nên có 1 wallet

---

### 1.2. Lấy thông tin Wallet

**Endpoint:** `GET /api/wallets/my-wallet/`

**Query Parameters:**
```
?user_id=2
```

**Full URL:**
```
http://localhost:8000/api/wallets/my-wallet/?user_id=2
```

**Response (Success - 200):**
```json
{
    "id": "c12d69ee-31c0-46a6-833d-d5e85b407636",
    "user_id": 2,
    "balance": "0",
    "created_at": "2025-10-31T00:38:52.210514+07:00",
    "updated_at": "2025-10-31T00:43:36.785580+07:00"
}
```

**💡 Lưu ý:**
- Nếu wallet chưa tồn tại, API sẽ tự động tạo mới
- Đây là cách an toàn để lấy wallet của user
- Không cần biết wallet_id trước

---

### 1.3. Kiểm tra số dư Wallet

**Endpoint:** `GET /api/wallets/balance/`

**Query Parameters:**
```
?user_id=2
```

**Full URL:**
```
http://localhost:8000/api/wallets/balance/?user_id=2
```

**Response (Success - 200):**
```json
{
  "user_id": 2,
  "balance": "3600000"
}
```

**💡 Tips:**
- Response chỉ trả về user_id và balance
- Nếu user chưa có wallet, sẽ tự động tạo với balance = 0

---

### 1.4. Nạp tiền vào Wallet

**Endpoint:** `POST /api/wallets/deposit/`

**Request:**
```json
{
  "user_id": 2,
  "amount": 1000000
}
```

**Response (Success - 200):**
```json
{
  "message": "Deposit successful",
  "wallet": {
    "id": "c12d69ee-31c0-46a6-833d-d5e85b407636",
    "user_id": 2,
    "balance": "1000000",
    "created_at": "2025-10-31T00:00:00Z",
    "updated_at": "2025-10-31T00:10:00Z"
  }
}
```

**💡 Lưu ý:**
- Amount phải > 0
- Amount là integer 
- Balance sẽ được cộng thêm vào số dư hiện tại
- updated_at sẽ được cập nhật

```

**📝 Test Cases Examples:**
1. ✅ Nạp 1,000,000 VND → Success
2. ✅ Nạp 500,000 VND → Balance = 1,500,000
3. ❌ Nạp 0 VND → Error
4. ❌ Nạp -100,000 VND → Error

---

### 1.5. Rút tiền từ Wallet

**Endpoint:** `POST /api/wallets/withdraw/`

**Request:**
```json
{
  "user_id": 2,
  "amount": 200000
}
```

**Response (Success - 200):**
```json
{
  "message": "Withdrawal successful",
  "wallet": {
    "id": "c12d69ee-31c0-46a6-833d-d5e85b407636",
    "user_id": 2,
    "balance": "1300000",
    "created_at": "2025-10-31T00:00:00Z",
    "updated_at": "2025-10-31T00:15:00Z"
  }
}
```

**💡 Tips:**
- Amount phải > 0
- Amount không được vượt quá balance hiện tại
- Balance sẽ bị trừ đi amount


**📝 Test Cases Examples:**
1. ✅ Rút 200,000 VND (balance = 1,300,000) → Success
2. ❌ Rút 2,000,000 VND (balance = 1,300,000) → Insufficient balance
3. ❌ Rút 0 VND → Error
4. ❌ Rút -100,000 VND → Error

---

### 1.5. Lấy thông tin Wallet theo ID

**Endpoint:** `GET /api/wallets/{wallet_id}/`

**Example:**
```
GET http://localhost:8000/api/wallets/550e8400-e29b-41d4-a716-446655440000/
```

**Response (Success - 200):**
```json
{
  "id": "c12d69ee-31c0-46a6-833d-d5e85b407636",
  "user_id": 2,
  "balance": "1300000",
  "created_at": "2025-10-31T00:00:00Z",
  "updated_at": "2025-10-31T00:15:00Z"
}
```

---

## 2. API PAYMENTS

### 2.1. Tạo Payment mới

**Endpoint:** `POST /api/payments/`

**Request:**
```json
{
  "booking_id": "8ab4ba3e-4729-403f-bc1f-a343e470e778",
  "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 200000,
  "payment_method": "Momo",
  "transaction_code": "MOMO123456789",
  "status": "Pending"
}
```

**Response (Success - 201):**
```json
{
  "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "booking_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "700000",
  "payment_method": "Momo",
  "payment_method_display": "Momo",
  "status": "Pending",
  "status_display": "Chờ xử lý",
  "payment_time": "2025-10-31T00:20:00Z",
  "transaction_code": "MOMO123456789"
}
```

**💡 Tips:**
- `booking_id` phải tồn tại trong database (UUID format)
- `wallet_id` phải tồn tại trong database (UUID format)
- `amount` phải > 0 và không được vượt quá wallet balance
- `payment_method` phải nằm trong danh sách cho phép (xem bên dưới)
- `transaction_code` là mã giao dịch từ payment gateway
- `status` mặc định là "Pending" nếu không truyền

**✅ Payment Methods hợp lệ:**
- `Momo` - Ví điện tử Momo
- `VNPay` - Cổng thanh toán VNPay
- `ZaloPay` - Ví điện tử ZaloPay
- `ViettelPay` - Ví điện tử ViettelPay
- `MBbank` - Ngân hàng Quân Đội
- `Techcombank` - Ngân hàng Kỹ Thương
- `Agribank` - Ngân hàng Nông nghiệp
- `Vietcombank` - Ngân hàng Ngoại Thương
- `Vietinbank` - Ngân hàng Công Thương

**✅ Payment Status hợp lệ:**
- `Pending` - Chờ xử lý (mặc định)
- `Completed` - Hoàn thành

**❌ Possible Errors:**
```json
// 400 Bad Request - Amount không hợp lệ
{
  "amount": ["Payment amount must be greater than zero."]
}

// 400 Bad Request - Payment method không hợp lệ
{
  "payment_method": ["\"InvalidMethod\" is not a valid choice."]
}

// 400 Bad Request - Booking không tồn tại
{
  "error": "Booking not found"
}

// 400 Bad Request - Wallet không đủ tiền
{
  "error": "Insufficient balance",
  "required": "700000",
  "available": "500000"
}
```

**📝 Test Cases Examples:**
1. ✅ Tạo payment với Momo, amount = 700,000 → Success
2. ✅ Tạo payment với VNPay, amount = 350,000 → Success
3. ❌ Tạo payment với amount = 0 → Error
4. ❌ Tạo payment với payment_method = "Invalid" → Error
5. ❌ Tạo payment với booking_id không tồn tại → Error
6. ❌ Tạo payment với wallet balance không đủ → Error

---

### 2.2. Lấy danh sách Payments (với filter)

**Endpoint:** `GET /api/payments/listing/`

**Query Parameters (Optional):**
- `status`: Filter theo trạng thái (Pending, Completed)
- `booking_id`: Filter theo booking ID (UUID)

**Examples:**

#### Lấy tất cả payments:
```
GET http://localhost:8000/api/payments/listing/
```

#### Filter theo status:
```
GET http://localhost:8000/api/payments/listing/?status=Pending
```

#### Filter theo booking_id:
```
GET http://localhost:8000/api/payments/listing/?booking_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

#### Filter cả hai:
```
GET http://localhost:8000/api/payments/listing/?status=Completed&booking_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response (Success - 200):**
```json
[
  {
    "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
    "booking_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": "700000",
    "payment_method": "Momo",
    "payment_method_display": "Momo",
    "status": "Pending",
    "status_display": "Chờ xử lý",
    "payment_time": "2025-10-31T00:20:00Z",
    "transaction_code": "MOMO123456789"
  },
  {
    "id": "12345678-abcd-ef12-3456-7890abcdef12",
    "booking_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": "350000",
    "payment_method": "VNPay",
    "payment_method_display": "VNPay",
    "status": "Completed",
    "status_display": "Hoàn thành",
    "payment_time": "2025-10-31T00:15:00Z",
    "transaction_code": "VNPAY987654321"
  }
]
```

**💡 Lưu ý:**
- Payments được sắp xếp theo `payment_time` giảm dần (mới nhất trước)
- Có thể kết hợp nhiều filters
- Empty array `[]` nếu không tìm thấy payment nào

---

### 2.3. Lấy thông tin Payment theo ID

**Endpoint:** `GET /api/payments/{payment_id}/`

**Example:**
```
GET http://localhost:8000/api/payments/f9e8d7c6-b5a4-3210-9876-543210fedcba/
```

**Response (Success - 200):**
```json
{
  "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "booking_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "700000",
  "payment_method": "Momo",
  "payment_method_display": "Momo",
  "status": "Pending",
  "status_display": "Chờ xử lý",
  "payment_time": "2025-10-31T00:20:00Z",
  "transaction_code": "MOMO123456789"
}
```

---

### 2.4. Kiểm tra trạng thái Payment

**Endpoint:** `GET /api/payments/{payment_id}/check-status/`

**Example:**
```
GET http://localhost:8000/api/payments/f9e8d7c6-b5a4-3210-9876-543210fedcba/check-status/
```

**Response (Success - 200):**
```json
{
  "payment_id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "status": "Pending"
}
```


### 2.5. Cập nhật trạng thái Payment

**Endpoint:** `PUT /api/payments/{payment_id}/update-status/`
**Hoặc:** `PATCH /api/payments/{payment_id}/update-status/`

**Example:**
```
PUT http://localhost:8000/api/payments/f9e8d7c6-b5a4-3210-9876-543210fedcba/update-status/
```

**Request Body:** None (status sẽ tự động chuyển từ Pending → Completed)

**Response (Success - 200):**
```json
{
  "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "booking_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "700000",
  "payment_method": "Momo",
  "payment_method_display": "Momo",
  "status": "Completed",
  "status_display": "Hoàn thành",
  "payment_time": "2025-10-31T00:20:00Z",
  "transaction_code": "MOMO123456789"
}
```

**💡 Tips:**
- API này thường được gọi bởi admin hoặc payment gateway callback
- Chỉ update status từ Pending → Completed
- Nếu payment đã completed, sẽ trả về error

**❌ Possible Errors:**
```json
// 400 Bad Request - Payment đã completed
{
  "error": "Payment is already completed."
}

// 404 Not Found
{
  "detail": "Payment not found"
}
```

---

## 3. Workflow hoàn chỉnh

### 3.1. Workflow: Thanh toán cho Booking

**Bước 1: Tạo Booking (nếu chưa có)**

```bash
POST /api/bookings/
```

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

**Lưu lại:** `booking_id` từ response (ví dụ: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

---

**Bước 2: Lấy/Tạo Wallet**

```bash
GET /api/wallets/my-wallet/?user_id=2
```

**Lưu lại:** `wallet_id` từ response (ví dụ: `550e8400-e29b-41d4-a716-446655440000`)

---

**Bước 3: Kiểm tra số dư**

```bash
GET /api/wallets/balance/?user_id=2
```

**Response:**
```json
{
  "user_id": 2,
  "balance": "500000"
}
```
---

**Bước 4: Nạp tiền (nếu không đủ)**

```bash
POST /api/wallets/deposit/
```

```json
{
  "user_id": 2,
  "amount": 500000
}
```

**Sau khi nạp:** Balance = 500,000 + 500,000 = 1,000,000

---

**Bước 5: Tạo Payment**

```bash
POST /api/payments/
```

```json
{
  "booking_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 700000,
  "payment_method": "Momo",
  "transaction_code": "MOMO_TXN_123456789",
  "status": "Pending"
}
```

**Lưu lại:** `payment_id` từ response

---

**Bước 6: Kiểm tra status **

```bash
GET /api/payments/{payment_id}/check-status/
```


---

**Bước 7: Update status (từ payment gateway hoặc admin)**

```bash
PUT /api/payments/{payment_id}/update-status/
```

Payment status chuyển từ "Pending" → "Completed"

---

**Bước 8: Kiểm tra lại số dư**

```bash
GET /api/wallets/balance/?user_id=2
```

**Response:**
```json
{
  "user_id": 2,
  "balance": "300000"
}
```

Balance = 1,000,000 - 700,000 = 300,000 ✅

---


**Happy Testing! 💳✨**
