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

Tavsiya etilgan rollar (avtomatik yaratilmaydi; admin ruxsatlarni beradi):
* `ADMIN` — Tizim administratori (`permissions: ["*"]`).
* `WAREHOUSE_MANAGER` — Ombor mas'uli (`permissions: ["catalog.view_material", "catalog.add_material", "catalog.change_material", "inventory.view_stock", "inventory.add_receipt", "inventory.view_purchase_price"]`).
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
        "permissions": ["catalog.view_material", "catalog.add_material", "catalog.change_material", "inventory.view_stock", "inventory.add_receipt", "inventory.view_purchase_price"],
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
      "permissions": ["catalog.view_material", "catalog.add_material", "catalog.change_material", "inventory.view_stock", "inventory.add_receipt", "inventory.view_purchase_price"],
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
### 3.6. Foydalanuvchilarni boshqarish (OQ-040)
Faqat Administrator (`IsAdminRole`) uchun ochiq. OQ-040 qaroriga ko‘ra:
* Faqat admin akkaunt yaratadi, parolni tiklaydi, rollarni o‘zgartiradi.
* Akkaunt bazadan o‘chirilmaydi (`DELETE` so‘rovi `405 Method Not Allowed`), faolsizlantiriladi (`is_active: false`); barcha harakatlar tarixi saqlanadi.

#### 3.6.1. Foydalanuvchilar ro‘yxati
* **Manzil:** `GET /api/auth/users/`
* **Filtrlar:** `?search=ism_yoki_login`, `?is_active=true|false`
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
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
          "permissions": ["catalog.view_material", "inventory.*"],
          "is_system": true
        }
      ],
      "role_codes": ["WAREHOUSE_MANAGER"],
      "primary_role": "WAREHOUSE_MANAGER",
      "phone": "+998901234567",
      "is_active": true,
      "date_joined": "2026-11-18T10:00:00Z"
    }
  ]
}
```

#### 3.6.2. Yangi foydalanuvchi yaratish
* **Manzil:** `POST /api/auth/users/`
* **So‘rov tanasi:**
```json
{
  "username": "omborchi_sardor",
  "password": "TemporaryPassword123!",
  "first_name": "Sardor",
  "last_name": "Rahimov",
  "email": "sardor@profur.uz",
  "phone": "+998901112233",
  "role_ids": [2],
  "is_active": true
}
```
* **Muvaffaqiyatli javob (`201 Created`):** yangi yaratilgan foydalanuvchi ma'lumoti (`password`siz).

#### 3.6.3. Foydalanuvchi ma'lumotlarini yangilash va rollarini almashtirish
* **Manzil:** `PATCH /api/auth/users/<id>/` (yoki `PUT`)
* **So‘rov tanasi:**
```json
{
  "first_name": "Sardorbek",
  "role_ids": [2, 3]
}
```
* **Muvaffaqiyatli javob (`200 OK`)**

#### 3.6.4. Akkauntni faolsizlantirish (O‘chirish o‘rniga)
* **Manzil:** `POST /api/auth/users/<id>/deactivate/`
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "message": "Foydalanuvchi muvaffaqiyatli faolsizlantirildi.",
  "user": { "id": 2, "is_active": false }
}
```

#### 3.6.5. Parolni tiklash
* **Manzil:** `POST /api/auth/users/<id>/reset-password/`
* **So‘rov tanasi:**
```json
{
  "new_password": "NewSecretPassword123!"
}
```
* **Muvaffaqiyatli javob (`200 OK`):**
```json
{
  "message": "Parol muvaffaqiyatli yangilandi."
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

## API ruxsat kodlari · 2026-11-18

Katalog API’si `catalog.*`, xarajatlar API’si `expenses.*` kodlarini tekshiradi. Eski `view_catalog` / `manage_catalog` kodlari bu endpointlarga ruxsat bermaydi. Mavjud rollarga kerakli aniq kodlarni admin beradi; rol nomining o‘zi ruxsat emas. Xarajat kodlari [expenses-api.md](expenses-api.md)da.
