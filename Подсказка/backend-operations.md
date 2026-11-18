# Backend · Chiqim va xarajatlar

**Egasi** — [Akbar (@thealiiheere)](https://github.com/thealiiheere).

**Mas’uliyat** — Ombor amallari va xarajatlar API’si.

## Ish tartibi

Xarajatlar API’sini alohida tayyorlang. Loyiha havolasi shaklini PM qarori bilan aniqlang. Chiqimda partiya tanlash qarorini PCRM-31 orqali tekshiring. @ozodbek101 bilan qoldiq tranzaksiyasi va migratsiyalarni, @jamoliddinusarov1-create bilan tasdiqlovchi ruxsatlarni kelishing.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-44](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-44) | Chiqim, qaytarish va hisobdan chiqarish | Ko‘rib chiqishda | Chiqim — [PR #34](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/34) birlashgan; qaytarish va hisobdan chiqarish — `feat/PCRM-44-returns-write-offs`; [issues-api.md](../docs/06-api-contract/issues-api.md), [returns-write-offs-api.md](../docs/06-api-contract/returns-write-offs-api.md). Ochiq: OQ-001 partiya tanlash (PM) |
| [PCRM-46](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-46) | Qo‘shimcha xarajatlar modeli va API | Ko‘rib chiqishda | API [PR #18](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/18) birlashgan; teskari yozuv bilan bekor qilish/tuzatish va majburiy loyiha (OQ-010) — `feat/PCRM-44-returns-write-offs`. [expenses-api.md](../docs/06-api-contract/expenses-api.md) |
| [PCRM-47](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-47) | Operatsiyalar tarixi API qismi. UI egasi frontend | Jarayonda | Chiqim/qaytarish/hisobdan chiqarish harakatlari `/api/v1/movements/` ga `reference` bilan ulangan (`feat/PCRM-44-returns-write-offs`); tarix API’si — Ozodbek [PR #27](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/27) birlashgan |

**Qabul mezoni** — Parallel chiqimda qoldiq manfiy qolmaydi. Qayta yuborilgan so‘rov bitta harakat yozadi, tasdiqlash qoldiqni faqat bir marta o‘zgartiradi.

## Oxirgi qayd

`2026-11-18 · PCRM-44 / PCRM-46 · Ko‘rib chiqishda · `feat/PCRM-44-returns-write-offs` (chiqim — PR #34 birlashgan) · qaytarish (OQ-003: asl chiqimga bog‘langan, ombor mas’uli tasdiqlaydi, material o‘z partiyasiga qaytadi, jami qaytarish asl chiqimdan oshmaydi — kutilayotganlar ham limitga kiradi, tasdiqda qulf ostida qayta tekshiriladi) va hisobdan chiqarish (OQ-007: sabab majburiy, admin tasdiqlaydi, qoldiq faqat tasdiqda kamayadi, tasdiqda qayta tekshiriladi); /api/v1/returns/ va /api/v1/write-offs/ (+ approve/reject), yaratish Idempotency-Key bilan, takroriy qaror harakat yozmaydi, qarama-qarshi qaror 409 already_decided; services.increase(); harakatlar /api/v1/movements/ da reference bilan, kutilayotgan so‘rov tarixda yo‘q · xarajat: POST /api/v1/expenses/{id}/reverse/ (teskari manfiy yozuv + sabab, ixtiyoriy to‘g‘ri yozuv bitta tranzaksiyada, asl yozuv o‘zgarmaydi, ikkinchi bekor 409), OQ-010 bo‘yicha project_id majburiy · tasdiqlanmagan: OQ-001 partiya tanlash — savol va A/B/C variantlar issues-api.md da, server partiyani o‘zi tanlamaydi · lokal (SQLite): pytest 188 o‘tdi, 5 tasi o‘tkazildi (PostgreSQL’ga xos); ruff va makemigrations --check toza; PostgreSQL sinovlari (7+7, parallel ikki marta tasdiq) CI’da · topshirildi: API — Shamsiddin, qoldiq integratsiyasi — Ozodbek, qabul ssenariylari — Jamoliddin (yangi PR izohlari) · Jira yangilanmadi: Atlassian ulanishi avtorizatsiya qilinmagan`

Avvalgi qayd: `2026-11-18 · PCRM-46 · Jarayonda · xarajatlar API’si main’ga birlashdi: PR #18 (fefc0a7), CI’dagi Ruff hamda PostgreSQL’dagi test va migratsiya tekshiruvlari o‘tdi; PR #20 da admin panel himoyalandi · qolgan ish: noto‘g‘ri xarajatni teskari yozuv va sabab bilan bekor qilish (TZ 6.8, BR-12) — Team Lead qaydiga ko‘ra shusiz Bajarildi qilinmaydi · ochiq savol: OQ-010 va TZ 6.6 (loyiha majburiymi), [expenses-api.md](../docs/06-api-contract/expenses-api.md) · parallel: PCRM-40 birlashgani uchun PCRM-44 boshlanishi mumkin`

Undan oldingi qayd: `2026-11-18 · PCRM-46 · Jarayonda · expenses ilovasi: xarajat turi (uz/ru/en nom, 3 ta boshlang‘ich tur) va xarajat (faqat USD, summa > 0, loyiha ixtiyoriy, o‘chirish/tahrirlash yo‘q), /api/v1/expenses/ va /api/v1/expense-types/, ru/en tarjimalar, ruxsat `accounts.permissions.HasPermissionCode` orqali (`expenses.*` kodlari) · main (#15) bilan birlashtirilgandan keyin pytest 50 o‘tdi, 2 tasi o‘tkazildi (SQLite), ruff check/format va makemigrations --check toza; PostgreSQL’da lokal sinov bajarilmadi (Docker ishlamayapti), CI tekshiradi · keyingi qadam: PR ko‘rigi (Shamsiddin, Jamoliddin); OQ-010 bo‘yicha savol [expenses-api.md](../docs/06-api-contract/expenses-api.md) da`

## Navbatdagi ish

1. **PCRM-46** bilan boshlang. Main’dagi Django va docs/06-api-contract hujjatini o‘qing. Xarajat turi, summa, valyuta, sana va loyiha havolasini tekshiring. OQ-010 bo‘yicha loyiha havolasi kelishilmagan bo‘lsa, muqobil usullarni PM uchun yozing. Mustaqil xarajat validatsiyasi va uning sinovlarini tayyorlang, saqlash/API yo‘lini kelishilgan shartnoma bilan tugating.
2. **PCRM-44** oldidan Ozodbek yaratgan katalog, partiya va qoldiq modelini tekshiring. Chiqim, qaytarish so‘rovi, hisobdan chiqarish so‘rovi hamda kim tasdiqlashini OQ-002,003,006,007 bilan moslashtiring. Yangi qoldiq modeli yaratish o‘rniga mavjud model bilan ishlang.
3. Qoldiq 10 bo‘lganda ikki alohida ulanishdan 7 tadan chiqim, qayta yuborilgan so‘rov va ikki marta tasdiqlash uchun PostgreSQL sinovini quring. Qaytarish asl chiqimning qaytarilmagan qismidan oshmasin.
4. **PCRM-47** da sana, amal va material bo‘yicha filtrlanadigan tarix API’sini Shamsiddin bilan kelishing. Ruxsat sinovini Jamoliddin accounts yechimi bilan bajaring.

Har bir bandning mavjud PR yoki kodda bajarilganini tekshirib navbatdagi ishga o‘ting. Ozodbekka kerakli umumiy model o‘zgarishini bitta aniq diff bilan taklif qiling.

## 2026-11-18 · Valyuta va til qarori

Chiqim tannarxi va barcha xarajatlar USD ($)da. Boshqa valyuta qiymatini API rad etsin. Xato va tasdiqlash xabarlari uz/ru/en tillariga mos bo‘lsin. [Qarorlar jurnali](../docs/09-decisions/decision-log.md).

## Birgalikdagi PR ko‘rigi · 2026-11-18

PR #16 (katalog), #17 (frontend) va #18 (xarajatlar) bir integratsiya tarmog‘ida tekshirildi. `config/urls.py` to‘qnashuvi ikkala API yo‘lini saqlab yechildi. Admin panelida xarajat turining kodi o‘zgarmas qilindi; xarajat yaratish muallifni server belgilaydigan API orqali amalga oshadi. Sessiya/CSRF va dinamik ruxsatlarni ikkala xizmatda tekshiruvchi integratsiya sinovi qo‘shildi.

Lokal: 76 backend testi o‘tdi, 2 PostgreSQL cheklovi sinovi SQLite’da o‘tkazildi; qo‘shimcha 2 integratsiya sinovi ham o‘tdi. Frontend build va 3 testi o‘tdi. PostgreSQL cheklovlari birlashtirish PR’ining CI’sida tekshiriladi. Katalog API va frontend ro‘yxati mavjud; kirim/partiya/qoldiq backend hali PCRM-40/42 vazifasi. PCRM-39 to‘liq UI mezonlari, PCRM-48 barcha sahifalar va PCRM-46 teskari yozuv jarayoni avtomatik Done qilinmaydi.

## PCRM-44 · 1-qism · 2026-11-18

`2026-11-18 · PCRM-44 · Jarayonda · chiqim: StockIssue va StockIssueAllocation modellari, services.decrease() va issue_stock() (avval qoldiq, keyin partiyalar id tartibida qulflanadi), POST/GET /api/v1/issues/ (Idempotency-Key majburiy, 409 insufficient_stock va batch_insufficient, narx OQ-041 bo‘yicha yashiriladi, PUT/PATCH/DELETE 405), tannarx partiya narxida USD, ru/en tarjimalar · partiyani mijoz tanlaydi, chunki OQ-001 PM’da · PR #27 (PCRM-42) ustiga qurilgan, avval u birlashishi kerak · lokal (SQLite): pytest 144 o‘tdi, 3 tasi o‘tkazildi; ruff va makemigrations --check toza; PostgreSQL’dagi «10 dan 7 + 7» parallel sinovi CI’da · keyingi qadam: qaytarish so‘rovi va tasdiqlash (OQ-003), keyin hisobdan chiqarish (OQ-007); `inventory.add_issue` kodini rollarga berish — Jamoliddin`
