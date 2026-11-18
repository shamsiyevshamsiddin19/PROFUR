# Autentifikatsiya, Rollar va Ruxsatlar API Kelishuvi (PCRM-32)

Ushbu hujjat frontend va backend o‘rtasidagi foydalanuvchi autentifikatsiyasi, sessiya xavfsizligi (CSRF), ko‘p tillilik (UZ/RU/EN) va dinamik rollar (OQ-037) shartnomasini belgilaydi.

---

## 1. Ko‘p tillilik (i18n)

Barcha API so‘rovlarida javob xabarlarining tilini belgilash uchun HTTP sarlavhasida `Accept-Language` yuboriladi:
* `Accept-Language: uz` — O‘zbekcha (standart)
* `Accept-Language: ru` — Ruscha
* `Accept-Language: en` — Inglizcha

---

## 2. Foydalanuvchi rollari (OQ-037)

OQ-037 qaroriga ko‘ra:
* Administrator istalgan nom va kod bilan yangi rollar yarata oladi va ularning ruxsatlarini (`permissions`) belgilaydi.
* Foydalanuvchiga bir vaqtning o‘zida **bir nechta rol** biriktirilishi mumkin (masalan: bir vaqtda ombor mas’uli va ishlab chiqarish nazoratchisi).

Standart tizim rollari:
* `ADMIN` — Tizim administratori (`permissions: ["*"]`).
* `WAREHOUSE_MANAGER` — Ombor mas'uli (`permissions: ["view_catalog", "manage_catalog", "view_inventory", "manage_inventory"]`).
* `PRODUCTION_SUPERVISOR` — Ishlab chiqarish nazoratchisi.
* `PROJECT_MANAGER` — Loyiha mas'uli.
* `WORKER` — Ishchi.

---

## 3. API Nuqtalari (Endpoints)

### 3.1. CSRF Token olish
* **Manzil:** `GET /api/auth/csrf/`
* **Ruxsat:** Barcha uchun ochiq (`AllowAny`)
* **Izoh:** Ushbu so‘rov brauzerda `csrftoken` cookie'sini o‘rnatadi va JSON shaklida tokenni qaytaradi.
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "csrfToken": "vYx...namuna_token..."
}
```

### 3.2. Tizimga kirish (Login)
* **Manzil:** `POST /api/auth/login/`
* **Ruxsat:** Barcha uchun ochiq (`AllowAny`)
* **Xavfsizlik talabi:** CSRF himoyasi yoqilgan. So‘rovda `X-CSRFToken` sarlavhasi bo‘lishi **shart**. Tokensiz so‘rov `403 Forbidden` bilan rad etiladi.
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
    "roles": [
      {
        "id": 2,
        "code": "WAREHOUSE_MANAGER",
        "name": "Ombor mas'uli",
        "description": "Ombor kirim-chiqimini boshqaradi",
        "permissions": ["view_catalog", "manage_catalog", "view_inventory", "manage_inventory"],
        "is_system": true
      }
    ],
    "role_codes": ["WAREHOUSE_MANAGER"],
    "primary_role": "WAREHOUSE_MANAGER",
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

### 3.3. Joriy foydalanuvchi profili (Me)
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
  "roles": [
    {
      "id": 2,
      "code": "WAREHOUSE_MANAGER",
      "name": "Ombor mas'uli",
      "description": "Ombor kirim-chiqimini boshqaradi",
      "permissions": ["view_catalog", "manage_catalog", "view_inventory", "manage_inventory"],
      "is_system": true
    }
  ],
  "role_codes": ["WAREHOUSE_MANAGER"],
  "primary_role": "WAREHOUSE_MANAGER",
  "phone": "+998901234567",
  "is_active": true,
  "date_joined": "2026-11-18T10:00:00Z"
}
```

### 3.4. Tizimdan chiqish (Logout)
* **Manzil:** `POST /api/auth/logout/`
* **Ruxsat:** Faqat tizimga kirganlar (`IsAuthenticated`)
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "message": "Tizimdan muvaffaqiyatli chiqildi."
}
```

### 3.5. Rollar ro‘yxati va yangi rol yaratish (OQ-037)
* **Ro‘yxat:** `GET /api/auth/roles/` (barcha xodimlar ko‘ra oladi)
* **Yaratish:** `POST /api/auth/roles/` (faqat Administrator yaratishi mumkin)
* **So‘rov tanasi (yaratish uchun):**
```json
{
  "code": "QUALITY_CONTROLLER",
  "name": "Sifat nazoratchisi",
  "description": "Mahsulotlar sifatini tekshiruvchi mutaxassis",
  "permissions": ["view_quality", "approve_batch"]
}
```
* **Muvaffaqiyatli javob (`201 Created`):**
```json
{
  "id": 6,
  "code": "QUALITY_CONTROLLER",
  "name": "Sifat nazoratchisi",
  "description": "Mahsulotlar sifatini tekshiruvchi mutaxassis",
  "permissions": ["view_quality", "approve_batch"],
  "is_system": false
}
```

---

## 4. DRF Ruxsatnomalari (Permissions) boshqa modullar uchun

Backend dasturchilari o‘z modullarida (`catalog`, `inventory`, `operations`):
* `IsAdminRole` — Faqat admin amallari uchun.
* `IsWarehouseManager` — Ombor mas'uli yoki administrator uchun.
* `IsProductionSupervisor` — Ishlab chiqarish nazoratchisi yoki admin uchun.
* `IsProjectManager` — Loyiha mas'uli yoki admin uchun.


## Endpoint ruxsatini ulash

Har bir biznes endpointida accounts.permissions.HasPermissionCode ishlatiladi.
Ko‘rinish required_permission orqali kerakli kodni beradi, masalan
inventory.add_receipt. Kod Role.permissions ro‘yxatidagi qiymat bilan aynan
mos kelishi kerak. Administrator rollarni shu kodlar bilan sozlaydi.
IsWarehouseManager umumiy manage_inventory kodini tekshiradi.
Rolga kod berish va undan kodni olib tashlash keyingi so‘rovga ta’sir qiladi.
