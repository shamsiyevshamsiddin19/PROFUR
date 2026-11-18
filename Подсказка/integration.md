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


