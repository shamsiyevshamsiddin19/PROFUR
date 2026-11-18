# Ombordan chiqim API’si · v1

**2026-11-18 · Taklif, ko‘rib chiqish kutilmoqda.** Jira: [PCRM-44](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-44), 1-qism (chiqim). Egasi: [Akbar (@thealiiheere)](https://github.com/thealiiheere).
Manbalar: TZ 6.3 va 6.8, [OQ-001, OQ-002, OQ-006, OQ-041](../01-requirements/open-questions.md), [valyuta va til qarori](../09-decisions/decision-log.md), [ombor API shartnomasi](warehouse-api-v1.md) 6-bo‘lim. Umumiy qoidalar (sana formati, sahifalash, o‘nlik sonlar satr ko‘rinishida, `Idempotency-Key`) shartnoma bilan bir xil.

Qaytarish (OQ-003, tasdiqlash bilan) va hisobdan chiqarish (OQ-007, admin tasdig‘i) keyingi qismlarda qo‘shiladi.

## Qoidalar

- **Qoldiq shu zahoti kamayadi** (OQ-002). Manfiy qoldiq taqiqlanadi (OQ-006): yetmasa `409`, hech narsa saqlanmaydi.
- **Partiya tanlash.** Qoida PM qaroriga bog‘liq (OQ-001). Qaror chiqquncha mijoz `allocations` da qaysi partiyadan qancha olinishini o‘zi yuboradi. Forma partiyalarni `GET /api/v1/stock/{material_id}/batches/` dan oladi va eng eskisidan boshlab to‘ldirib taklif qilishi mumkin. Chiqim miqdori — qismlar yig‘indisi.
- **Tannarx USD’da.** Har qism `miqdor × partiya.unit_price`, yakuniy yig‘indi sentgacha `ROUND_HALF_UP`. Keyingi kirimlar eski chiqim qiymatini o‘zgartirmaydi.
- **Narx yashiriladi.** `inventory.view_purchase_price` ruxsati bo‘lmasa javobda `total_cost`, `currency` va `allocations[].unit_price` bo‘lmaydi (OQ-041).
- **Chiqim o‘zgarmas** (TZ 6.8). `PUT`, `PATCH`, `DELETE` → `405`. Xato chiqim keyinchalik qaytarish bilan to‘g‘rilanadi.
- **Loyiha.** `project_id` ixtiyoriy butun son. Loyihalar moduli kelganda havolaga aylanadi (xarajatlar bilan bir xil yondashuv).
- **Faol bo‘lmagan material.** Undan chiqim qilish mumkin: katalogdan olingan materialning ombordagi qoldig‘i baribir berilishi kerak.
- **Til.** Xato matni `Accept-Language: uz | ru | en` bo‘yicha.

## Ruxsatlar

| Amal | Ruxsat kodi |
|---|---|
| Chiqimlarni ko‘rish | `inventory.view_stock` |
| Chiqim yozish | `inventory.add_issue` |
| Narx va tannarxni ko‘rish | `inventory.view_purchase_price` |

Tekshiruv `accounts.permissions.HasPermissionCode` orqali. Ruxsat yo‘q yoki tizimga kirilmagan — `403`.

## Chiqim yozish

`POST /api/v1/issues/` · sarlavha `Idempotency-Key: <UUID>` (**majburiy**)

```json
{
  "material_id": 41,
  "issued_on": "2026-11-18",
  "recipient_name": "Sardor (sex 2)",
  "project_id": 7,
  "note": "Shkaf korpusi",
  "allocations": [
    {"batch_id": 12, "quantity": "5.00"},
    {"batch_id": 15, "quantity": "2.00"}
  ]
}
```

`issued_on` ixtiyoriy (standart — bugun), kelajak sana `400`. `note` ixtiyoriy. `allocations` 1–50 qism, har biri `quantity > 0`.

`201` javobi:

```json
{
  "id": 3,
  "material": {"id": 41, "display_name": "LDSP Egger · oq", "unit": "sheet"},
  "quantity": "7.00",
  "issued_on": "2026-11-18",
  "recipient_name": "Sardor (sex 2)",
  "project_id": 7,
  "note": "Shkaf korpusi",
  "allocations": [
    {"batch_id": 12, "received_on": "2026-11-15", "quantity": "5.00", "unit_price": "20.000000"},
    {"batch_id": 15, "received_on": "2026-11-18", "quantity": "2.00", "unit_price": "30.000000"}
  ],
  "total_cost": "160.00",
  "currency": "USD",
  "created_by": {"id": 2, "name": "Akbar"},
  "created_at": "2026-11-18T10:24:05Z",
  "quantity_on_hand_after": "3.00"
}
```

Har qism uchun bitta `issue` harakati yoziladi (`quantity` manfiy, `reference_kind = "issue"`, `reference_id = id`). Ular `/api/v1/movements/` da ko‘rinadi.

### Xatolar

| Holat | Javob |
|---|---|
| Umumiy qoldiq yetmaydi | `409`, `{"code": "insufficient_stock", "available": "3.00", "requested": "5.00", "detail": "…"}` |
| Tanlangan partiyada yetmaydi (masalan, boshqa xodim shu vaqtda olgan) | `409`, `{"code": "batch_insufficient", "batch_id": "12", "available": "2.00", "requested": "3.00", "detail": "…"}` |
| Bir partiya ikki marta | `400`, `allocations[0].code = "duplicate_batch"` |
| Partiya boshqa materialniki yoki yo‘q | `400`, `allocations[0].code = "batch_not_of_material"` |
| Kelajak sana | `400`, `issued_on[0].code = "date_in_future"` |
| `Idempotency-Key` yo‘q yoki UUID emas | `400`, `idempotency_key[0].code = "idempotency_key_required"` |
| Kalit bir xil, tana boshqacha | `409`, `idempotency_conflict` |

Bir xil kalit va tana qayta yuborilsa, yangi chiqim yozilmaydi: birinchi javob `200` bilan qaytadi. Xato bilan tugagan so‘rov kalitni band qilmaydi — to‘g‘rilangan tanani shu kalit bilan yuborish mumkin.

## Chiqimlarni ko‘rish

`GET /api/v1/issues/?material=41&project_id=7&date_from=2026-11-01&date_to=2026-11-30` — eng yangisi birinchi, sahifalangan (`count`, `next`, `previous`, `results`). Har bir yozuv yuqoridagi shaklda, `quantity_on_hand_after` siz.
`GET /api/v1/issues/{id}/` — bitta chiqim.

## Sinovlar

`tests/test_inventory_issues.py`: qoldiq/partiya kamayishi va harakat, ikki partiyali tannarx, yaxlitlash, ikkala `409`, validatsiya, idempotentlik, ruxsatlar, narxni yashirish, `405`, filtrlar, uz/ru/en xabarlari. PostgreSQL’da: qoldiq 10 bo‘lganda ikki ulanishdan bir vaqtda 7 tadan chiqim — bittasi `201`, ikkinchisi `409`, qoldiq 3 (CI’da ishlaydi).

## Ochiq savollar

- **OQ-001 (PM: P1).** Partiya tanlash qoidasi (FIFO yoki qo‘lda). Qaror chiqsa, `allocations` ixtiyoriy bo‘lib, server o‘zi taqsimlaydi; mavjud mijozlar o‘zgarishsiz ishlayveradi.
- **`recipient_name`** hozir erkin matn. Ishchilar ro‘yxati paydo bo‘lsa, `recipient_id` qo‘shiladi.
- **`inventory.add_issue`** kodini admin rollarga berishi kerak (Jamoliddin, accounts).
