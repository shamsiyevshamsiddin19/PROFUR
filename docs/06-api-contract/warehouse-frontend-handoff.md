# Ombor API · frontendga topshiriq

**2026-11-18 · Ozodbek (@ozodbek101) → Shamsiddin (frontend).** Hammasi `main` da ishlaydi. Namunalar haqiqiy API javoblaridan olingan (vaqtinchalik PostgreSQL bazasi, `Accept-Language: uz`). To‘liq qoidalar — [warehouse-api-v1.md](warehouse-api-v1.md), chiqim — [issues-api.md](issues-api.md), qaytarish va hisobdan chiqarish — [returns-write-offs-api.md](returns-write-offs-api.md) (Akbar).

## Har so‘rovda

| Nima | Qoida |
|---|---|
| Kirish | Sessiya cookie. `POST`/`PATCH` oldidan `GET /api/auth/csrf/` va `X-CSRFToken` sarlavhasi. |
| Til | `Accept-Language: uz` / `ru` / `en` — xato matni shu tilda keladi. |
| Takror bosish | `POST /receipts/` va `POST /issues/` uchun `Idempotency-Key: <UUID>` **majburiy**. Kalitni forma ochilganda yarating, muvaffaqiyatli javobgacha o‘zgartirmang. Qayta yuborilgan bir xil so‘rov → `200` va birinchi javob; bir xil kalit, boshqa tana → `409 idempotency_conflict`. |
| Sonlar | Pul va miqdor **satr**: `"540.00"`. Hisoblash uchun `decimal.js` kabi kutubxona; `Number()` ishlatmang. |
| Sahifalash | Ro‘yxatlar `?page=N`, 20 tadan: `{"count", "next", "previous", "results"}`. |
| Narx | `inventory.view_purchase_price` bo‘lmasa server narx maydonlarini **umuman qaytarmaydi** (`total_amount`, `unit_price`, `currency`, `value_by_currency`, `total_cost`). UI maydon yo‘qligini «—» deb ko‘rsatsin, `undefined` ni `$0` qilmasin. |

## Endpointlar

| Metod va manzil | Ruxsat kodi | Filtrlar / tana |
|---|---|---|
| `GET /api/v1/categories/` | `catalog.view_material` | `search`, `is_active` |
| `GET /api/v1/materials/` · `/{id}/` | `catalog.view_material` | `search` (nom, rang), `category`, `unit`, `is_active` |
| `POST /api/v1/materials/` · `PATCH /{id}/` | `catalog.add_material` · `catalog.change_material` | `category_id`, `name`, `unit`, `color?`, `length_cm?`, `width_cm?`, `thickness_cm?`, `is_active` |
| `GET /api/v1/receipts/` · `/{id}/` | `inventory.view_stock` | `material`, `date_from`, `date_to` (YYYY-MM-DD) |
| `POST /api/v1/receipts/` | `inventory.add_receipt` | `material_id`, `received_on`, `quantity`, `total_amount`, `currency: "USD"`, `supplier?`, `document_number?`, `note?` |
| `GET /api/v1/stock/` · `/{material_id}/` | `inventory.view_stock` | `search`, `category`, `below_min=true` |
| `PATCH /api/v1/stock/{material_id}/` | `inventory.change_min_quantity` | `{"min_quantity": "15.00"}` yoki `null` |
| `GET /api/v1/stock/{material_id}/batches/` | `inventory.view_stock` | qoldig‘i bor partiyalar, eng eskisi birinchi. Avtomatik FIFO taqsimoti OQ-001/P1 bo‘yicha PM tasdig‘igacha qo‘llanmaydi; mijoz tanlangan partiya qismlarini yuboradi |
| `GET /api/v1/movements/` | `inventory.view_stock` | `material`, `type` (`receipt`, `issue`, `return`, `write_off`), `date_from`, `date_to` |
| `POST /api/v1/issues/` | `inventory.add_issue` | [issues-api.md](issues-api.md) |
| `/api/v1/returns/`, `/api/v1/write-offs/` | `inventory.add_return`, `inventory.approve_return`, `inventory.add_write_off`, `inventory.approve_write_off` | [returns-write-offs-api.md](returns-write-offs-api.md) |

Hammasida `DELETE` va `PUT` → `405`: ombor yozuvlari o‘chirilmaydi.

## Haqiqiy javoblar

`POST /api/v1/receipts/` → `201`:

```json
{
  "id": 1,
  "material": {"id": 1, "display_name": "LDSP Egger · oq · 280×207×1.6", "unit": "sheet"},
  "received_on": "2026-11-18",
  "quantity": "20.00",
  "quantity_remaining": "20.00",
  "total_amount": "540.00",
  "unit_price": "27.000000",
  "currency": "USD",
  "supplier": "Egger Tashkent",
  "document_number": "NK-1182",
  "note": "",
  "created_by": {"id": 1, "name": "Vali Aliyev"},
  "created_at": "2026-11-18T18:18:09.248379+05:00",
  "quantity_on_hand_after": "20.00"
}
```

`unit_price` 6 xonali: ekranda 2 xonaga yaxlitlab ko‘rsating, summani esa `total_amount` dan oling.

`GET /api/v1/stock/?below_min=true` (20 × $27 va 15 × $30 kirim, 25 chiqim, chegara 15):

```json
{
  "count": 1, "next": null, "previous": null,
  "results": [{
    "material": {"id": 1, "display_name": "LDSP Egger · oq · 280×207×1.6", "unit": "sheet", "category": {"id": 5, "name": "LDSP"}},
    "quantity_on_hand": "10.00",
    "open_batches": 1,
    "min_quantity": "15.00",
    "is_below_min": true,
    "value_by_currency": [{"currency": "USD", "amount": "300.00"}]
  }]
}
```

Narx ruxsatisiz o‘sha qator — `value_by_currency` yo‘q, qolgani bir xil. Kirimsiz material: `quantity_on_hand: "0.00"`, `open_batches: 0`, `value_by_currency: []`.

`GET /api/v1/stock/1/batches/` → `results: [{"id": 2, "received_on": "2026-11-18", "quantity": "15.00", "quantity_remaining": "10.00", "unit_price": "30.000000", "currency": "USD"}]`

`GET /api/v1/movements/?material=1` (eng yangisi birinchi):

```json
{
  "id": 4,
  "type": "issue",
  "material": {"id": 1, "display_name": "LDSP Egger · oq · 280×207×1.6", "unit": "sheet"},
  "batch_id": 2,
  "quantity": "-5.00",
  "quantity_on_hand_after": "10.00",
  "reference": {"kind": "issue", "id": 1},
  "reason": "",
  "created_by": {"id": 1, "name": "Vali Aliyev"},
  "created_at": "2026-11-18T18:18:09.284245+05:00"
}
```

`quantity` manfiy — qoldiq kamaygan. `reference` bo‘yicha kirim yoki chiqim tafsilotiga o‘tish mumkin.

## Xatolarni ko‘rsatish

| Javob | UI |
|---|---|
| `400 {"quantity": ["…"]}` | Matnni shu maydon ostida. `non_field_errors` — forma tepasida. |
| `400 {"non_field_errors": ["Bunday material allaqachon mavjud."], "existing_id": 1}` | «Mavjud materialni tanlash» tugmasi `existing_id` bilan. |
| `403 {"detail": "Authentication credentials were not provided."}` | Login sahifasiga. |
| `403 {"detail": "You do not have permission to perform this action."}` | «Ruxsat yo‘q» xabari; tugmani yashirish yetarli emas, server baribir rad etadi. |
| `409 {"detail": "…", "code": "idempotency_conflict"}` | Avval shu kalitning asl tanasi va natijasini tekshiring. Noma’lum natijada avtomatik yangi kalit bilan yubormang; tuzatilgan tana alohida yangi amal bo‘lishi kerak. |
| `409 {"detail": "…", "code": "material_has_history"}` | Birlik va o‘lcham maydonlarini kirimi bor materialda bloklang. |
| `409 {"detail": "…", "code": "insufficient_stock", "available": "10.00", "requested": "99.00"}` | `available` ni ko‘rsating; hech narsa saqlanmagan. |

`api.ts` dagi `fieldErrors()` bu shaklni allaqachon o‘qiydi; 409 uchun `error.data.code` ni tekshiring.

## Frontend ulanishi · PR #39

Minimal chegara, partiyalar, chiqim/qaytarish/hisobdan chiqarish va tasdiqlar, material/kategoriya formasi, xarajat/teskari yozuv, filtrli tarix va barcha sahifalarni qamrovchi CSV PR #39 da ulandi. Ruxsatlar UI va serverda tekshiriladi; uzilgan ombor POST so‘rovi ayni tana/kalit bilan tiklanadi. PM’ning P1/P3/P5 qarorlari va PM/buyurtmachi yakuniy qabuli ochiq qoladi.

### Qaytarishning joriy chegarasi · 2026-11-19

`GET /api/v1/issues/{id}/returnable/` — `inventory.view_stock` ruxsati bilan `{allocations: [...]}`. Har qismda avvalgi `batch_id`, `quantity`, `received_on` va yangi `returnable_quantity` bor. Narxlar faqat `inventory.view_purchase_price` bilan. Chegara mavjud `returnable_by_batch(include_pending=True)` servisi orqali hisoblanadi: tasdiqlangan va kutilayotgan qaytarishlar ayiriladi, rad etilganlar ayirilmaydi. GET qoldiqni o‘zgartirmaydi. Frontend shu qiymatni miqdor chegarasida ko‘rsatadi; yakuniy yozishda server yana tekshiradi.
