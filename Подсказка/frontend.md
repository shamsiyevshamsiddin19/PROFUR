# Frontend va Team Lead

**Egasi** — Shamsiddin.

**Mas’uliyat** — frontend/.

## Ish tartibi

API kelishuvidan keyin material qidirish, tanlash va kirim yuborish oqimini quring. Namuna javobdan haqiqiy API’ga o‘ting. Formada kutish, muvaffaqiyat, validatsiya va server xatosiga mos holatlarni ko‘rsating. @ozodbek101 bilan katalog va qoldiqni, Akbar (@thealiiheere) bilan chiqim va tarixni, @jamoliddinusarov1-create bilan login va qabul sinovini ulang.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-48](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-48) | Responsive ekran tuzilmasi, navigatsiya va UZ/RU/EN | Ko‘rikda | [PR #17](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/17) |
| [PCRM-39](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-39) | Material katalogi UI | Reja | — |
| [PCRM-41](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-41) | Kirim formasi va API integratsiyasi | Jarayonda | [PR #17](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/17), kirim backendiga bog‘liq |
| [PCRM-43](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-43) | Qoldiq, filtrlar va partiya tafsiloti | Reja | — |
| [PCRM-45](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-45) | Chiqim, qaytarish va tasdiqlash ekranlari | Reja | — |
| [PCRM-47](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-47) | Tarix va hisobot UI | Reja | — |

**Qabul mezoni** — Kirim formasi telefon, planshet va desktopda ishlaydi. Saqlashdan keyin API qaytargan qoldiq va harakat ko‘rinadi.

## Oxirgi qayd

2026-11-18 · PCRM-48/PCRM-41 · Ko‘rikda / Jarayonda · React/TypeScript frontend, uch til, Django login, USD kirim shakli · npm run build va 3 frontend testi o‘tdi, brauzerda 320/390/768 px va desktop tekshirildi · keyingi qadam katalog/kirim API’siga ulash.

## Navbatdagi ish

[PR #17](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/17)dagi React/TypeScript/Vite frontendni davom ettiring. Yangi frontend yoki parallel maket boshlamang. Ozodbekning katalog PR #16 va PCRM-40 kirim API’si tayyor bo‘lgach, haqiqiy material tanlash va kirim saqlashni ulang. API maydonlari va ruxsatlarni shartnoma bilan solishtiring. Kirimdan keyin qoldiq/partiya yangilanishi hamda bir xil Idempotency-Key bilan takroriy so‘rov yangi kirim yaratmasligini haqiqiy backendda tekshiring. Backend integratsiyasi tugamaguncha PCRM-41 ni Done qilmang.

## 2026-11-18 · Valyuta va til qarori

Barcha pul summalarini USD ($)da ko‘rsating. Barcha sahifa, shakl va xato xabarlari uchun uz/ru/en tarjimalarini bering. Til almashganda tanlov saqlansin va USD pul birligi qo‘llansin. [Qarorlar jurnali](../docs/09-decisions/decision-log.md).

## 2026-11-18 · Frontendning birinchi ishlaydigan qismi

PCRM-48 va PCRM-41 uchun React/TypeScript/Vite asosi, uz/ru/en tarjimalari,
moslashuvchan menyu, login/logout va USD kirim shakli tayyorlandi.
Login haqiqiy accounts API’si bilan ishlaydi. Katalog va kirim backendiga
bog‘liqlik saqlanadi, xizmat mavjud bo‘lmasa saqlash bloklanadi.
Avtomatik sinovlar CSRF bilan login, uzilgan so‘rovning ayni kalit bilan
qayta yuborilishi va katalog mavjud bo‘lmagan holatni tekshiradi.
Brauzerda 320, 390 va 768 px hamda desktop ko‘rinishlari, til almashishi,
tanlov saqlanishi va mobil menyu tekshirildi.
Holat — frontend asosi ko‘rikda, kirim integratsiyasi backendga bog‘liq. Keyingi qadam — Ozodbekning
PCRM-39 va PCRM-40 API’larini haqiqiy ma’lumotlar bilan ulab sinash.
