# Qarorlar jurnali

**PM OQ-001–OQ-048 javoblarini tasdiqlagan.** PM OQ-001–OQ-048 javoblarini tasdiqlagani Team Lead tomonidan 2026-11-18 kuni xabar qilindi. Bu sana tasdiq haqidagi xabar qayd etilgan sanadir. [Tasdiqlangan javoblar](../01-requirements/oq-001-048-team-lead-answers.md).

**Tasdiqlangan joriy doira** — TZning 1-qismi, ombor/kirim-chiqim va barcha ekranlarga mos veb-sayt.

| ID | Qaror mavzusi | Holat | Mas'ul | Sana |
|---|---|---|---|---|
| Q-001 | Material tannarxini hisoblash usuli | PM tasdiqlagan; tafsilotlar tegishli OQ izohida | PM | Xabar 2026-11-18 |
| Q-002 | Materialni zaxiraga olish va qoldiqdan ayirish vaqti | PM tasdiqlagan; tafsilotlar tegishli OQ izohida | PM | Xabar 2026-11-18 |
| Q-003 | Admin yangi rol va ruxsat yarata olishi | PM tasdiqlagan; tafsilotlar tegishli OQ izohida | PM | Xabar 2026-11-18 |
| Q-004 | Guruh akkauntida shaxsiy hisob va ishbay stavkalar | PM tasdiqlagan; tafsilotlar tegishli OQ izohida | PM | Xabar 2026-11-18 |
| Q-005 | Mobil platforma va internetsiz ishlash | PM tasdiqlagan; tafsilotlar tegishli OQ izohida | PM | Xabar 2026-11-18 |
| Q-006 | Dasturlash texnologiyalarini tanlash | TAKLIF | Jamoa yetakchisi / PM | — |

## Valyuta va til bo‘yicha joriy qaror

**2026-11-18 · Team Leadning bevosita aniqlashtirishi.** Barcha pul hisoblari faqat AQSH dollarida — USD ($). Bu kirim, birlik narxi, qoldiq qiymati, chiqim tannarxi, xarajat va kelgusi moliyaviy hisoblariga tegishli. OQ-004, OQ-016 va OQ-034 dagi boshqa valyuta/kursga doir avvalgi izohlar shu qaror bilan almashtiriladi.

Interfeys uch tilda — o‘zbek (lotin), rus va ingliz. Texnik til kodlari `uz`, `ru`, `en`. Foydalanuvchi interfeys tilini almashtirganda pul birligi USD bo‘lib qoladi. OQ-045 talabini ekranlar, shakllar, tekshiruv va xato xabarlari hamda bildirishnomalarda qo‘llang.

Amaliy shartlar:
- API’dagi `currency` maydoni mavjud bo‘lsa, qiymati faqat `USD`. Server boshqa kodni rad etadi.
- Pul aniq o‘nlik son bilan saqlanadi va API’da satr ko‘rinishida uzatiladi. Interfeysda $ bilan ko‘rsatiladi. Miqdor va narx aniqligi haqidagi ochiq savollar o‘z holicha yuritiladi.
- Frontend kirim va xarajat misollarini USD’da beradi. Til tanlovi foydalanuvchining tanlovini saqlaydi, standart boshlang‘ich til alohida aniqlanadi.
- Sinovlarda USD qabul qilinishi va boshqa valyuta rad etilishi, uch til orasida almashtirish, xato matnlari va tanlovni qayta ochganda saqlanishi tekshiriladi.
- Ochiq PR’lar, API namunasi, shakl, serializer va bazada avvalgi taklifdan qolgan valyuta/til qoidalarini vazifa egasi shu qarorga moslashtiradi. Eski pul yozuvlari topilsa, ularni USD deb qayta belgilashdan oldin asl qiymat va xavfsiz ko‘chirish qarorini aniqlaydi.

## Qaror qaydi namunasi

- Qaror ID:
- Tegishli savol ID:
- Qabul qilingan qaror:
- Ko‘rib chiqilgan boshqa variantlar:
- Qaror sababi:
- Kim tasdiqladi:
- Sana:
- Ta'sir qiladigan Jira vazifalari va hujjatlar:
- Holat: TASDIQLANGAN / RAD ETILGAN / KEYINGA QOLDIRILGAN

[Barcha ochiq savollar](../01-requirements/open-questions.md)
