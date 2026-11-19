# Backend · Chiqim va xarajatlar

**Egasi** — [Akbar (@thealiiheere)](https://github.com/thealiiheere).

**Mas’uliyat** — Ombor amallari va xarajatlar API’si.

## Ish tartibi

Xarajatlar API’sini alohida tayyorlang. Loyiha havolasi shaklini PM qarori bilan aniqlang. Chiqimda partiya tanlash qarorini PCRM-31 orqali tekshiring. @ozodbek101 bilan qoldiq tranzaksiyasi va migratsiyalarni, @jamoliddinusarov1-create bilan tasdiqlovchi ruxsatlarni kelishing.

## Joriy natija · 2026-11-19

1-qismning texnik yig‘masi main’ga [PR #46](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/46) orqali birlashdi (`28d290c`). Team Lead qolgan ishlarni o‘z zimmasiga olib yakunladi, jamoaning mavjud kodi saqlandi. [CI #44449909326](https://github.com/shamsiyevshamsiddin19/PROFUR/actions/runs/44449909326): 231 backend, 10 frontend, 12 Chromium (telefon/planshet/desktop), Ruff/build/migratsiya va alohida PostgreSQL restore o‘tdi.

Admin akkaunt/rol va alohida xarajat turi ekranlari, saqlanadigan minimal qoldiq xabarlari va backup/restore vositalari mavjud. Ko‘rikdagi `*` vakolatini olib tashlash va xarajat turi sahifasining ruxsatlarini ajratish muammolari tuzatildi, regressiyalar o‘tdi. Main PR va uch majburiy CI tekshiruvi bilan himoyalangan.

[Topshirish reyestri](../docs/08-delivery/phase-one-acceptance.md) joriy manba. P1/P3/P5 yangi biznes qarorlari ochiq: hozir partiyalar qo‘lda aniq tanlanadi, miqdor 2 kasr xona, USD. Kirimni tuzatish API’si mavjud emas. Production timer/domen va PM/buyurtmachi jonli qabuli alohida; ular bajarilgan deb belgilanmagan. Quyidagi avvalgi kun qaydlari tarixiy; “navbatdagi ish”larni qayta boshlamang.

## Keyingi qadam

Team Lead bilan sinov muhitida ko‘rib chiqish; kerak bo‘lsa P1/P3/P5 ni tasdiqlash, keyin server/domen, kunlik zaxira va PM/xodimlar qabuli. Omborning mavjud API/UI ishlarini takrorlamang. Joriy Jira PCRM-5–9, PCRM-32/37/38–50 texnik vazifalari Done; kelgusi modullar bu doiraga kirmaydi.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-44](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-44) | Chiqim, qaytarish va hisobdan chiqarish | Bajarildi (texnik) | [PR #46](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/46), [CI 231/10/12](https://github.com/shamsiyevshamsiddin19/PROFUR/actions/runs/44449909326); joriy 1-qism doirasi. |
| [PCRM-46](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-46) | Qo‘shimcha xarajatlar modeli va API | Bajarildi (texnik) | [PR #46](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/46), [CI 231/10/12](https://github.com/shamsiyevshamsiddin19/PROFUR/actions/runs/44449909326); joriy 1-qism doirasi. |
| [PCRM-47](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-47) | Operatsiyalar tarixi API qismi. UI egasi frontend | Bajarildi (backend qismi) | Chiqim/qaytarish/hisobdan chiqarish harakatlari `/api/v1/movements/` ga `reference` bilan ulangan ([PR #35](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/35)), filtrlar material/tur/sana — Ozodbek [PR #27](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/27). UI — Shamsiddin [PR #39](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/39) |

**Qabul mezoni** — Parallel chiqimda qoldiq manfiy qolmaydi. Qayta yuborilgan so‘rov bitta harakat yozadi, tasdiqlash qoldiqni faqat bir marta o‘zgartiradi.

## Oxirgi qayd

`2026-11-18 · PCRM-46 · Ko‘rib chiqishda · `feat/PCRM-46-expense-idempotency` · tekshiruv: PR #34, #35 main’ga birlashgan va CI o‘tgan; PR #39 (frontend) xarajat POST’ida takroriy yuborish himoyasi yo‘qligini qayd etgan edi — `POST /expenses/` va `POST /expenses/{id}/reverse/` endi `Idempotency-Key` ni qabul qiladi (ixtiyoriy, eski mijoz buzilmaydi), ombor bilan bir xil kalitlar jadvali; umumiy mixin’da `replay_body()` qo‘shildi, xarajat javobidagi `currency` olib tashlanmaydi · sinov: 4 yangi sinov, tegishli 78 sinov o‘tdi · keyingi: Shamsiddin frontendda xarajat uchun kalit yuborsin; OQ-001 PM javobi; Jira yangilanmadi (Atlassian avtorizatsiyasi yo‘q)`

Avvalgi qayd: `2026-11-18 · PCRM-44 / PCRM-46 · Ko‘rib chiqishda · `feat/PCRM-44-returns-write-offs` (chiqim — PR #34 birlashgan) · qaytarish (OQ-003: asl chiqimga bog‘langan, ombor mas’uli tasdiqlaydi, material o‘z partiyasiga qaytadi, jami qaytarish asl chiqimdan oshmaydi — kutilayotganlar ham limitga kiradi, tasdiqda qulf ostida qayta tekshiriladi) va hisobdan chiqarish (OQ-007: sabab majburiy, admin tasdiqlaydi, qoldiq faqat tasdiqda kamayadi, tasdiqda qayta tekshiriladi); /api/v1/returns/ va /api/v1/write-offs/ (+ approve/reject), yaratish Idempotency-Key bilan, takroriy qaror harakat yozmaydi, qarama-qarshi qaror 409 already_decided; services.increase(); harakatlar /api/v1/movements/ da reference bilan, kutilayotgan so‘rov tarixda yo‘q · xarajat: POST /api/v1/expenses/{id}/reverse/ (teskari manfiy yozuv + sabab, ixtiyoriy to‘g‘ri yozuv bitta tranzaksiyada, asl yozuv o‘zgarmaydi, ikkinchi bekor 409), OQ-010 bo‘yicha project_id majburiy · tasdiqlanmagan: OQ-001 partiya tanlash — savol va A/B/C variantlar issues-api.md da, server partiyani o‘zi tanlamaydi · lokal (SQLite): pytest 188 o‘tdi, 5 tasi o‘tkazildi (PostgreSQL’ga xos); ruff va makemigrations --check toza; PostgreSQL sinovlari (7+7, parallel ikki marta tasdiq) CI’da · topshirildi: API — Shamsiddin, qoldiq integratsiyasi — Ozodbek, qabul ssenariylari — Jamoliddin (yangi PR izohlari) · Jira yangilanmadi: Atlassian ulanishi avtorizatsiya qilinmagan`

Undan oldingi qayd: `2026-11-18 · PCRM-46 · Jarayonda · xarajatlar API’si main’ga birlashdi: PR #18 (fefc0a7), CI’dagi Ruff hamda PostgreSQL’dagi test va migratsiya tekshiruvlari o‘tdi; PR #20 da admin panel himoyalandi · qolgan ish: noto‘g‘ri xarajatni teskari yozuv va sabab bilan bekor qilish (TZ 6.8, BR-12) — Team Lead qaydiga ko‘ra shusiz Bajarildi qilinmaydi · ochiq savol: OQ-010 va TZ 6.6 (loyiha majburiymi), [expenses-api.md](../docs/06-api-contract/expenses-api.md) · parallel: PCRM-40 birlashgani uchun PCRM-44 boshlanishi mumkin`

Eng avvalgi qayd: `2026-11-18 · PCRM-46 · Jarayonda · expenses ilovasi: xarajat turi (uz/ru/en nom, 3 ta boshlang‘ich tur) va xarajat (faqat USD, summa > 0, loyiha ixtiyoriy, o‘chirish/tahrirlash yo‘q), /api/v1/expenses/ va /api/v1/expense-types/, ru/en tarjimalar, ruxsat `accounts.permissions.HasPermissionCode` orqali (`expenses.*` kodlari) · main (#15) bilan birlashtirilgandan keyin pytest 50 o‘tdi, 2 tasi o‘tkazildi (SQLite), ruff check/format va makemigrations --check toza; PostgreSQL’da lokal sinov bajarilmadi (Docker ishlamayapti), CI tekshiradi · keyingi qadam: PR ko‘rigi (Shamsiddin, Jamoliddin); OQ-010 bo‘yicha savol [expenses-api.md](../docs/06-api-contract/expenses-api.md) da`

## Arxiv — avvalgi navbatdagi ish

Avvalgi 1–4 bandlar bajarildi (PCRM-46: #18, #35; PCRM-44: #34, #35; PostgreSQL 7+7 va ikki marta tasdiq sinovlari CI’da; PCRM-47 harakatlar ulanishi).

1. **OQ-001 (PM orqali Shamsiddin).** Javob kelsa, `services.decrease()` ga bitta taqsimlash funksiyasi qo‘shing (variantlar va tavsiya — [issues-api.md](../docs/06-api-contract/issues-api.md) oxirida). `allocations` yuborgan mijozlar o‘zgarishsiz ishlashi kerak.
2. **Xarajat takroriy yuborish himoyasi** — PR ko‘rigi va birlashtirish. Frontend kalit yubora boshlagach, sarlavhani majburiy qilish Shamsiddin bilan kelishiladi.
3. **Ruxsat kodlari (Jamoliddin).** `inventory.add_issue`, `inventory.add_return`, `inventory.approve_return`, `inventory.add_write_off`, `inventory.approve_write_off` (faqat admin), `expenses.reverse_expense` real rollarga berilganini tekshiring.
4. **Loyihalar moduli kelganda (keyingi bosqich).** `StockIssue.project_id` va `Expense.project_id` ni loyihaga havola (FK) qilish — OQ-010 integratsiya bosqichi.
5. **Jira.** PCRM-44/46/47 holatini shu jadvaldagi dalillar bilan yangilang.

## 2026-11-18 · Valyuta va til qarori

Chiqim tannarxi va barcha xarajatlar USD ($)da. Boshqa valyuta qiymatini API rad etsin. Xato va tasdiqlash xabarlari uz/ru/en tillariga mos bo‘lsin. [Qarorlar jurnali](../docs/09-decisions/decision-log.md).

## Birgalikdagi PR ko‘rigi · 2026-11-18

PR #16 (katalog), #17 (frontend) va #18 (xarajatlar) bir integratsiya tarmog‘ida tekshirildi. `config/urls.py` to‘qnashuvi ikkala API yo‘lini saqlab yechildi. Admin panelida xarajat turining kodi o‘zgarmas qilindi; xarajat yaratish muallifni server belgilaydigan API orqali amalga oshadi. Sessiya/CSRF va dinamik ruxsatlarni ikkala xizmatda tekshiruvchi integratsiya sinovi qo‘shildi.

Lokal: 76 backend testi o‘tdi, 2 PostgreSQL cheklovi sinovi SQLite’da o‘tkazildi; qo‘shimcha 2 integratsiya sinovi ham o‘tdi. Frontend build va 3 testi o‘tdi. PostgreSQL cheklovlari birlashtirish PR’ining CI’sida tekshiriladi. Katalog API va frontend ro‘yxati mavjud; kirim/partiya/qoldiq backend hali PCRM-40/42 vazifasi. PCRM-39 to‘liq UI mezonlari, PCRM-48 barcha sahifalar va PCRM-46 teskari yozuv jarayoni avtomatik Done qilinmaydi.

## PCRM-44 · 1-qism · 2026-11-18

`2026-11-18 · PCRM-44 · Jarayonda · chiqim: StockIssue va StockIssueAllocation modellari, services.decrease() va issue_stock() (avval qoldiq, keyin partiyalar id tartibida qulflanadi), POST/GET /api/v1/issues/ (Idempotency-Key majburiy, 409 insufficient_stock va batch_insufficient, narx OQ-041 bo‘yicha yashiriladi, PUT/PATCH/DELETE 405), tannarx partiya narxida USD, ru/en tarjimalar · partiyani mijoz tanlaydi, chunki OQ-001 PM’da · PR #27 (PCRM-42) ustiga qurilgan, avval u birlashishi kerak · lokal (SQLite): pytest 144 o‘tdi, 3 tasi o‘tkazildi; ruff va makemigrations --check toza; PostgreSQL’dagi «10 dan 7 + 7» parallel sinovi CI’da · keyingi qadam: qaytarish so‘rovi va tasdiqlash (OQ-003), keyin hisobdan chiqarish (OQ-007); `inventory.add_issue` kodini rollarga berish — Jamoliddin`


## PR #35 · ko‘rik tuzatishi · 2026-11-18

`2026-11-18 · PCRM-44 / PCRM-46 · Ko‘rikda · PR #35: qaytarish so‘rovi, tasdiq/rad, hisobdan chiqarish, xarajatni teskari yozuv bilan bekor qilish. Ko‘rikda topilgan OQ-041 xatosi (#36) tuzatildi: kirim/chiqim/qaytarish/hisobdan chiqarishda idempotent javob ham joriy narx ruxsatiga mos filtrlanadi, saqlangan javob va biznes amal o‘zgarmaydi · 4 yangi endpoint regressiya testi tuzatishdan oldin yiqildi, keyin o‘tdi; Ruff check/format, makemigrations --check va diff tekshiruvi toza · keyingi qadam: yangilangan PR CI (PostgreSQL va real brauzer) o‘tgach main’ga birlashtirish. OQ-001 algoritm qarori va to‘liq frontend qabul mezonlari alohida qoladi.`
