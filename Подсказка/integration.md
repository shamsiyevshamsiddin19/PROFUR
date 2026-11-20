# Login, ruxsatlar, test va CI

**Egasi** — [@jamoliddinusarov1-create](https://github.com/jamoliddinusarov1-create).

**Mas’uliyat** — Ishga tushirish yo‘riqnomasi, kirish va ruxsat moduli, CI hamda tizim sinovlari.

## Ish tartibi

Avval umumiy ishga tushirish tartibi, muhit sozlamasi namunasi va tekshiruv buyruqlarini tayyorlang. Login va ombor rol huquqlarini backendchilar bilan kelishing. Har bir dasturchi o‘z funksiyasining testini yozadi. Siz foydalanuvchi oqimini birlashtirib tekshirasiz.

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
| [PCRM-32](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-32) | Login/session, ombor ruxsatlari va admin foydalanuvchi boshqaruvi (OQ-040) | Bajarildi (texnik) | [PR #46](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/46), [CI 231/10/12](https://github.com/shamsiyevshamsiddin19/PROFUR/actions/runs/44449909326); joriy 1-qism doirasi. |
| [PCRM-37](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-37) | Ishga tushirish sozlamalari, PostgreSQL, backup/restore, frontend build va CI | Bajarildi (texnik) | [PR #46](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/46), [CI 231/10/12](https://github.com/shamsiyevshamsiddin19/PROFUR/actions/runs/44449909326); joriy 1-qism doirasi. |
| [PCRM-50](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-50) | Qabul sinovlari, PostgreSQL parallel konkurentlik va 3 ekranli Chromium E2E | Bajarildi (texnik) | [PR #46](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/46), [CI 231/10/12](https://github.com/shamsiyevshamsiddin19/PROFUR/actions/runs/44449909326); joriy 1-qism doirasi. |

**Qabul mezoni** — To‘rt jamoadosh loyihani toza muhitda ishga tushira oladi. Ruxsatsiz amal rad etiladi. Haqiqiy PostgreSQL'da parallel amallar qoldiqni buzmaydi. Brauzerda mobil, planshet va kompyuter ekranlarida to'liq oqim va uch tilda barqaror ishlaydi.

## Jamoadoshlarga topshirish (joriy)

- **PCRM-32 / OQ-040:** admin uchun foydalanuvchi yaratish, qidirish, tahrirlash, rol biriktirish, faolsizlantirish va parolni tiklash API’si PR #44 da. Parol yaratish/tiklash loyiha validatorlari bilan tekshiriladi. Joriy main’dagi ADMIN/superuser va aniq permission kodlari kontrakti saqlandi; prefiks maskalari yoki tasdiqlanmagan yangi admin vakolati modeli qo‘shilmadi.
- **PCRM-37:** backup/restore yo‘riqnomasi mavjud. Muallif lokal drill bajarganini yozgan; ushbu integratsiya ko‘rigida production backup rejasi yoki tiklash amali bajarilgani da’vo qilinmaydi.
- **PCRM-50:** PostgreSQL mustaqil ulanishlar testi, uch ekranli Chromium, uz/ru/en va uzun nom sinovlari bor. Main’dagi to‘liq kirim → chiqim → qaytarish/tasdiq → hisobdan chiqarish/tasdiq → xarajat/teskari yozuv → qoldiq/minimum → tarix/CSV ssenariysi saqlandi. Har ekran o‘z materiali/loyihasi bilan ajratildi, kutishlar aniq natijani tekshiradi.
- **Ochiq:** PM/buyurtmachi va haqiqiy xodimlar bilan yakuniy qabul, P1/P3/P5 qarorlari. OQ-014 xabarnoma hajmini o‘zidan 2-bosqichga ko‘chirmang; tasdiqlangan doira bilan kelishing. StockMovement auditi avtomatik xabarnoma o‘rnini bosmaydi.

## Oxirgi qayd

2026-11-18 · PCRM-32/37/50 · Ko‘rikda · PR #44: joriy main bilan to‘qnashuvlar yechildi, kuchsiz parolni qabul qilish xatosiga regressiya qo‘shildi, auth kontrakti va barcha yangi ombor oqimlari saqlandi. Python yo‘li CI’ga moslandi; uch ekranli E2E ma’lumotlari ajratildi. Lokal tekshiruv va CI dalili PR’da. PR merge va PM/buyurtmachi qabulisiz PCRM-50 Done qilinmaydi.

## Arxiv — avvalgi navbatdagi ish

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

2026-11-20 · PCRM-50 · Sex suhbati bo‘yicha ombor yakuniy oqimi: ikki narx usuli, boshlang‘ich qoldiq, ishchining darhol chiqimi, kesilgan qoldiq, admin ko‘rigi va oylik hisobot. Qoidalar va sinov doirasi [1-qism qabul hujjatida](../docs/08-delivery/phase-one-acceptance.md). Ishchiga vakolatlar Boshqaruv sahifasida ataylab tayinlanadi.
