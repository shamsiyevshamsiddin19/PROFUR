# Autentifikatsiya va Ruxsatlar API Kelishuvi (PCRM-32)

Ushbu hujjat frontend va backend o‘rtasidagi foydalanuvchi autentifikatsiyasi, sessiya va ruxsatlar shartnomasini belgilaydi.

---

## Foydalanuvchi rollari (Roles)

Tizimda 5 ta asosiy rol mavjud:
1. `ADMIN` — Tizim administratori (barcha amallarga to‘liq huquq).
2. `WAREHOUSE_MANAGER` — Ombor mas'uli (materiallar katalogi, kirim, chiqim, hisobdan chiqarish so‘rovlari).
3. `PRODUCTION_SUPERVISOR` — Ishlab chiqarish nazoratchisi.
4. `PROJECT_MANAGER` — Loyiha mas'uli.
5. `WORKER` — Ishchi (vazifalar va shaxsiy ishbay hisobi).

---

## API Nuqtalari (Endpoints)

### 1. CSRF Token olish
* **Manzil:** `GET /api/auth/csrf/`
* **Ruxsat:** Barcha uchun ochiq (`AllowAny`)
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "csrfToken": "vYx...namuna_token..."
}
```

### 2. Tizimga kirish (Login)
* **Manzil:** `POST /api/auth/login/`
* **Ruxsat:** Barcha uchun ochiq (`AllowAny`)
* **Sarlavhalar (Headers):**
  * `Content-Type: application/json`
  * `X-CSRFToken: <csrf_token>`
* **So‘rov tanasi (Request Body):**
```json
{
  "username": "omborchi_vali",
  "password": "maxfiy_parol"
}
```
* **Muvaffaqiyatli javob (`200 OK`):**
*(Avtomatik ravishda `sessionid` cookie o‘rnatiladi)*
```json
{
  "message": "Tizimga muvaffaqiyatli kirildi.",
  "user": {
    "id": 2,
    "username": "omborchi_vali",
    "email": "vali@profur.uz",
    "first_name": "Vali",
    "last_name": "Aliyev",
    "role": "WAREHOUSE_MANAGER",
    "role_display": "Ombor mas'uli",
    "phone": "+998901234567",
    "is_active": true,
    "date_joined": "2026-11-18T10:00:00Z"
  }
}
```
* **Xato javob (`400 Bad Request`):**
```json
{
  "non_field_errors": [
    "Login yoki parol noto'g'ri kiritildi."
  ]
}
```

### 3. Joriy foydalanuvchi ma'lumotlari (Me)
* **Manzil:** `GET /api/auth/me/`
* **Ruxsat:** Faqat tizimga kirganlar (`IsAuthenticated`)
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "id": 2,
  "username": "omborchi_vali",
  "email": "vali@profur.uz",
  "first_name": "Vali",
  "last_name": "Aliyev",
  "role": "WAREHOUSE_MANAGER",
  "role_display": "Ombor mas'uli",
  "phone": "+998901234567",
  "is_active": true,
  "date_joined": "2026-11-18T10:00:00Z"
}
```
* **Ruxsatsiz kirilganda (`403 Forbidden` / `401 Unauthorized`):**
```json
{
  "detail": "Autentifikatsiyadan o'tilmagan."
}
```

### 4. Tizimdan chiqish (Logout)
* **Manzil:** `POST /api/auth/logout/`
* **Ruxsat:** Faqat tizimga kirganlar (`IsAuthenticated`)
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "message": "Tizimdan muvaffaqiyatli chiqildi."
}
```

---

## DRF Ruxsatnomalari (Permissions) boshqa modullar uchun

Boshqa ilovalar (`catalog`, `inventory`, `operations`) quyidagi ruxsatnomalarni ishlatishi mumkin:
* `IsAdminRole` — Faqat admin amallari uchun (foydalanuvchi boshqaruvi, audit).
* `IsWarehouseManager` — Ombor amallari (materiallar yaratish, kirim kiritish, chiqim qilish).
* `IsProductionSupervisor` — Ishlab chiqarish nazorati.
* `IsProjectManager` — Loyiha mas'uli amallari.
