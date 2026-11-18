# Backend · Chiqim va xarajatlar

**Egasi** — [Akbar (@thealiiheere)](https://github.com/thealiiheere).

**Mas’uliyat** — Ombor amallari va xarajatlar API’si.

## Ish tartibi

Xarajatlar API’sini alohida tayyorlang. Loyiha havolasi shaklini PM qarori bilan aniqlang. Chiqimda partiya tanlash qarorini PCRM-31 orqali tekshiring. @ozodbek101 bilan qoldiq tranzaksiyasi va migratsiyalarni, @jamoliddinusarov1-create bilan tasdiqlovchi ruxsatlarni kelishing.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-44](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-44) | Chiqim, qaytarish va hisobdan chiqarish | Reja | — |
| [PCRM-46](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-46) | Qo‘shimcha xarajatlar modeli va API | Jarayonda | `akbar` branch (73e1691), [expenses-api.md](../docs/06-api-contract/expenses-api.md) |
| [PCRM-47](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-47) | Operatsiyalar tarixi API qismi. UI egasi frontend | Reja | — |

**Qabul mezoni** — Parallel chiqimda qoldiq manfiy qolmaydi. Qayta yuborilgan so‘rov bitta harakat yozadi, tasdiqlash qoldiqni faqat bir marta o‘zgartiradi.

## Oxirgi qayd

`2026-11-18 · PCRM-46 · Jarayonda · expenses ilovasi: xarajat turi (uz/ru/en nom, 3 ta boshlang‘ich tur) va xarajat (faqat USD, summa > 0, loyiha ixtiyoriy, o‘chirish/tahrirlash yo‘q), /api/v1/expenses/ va /api/v1/expense-types/, ru/en tarjimalar, ruxsat `accounts.permissions.HasPermissionCode` orqali (`expenses.*` kodlari) · main (#15) bilan birlashtirilgandan keyin pytest 50 o‘tdi, 2 tasi o‘tkazildi (SQLite), ruff check/format va makemigrations --check toza; PostgreSQL’da lokal sinov bajarilmadi (Docker ishlamayapti), CI tekshiradi · keyingi qadam: PR ko‘rigi (Shamsiddin, Jamoliddin); OQ-010 bo‘yicha savol [expenses-api.md](../docs/06-api-contract/expenses-api.md) da`

## Navbatdagi ish

1. **PCRM-46** bilan boshlang. Main’dagi Django va docs/06-api-contract hujjatini o‘qing. Xarajat turi, summa, valyuta, sana va loyiha havolasini tekshiring. OQ-010 bo‘yicha loyiha havolasi kelishilmagan bo‘lsa, muqobil usullarni PM uchun yozing. Mustaqil xarajat validatsiyasi va uning sinovlarini tayyorlang, saqlash/API yo‘lini kelishilgan shartnoma bilan tugating.
2. **PCRM-44** oldidan Ozodbek yaratgan katalog, partiya va qoldiq modelini tekshiring. Chiqim, qaytarish so‘rovi, hisobdan chiqarish so‘rovi hamda kim tasdiqlashini OQ-002,003,006,007 bilan moslashtiring. Yangi qoldiq modeli yaratish o‘rniga mavjud model bilan ishlang.
3. Qoldiq 10 bo‘lganda ikki alohida ulanishdan 7 tadan chiqim, qayta yuborilgan so‘rov va ikki marta tasdiqlash uchun PostgreSQL sinovini quring. Qaytarish asl chiqimning qaytarilmagan qismidan oshmasin.
4. **PCRM-47** da sana, amal va material bo‘yicha filtrlanadigan tarix API’sini Shamsiddin bilan kelishing. Ruxsat sinovini Jamoliddin accounts yechimi bilan bajaring.

Har bir bandning mavjud PR yoki kodda bajarilganini tekshirib navbatdagi ishga o‘ting. Ozodbekka kerakli umumiy model o‘zgarishini bitta aniq diff bilan taklif qiling.

## 2026-11-18 · Valyuta va til qarori

Chiqim tannarxi va barcha xarajatlar USD ($)da. Boshqa valyuta qiymatini API rad etsin. Xato va tasdiqlash xabarlari uz/ru/en tillariga mos bo‘lsin. [Qarorlar jurnali](../docs/09-decisions/decision-log.md).
