# Backend · Katalog, kirim va qoldiq

**Egasi** — [@ozodbek101](https://github.com/ozodbek101).

**Mas’uliyat** — Katalog va qoldiq modellari, migratsiyalar va kirim API’si.

## Ish tartibi

Avval frontend bilan kirim so‘rovi, javobi va xatolarini kelishing. Material va partiyani ajrating. Kirim va qoldiqni bitta tranzaksiyada yozing. Qoldiqni o‘zgartiradigan umumiy amalni Akbar (@thealiiheere) bilan kelishing va birgalikda tekshiring.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-38](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-38) | Kategoriya va material modellari. Partiya PCRM-40 bilan | Bajarildi | [PR #11](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/11) → [#15](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/15) main’da, CI o‘tgan |
| [PCRM-39](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-39) | Katalog API qismi. UI egasi frontend | Jarayonda | branch `feat/PCRM-39-catalog-api` |
| [PCRM-40](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-40) | Kirim API’si va birlik narxi | Reja | — |
| [PCRM-42](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-42) | Qoldiq, minimal chegara va manfiy qoldiqni bloklash | Reja | — |
| [PCRM-49](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-49) | ERD va API shartnomasini yig‘ish | Jarayonda | Katalog/kirim/qoldiq qismi [PR #13](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/13) → [#15](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/15) main’da; chiqim/xarajat qismi Akbar bilan |

**Qabul mezoni** — Bir materialning ikki xil narxdagi kirimi alohida partiya bo‘ladi. API javobi, qoldiq va harakat tarixi mos keladi.

## Oxirgi qayd

2026-11-18 · PCRM-38 · Ko‘rikda · `catalog` ilovasi: Category, Material, Unit, 0001_initial migratsiyasi, admin, docs/05-data-model dagi taklif · PostgreSQL 16 da ruff, makemigrations --check va pytest (15 ta) o‘tdi, [PR #11](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/11) · Akbar va Jamoliddin ko‘rigi, «list/dona» bo‘yicha Team Lead javobi; keyingi ish — PCRM-49 API shartnomasi

2026-11-18 · PCRM-49 · Jarayonda · `docs/06-api-contract/warehouse-api-v1.md`: katalog, kirim (idempotentlik, summa → birlik narxi), qoldiq va tarix API’si, ruxsat kodlari, `inventory` moduli chegarasi, PMga 5 ta savol · Faqat hujjat, kod sinovi yo‘q; PR #11 ustiga qurilgan · Shamsiddin (forma), Akbar (`inventory` xizmatlari), Jamoliddin (xato shakli, ruxsatlar) bilan kelishish; P1–P5 ni Team Lead orqali PMga

2026-11-18 · PCRM-39 · Ko‘rikda · `/api/v1/categories/` va `/api/v1/materials/`: ro‘yxat, qidiruv/filtr, yaratish, PATCH; ruxsat `accounts.permissions.HasPermissionCode` va shartnoma kodlari (`catalog.view_material`, `catalog.add_material` …) bilan; `material_duplicate` + `existing_id`, `category_inactive`; DELETE/PUT yo‘q · main (#15) ustida PostgreSQL 18’da pytest 56 ta o‘tdi, ruff va makemigrations --check toza · Jira’da PCRM-39 Shamsiddinga biriktirilgan — backend qismini kelishish; `quantity_on_hand` va `material_has_history` PCRM-40 da; standart rollarga `catalog.*` kodlarini qo‘shishni Jamoliddin bilan kelishish

## Navbatdagi ish

1. **PCRM-38** bilan boshlang. Main’dagi Django asosini oling. requirements.txt, settings.py, OQ-005 va OQ-008 hamda ma’lumotlar modelini tekshiring. Katalog va kirim partiyasini ajratish, birliklar, o‘lchamlar va majburiy maydonlar bo‘yicha kichik model taklifini docs/05-data-model ichidagi mavjud hujjatda yozing. Birinchi ishlaydigan kategoriya/material modeli, migratsiya va haqiqiy saqlash sinovini PR qiling.
2. **PCRM-39 / PCRM-49** doirasida kategoriya/material qidiruvi va kirim so‘rovining API manzili, maydonlari, majburiyligi, xato va javob namunalarini docs/06-api-contract ichidagi hujjatda aniqlang. Shamsiddin va Akbar uchun tayyor qismini yozing.
3. **PCRM-40** bilan kirimni bazaga saqlash, asl narx/valyuta, birlik narxi, qoldiq va tarixni bitta tranzaksiyada yozishni quring. Har xil narxdagi ikki partiya va takror so‘rov sinovini bajaring. Yaxlitlash yoki partiya tanlashdagi ochiq qarorni PMga qayd eting.
4. **PCRM-42** uchun mavjud qoldiq, minimal chegara va chiqim bilan umumiy qoldiq tekshiruvini Akbar bilan kelishing.

Boshlashda har bir band allaqachon kod yoki PR’da bajarilganini tekshiring. Akbarga model nomi, identifikator, migratsiya va qoldiq amalining kirish/chiqishini aniq topshiring.

## 2026-11-18 · Valyuta va til qarori

Barcha kirimlar, birlik narxi va qoldiq qiymati faqat USD. API boshqa valyutani rad etsin. API shartnomasidagi ko‘p valyutali misollarni USD bilan moslashtiring. Xato xabarlari uz/ru/en tillariga mos bo‘lsin. [Qarorlar jurnali](../docs/09-decisions/decision-log.md).

## Birlashtirish tekshiruvi · 2026-11-18

PR #11, #12 va #13 bitta integratsiya tarmog‘ida tekshirildi. Katalogning 9 ta boshlang‘ich kategoriyasi migratsiyada qo‘shildi. Login CSRF va uch til sinovlari saqlandi, dinamik ruxsatni berish/olib tashlash regressiya sinovlari qo‘shildi. Holat — main’ga birlashtirish uchun tekshiruvda. Keyingi ish — PCRM-39/40 va frontend bilan kirimni ulash.
