# Qo‘shimcha xarajatlar API’si · v1

**2026-11-18 · Taklif, ko‘rib chiqish kutilmoqda.** Jira: [PCRM-46](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-46). Egasi: [Akbar (@thealiiheere)](https://github.com/thealiiheere).
Manbalar: TZ 6.6 va 6.8, [OQ-010](../01-requirements/open-questions.md), [valyuta va til qarori](../09-decisions/decision-log.md). Umumiy qoidalar (sana formati, sahifalash, o‘nlik sonlar satr ko‘rinishida) [ombor API shartnomasi](warehouse-api-v1.md) bilan bir xil.

## Qoidalar

- **Valyuta faqat USD.** `currency` ixtiyoriy, standart `"USD"`. Boshqa qiymat — `400`. Bazada ham cheklov bor.
- **Summa** satr ko‘rinishida: `"150.25"`. 0 dan katta, verguldan keyin ko‘pi bilan 2 xona. Server yaxlitlamaydi, ortiqcha xonani rad etadi.
- **Xarajat o‘chirilmaydi va tahrirlanmaydi** (TZ 6.8). `PUT`, `PATCH`, `DELETE` → `405`. Xato yozuv teskari yozuv bilan bekor qilinadi — pastdagi «Bekor qilish va tuzatish» bo‘limi.
- **Til.** Xato matni `Accept-Language: uz | ru | en` bo‘yicha. Tur nomi `expense_type_name` va `name` maydonlarida shu tilda keladi. Tarjima bo‘lmasa o‘zbekcha nom qaytadi.
- **Loyiha majburiy** (OQ-010, PM tasdiqlagan: har bir qo‘shimcha xarajat aniq loyihaga biriktiriladi). `project_id` yuborilmasa yoki `null` bo‘lsa — `400`. Loyihalar moduli 1-qismdan keyin keladi, shuning uchun raqam hozircha mavjud loyihalar ro‘yxati bilan tekshirilmaydi; modul kelganda maydon loyihaga havola (FK) bo‘ladi. Bazadagi ustun eski yozuvlar uchun `null` ga ruxsat beradi.

## Ruxsatlar

| Amal | Ruxsat kodi |
|---|---|
| Xarajatlarni ko‘rish | `expenses.view_expense` |
| Xarajat kiritish | `expenses.add_expense` |
| Xarajatni bekor qilish / tuzatish | `expenses.reverse_expense` |
| Turlarni ko‘rish | `expenses.view_expensetype` |
| Tur qo‘shish / tahrirlash | `expenses.add_expensetype` / `expenses.change_expensetype` |

Tekshiruv `accounts.permissions.HasPermissionCode` orqali ([auth-api.md](auth-api.md)): kod foydalanuvchi rolidagi `Role.permissions` ro‘yxatida aynan shu ko‘rinishda bo‘lishi kerak. Administrator kodlarni ombor mas’uli kabi rollarga beradi. Ishchi roli bu kodlarni olmaydi (TZ 3: ishchi pulni ko‘rmaydi). Ruxsat yo‘q yoki tizimga kirilmagan — `403`.

## Xarajatlar

`POST /api/v1/expenses/`

```json
{
  "expense_type": "tax",
  "amount": "150.25",
  "currency": "USD",
  "spent_on": "2026-11-18",
  "project_id": 7,
  "note": "Noyabr solig‘i"
}
```

Javob `201`:

```json
{
  "id": 1,
  "expense_type": "tax",
  "expense_type_name": "Soliq",
  "amount": "150.25",
  "currency": "USD",
  "spent_on": "2026-11-18",
  "project_id": 7,
  "note": "Noyabr solig‘i",
  "reverses": null,
  "reversal": null,
  "created_by": 3,
  "created_at": "2026-11-18T14:05:00+05:00"
}
```

`GET /api/v1/expenses/` — sahifalangan ro‘yxat, yangi sanalar birinchi. Ixtiyoriy filtrlar: `expense_type` (kod), `project_id`, `date_from`, `date_to` (`YYYY-MM-DD`, chegaralar kiradi). Noto‘g‘ri filtr → `400`.

`GET /api/v1/expenses/{id}/` — bitta xarajat.

## Bekor qilish va tuzatish (TZ 6.8, BR-11/12)

Asl yozuv o‘chirilmaydi va o‘zgarmaydi. Uni **teskari yozuv** bekor qiladi: o‘sha tur, valyuta va loyiha, summasi manfiy, `note` — sabab, `reverses` — asl yozuv raqami, sanasi — bugun. Shu sabab barcha yozuvlar `amount` yig‘indisi doim to‘g‘ri (bekor qilingan xarajat 0 beradi) va hisobotda ikki marta hisoblanmaydi.

`POST /api/v1/expenses/{id}/reverse/` (ruxsat `expenses.reverse_expense`)

```json
{
  "reason": "Summa xato kiritilgan",
  "replacement": {"expense_type": "tax", "amount": "105.25", "spent_on": "2026-11-10", "project_id": 7}
}
```

`replacement` ixtiyoriy: berilsa, to‘g‘ri yangi yozuv teskari yozuv bilan **bitta tranzaksiyada** qo‘shiladi (BR-12: teskari yozuv + to‘g‘ri yozuv). U oddiy `POST /expenses/` kabi tekshiriladi; xato bo‘lsa `400` va hech narsa saqlanmaydi.

Javob `201`:

```json
{
  "reversal": {"id": 9, "amount": "-150.25", "reverses": 1, "note": "Summa xato kiritilgan", "...": "..."},
  "replacement": {"id": 10, "amount": "105.25", "reverses": null, "...": "..."}
}
```

Asl yozuvda shundan keyin `"reversal": {"id": 9, "reason": "…", "created_by": 3, "created_at": "…"}` ko‘rinadi — frontend uni «Bekor qilingan» deb belgilaydi.

| Holat | Javob |
|---|---|
| Sabab bo‘sh | `400` (`reason`) |
| Yozuv avval bekor qilingan (ikki marta bosish ham) | `409`, `code = "already_reversed"` |
| Teskari yozuvning o‘zini bekor qilish | `409`, `code = "reversal_not_reversible"` |
| Ruxsat yo‘q | `403` |

Bekor qilish uchun alohida tasdiqlash bosqichi TZ/OQ’da belgilanmagan, shuning uchun qo‘shilmadi: ruxsat kodi kimga berilishini admin hal qiladi.

## Xarajat turlari

`GET /api/v1/expense-types/` (`?is_active=true` — faqat faollari), `GET /api/v1/expense-types/{id}/`, `POST /api/v1/expense-types/`, `PATCH /api/v1/expense-types/{id}/`.

```json
{"id": 1, "code": "tax", "name": "Soliq", "name_uz": "Soliq", "name_ru": "Налог", "name_en": "Tax", "is_active": true}
```

Boshlang‘ich turlar migratsiya bilan qo‘shiladi: `tax` (Soliq), `products` (Mahsulot), `machine` (Stanok). `code` yaratilgandan keyin o‘zgarmaydi. Tur o‘chirilmaydi, `is_active: false` bilan yashiriladi. Faol bo‘lmagan turga yangi xarajat yozilmaydi.

## Ochiq savollar

| # | Savol | Hozirgi yechim |
|---|---|---|
| 1 | ~~OQ-010: xarajat har doim loyihaga bog‘lanadimi?~~ | **Yopildi.** PM: aniq loyihaga biriktiriladi — `project_id` majburiy (2026-11-18). Ochiq qolgani faqat loyihalar moduli bilan integratsiya bosqichi. |
| 2 | «Produkta» nimani bildiradi: mahsulot yoki ishchilar ovqati? (TZ 19-bo‘lim, 3-savol) | Kod `products`, nomini admin o‘zgartira oladi. |
| 3 | ~~Xato kiritilgan xarajat qanday bekor qilinadi?~~ | **Yopildi.** TZ 6.8/BR-12 bo‘yicha teskari yozuv + ixtiyoriy to‘g‘ri yozuv, `POST /expenses/{id}/reverse/`. |
| 4 | Umumiy xato shakli (`{"error": {...}}`, PCRM-49). | Hozircha DRF standart shakli: `{"maydon": ["xabar"]}`. |
