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

2026-11-18 · PCRM-48/PCRM-41 · Ko‘rikda / Jarayonda · React/TypeScript frontend, uch til, Django login, USD kirim shakli · npm run build va 3 frontend testi o‘tdi, brauzerda 320/390/768 px va desktop tekshirildi · keyingi qadam mavjud katalogni tekshirish va kirim API’siga ulash.

## Navbatdagi ish

[PR #17](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/17)dagi React/TypeScript/Vite frontendni davom ettiring. Yangi frontend yoki parallel maket boshlamang. Katalog PR #16 integratsiya tarkibida mavjud; PCRM-40 kirim API’si tayyor bo‘lgach, haqiqiy material tanlash va kirim saqlashni ulang. API maydonlari va ruxsatlarni shartnoma bilan solishtiring. Kirimdan keyin qoldiq/partiya yangilanishi hamda bir xil Idempotency-Key bilan takroriy so‘rov yangi kirim yaratmasligini haqiqiy backendda tekshiring. Backend integratsiyasi tugamaguncha PCRM-41 ni Done qilmang.

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

## Birgalikdagi PR ko‘rigi · 2026-11-18

PR #16 (katalog), #17 (frontend) va #18 (xarajatlar) bir integratsiya tarmog‘ida tekshirildi. `config/urls.py` to‘qnashuvi ikkala API yo‘lini saqlab yechildi. Admin panelida xarajat turining kodi o‘zgarmas qilindi; xarajat yaratish muallifni server belgilaydigan API orqali amalga oshadi. Sessiya/CSRF va dinamik ruxsatlarni ikkala xizmatda tekshiruvchi integratsiya sinovi qo‘shildi.

Lokal: 76 backend testi o‘tdi, 2 PostgreSQL cheklovi sinovi SQLite’da o‘tkazildi; qo‘shimcha 2 integratsiya sinovi ham o‘tdi. Frontend build va 3 testi o‘tdi. PostgreSQL cheklovlari birlashtirish PR’ining CI’sida tekshiriladi. Katalog API va frontend ro‘yxati mavjud; kirim/partiya/qoldiq backend hali PCRM-40/42 vazifasi. PCRM-39 to‘liq UI mezonlari, PCRM-48 barcha sahifalar va PCRM-46 teskari yozuv jarayoni avtomatik Done qilinmaydi.

## PCRM-48 · Referensga mos ko‘rinish · 2026-11-18

Foydalanuvchi yangi Warehouse Inventory System rasmining uslubini ma’qulladi va amalga oshirishni buyurdi. Mavjud frontendning ko‘rinishi yangilandi: to‘q ko‘kimtir menyu, och ish maydoni, oltin aksent, ixcham oq shakllar va jadvallar. [Vizual uslub](../docs/07-ux-ui/visual-style.md) keyingi komponentlar uchun asos. API va biznes oqimlari o‘zgarmadi.

Tekshiruv: frontend build va mavjud 3 test o‘tdi; brauzerda login/logout, UZ/RU/EN, materiallar jadvali va mobil menyu tekshirildi. 320/390/768 px hamda desktopda sahifa gorizontal chiqmaydi. Kirim backendiga bog‘liqlik saqlanadi.

## PCRM-48 · Barcha ranglarni qayta ishlash · 2026-11-18

Foydalanuvchi «ranglarini ham hammasini boshidan» qayta ishlashni buyurdi. Barcha komponent ranglari `frontend/src/tokens.css`ga yig‘ildi: fon, matn, tugma, jadval, shakl, fokus/disabled/autofill, status xabarlari, soyalar va brauzer theme-color. Tarqoq hex ranglar styles.css ichida qolmadi. Vizual uslub hujjati yangi qiymatlar bilan yangilandi.

Tekshiruv: build va 3 mavjud test o‘tdi; brauzerda haqiqiy kirish/chiqish va xato, fokus, mobil menyu, ru/en/uz hamda 320/768 px va desktop ko‘rinishlari tekshirildi. Qabul qilingan matn/yuza juftliklari kontrasti hisoblandi. Biznes/API oqimi o‘zgarmadi.

## PCRM-48 · Kirish bezagi olib tashlandi · 2026-11-18

Foydalanuvchi so‘roviga ko‘ra kirish sahifasidagi oltin qutilar tasviri butunlay olib tashlandi. Login formasi markazga joylandi. Tasvirning JSX, CSS va foydalanilmaydigan ranglari o‘chirildi. Yangi dekorativ tasvir qo‘shmang.
