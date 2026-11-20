# PROFUR · 1-qismni topshirish

Joriy doira: bitta ombor, responsive veb, UZ/RU/EN, faqat USD. Buyurtma, ishlab chiqarish, ishbay haq va alohida mobil ilova keyingi qismlar.

## Talab va tekshiruv dalili

| Talab | Natija | Dalil |
|---|---|---|
| TZ 2.1 / PCRM-5 | 9 kategoriya, yangi kategoriya/material, rang/o‘lcham/birlik, faolsizlantirish | catalog API/model testlari, Catalog ekrani |
| TZ 2.2 / PCRM-6 | Alohida narxli partiyalar, aniq summa/miqdor, bir martalik kirim | receipt va ledger testlari, uch ekranli real brauzer oqimi |
| PCRM-7 | Qoldiq, partiyalar, minimum, mobil kartalar va saqlanadigan xabarlar | stock va notification testlari, Chromium |
| PCRM-8/44 | Amaldagi chiqim, tasdiqlanadigan qaytarish va hisobdan chiqarish; manfiy qoldiq taqiqlangan | PostgreSQL parallel 7+7, ikki tasdiq, idempotency, Chromium |
| PCRM-9/46 | Loyiha raqamiga bog‘liq USD xarajat, sababli teskari yozuv, tarix/CSV | expenses/reversal/replay va brauzer oqimi |
| OQ-037/040 / PCRM-32 | Admin akkaunt/rol yaratadi, tahrirlaydi, faolsizlantiradi va parolni tiklaydi; akkaunt o‘chirilmaydi | auth API regressiyalari, Administration ekrani va Chromium |
| PCRM-37 | README, PR shabloni, lint/test/build/migratsiya CI, backup/restore vositasi | .github, ops, CI |
| PCRM-50 | Ruxsatlar, moliyaviy maydonlarni yashirish, uz/ru/en, mobil/planshet/desktop, tarmoq qayta urinishi | tests/, frontend/e2e/ |

Yangi xabarlar faqat faol, `inventory.view_stock` ruxsatiga ega xodimlarga (ADMIN/superuser ham) yaratiladi. Xabar foydalanuvchiga tegishli; boshqaning xabarini o‘qish mumkin emas. Xabarda narx yo‘q. Chegaradan birinchi tushishda yaratiladi, qoldiq tiklanguncha takrorlanmaydi; qayta tushsa yangi xabar keladi. Xabar/flag va qoldiq ayni tranzaksiyada yoziladi. Eski minimumlarni bir marta sinxronlash: `python backend/manage.py notify_low_stock`. Inbox va o‘qilgan holat serverda saqlanadi; navigatsiya soni 30 soniyada yangilanadi. Bu veb-push xizmatiga ulanilganini anglatmaydi. OQ-028 dagi ishchi vazifa pushlari ishlab chiqarish moduli bilan alohida qamrab olinadi.

## Hozirgi hisob shartnomasi

Partiyalar qo‘lda aniq tanlanadi; server `allocations` talab qiladi. Miqdor 2, birlik narxi 6 kasr xona; ortiqcha aniqlik rad etiladi, yashirin yaxlitlanmaydi. Kirimning asl summasi saqlanadi. Xato xarajat teskari yozuv bilan tuzatiladi. Kirim o‘chirilmaydi yoki yashirin tahrirlanmaydi; kirimni tuzatish API’si mavjud emas.

P1 (FIFO yoki qo‘lda), P3 (miqdor aniqligini o‘zgartirish), P5 (kirim tuzatish vakolati/algoritmi) bo‘yicha takliflar tasdiqlangan qaror deb ko‘rsatilmaydi. Team Leadga tavsiya va variantlar yuborilgan. Bu hujjat ushbu biznes qarorlarini o‘zidan tasdiqlamaydi.

`project_id` keyingi loyihalar moduli kelguncha musbat tashqi raqam; mavjud loyiha ekanligi hozir tekshirilmaydi. Xarajatda majburiy, chiqimda ixtiyoriy. Ishchi chiqimda `recipient_name` bilan qayd etiladi. Loyiha/ishchi kataloglari hozirgi qismga qo‘shilmaydi.

## Backup va joylashtirish

`ops/backup.py` PostgreSQL custom dump, format tekshiruvi va SHA-256 manifest yaratadi. `ops/restore_drill.py` nazorat summasini tekshiradi, alohida yangi bazaga tiklaydi, qoldiq=partiyalar=harakatlar va manfiy qoldiq yo‘qligini tekshiradi; faqat o‘zi yaratgan vaqtinchalik bazani tozalaydi. [O‘rnatish tartibi](backup-restore.md).

2026-11-18 lokal PostgreSQL mashqi: alohida `profur_closeout_review` bazasida 1 material, 20 birlik/$600 kirim, 1 partiya va 1 harakat. Arxiv yaratildi, SHA-256 tekshirildi, boshqa yangi bazaga tiklandi; invariant tekshiruvi o‘tdi, tiklash 1.04 soniya. Bu kichik sinov production hajmidagi RTO kafolati emas. Kundalik timer fayli tayyor; production’da o‘rnatilgani da’vo qilinmaydi. Retention/RPO va serverdan tashqari zaxira manzili kelishiladi. Mavjud zaxiralar avtomatik o‘chirilmaydi.

## Yakuniy qabul chegarasi

Avtomatik sinov va main’ga merge — texnik topshirish dalili. OQ-047 bo‘yicha PM/buyurtmachi va haqiqiy xodimlar bilan qabul ularning nomidan belgilanmaydi. Server/domen sozlash va jonli muhitdagi kundalik zaxira dalili alohida kerak. 2026-11-19: [PR #46](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/46) main’ga `28d290c` sifatida birlashdi. [CI #44449909326](https://github.com/shamsiyevshamsiddin19/PROFUR/actions/runs/44449909326) — 231 backend, 10 frontend, 12 Chromium, lint/build/migratsiya va PostgreSQL 16 konteyneri bilan restore o‘tdi (kichik ma’lumotda 1.1 s). Jira PCRM-5–9, PCRM-32/37/38–50 texnik vazifalari Done. Bu PM yoki production qabuli emas.

## 2026-11-20 · Sex ombori ssenariysi

- Kirimda miqdor bilan **jami summa yoki birlik narxi** kiritiladi. Ikkinchi raqam oldindan ko‘rsatiladi va serverda hisoblanadi. Pul USD; birlik narxi uchun 6 kasr xona, hujjat summasi uchun 2 kasr xona. Administrator haqiqiy birinchi xariddan oldin boshlang‘ich qoldiqni belgilab yozishi mumkin. Bu qoldiq joriy kapitalda yuradi, oylik yangi xaridga qo‘shilmaydi. Eski kirim tasnifi avtomatik o‘zgartirilmaydi.
- Ishchi o‘zi olgan miqdor va loyiha raqamini kiritadi. Ombor qoldig‘i bir tranzaksiyada darhol kamayadi, tizim kishini akkauntdan oladi. Ishchi shakli eski ochiq partiyalardan boshlab taqsimlaydi (sana, keyin ID), administratorning qo‘lda partiya tanlashi saqlanadi. Loyiha bo‘limi kelguncha loyiha raqami ishlatiladi.
- Kesilgan bo‘lak asl chiqimga bog‘lanadi, o‘lchami mm va bo‘laklar soni bilan alohida ro‘yxatda yuradi. Butun qoldiq soniga qo‘shilmaydi. Bo‘laklar dastlabki chiqimdan va qaytarilmagan hajmdan oshmaydi. Yaroqli bo‘lak qayta ishlatilganda uning soni darhol kamayadi va bo‘shagan qator tarix uchun saqlanadi.
- Ishchi chiqimi, bo‘lak qo‘shish va bo‘lakni ishlatish darhol bajariladi va administratorning **Amallar ko‘rigi** ro‘yxatiga tushadi. Ko‘rik nazorat uchun. Xato bo‘lak yozuvi sabab bilan teskari amal orqali tuzatiladi. Butun chiqim xatosi asl yozuvga bog‘langan qaytarish va kerak bo‘lsa yangidan chiqim bilan tuzatiladi. Oddiy butun material qaytarishi avvalgidek alohida tasdiqlanadi.
- **Boshqaruv → Rollar** orqali ishchi rejimi va kerakli ombor vakolatlari biriktiriladi. Katalogda materialga rol kodlari tanlanadi. Ishchi ariza topshirganda rol taklif qiladi; vakolat faqat admin tasdiqlaganidan keyin kuchga kiradi. Oldingi akkaunt va rollarga qo‘shimcha vakolat avtomatik berilmaydi.
- Oylik hisobot xarid, ishlab chiqarishga berilgan material, tasdiqlangan qaytish, hisobdan chiqarish va xarajatni ajratadi. Qaytish xarid sifatida sanalmaydi; hisobdan chiqarish ishlab chiqarishga berilgan tannarxga qo‘shilmaydi. Kesilgan bo‘laklar jismoniy hisobda, butun partiya qiymatiga qayta qo‘shilmaydi.
