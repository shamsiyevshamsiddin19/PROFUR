# Login, ruxsatlar, test va CI

**Egasi** — [@jamoliddinusarov1-create](https://github.com/jamoliddinusarov1-create).

**Mas’uliyat** — Ishga tushirish yo‘riqnomasi, kirish va ruxsat moduli, CI hamda tizim sinovlari.

## Ish tartibi

Avval umumiy ishga tushirish tartibi, muhit sozlamasi namunasi va tekshiruv buyruqlarini tayyorlang. Login va ombor rol huquqlarini backendchilar bilan kelishing. Har bir dasturchi o‘z funksiyasining testini yozadi. Siz foydalanuvchi oqimini birlashtirib tekshirasiz.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-32](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-32) | Login/session va omborga tegishli ruxsatlar | Reja | — |
| [PCRM-37](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-37) | Ishga tushirish sozlamalari, lint, test va migratsiya tekshiruvi | Ko‘rikda | [feat/PCRM-37-setup-and-ci](https://github.com/shamsiyevshamsiddin19/PROFUR/tree/feat/PCRM-37-setup-and-ci) |
| [PCRM-50](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-50) | Brauzerda kirimdan qoldiqqacha qabul sinovi va salbiy holatlar | Reja | — |

**Qabul mezoni** — To‘rt jamoadosh loyihani mahalliy ishga tushira oladi. Ruxsatsiz amal rad etiladi. birinchi brauzer sinovida kirim bir marta saqlanib, qoldiq yangilanadi.

## Jamoadoshlarga topshirish (Handoff)

- **Tayyorlangan poydevor:** `backend/` ichida Django + DRF loyihasi, modulli `apps/` arxitekturasi, `requirements.txt`, `tests/test_health.py` (pytest), `pyproject.toml` (Ruff sozlamalari), `docker-compose.yml` (PostgreSQL 16) va GitHub Actions CI to‘liq tayyorlandi.
- **Backendchilarga ([@ozodbek101](https://github.com/ozodbek101), [Akbar (@thealiiheere)](https://github.com/thealiiheere)):** Django muhiti tayyor. O‘z ilovalaringizni `backend/apps/` papkasiga qo‘shishingiz, PostgreSQL bazani `docker compose up -d` orqali ko‘tarishingiz va testlarni `pytest` bilan ishlatishingiz mumkin.
- **Frontend va Team Leadga (Shamsiddin):** Django backend asosiy sozlamalari, CORS, `/api/health/` API tekshiruvi va CI ko‘rikka taqdim etildi.

## Oxirgi qayd

2026-11-17 · PCRM-37 · Ko‘rikda · Django backend loyihasi, DRF, CORS, requirements.txt, health API va pytest sinovlari to‘liq sozlandi · [feat/PCRM-37-setup-and-ci](https://github.com/shamsiyevshamsiddin19/PROFUR/tree/feat/PCRM-37-setup-and-ci) · PR ko‘rikdan o‘tgach birlashtirish va PCRM-32 (Login/ruxsatlar)ga o‘tish



## Navbatdagi ish

1. **PCRM-37** qaytadan tekshiriladi. Django asosi PR #8 orqali main’ga birlashgan. README’ni boshqa jamoadosh kompyuteridagi ketma-ketlik bilan tekshiring. Xususan, migratsiyadan oldin PostgreSQL ishlashi, muhit sozlamalari yuklanishi va health javobini tekshiring. Kichik tuzatish kerak bo‘lsa alohida PR qiling.
2. **PCRM-32** uchun mavjud foydalanuvchi modeli, auth/session va DRF sozlamalarini ko‘ring. Admin hamda ombor mas’ulining amallar jadvalini docs ichida aniqlang. Login, logout va joriy foydalanuvchi/ruxsatlar javobini Shamsiddin bilan kelishing. Model migratsiyasi boshqa app’larning bog‘liqligiga ta’sir qilsa backendchilar bilan muvofiqlashtiring.
3. Tizimga kirmagan foydalanuvchi, vakolatsiz foydalanuvchi va ruxsatli foydalanuvchi uchun haqiqiy API sinovini bajaring. Session usuli tanlansa kirish va yozish amallarida CSRF tekshiruvini ham sinang.
4. **PCRM-50** da frontend/API tayyor bo‘lgach kirim → partiya → qoldiq oqimini birlashtirib sinang. Dalilni PR va rol fayliga kiriting.

Har band boshida main va ochiq PR’larni solishtiring. requirements.txt’dagi haqiqiy versiya cheklovlarini hisobga oling. AI tavsiyasidagi versiyani repoda o‘rnatilgan versiya deb ko‘rsatmang.

## 2026-11-18 · Valyuta va til qarori

USD qabul qilinishi, boshqa valyuta rad etilishi va uz/ru/en til almashishi bo‘yicha sinovlarni tegishli API/UI ishlariga bog‘lang. Sessiya va ruxsat xabarlari ham uch tilda bo‘lsin. [Qarorlar jurnali](../docs/09-decisions/decision-log.md).
