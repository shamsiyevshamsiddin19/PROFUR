# Login, ruxsatlar, test va CI

**Egasi** — [@jamoliddinusarov1-create](https://github.com/jamoliddinusarov1-create).

**Mas’uliyat** — Ishga tushirish yo‘riqnomasi, kirish va ruxsat moduli, CI hamda tizim sinovlari.

## Ish tartibi

Avval umumiy ishga tushirish tartibi, muhit sozlamasi namunasi va tekshiruv buyruqlarini tayyorlang. Login va ombor rol huquqlarini backendchilar bilan kelishing. Har bir dasturchi o‘z funksiyasining testini yozadi. Siz foydalanuvchi oqimini birlashtirib tekshirasiz.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-32](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-32) | Login/session, ombor ruxsatlari va admin foydalanuvchi boshqaruvi (OQ-040) | Bajarildi | [#12](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/12), [commit `f0078b2`] |
| [PCRM-37](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-37) | Ishga tushirish sozlamalari, PostgreSQL, backup/restore, frontend build va CI | Bajarildi | [#8](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/8), [backup-restore.md](../docs/08-delivery/backup-restore.md) |
| [PCRM-50](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-50) | Qabul sinovlari, PostgreSQL parallel konkurentlik va 3 ekranli Chromium E2E | Bajarildi | [#26](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/26), [tests/test_concurrency_postgres.py](../tests/test_concurrency_postgres.py), [frontend/e2e/receipt.spec.ts](../frontend/e2e/receipt.spec.ts) |

**Qabul mezoni** — To‘rt jamoadosh loyihani toza muhitda ishga tushira oladi. Ruxsatsiz amal rad etiladi. Haqiqiy PostgreSQL'da parallel amallar qoldiqni buzmaydi. Brauzerda mobil, planshet va kompyuter ekranlarida to'liq oqim va uch tilda barqaror ishlaydi.

## Jamoadoshlarga topshirish (Handoff)

- **PCRM-32 & OQ-040 (Foydalanuvchilar va Rollar):**
  - Foydalanuvchilarni to'liq boshqarish API'si tayyorlandi: `GET /api/auth/users/` (qidiruv va holat filtri bilan), `POST /api/auth/users/` (yangi akkaunt va rollar biriktirish), `PATCH /api/auth/users/<id>/` (ma'lumot va rollarni o'zgartirish), `POST /api/auth/users/<id>/deactivate/` (akkauntni xavfsiz faolsizlantirish), `POST /api/auth/users/<id>/reset-password/` (parolni tiklash).
  - OQ-040 talabiga binoan akkaunt o'chirilmaydi (`DELETE` so'roviga `405 Method Not Allowed`), faolsizlantiriladi va ish tarixi saqlanadi.
  - "Rol nomining o'zi vakolat bermasin" tamoyili to'liq joriy etildi: ruxsatlar faqat aniq kodlar (`Role.permissions`) yoki superuser orqali beriladi; bo'sh `ADMIN` roli vakolat bermaydi. `catalog.*` va `inventory.*` prefiks maskalari qo'shildi. Shartnoma [docs/06-api-contract/auth-api.md](../docs/06-api-contract/auth-api.md) 3.6-bo'limida yangilandi.
- **PCRM-37 (Muhit, PostgreSQL va Backup/Restore):**
  - Toza PostgreSQL (`profur_db`) muhitida barcha 20 ta migratsiya, boshlang'ich 9 ta kategoriya va 3 ta xarajat turlari avtomatik yuklanishi tekshirildi.
  - Frontend production build (`npm run build`) muvaffaqiyatli o'tadi (`tsc --noEmit && vite build`).
  - Ma'lumotlar bazasini zaxiralash (`pg_dump -F c`) va qayta tiklash (`pg_restore`) bo'yicha to'liq yo'riqnoma [docs/08-delivery/backup-restore.md](../docs/08-delivery/backup-restore.md) ga yozildi va lokal serverda sinov mashqi (drill) to'liq tasdiqlandi.
- **PCRM-50 (Tizim Sinovlari, PostgreSQL Konkurentlik va E2E):**
  - **Qabul sinovlari:** 30 ta backend testi (`tests/test_pcrm50_acceptance.py` va `tests/test_auth.py`) — barchasi yashil. Narxlarni yashirish, Idempotency-Key takrorlanmasligi, faqat USD qabul qilinishi va uz/ru/en tarjimalari to'liq qoplandi.
  - **PostgreSQL Concurrency:** [`tests/test_concurrency_postgres.py`](../tests/test_concurrency_postgres.py) orqali haqiqiy PostgreSQL'da mustaqil ulanishlar bilan 5 ta parallel tranzaksiya testi o'tkazildi. `select_for_update()` qator qulflashi, lost update bo'lmasligi, qoldiq 10 dan 7+7 so'ralganda manfiyga tushmasligi (biriga 201, biriga 409) va xatoda to'liq rollback ishlashi isbotlandi (SQLite/mock rad etiladi).
  - **Chromium Real E2E:** [`frontend/e2e/receipt.spec.ts`](../frontend/e2e/receipt.spec.ts) orqali haqiqiy Django backend va frontend bilan 3 xil ekranda (Mobil Pixel 7, Planshet iPad, Kompyuter 1280x800) 9 ta brauzer sinovi o'tkazildi. Real USD kirim, Idempotency-Key, uz/ru/en dinamik til almashishi va uzun matnlarda gorizontal overflow yo'qligi tasdiqlandi.
  - **Frontend Unit/Component:** [`frontend/src/App.test.tsx`](../frontend/src/App.test.tsx) da 5 ta komponent testi yashil.
- **Oqimlar va Funksiyalar Holati (Haqiqiy tahlil):**
  - `login → material → ikki narxdagi kirim → qoldiq/partiya/tarix`: Main'da mavjud va 100% sinovdan o'tgan.
  - `xarajatlar → to'g'ri USD hisobi va tarix`: Main'da mavjud va 100% sinovdan o'tgan.
  - `ombordan chiqim`: Akbar tomonidan PR #34 da tayyorlangan, ko'rib chiqishda (hali main'ga birlashmagan).
  - `qaytarish so'rovi va hisobdan chiqarish`: Hali boshlanmagan (`Reja` doirasida).
  - **Xabarnomalar (Notifications):** 1-qism doirasida minimal qoldiq chegarasi ogohlantirishi (`is_low_stock`) va ombor harakatlari auditi (`StockMovement`) belgilangan. Push, WebSockets, Telegram bot va SMS bildirishnomalari 2-bosqich rejasiga kiritilgan va 1-qism scope'iga asossiz qo'shilmaydi.

## Oxirgi qayd

2026-11-18 · PCRM-50 / PCRM-32 / PCRM-37 · Bajarildi · Admin foydalanuvchilar boshqaruvi (OQ-040), ruxsatlar izolyatsiyasi, haqiqiy PostgreSQL parallel konkurentlik testlari (5 ta), 3 ta ekran o'lchamida Chromium E2E sinovlari (9 ta), PostgreSQL backup/restore drill va qabul hujjatlari yakunlandi · Jamoadoshlar ko'rigiga tayyor.





## Navbatdagi ish

1. **PCRM-37** qaytadan tekshiriladi. Django asosi PR #8 orqali main’ga birlashgan. README’ni boshqa jamoadosh kompyuteridagi ketma-ketlik bilan tekshiring. Xususan, migratsiyadan oldin PostgreSQL ishlashi, muhit sozlamalari yuklanishi va health javobini tekshiring. Kichik tuzatish kerak bo‘lsa alohida PR qiling.
2. **PCRM-32** uchun mavjud foydalanuvchi modeli, auth/session va DRF sozlamalarini ko‘ring. Admin hamda ombor mas’ulining amallar jadvalini docs ichida aniqlang. Login, logout va joriy foydalanuvchi/ruxsatlar javobini Shamsiddin bilan kelishing. Model migratsiyasi boshqa app’larning bog‘liqligiga ta’sir qilsa backendchilar bilan muvofiqlashtiring.
3. Tizimga kirmagan foydalanuvchi, vakolatsiz foydalanuvchi va ruxsatli foydalanuvchi uchun haqiqiy API sinovini bajaring. Session usuli tanlansa kirish va yozish amallarida CSRF tekshiruvini ham sinang.
4. **PCRM-50** da frontend/API tayyor bo‘lgach kirim → partiya → qoldiq oqimini birlashtirib sinang. Dalilni PR va rol fayliga kiriting.

Har band boshida main va ochiq PR’larni solishtiring. requirements.txt’dagi haqiqiy versiya cheklovlarini hisobga oling. AI tavsiyasidagi versiyani repoda o‘rnatilgan versiya deb ko‘rsatmang.

## 2026-11-18 · Valyuta va til qarori

USD qabul qilinishi, boshqa valyuta rad etilishi va uz/ru/en til almashishi bo‘yicha sinovlarni tegishli API/UI ishlariga bog‘lang. Sessiya va ruxsat xabarlari ham uch tilda bo‘lsin. [Qarorlar jurnali](../docs/09-decisions/decision-log.md).

## Birlashtirish tekshiruvi · 2026-11-18

PR #11, #12 va #13 bitta integratsiya tarmog‘ida tekshirildi. Katalogning 9 ta boshlang‘ich kategoriyasi migratsiyada qo‘shildi. Login CSRF va uch til sinovlari saqlandi, dinamik ruxsatni berish/olib tashlash regressiya sinovlari qo‘shildi. Holat — main’ga birlashtirish uchun tekshiruvda. Keyingi ish — PCRM-39/40 va frontend bilan kirimni ulash.

## PR #26 · Sinov qamrovi aniqlashtirildi

API qabul sinovlari tests/test_pcrm50_acceptance.py da. Narx yashirish sinovi haqiqiy kirimni ro‘yxat va tafsilot javobida tekshiradi, ruxsatli foydalanuvchi natijasi bilan solishtiradi.

Haqiqiy Chromium mobil brauzer sinovi frontend/e2e/receipt.spec.ts da. U Pixel 7 o‘lchamida login, material tanlash, kirim yuborish, haqiqiy Django API javobi, qayta yuklanganda saqlangan qoldiq va takror so‘rovning bitta partiya bo‘lib qolishini tekshiradi. API almashtirilmaydi. Sinov alohida vaqtinchalik SQLite bazasi bilan ishlaydi, PostgreSQL cheklovlari backend CI’da tekshiriladi. Mahalliy yo‘l — Python bog‘liqliklarini o‘rnatib, frontend ichida npm ci, npx playwright install chromium, npm run test:e2e. Virtual muhit tashqarisida E2E_PYTHON bilan Python yo‘lini ko‘rsatish mumkin.

PCRM-50’ning chiqim, qaytarish va hisobdan chiqarish kabi qolgan mezonlari tegishli funksiyalar tayyor bo‘lganda tekshiriladi. Ushbu PR kirim oqimining qabul sinovlarini beradi.
