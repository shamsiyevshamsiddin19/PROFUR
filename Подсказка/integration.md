# Login, ruxsatlar, test va CI

**Egasi** — [@jamoliddinusarov1-create](https://github.com/jamoliddinusarov1-create).

**Mas’uliyat** — Ishga tushirish yo‘riqnomasi, kirish va ruxsat moduli, CI hamda tizim sinovlari.

## Ish tartibi

Avval umumiy ishga tushirish tartibi, muhit sozlamasi namunasi va tekshiruv buyruqlarini tayyorlang. Login va ombor rol huquqlarini backendchilar bilan kelishing. Har bir dasturchi o‘z funksiyasining testini yozadi. Siz foydalanuvchi oqimini birlashtirib tekshirasiz.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-32](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-32) | Login/session va omborga tegishli ruxsatlar | Ko‘rikda | [#12](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/12) |
| [PCRM-37](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-37) | Ishga tushirish sozlamalari, lint, test va migratsiya tekshiruvi | Bajarildi | [#8](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/8) |
| [PCRM-50](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-50) | Brauzerda kirimdan qoldiqqacha qabul sinovi va salbiy holatlar | Reja | — |

**Qabul mezoni** — To‘rt jamoadosh loyihani mahalliy ishga tushira oladi. Ruxsatsiz amal rad etiladi. birinchi brauzer sinovida kirim bir marta saqlanib, qoldiq yangilanadi.

## Jamoadoshlarga topshirish (Handoff)

- **PCRM-37 (Umumiy asos):** PR #8 orqali main’ga birlashtirildi. Django + DRF, Ruff, docker-compose va CI to‘liq ishlamoqda.
- **PCRM-32 (Accounts va Ruxsatlar):** `accounts` ilovasi, kengaytirilgan `User` modeli (`Role` ko‘pdan-ko‘p bog‘lanishi bilan, OQ-037), login/logout/me/csrf hamda rollar API nuqtalari (`/api/auth/roles/`) va DRF ruxsatlari (`IsAdminRole`, `IsWarehouseManager`, `IsProductionSupervisor`, `IsProjectManager`) tayyorlandi. Login CSRF himoyasi bilan ta'minlandi, xabarlar 3 tilda (UZ/RU/EN) tarjima qilindi.
- **Backendchilarga ([@ozodbek101](https://github.com/ozodbek101), [Akbar (@thealiiheere)](https://github.com/thealiiheere)):** Katalog, ombor va xarajatlar modullarida foydalanuvchi tekshiruvi uchun `request.user` va `accounts.permissions` ruxsatnomalaridan foydalanishingiz mumkin.
- **Frontend va Team Leadga (Shamsiddin):** Kirish, chiqish, joriy foydalanuvchi ma'lumoti, CSRF token hamda rol boshqaruvi (OQ-037) API shartnomasi [docs/06-api-contract/auth-api.md](../docs/06-api-contract/auth-api.md) hujjatiga kiritildi.

## Oxirgi qayd

2026-11-18 · PCRM-32 · Ko‘rikda · Review asosida login CSRF himoyasi, 3 tildagi xabarlar (UZ/RU/EN) va OQ-037 dinamik rollar qo‘shildi · 12 ta test muvaffaqiyatli (pytest, ruff pass), PR [#12](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/12) · Team Lead va jamoadoshlar ko‘rigidan so‘ng main'ga birlashtirish





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
