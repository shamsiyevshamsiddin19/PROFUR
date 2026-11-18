# Qaytarish va hisobdan chiqarish API’si · v1

**2026-11-18 · Ko‘rib chiqish kutilmoqda.** Jira: [PCRM-44](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-44). Egasi: [Akbar (@thealiiheere)](https://github.com/thealiiheere).
Manbalar: [OQ-003, OQ-006, OQ-007, OQ-041](../01-requirements/open-questions.md) (PM tasdiqlagan), TZ 6.8 / BR-11–12, [muhandislik rejasi](../03-architecture/warehouse-engineering-plan.md) sinovlari, [chiqim API’si](issues-api.md). Umumiy qoidalar (sahifalash, o‘nlik sonlar satr ko‘rinishida, `Idempotency-Key`, uz/ru/en xabarlar, faqat USD) chiqim API’si bilan bir xil.

## Umumiy oqim

```
POST /returns/ yoki /write-offs/   → status = "pending"   (qoldiq o‘zgarmaydi)
POST /{id}/approve/                → status = "approved"  (harakat yoziladi, qoldiq o‘zgaradi)
POST /{id}/reject/                 → status = "rejected"  (qoldiq o‘zgarmaydi)
```

- **Qoldiq faqat tasdiqda o‘zgaradi.** Kutilayotgan va rad etilgan so‘rov `/api/v1/movements/` da ko‘rinmaydi, shuning uchun tarix va hisobotda hech narsa ikki marta hisoblanmaydi.
- **Qaror bir marta.** Xuddi shu qarorni takrorlash (ikki marta bosish, internet uzilib qayta yuborish) `200` qaytaradi, joriy holatni beradi va **ikkinchi harakat yozmaydi**. Qarama-qarshi qaror (rad etilganni tasdiqlash) — `409 already_decided`. So‘rov qatori qulflanadi, shu sabab ikki ulanishdan bir vaqtdagi tasdiq ham bitta harakat yozadi (PostgreSQL sinovi).
- **Yaratish idempotent.** `POST /returns/` va `POST /write-offs/` uchun `Idempotency-Key` (UUID) majburiy: bir xil kalit va tana — birinchi javob `200`; bir xil kalit, boshqa tana — `409 idempotency_conflict`.
- **O‘zgarmas tarix.** So‘rovlar o‘chirilmaydi va tahrirlanmaydi (`PUT`/`PATCH`/`DELETE` — `405`). Har so‘rovda kim, qachon kiritgani, sabab, kim/qachon qaror qilgani va qaror izohi saqlanadi. Harakatda `reason`, `batch_id`, `created_by` va `reference` bor.
- **Tranzaksiya.** Tasdiq — bitta tranzaksiya: so‘rov holati, partiya qoldig‘i, umumiy qoldiq va harakat birga saqlanadi yoki birga bekor bo‘ladi.
- **Partiya.** So‘rovda `allocations` — qaysi partiyadan qancha. Qaytarishda faqat asl chiqim olingan partiyalar. Hisobdan chiqarishda partiyani tanlash OQ-001 qaroriga bog‘liq: qaror chiqquncha mijoz o‘zi yuboradi.
- **Narx.** `total_cost`, `currency` va `allocations[].unit_price` faqat `inventory.view_purchase_price` bilan ko‘rinadi (OQ-041).

## Ruxsatlar

| Amal | Ruxsat kodi | Kimga (OQ bo‘yicha) |
|---|---|---|
| Ko‘rish (ikkala ro‘yxat) | `inventory.view_stock` | Ombor mas’uli, admin, nazoratchi |
| Qaytarish so‘rovi | `inventory.add_return` | Ombor mas’uli |
| Qaytarishni tasdiqlash/rad etish | `inventory.approve_return` | Ombor mas’uli (OQ-003) |
| Hisobdan chiqarish so‘rovi | `inventory.add_write_off` | Ombor mas’uli (OQ-007) |
| Hisobdan chiqarishni tasdiqlash/rad etish | `inventory.approve_write_off` | Admin (OQ-007) |

`ADMIN` roli barcha kodlarga ega. `inventory.approve_write_off` kodini ombor mas’uli roliga **bermang** — OQ-007 bo‘yicha tasdiq adminniki. Ruxsat yo‘q yoki tizimga kirilmagan — `403`.

## Qaytarish (OQ-003)

`POST /api/v1/returns/` · `Idempotency-Key: <UUID>`

```json
{
  "issue_id": 3,
  "returned_on": "2026-11-18",
  "reason": "Ortib qoldi",
  "allocations": [{"batch_id": 12, "quantity": "2.00"}]
}
```

`returned_on` ixtiyoriy (standart — bugun), kelajak yoki chiqim sanasidan oldingi sana — `400`. Frontend qismlarni `GET /api/v1/issues/{id}/` dagi `allocations` dan to‘ldiradi.

Javob (`201`, tasdiqdan keyin ham shu shakl):

```json
{
  "id": 5,
  "issue": {"id": 3, "issued_on": "2026-11-18", "recipient_name": "Sardor", "project_id": 7, "quantity": "6.00"},
  "material": {"id": 41, "display_name": "LDSP Egger · oq", "unit": "sheet"},
  "quantity": "2.00",
  "returned_on": "2026-11-18",
  "reason": "Ortib qoldi",
  "allocations": [{"batch_id": 12, "received_on": "2026-11-15", "quantity": "2.00", "unit_price": "10.000000"}],
  "total_cost": "20.00",
  "currency": "USD",
  "status": "pending",
  "decided_by": null,
  "decided_at": null,
  "decision_note": "",
  "created_by": {"id": 2, "name": "Akbar"},
  "created_at": "2026-11-18T10:24:05Z"
}
```

**Limit.** Har partiya bo‘yicha: `asl chiqim − tasdiqlangan − kutilayotgan qaytarishlar`. Oshsa `409`:

```json
{"code": "return_exceeds_issue", "batch_id": "12", "available": "1.00", "requested": "2.00", "detail": "…"}
```

Rad etilgan so‘rov limitni bo‘shatadi. Tasdiq paytida limit qulf ostida yana tekshiriladi (faqat tasdiqlanganlar bo‘yicha), shuning uchun jami qaytarish hech qachon asl chiqimdan oshmaydi.

`POST /api/v1/returns/{id}/approve/` va `POST /api/v1/returns/{id}/reject/` — tana ixtiyoriy: `{"note": "Ko‘rildi"}`. Javob `200`, yuqoridagi shakl. Tasdiqda material **o‘zi chiqqan partiyaga** qaytadi: `Batch.quantity_remaining` va umumiy qoldiq oshadi, har qism uchun `type = "return"`, `reference = {"kind": "return", "id": 5}` harakati yoziladi.

`GET /api/v1/returns/?issue=3&material=41&status=pending&date_from=…&date_to=…` (sana — yaratilgan kun), `GET /api/v1/returns/{id}/`.

## Hisobdan chiqarish (OQ-007)

`POST /api/v1/write-offs/` · `Idempotency-Key: <UUID>`

```json
{
  "material_id": 41,
  "reason": "Namlikdan buzildi",
  "allocations": [{"batch_id": 12, "quantity": "3.00"}]
}
```

`reason` majburiy (bo‘sh — `400`). Hozir omborda yo‘q miqdorga so‘rov yaratilmaydi: `409 insufficient_stock` yoki `409 batch_insufficient` (chiqim API’sidagi shakl).

Javob: `id`, `material`, `quantity`, `reason`, `allocations`, `total_cost`, `currency`, `status`, `decided_by`, `decided_at`, `decision_note`, `created_by`, `created_at`.

`POST /api/v1/write-offs/{id}/approve/` (admin) — qoldiq va partiyalar kamayadi, `type = "write_off"`, `reference = {"kind": "write_off", "id": …}`, `reason` — so‘rov sababi, `created_by` — tasdiqlagan admin. So‘rovdan keyin material chiqib ketgan bo‘lsa — `409 insufficient_stock`/`batch_insufficient`, so‘rov `pending` qoladi.
`POST /api/v1/write-offs/{id}/reject/` — qoldiq o‘zgarmaydi.

`GET /api/v1/write-offs/?material=41&status=pending&date_from=…&date_to=…`, `GET /api/v1/write-offs/{id}/`.

## Harakatlar tarixi bilan bog‘lanish (PCRM-42/47)

`GET /api/v1/movements/` (Ozodbek) ombordagi har bir o‘zgarishni ko‘rsatadi. Akbar amallari:

| `type` | `reference.kind` | `quantity` | Qachon yoziladi | Manba sahifasi |
|---|---|---|---|---|
| `issue` | `issue` | manfiy, har partiyaga bittadan | Chiqim yozilganda | `/api/v1/issues/{id}/` |
| `return` | `return` | musbat, har partiyaga bittadan | Qaytarish **tasdiqlanganda** | `/api/v1/returns/{id}/` |
| `write_off` | `write_off` | manfiy, har partiyaga bittadan | Hisobdan chiqarish **tasdiqlanganda** | `/api/v1/write-offs/{id}/` |

Bir amal bir nechta partiyaga tegsa, harakatlar ham bir nechta, lekin `reference` bitta. Frontend amallarni `reference` bo‘yicha guruhlaydi, miqdorlarni esa harakatlardan yig‘adi: barcha harakatlar `quantity` yig‘indisi `quantity_on_hand` ga teng (sinov: `test_movements_history_counts_each_operation_once`).

## Xatolar

| Kod | HTTP | Qachon |
|---|---|---|
| `return_exceeds_issue` | 409 | Qaytarish asl chiqimning qaytarilmagan qismidan oshadi |
| `already_decided` | 409 | So‘rov boshqa qaror bilan yopilgan; javobda `status` |
| `insufficient_stock` / `batch_insufficient` | 409 | Hisobdan chiqarishda qoldiq yoki partiya yetmaydi |
| `idempotency_conflict` | 409 | Kalit boshqa tana bilan ishlatilgan |
| `idempotency_key_required` | 400 | `POST` yaratishda kalit yo‘q |
| `batch_not_in_issue` | 400 | Qaytarish partiyasi asl chiqimda yo‘q |
| `batch_not_of_material`, `duplicate_batch` | 400 | Hisobdan chiqarish partiyasi xato |
| `date_in_future`, `before_issue` | 400 | Qaytarish sanasi xato |

## Sinovlar

`tests/test_inventory_requests.py`: tasdiqgacha qoldiq o‘zgarmasligi, partiyaga qaytish, ikki marta tasdiq — bitta harakat, limit (kutilayotganlar bilan va qulf ostida), rad etish, idempotentlik, ruxsatlar (`403`/`405`), narxni yashirish, harakatlar tarixida har amal bir marta, jarayon o‘rtasidagi xatoda to‘liq ortga qaytish. PostgreSQL’da: ikki ulanishdan bir vaqtda qaytarish va hisobdan chiqarishni tasdiqlash — bitta harakat.
