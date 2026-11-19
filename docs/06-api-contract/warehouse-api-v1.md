# Ombor API shartnomasi · v1 (katalog, kirim, qoldiq)

**18-noyabr 2026 · Amaldagi kod bilan moslangan** (main: #15, #20, #21, #27, #34, #35). Javob namunalari haqiqiy API’dan olingan; frontend uchun qisqa topshiriq — [warehouse-frontend-handoff.md](warehouse-frontend-handoff.md). Jira: [PCRM-49](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-49), [PCRM-39](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-39), [PCRM-40](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-40), [PCRM-42](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-42). Egasi: [@ozodbek101](https://github.com/ozodbek101).
Manbalar: [OQ reyestri](../01-requirements/open-questions.md) (OQ-001, 004–009, 013, 016, 034, 037–041), [muhandislik rejasi](../03-architecture/warehouse-engineering-plan.md), [katalog modeli](../05-data-model/data-model.md#katalog-modeli--pcrm-38) (PR #11).

Bu hujjat birinchi oqimni qamraydi: **material yaratish → kirim → qoldiqni ko‘rish**. Chiqim — [issues-api.md](issues-api.md), qaytarish va hisobdan chiqarish — [returns-write-offs-api.md](returns-write-offs-api.md), xarajatlar — [expenses-api.md](expenses-api.md) (Akbar, @thealiiheere). Ular bu yerdagi umumiy qoidalar va [ombor moduli chegarasi](#6-ombor-moduli-chegarasi--akbar-uchun)ga tayanadi.

PM qaroriga bog‘liq qismlar **[PM]** bilan belgilangan va [8-bo‘limda](#8-pmga-ochiq-savollar-team-lead-orqali) jamlangan; ular hal bo‘lguncha kod taklif qilingan xatti-harakat bilan ishlaydi.

**2026-11-18 · Foydalanuvchining keyingi aniqlashtirishi.** Yagona valyuta USD ($), tizim tillari uz/ru/en. Shu qaror avvalgi ko‘p valyutali taklifni almashtiradi.

## 1. Umumiy qoidalar

| Mavzu | Qoida |
|---|---|
| Manzil | Hamma ombor API’si `/api/v1/` ostida. Oxiri `/` bilan tugaydi (Django odati). |
| Format | JSON, UTF-8. |
| O‘nlik sonlar | **Satr** sifatida keladi va ketadi: `"12.50"`. JavaScript `number` pul va miqdorni buzishi mumkin. DRF’da bu standart xatti-harakat. |
| Sana | `received_on` kabi kunlar — `YYYY-MM-DD`. Vaqt — ISO 8601, Toshkent vaqti bilan: `2026-11-18T14:05:00+05:00`. |
| Kirish | Sessiya cookie (`SessionAuthentication`, amaldagi `settings.py`). Yozuvchi so‘rovlar `X-CSRFToken` sarlavhasini yuboradi. Login API’si — Jamoliddin vazifasi. |
| Til | Frontend `Accept-Language: uz` / `ru` / `en` yuboradi. Server xato `message`ini shu tilda qaytaradi. Birlik va tur kabi qiymatlar **kod** bo‘lib keladi (`sheet`, `receipt`). Ularning yozuvini frontend tarjima qiladi. |
| Sahifalash | Ro‘yxatlar: `?page=2`. Javob: `{"count", "next", "previous", "results"}`. Bir sahifada 20 ta yozuv bo‘ladi (amaldagi sozlama). |
| O‘chirish | Ombor yozuvlari o‘chirilmaydi. Katalog `is_active=false` bilan faolsizlantiriladi. Kirimdagi xato tuzatish harakati bilan to‘g‘rilanadi ([8-bo‘lim](#8-pmga-ochiq-savollar-team-lead-orqali), P5). |

**Amaldagi ruxsat ulanishi:** endpointlar accounts.permissions.HasPermissionCode va ko‘rinishdagi required_permission orqali jadvaldagi kodni tekshiradi. Masalan, kirim uchun inventory.add_receipt.

### Xato javobi (amaldagi)

Umumiy `EXCEPTION_HANDLER` qo‘shilmadi, shuning uchun xatolar DRF shaklida keladi. Matn `Accept-Language` bo‘yicha tarjima qilinadi; frontend matnni ko‘rsatadi, 409 da esa `code` bo‘yicha qaror qiladi.

| HTTP | Shakl | Qachon |
|---|---|---|
| 400 | `{"quantity": ["…"], "currency": ["…"]}` — maydon nomi → xabarlar ro‘yxati; umumiy xato `non_field_errors` da | Maydon xatosi |
| 400 | `{"non_field_errors": ["Bunday material allaqachon mavjud."], "existing_id": 1}` | Takror material |
| 400 | `{"idempotency_key": ["…"]}` | `Idempotency-Key` yo‘q yoki UUID emas |
| 403 | `{"detail": "Authentication credentials were not provided."}` | Sessiya yo‘q (SessionAuthentication 401 emas, 403 qaytaradi) |
| 403 | `{"detail": "You do not have permission to perform this action."}` | Rolda ruxsat kodi yo‘q |
| 404 | `{"detail": "…"}` | Yozuv yo‘q |
| 405 | `{"detail": "…"}` | `PUT`, `DELETE` va boshqa yo‘q metodlar |
| 409 | `{"detail": "…", "code": "<kod>", …}` | Biznes qoidasi: `idempotency_conflict`, `material_has_history`, `insufficient_stock` (+ `available`, `requested`), `batch_insufficient` (+ `batch_id`) |

Haqiqiy 409 namunasi (`Accept-Language: ru`):

```json
{"detail": "На складе недостаточно материала.", "code": "insufficient_stock", "available": "10.00", "requested": "99.00"}
```

## 2. Ruxsatlar

OQ-037 ga ko‘ra rollar admin tomonidan erkin yaratiladi. Shuning uchun API rol nomini emas, **ruxsat kodini** tekshiradi: kod `Role.permissions` ro‘yxatida bo‘lishi kerak (`accounts.permissions.HasPermissionCode`, [auth-api.md](auth-api.md)). Admin roli `*` bilan hammasini oladi.

| Ruxsat kodi | Nima beradi | Admin | Ombor mas’uli | Ishlab chiqarish nazoratchisi |
|---|---|---|---|---|
| `catalog.view_material` | Kategoriya va materiallarni ko‘rish | ✓ | ✓ | ✓ |
| `catalog.add_category`, `catalog.change_category` | Kategoriya qo‘shish va tahrirlash | ✓ | — | — |
| `catalog.add_material`, `catalog.change_material` | Material qo‘shish va tahrirlash | ✓ | ✓ | — |
| `inventory.view_stock` | Qoldiq miqdori va harakatlar tarixi | ✓ | ✓ | ✓ |
| `inventory.add_receipt` | Kirim yozish | ✓ | ✓ | — |
| `inventory.add_issue` | Chiqim yozish ([issues-api.md](issues-api.md)) | ✓ | ✓ | — |
| `inventory.view_purchase_price` | Narx, summa va valyuta maydonlarini ko‘rish | ✓ | ✓ | — |
| `inventory.change_min_quantity` | Minimal qoldiq chegarasini belgilash (OQ-014) | ✓ | — | — |

Rollar jadvali OQ-038 va OQ-041 asosidagi tavsiya. `auth-api.md` dagi standart `WAREHOUSE_MANAGER` rolida hozir `catalog.view_material`, `catalog.add_material`, `catalog.change_material`, `inventory.view_stock`, `inventory.add_receipt`, `inventory.view_purchase_price` bor; `inventory.add_issue` va `inventory.change_min_quantity` ni admin beradi.
Agar foydalanuvchida `inventory.view_purchase_price` bo‘lmasa, server narx maydonlarini (`total_amount`, `unit_price`, `currency`, `value_by_currency`, chiqimda `total_cost`) javobdan **olib tashlaydi** — kirim, qoldiq, partiyalar, chiqim, qaytarish, hisobdan chiqarish va tarixning hammasida (`tests/test_warehouse_ledger.py`). Ular `null` bilan to‘ldirilmaydi. Bu ruxsat frontendda emas, serverda tekshiriladi.

## 3. Katalog API’si · PCRM-39

### 3.1 Kategoriyalar

`GET /api/v1/categories/?search=ldsp&is_active=true`

```json
{"count": 1, "next": null, "previous": null,
 "results": [{"id": 3, "name": "LDSP", "is_active": true, "material_count": 12}]}
```

| So‘rov | Tana | Javob |
|---|---|---|
| `POST /api/v1/categories/` | `{"name": "LDSP"}` | `201` + yozuv. Nom takrorlansa `400`, `fields.name[0].code = "unique"`. |
| `PATCH /api/v1/categories/{id}/` | `{"name"?, "is_active"?}` | `200` + yozuv. |

Kategoriya faolsizlantirilsa, uning materiallari ishlayveradi. Faqat yangi material qo‘shishda bu kategoriya ro‘yxatda chiqmaydi.

### 3.2 Materiallar

`GET /api/v1/materials/?search=egger&category=3&unit=sheet&is_active=true`

`search` maydoni nom va rang bo‘yicha qidiradi, katta-kichik harf farqlanmaydi. Kirim formasidagi tanlov maydoni uchun shu manzilning o‘zi ishlatiladi.

```json
{
  "id": 41,
  "category": {"id": 3, "name": "LDSP"},
  "name": "LDSP Egger",
  "color": "oq",
  "length_cm": "280.00",
  "width_cm": "207.00",
  "thickness_cm": "1.60",
  "unit": "sheet",
  "display_name": "LDSP Egger · oq · 280×207×1.6",
  "is_active": true,
  "quantity_on_hand": "35.00"
}
```

| So‘rov | Tana | Javob |
|---|---|---|
| `GET /api/v1/materials/{id}/` | — | `200` + yozuv. |
| `POST /api/v1/materials/` | `{"category_id", "name", "unit", "color"?, "length_cm"?, "width_cm"?, "thickness_cm"?}` | `201` + yozuv. |
| `PATCH /api/v1/materials/{id}/` | Yuqoridagi maydonlardan istalgani va `is_active` | `200` + yozuv. |

Tekshiruvlar (PR #11 dagi baza cheklovlari bilan bir xil):

- `unit`: `sheet`, `piece`, `kg`, `liter`, `meter`, `m2`. «list/dona» masalasi PR #11 da ochiq.
- O‘lchamlar santimetrda. Berilsa, `> 0` bo‘lishi va verguldan keyin ko‘pi bilan 2 xona bo‘lishi kerak.
- Bir xil material (kategoriya + nom + rang + o‘lchamlar + birlik) takrorlansa `400`: `{"non_field_errors": ["…"], "existing_id": 1}`. Forma «mavjud materialni tanlash»ni taklif qila oladi.
- Faol bo‘lmagan kategoriyaga material qo‘shib bo‘lmaydi: `400`, `{"category_id": ["…"]}`.
- Kirimi bor materialning `unit` yoki o‘lchamlarini o‘zgartirish taqiqlanadi: `409`, `{"detail": "…", "code": "material_has_history"}`. Aks holda eski partiyalar boshqa o‘lchovga tegishli bo‘lib qoladi. Nom, rang va `is_active` o‘zgartirilishi mumkin.
- `DELETE` qo‘llab-quvvatlanmaydi: `405`.

## 4. Kirim API’si · PCRM-40

### 4.1 Kirim yozish

`POST /api/v1/receipts/`
Sarlavha: `Idempotency-Key: 6f1c2a1e-6f0b-4b3e-9d0e-4f6b8a1d2c33` (UUID, **majburiy**).

```json
{
  "material_id": 41,
  "received_on": "2026-11-18",
  "quantity": "20.00",
  "total_amount": "540.00",
  "currency": "USD",
  "supplier": "Egger Tashkent",
  "document_number": "NK-1182",
  "note": ""
}
```

| Maydon | Majburiy | Qoida |
|---|---|---|
| `material_id` | ha | Faol material. Topilmasa `does_not_exist`, faol bo‘lmasa `material_inactive`. |
| `received_on` | ha | Kelajak sana bo‘lishi mumkin emas (`date_in_future`). |
| `quantity` | ha | `> 0`, verguldan keyin ko‘pi bilan 2 xona. **[PM: P3]** |
| `total_amount` | ha | Hujjatdagi umumiy summa. `> 0`, verguldan keyin ko‘pi bilan 2 xona. |
| `currency` | ha | Faqat `USD`. Boshqasi `400`: `{"currency": ["\"EUR\" is not a valid choice."]}`. |
| `supplier` | yo‘q | 200 belgigacha (OQ-004: majburiy emas). |
| `document_number` | yo‘q | 100 belgigacha (OQ-004: majburiy emas). |
| `note` | yo‘q | 500 belgigacha. |

**Nega birlik narxi emas, umumiy summa yuboriladi.** Omborchining qo‘lidagi hujjatda odatda umumiy summa yozilgan bo‘ladi. Agar u birlik narxini o‘zi hisoblab kiritsa, yaxlitlash sabab summa hujjatdagidan bir necha so‘m farq qilishi mumkin. Shuning uchun summa aynan saqlanadi. Birlik narxini server hisoblaydi: `unit_price = total_amount / quantity`. Natija verguldan keyin 6 xonagacha `ROUND_HALF_UP` bilan saqlanadi. Ekranda u 2 xona bilan ko‘rsatiladi. Hisobotda kerak bo‘lsa, summa `total_amount` maydonidan olinadi, `unit_price × quantity` qayta hisoblanmaydi.

Javob `201 Created`:

```json
{
  "id": 105,
  "material": {"id": 41, "display_name": "LDSP Egger · oq · 280×207×1.6", "unit": "sheet"},
  "received_on": "2026-11-18",
  "quantity": "20.00",
  "quantity_remaining": "20.00",
  "total_amount": "540.00",
  "unit_price": "27.000000",
  "currency": "USD",
  "supplier": "Egger Tashkent",
  "document_number": "NK-1182",
  "note": "",
  "created_by": {"id": 7, "name": "Ombor mas’uli"},
  "created_at": "2026-11-18T14:05:00+05:00",
  "quantity_on_hand_after": "35.00"
}
```

`id` — bu partiya identifikatori. Har bir kirim alohida partiya bo‘ladi (OQ-001, OQ-008). Bir materialning ikki xil narxdagi kirimi hech qachon birlashtirilmaydi.

**Bitta tranzaksiya.** Partiya, `receipt` turidagi harakat, materialning umumiy qoldig‘i va idempotentlik yozuvi bitta `transaction.atomic()` ichida yoziladi. Biror qadam xato bersa, hech narsa saqlanmaydi.

**Takror yuborish (idempotentlik).** Internet uzilib, brauzer so‘rovni qayta yuborishi mumkin:

| Holat | Javob |
|---|---|
| Kalit yangi | Kirim yoziladi, `201`. |
| Kalit va tana avvalgisi bilan bir xil | Yangi yozuv yaratilmaydi. Birinchi javob `200` bilan qaytadi. |
| Kalit bir xil, tana boshqacha | `409`, `{"detail": "…", "code": "idempotency_conflict"}`. |
| Kalit yo‘q yoki UUID emas | `400`, `{"idempotency_key": ["…"]}`. |

Frontend kalitni forma ochilganda yaratadi va muvaffaqiyatli javob kelguncha o‘zgartirmaydi. Kalit 24 soat saqlanadi; kalit har foydalanuvchi va manzil uchun alohida. Xato (400) bilan tugagan so‘rov kalitni band qilmaydi. Chiqim API’si ham shu qoidaga amal qiladi.

### 4.2 Kirimlarni ko‘rish

`GET /api/v1/receipts/?material=41&date_from=2026-11-01&date_to=2026-11-30&currency=USD` — eng yangisi birinchi. Har bir yozuv 4.1 dagi javob bilan bir xil shaklda, faqat `quantity_on_hand_after` maydonisiz qaytadi.
`GET /api/v1/receipts/{id}/` — bitta kirim.
`PUT`, `PATCH`, `DELETE` qo‘llab-quvvatlanmaydi (`405`). Xato kirim tuzatish harakati bilan to‘g‘rilanadi. **[PM: P5]**

## 5. Qoldiq va tarix · PCRM-42

`GET /api/v1/stock/?search=ldsp&category=3&below_min=true`

```json
{
  "material": {"id": 41, "display_name": "LDSP Egger · oq · 280×207×1.6", "unit": "sheet", "category": {"id": 3, "name": "LDSP"}},
  "quantity_on_hand": "35.00",
  "open_batches": 2,
  "min_quantity": "50.00",
  "is_below_min": true,
  "value_by_currency": [{"currency": "USD", "amount": "990.00"}]
}
```

- Ro‘yxatda hamma materiallar bor; kirimi bo‘lmagan material `quantity_on_hand: "0.00"`, `open_batches: 0`, `value_by_currency: []` bilan keladi. `GET /api/v1/stock/{material_id}/` — bitta qator.
- `min_quantity` — chegara qo‘yilmagan bo‘lsa `null`. `is_below_min` — chegara bor va qoldiq undan kam bo‘lsa `true`, aks holda `false`. `below_min=true` faqat shunday materiallarni qaytaradi.
- `value_by_currency` — qoldig‘i bor partiyalar bo‘yicha `quantity_remaining × unit_price` yig‘indisi, faqat USD. Narx ko‘rish ruxsati bo‘lmasa maydon javobda bo‘lmaydi.

`PATCH /api/v1/stock/{material_id}/` `{"min_quantity": "50.00"}` yoki `{"min_quantity": null}` — minimal chegarani admin belgilaydi (OQ-014). Ruxsat: `inventory.change_min_quantity`. `>= 0`, aks holda `400 min_value`. Javob — yangilangan qoldiq qatori. `PUT`, `POST`, `DELETE` yo‘q (`405`). Chegaradan pastga tushganda xabarnoma yuborish keyingi vazifada.

`GET /api/v1/stock/{material_id}/batches/` — qoldig‘i bor partiyalar: `id`, `received_on`, `quantity`, `quantity_remaining`, `unit_price`, `currency`. Eng eskisi birinchi keladi. Chiqim formasida partiya tanlash kerak bo‘lsa, shu ro‘yxat ishlatiladi. **[PM: P1]**

`GET /api/v1/movements/?material=41&type=receipt&date_from=2026-11-01`

```json
{
  "id": 880,
  "type": "receipt",
  "material": {"id": 41, "display_name": "LDSP Egger · oq · 280×207×1.6", "unit": "sheet"},
  "batch_id": 105,
  "quantity": "20.00",
  "quantity_on_hand_after": "35.00",
  "reference": {"kind": "receipt", "id": 105},
  "reason": "",
  "created_by": {"id": 7, "name": "Ombor mas’uli"},
  "created_at": "2026-11-18T14:05:00+05:00"
}
```

`quantity` musbat bo‘lsa qoldiq oshadi, manfiy bo‘lsa kamayadi. Harakatlar tarixi o‘zgartirilmaydi, unga faqat yangi yozuv qo‘shiladi.

## 6. Ombor moduli chegarasi · Akbar uchun

**Kelishilgan va kodda:** kirim (Ozodbek) va chiqim (Akbar, PR #34) bitta `inventory` ilovasida, bitta `StockBalance` qoldig‘ida ishlaydi; alohida qoldiq modeli yo‘q. Chiqim, qaytarish va hisobdan chiqarish hujjatlari — Akbarning modellari (PR #34, #35; [issues-api.md](issues-api.md), [returns-write-offs-api.md](returns-write-offs-api.md)).

| Model | Asosiy maydonlar | Kim yozadi |
|---|---|---|
| `Batch` (partiya = kirim) | `material` → `catalog.Material` (bigint), `received_on`, `quantity`, `quantity_remaining`, `total_amount`, `unit_price`, `currency`, `supplier`, `document_number`, `note`, `created_by`, `created_at` | Kirim yaratadi. `quantity_remaining` ni chiqim kamaytiradi, qaytarish oshiradi. |
| `StockBalance` | `material` (bitta qator, 1:1), `quantity_on_hand` | Faqat umumiy xizmat funksiyalari orqali. |
| `StockMovement` | `type` (`receipt`, `issue`, `return`, `write_off`, `adjustment`), `material`, `batch` (ixtiyoriy), `quantity` (± ishorali), `quantity_on_hand_after`, `reference_kind`, `reference_id`, `reason`, `created_by`, `created_at` | Har bir amal bitta yoki bir nechta harakat qo‘shadi. |
| `IdempotencyKey` | `key`, `user`, `endpoint`, `request_hash`, `response_status`, `response_body`, `created_at` | Kirim va chiqim POST’lari. |

Baza cheklovlari: `quantity_on_hand >= 0` va `0 <= quantity_remaining <= quantity` (OQ-006: manfiy qoldiq taqiqlanadi).

**Umumiy xizmat funksiyalari** (`inventory/services.py`). Qoldiqni faqat shular o‘zgartiradi, view yoki serializer to‘g‘ridan-to‘g‘ri o‘zgartirmaydi:

```python
def locked_balance(material) -> StockBalance: ...  # qoldiq qatorini qulflaydi
def ensure_available(balance, quantity) -> None: ...  # yetmasa InsufficientStockError
def receive(
    *, material, received_on, quantity, total_amount, user, currency="USD", **extra
) -> tuple[Batch, StockBalance]: ...
def decrease(
    *, material, quantity, movement_type, user, reference, allocations, reason=""
) -> list[StockMovement]: ...  # Akbar, PR #34
def increase(
    *, material, quantity, movement_type, user, reference, batch, reason=""
) -> StockMovement: ...  # Akbar, PR #35 (qaytarish)
```

- Tartib hamma joyda bir xil: avval `locked_balance()` (qoldiq qatori `select_for_update()`), keyin partiyalar `id` tartibida qulflanadi — parallel so‘rovlar navbat bilan bajariladi va bir-birini to‘sib qo‘ymaydi.
- Qoldiq tekshiruvi bitta joyda: `decrease()` ichida `ensure_available()`. Yetmasa `InsufficientStockError(available, requested)` → API `409 insufficient_stock`; tanlangan partiyada yetmasa `BatchUnavailableError` → `409 batch_insufficient`. Ikkala holatda tranzaksiya to‘liq ortga qaytadi.
- Harakat `reference_kind`: `receipt` (kirim id), `issue` (chiqim id), `return` (qaytarish id), `write_off` (hisobdan chiqarish id). Qaytarish va hisobdan chiqarish qoldiqni faqat tasdiqdan keyin o‘zgartiradi (OQ-003, OQ-007). Chiqim har partiya qismi uchun bitta manfiy harakat yozadi.
- `allocations` — qaysi partiyadan qancha olinishi. Tanlash qoidasi PM qaroriga bog‘liq. **[PM: P1]** Qaror chiqquncha xizmat partiyalarni ichida tanlamaydi: chaqiruvchi taqsimotni aniq beradi yoki bitta partiyani ko‘rsatadi.

## 7. Avtomatik sinovlar (hammasi yozilgan va CI’da o‘tadi)

Fayllar: `tests/test_inventory_receipts.py`, `tests/test_inventory_stock.py`, `tests/test_inventory_issues.py`, `tests/test_warehouse_ledger.py`, `tests/test_pcrm50_acceptance.py`.

1. Bir materialga ikki xil narxda kirim qilinadi → ikki partiya hosil bo‘ladi, `quantity_on_hand` ikkalasining yig‘indisiga teng, tarixda ikkita `receipt` harakati bor.
2. Bir xil `Idempotency-Key` va tana bilan ikki marta POST yuboriladi → bitta partiya, ikkinchi javob `200`. Kalit bir xil, `quantity` boshqa bo‘lsa → `409`.
3. `total_amount = 100.00` va `quantity = 3` yuboriladi → `unit_price = "33.333333"`, `total_amount` esa aynan `"100.00"` bo‘lib qoladi.
4. Narx ko‘rish ruxsati yo‘q foydalanuvchining javobida `total_amount`, `unit_price`, `currency` maydonlari yo‘q.
5. `inventory.add_receipt` ruxsati yo‘q foydalanuvchi kirim yuboradi → `403`. Tizimga kirmagan foydalanuvchi → `403` (SessionAuthentication).
6. Faol bo‘lmagan material, kelajak sana, `quantity = 0` → `400` va to‘g‘ri `code`.
7. Kirimi bor materialning `unit` maydonini o‘zgartirish → `409 material_has_history`.
8. Kirim ichida xato yuzaga keladi (masalan, harakat yozilmaydi) → partiya ham, qoldiq o‘zgarishi ham saqlanmaydi.
9. PostgreSQL’da ikki alohida ulanishdan bir vaqtda 7 tadan chiqim (qoldiq 10) → bittasi `201`, ikkinchisi `409`, qoldiq va partiya 3, chiqim hujjati bitta (`test_parallel_issues_never_make_stock_negative`).
12. Kirim → chiqim → qoldiq: qoldiq = ochiq partiyalar yig‘indisi = harakatlar yig‘indisi; rad etilgan chiqim hech narsani o‘zgartirmaydi; qaytarish va hisobdan chiqarish tasdiqdan keyin shu hisobni yuritadi; narx ruxsatisiz foydalanuvchi 11 ta ombor endpointida birorta narx maydonini olmaydi (`test_warehouse_ledger.py`).

10. USD qabul qilinadi, EUR kabi boshqa valyuta kodi rad etiladi.
11. Interfeysdagi uz/ru/en tanlovi saqlanadi. API xabarlari so‘ralgan tilga mos qaytadi, summa har uchala tilda USD bo‘lib qoladi.

## 8. PMga ochiq savollar (Team Lead orqali)

Bu savollar javobi chiqquncha shartnomadagi tegishli qism taklif sifatida qoladi. Qaror qabul qilingach, [qarorlar jurnaliga](../09-decisions/decision-log.md) yoziladi.

| # | Savol | Taklif | Ta’sir |
|---|---|---|---|
| P1 | Chiqimda material qaysi partiyadan olinadi: eng eskisidan (FIFO), omborchi tanlaganidan yoki boshqa usulda? (OQ-001 izohi) | Standart holatda FIFO (eng eski `received_on`), omborchi kerak bo‘lsa boshqa partiyani tanlay oladi. | Akbarning chiqim API’si, loyiha tannarxi |
| P2 · hal qilingan | Yagona valyuta nima? | 2026-11-18 foydalanuvchi qarori — faqat USD ($), kirim va xarajatlar ham USD. | Kirim formasi, qoldiq qiymati |
| P3 | Miqdor verguldan keyin necha xonagacha bo‘ladi? Masalan, 0.125 kg kley. (OQ-013 dagi «ikki xona» va «yaxlitlamaslik» ziddiyati) | 2 xona. Kerak bo‘lsa, 3 xonaga o‘tish bitta migratsiya bilan bajariladi. | Kirim/chiqim formalari, baza |
| P4 | «List» va «dona» alohida birliklarmi? (OQ-005) | Alohida birliklar (PR #11). | Katalog |
| P5 | Noto‘g‘ri yozilgan kirimni kim va qanday tuzatadi? | Admin sabab ko‘rsatib `adjustment` harakati yaratadi. Asl yozuv o‘zgarmaydi. | Kirim, tarix, ruxsatlar |

## 9. Bu versiyaga kirmaganlar

Login va rol boshqaruvi (Jamoliddin). Minimal chegaradan pastga tushganda xabarnoma (OQ-014) — alohida vazifa. Loyiha va ishchi havolalari: ular keyingi bosqichda bo‘lgani uchun `StockMovement.reference_kind/reference_id` orqali ulanadi, to‘g‘ridan-to‘g‘ri bog‘lanmaydi. Birliklar orasidagi konvertatsiya (OQ-005).


## Minimal qoldiq xabarlari · PR #46

- `GET /api/v1/notifications/?unread=true` — faqat joriy foydalanuvchining xabarlari, standart pagination (`count/next/results`). `unread` bo‘lmasa barchasi.
- `POST /api/v1/notifications/{id}/read/` — o‘qilgan deb belgilash; takror yuborish xavfsiz (200), boshqa xodim yozuvi 404.
- Ikkala amal ham `inventory.view_stock` talab qiladi. Maydonlar: `id`, `material`, `material_name`, `quantity`, `minimum`, `created_at`, `read_at`. Miqdorlar xabar vaqtidagi nusxa; narx yo‘q.
- Birinchi pastga o‘tishda faol ruxsatli xodimlarga yoziladi, qoldiq tiklanmaguncha takrorlanmaydi. Minimumni o‘rnatish ham joriy qoldiq past bo‘lsa xabar yaratadi. Tranzaksiya qaytsa xabar ham qaytadi. Eski qoldiqlar uchun `notify_low_stock` buyrug‘i takroriy xabar bermasdan ishlaydi.
