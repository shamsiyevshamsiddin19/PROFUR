# Qo‘shimcha xarajatlar API’si · v1

**2026-11-18 · Taklif, ko‘rib chiqish kutilmoqda.** Jira: [PCRM-46](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-46). Egasi: [Akbar (@thealiiheere)](https://github.com/thealiiheere).
Manbalar: TZ 6.6 va 6.8, [OQ-010](../01-requirements/open-questions.md), [valyuta va til qarori](../09-decisions/decision-log.md). Umumiy qoidalar (sana formati, sahifalash, o‘nlik sonlar satr ko‘rinishida) [ombor API shartnomasi](https://github.com/shamsiyevshamsiddin19/PROFUR/blob/docs/PCRM-49-api-contract/docs/06-api-contract/warehouse-api-v1.md) bilan bir xil.

## Qoidalar

- **Valyuta faqat USD.** `currency` ixtiyoriy, standart `"USD"`. Boshqa qiymat — `400`. Bazada ham cheklov bor.
- **Summa** satr ko‘rinishida: `"150.25"`. 0 dan katta, verguldan keyin ko‘pi bilan 2 xona. Server yaxlitlamaydi, ortiqcha xonani rad etadi.
- **Xarajat o‘chirilmaydi va tahrirlanmaydi** (TZ 6.8). `PUT`, `PATCH`, `DELETE` → `405`.
- **Til.** Xato matni `Accept-Language: uz | ru | en` bo‘yicha. Tur nomi `expense_type_name` va `name` maydonlarida shu tilda keladi. Tarjima bo‘lmasa o‘zbekcha nom qaytadi.
- **Loyiha.** `project_id` ixtiyoriy. Bo‘sh bo‘lsa — umumiy xarajat. Loyihalar moduli kelganda bu maydon loyihaga havola bo‘ladi.

## Ruxsatlar

| Amal | Ruxsat kodi |
|---|---|
| Xarajatlarni ko‘rish | `expenses.view_expense` |
| Xarajat kiritish | `expenses.add_expense` |
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
  "created_by": 3,
  "created_at": "2026-11-18T14:05:00+05:00"
}
```

`GET /api/v1/expenses/` — sahifalangan ro‘yxat, yangi sanalar birinchi. Ixtiyoriy filtrlar: `expense_type` (kod), `project_id`, `date_from`, `date_to` (`YYYY-MM-DD`, chegaralar kiradi). Noto‘g‘ri filtr → `400`.

`GET /api/v1/expenses/{id}/` — bitta xarajat.

## Xarajat turlari

`GET /api/v1/expense-types/` (`?is_active=true` — faqat faollari), `GET /api/v1/expense-types/{id}/`, `POST /api/v1/expense-types/`, `PATCH /api/v1/expense-types/{id}/`.

```json
{"id": 1, "code": "tax", "name": "Soliq", "name_uz": "Soliq", "name_ru": "Налог", "name_en": "Tax", "is_active": true}
```

Boshlang‘ich turlar migratsiya bilan qo‘shiladi: `tax` (Soliq), `products` (Mahsulot), `machine` (Stanok). `code` yaratilgandan keyin o‘zgarmaydi. Tur o‘chirilmaydi, `is_active: false` bilan yashiriladi. Faol bo‘lmagan turga yangi xarajat yozilmaydi.

## Ochiq savollar

| # | Savol | Hozirgi yechim |
|---|---|---|
| 1 | OQ-010: xarajat har doim loyihaga bog‘lanadimi? TZ 6.6 da loyiha ixtiyoriy («umumiy xarajat»). | `project_id` ixtiyoriy. Majburiy bo‘lsa, bitta tekshiruv qo‘shiladi. |
| 2 | «Produkta» nimani bildiradi: mahsulot yoki ishchilar ovqati? (TZ 19-bo‘lim, 3-savol) | Kod `products`, nomini admin o‘zgartira oladi. |
| 3 | Xato kiritilgan xarajat qanday bekor qilinadi? (TZ 6.8: teskari yozuv va sabab) | Hozir faqat yaratish. Bekor qilish keyingi bosqichda. |
| 4 | Umumiy xato shakli (`{"error": {...}}`, PCRM-49). | Hozircha DRF standart shakli: `{"maydon": ["xabar"]}`. |
