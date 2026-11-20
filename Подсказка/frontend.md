# Frontend va Team Lead

**Egasi** — Shamsiddin.

**Mas’uliyat** — frontend/.

## Ish tartibi

API kelishuvidan keyin material qidirish, tanlash va kirim yuborish oqimini quring. Namuna javobdan haqiqiy API’ga o‘ting. Formada kutish, muvaffaqiyat, validatsiya va server xatosiga mos holatlarni ko‘rsating. @ozodbek101 bilan katalog va qoldiqni, Akbar (@thealiiheere) bilan chiqim va tarixni, @jamoliddinusarov1-create bilan login va qabul sinovini ulang.

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
| [PCRM-48](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-48) | Responsive ekran tuzilmasi, navigatsiya va UZ/RU/EN | Bajarildi | [PR #39](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/39) va [#42](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/42) main’da; CI va Jira Done |
| [PCRM-39](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-39) | Material katalogi UI | Bajarildi | [PR #39](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/39) va [#42](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/42) main’da; CI va Jira Done |
| [PCRM-41](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-41) | Kirim formasi va API integratsiyasi | Bajarildi | [PR #39](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/39) va [#42](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/42) main’da; CI va Jira Done |
| [PCRM-43](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-43) | Qoldiq, filtrlar va partiya tafsiloti | Bajarildi | [PR #39](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/39) va [#42](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/42) main’da; CI va Jira Done |
| [PCRM-45](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-45) | Chiqim, qaytarish va tasdiqlash ekranlari | Bajarildi | [PR #39](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/39) va [#42](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/42) main’da; CI va Jira Done |
| [PCRM-47](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-47) | Tarix va hisobot UI | Bajarildi | [PR #39](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/39) va [#42](https://github.com/shamsiyevshamsiddin19/PROFUR/pull/42) main’da; CI va Jira Done |

**Qabul mezoni** — Kirim formasi telefon, planshet va desktopda ishlaydi. Saqlashdan keyin API qaytargan qoldiq va harakat ko‘rinadi.

## Oxirgi qayd

2026-11-18 · PCRM-39/41/43/45/47/48 · Bajarildi · PR #39 (`36787ec`) va #42 (`28ef64e`) main’da; Jira Done. Yakuniy CI: 206 backend testi, 10 frontend testi va haqiqiy Chromium/Django ombor oqimi (kategoriya/min. chegara ham). Quyidagi avvalgi sana qaydlari tarixiy; joriy holat shu bo‘lim va yakuniy topshirishda.

## Arxiv — avvalgi navbatdagi ish

1. **PCRM-50 qabulini qo‘llab-quvvatlang.** Jamoliddinning qabul matritsasi va yangi PR’ini joriy main ustida ko‘rib chiqing. Mavjud kirim → chiqim → qaytarish/tasdiq → hisobdan chiqarish/tasdiq → xarajat/teskari yozuv → tarix/CSV Chromium ssenariysini qayta yaratmang.
2. **Ochiq PM qarorlari.** P1/P3/P5 bo‘yicha aniq qaror kelganda API va UI ta’sirini kelishing. FIFO yoki kirimni tuzatish mexanizmini o‘zingiz tasdiqlangan deb joriy qilmang.
3. **Qolgan integratsiya.** Akkaunt boshqaruvi kabi yangi backend imkoniyatlari Jamoliddinning PR’ida tasdiqlangandan keyin tegishli ekran/API ulanishini alohida bajaring. Hali mavjud bo‘lmagan endpointni o‘ylab topmang.
4. **PM/buyurtmachi qabuli.** Butun 1-qism faqat PCRM-50 va yakuniy qabul dalili bilan yopiladi. Frontend ticketlarining texnik Done holati shu umumiy qabulni almashtirmaydi.

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

## PCRM-48 · Oq fon va professional UI ko‘rigi · 2026-11-18

Foydalanuvchi oq fon saqlanishini va tizim ranglari/dizayn kamchiliklari tuzatilishini so‘radi. Safir ko‘k asosiy amallar, grafit matn va neytral status tizimi tanlandi. Mayda yozuvlar, maydon chegarasi kontrasti, takroriy bezaklar, mobil yorliq tekisligi va sana maydoni tuzatildi. Mobil menyu logout/login holati ham yopildi; yangi regressiya sinovi qo‘shildi. Rang va boshqaruv o‘lchamlari uchun Atlassian/W3C manbalari o‘rganilib, vizual uslubga kiritildi. Biznes/API o‘zgarmadi.

Dalil: build va 4 frontend testi; matn/fon hamda boshqaruv/fon kontrast hisoblari; brauzerda 320/768 px va desktop, uz/ru/en, mobil menyu va maydon joylashuvi. Keyingi UI ishlarida yangi vizual uslubga tayaning.

## PCRM-43 · Ozodbekning Qoldiq (Stock) API'siga frontendni ulash · 2026-11-18

Frontend qoldiq ekrani (`#stock`) Ozodbek yaratgan `/api/v1/stock/` API'siga to‘liq ulandi.
- Jadvalda har bir material qoldig‘i, ochiq partiyalar soni (`open_batches`), minimal chegara (`min_quantity`) va umumiy qiymati (`value_by_currency`) ko‘rsatiladi.
- Agar qoldiq minimal chegaradan past bo‘lsa (`is_below_min: true`), «Kam qoldiq» (Low stock) ogohlantiruvchi badge chiqadi.
- Qidiruv va «Faqat kam qolganlar» (`below_min=true`) filtri qo‘shildi.
- Narx ko‘rish ruxsati bo‘lmaganda qiymat xatosiz yashiriladi (OQ-041).
- Avtomatik sinovlar (`App.test.tsx` 6 ta test) va TypeScript build to‘liq o‘tdi.

## Ombor ekranlari · 2026-11-18 · PCRM-39/43/45/47/48

Holat: **Ko‘rikda**. Issue #38; `feat/PCRM-45-warehouse-workflows` branch.

Material/kategoriya yaratish, tahrirlash va faolsizlantirish; qoldiqdan partiya tafsiloti va minimal chegara; chiqim, asl chiqimga qaytarish va hisobdan chiqarish so‘rovi/tasdiq/rad; loyiha xarajatlari va sababli teskari/to‘g‘ri yozuv; sana/material/amal filtrli tarix va barcha sahifalardan CSV eksporti qo‘shildi. Partiyani foydalanuvchi tanlaydi; FIFO yoki boshqa ochiq PM algoritmi tasdiqlangan deb qo‘llanmadi. Superuser belgisi auth javobida faqat o‘qiladi. Qolgan backend chegaralari buzilmadi.

Barcha yangi matnlar uz/ru/en, barcha pul USD. Noma’lum chiqim/qaytarish/hisobdan chiqarish javobi ayni kalit va tana bilan qayta tiklanadi. Xarajat yaratish API’sida idempotency bo‘lmagani uchun noma’lum javobdan keyin ro‘yxatni tekshirish ko‘rsatiladi. Jadval surilishi uning konteyneri ichida.

Dalil: TypeScript build va 9 frontend testi; Ruff va diff tekshiruvi. Alohida lokal bazada brauzer orqali material → 20 kirim → 7 chiqim → 2 qaytarish tasdig‘i → 1 hisobdan chiqarish tasdig‘i, $12.50 xarajat va −$12.50 teskari yozuv bajarildi. CI real Chromium ssenariysi shu amallar, tarix va CSV yuklashgacha kengaytirildi. Yakuniy PostgreSQL/Chromium CI dalili PR’da tekshiriladi. PM/buyurtmachi qabuli va ochiq algoritm qarorlari tugamaguncha 1-qism avtomatik Done qilinmaydi.


### PR #39 · yakuniy integratsiya yangilanishi

Ozodbekning #37/#40 va Akbarning #41 PR’lari ko‘rikdan o‘tib main’ga qo‘shildi. Xarajat yaratish va teskari yozuv ham frontendda Idempotency-Key, sessiyada tana/kalitni saqlash va ayni so‘rovni davom ettirishga ulandi; oldingi «xarajat API’sida idempotency yo‘q» cheklovi #41 bilan bartaraf etildi. Formadagi yorliqlar boshqaruvlarga alohida bog‘landi, tanlov variantlari yorliq matniga aralashmaydi. Build va 10 frontend testi o‘tdi; yakuniy integratsiya CI’si kutilmoqda.


## PR #39 main’da · 2026-11-18

PR #39 `36787ec` bilan main’ga birlashdi. Tekshirilgan head: `4f9df46`. CI’da 206 backend testi (PostgreSQL), 10 frontend testi va haqiqiy Chromium/Django ombor ssenariysi o‘tdi. Ozodbekning #37/#40 va Akbarning #41 ishlari ko‘rikdan o‘tib main’da. Jira PCRM-39/41/43/45/47/48 — yakuniy mezon tekshiruvi sabab Jarayonda.

PCRM-43 mezonini to‘liq yopish uchun kichik ekranda qoldiq jadvali bitta DOM asosidagi kartalarga o‘tkazildi (kategoriya, birlik, miqdor, min. chegara, qiymat va partiyalar), kategoriya filtri qo‘shildi. Partiya/minimal chegara oynasi saqlanadi. Takroriy satrlar yo‘q; narx ruxsati API tomonidan boshqariladi. Browser ssenariysiga kategoriya filtri va min. chegara qo‘shildi. Build va 10 frontend testi o‘tdi; shu qo‘shimchaning CI’si kutilmoqda.

## Yakuniy texnik topshirish · 2026-11-18

**PCRM-39/41/43/45/47/48 — Bajarildi.** PR #39 (`36787ec`) va #42 (`28ef64e`) main’da. Jira holatlari tekshirilgan natija va PR/CI havolali izoh bilan Done ga o‘tkazildi. Yakuniy kod head’i `f4ec008` uchun CI: 206 backend testi, 10 frontend testi va haqiqiy Chromium/Django ombor ssenariysi o‘tdi (kategoriya filtri, minimal chegara, chiqim, qaytarish/tasdiq, hisobdan chiqarish/tasdiq, xarajat/teskari yozuv, tarix/CSV). Oq fon, uz/ru/en va USD saqlangan.

**Keyingi qadam — PCRM-50:** Jamoliddinning yakuniy qabul matritsasi va qolgan integratsiya ishlari, PM/buyurtmachi qabuli. P1 (partiya tanlash), P3 (aniqlik), P5 (kirimni tuzatish) bo‘yicha ochiq qarorlar frontend ticketlari Done bo‘lishi bilan tasdiqlangan hisoblanmaydi. Yangi ishda avval main, ochiq PR va [API topshirig‘i](../docs/06-api-contract/warehouse-frontend-handoff.md)ni o‘qing; mavjud ekranlarni qayta yaratmang.

## 2026-11-19 · PCRM-48 — vizual yaxshilash

Team Lead topshirig‘i: palitra, chap panel va sozlamalar. Standart zumrad rang, guruhlangan navigatsiya va `#settings` qo‘shildi. Aksent/ixchamlik/animatsiya tanlovi brauzerda saqlanadi; USD va server ruxsatlari o‘zgarmaydi. Build va mavjud testlar, uch ekranda sozlamalar saqlanishi, rus/ingliz til almashtirish va 320px overflow tekshiruvi bajariladi. Ranglar tokens.css da, yangi vizual qoidalar refinements.css da.

2026-11-19 · PCRM-48 · Foydalanuvchi chap paneldagi “Asosiy ombor / Ombor boshqaruvi” kartasini rad etdi. Butun blok va uning maxsus uslublari olib tashlandi; qaytarilmang. Sozlamalardagi ombor ma’lumoti bu o‘zgarishga kirmaydi.

2026-11-19 · PCRM-48 · UI/UX tahlili asosida jadval viewporti, sticky sarlavha, haqiqiy scroll soyasi/ko‘rsatmasi, raqamlar tekisligi, 11px nav guruhlari, bo‘sh natija amallari va qidiruv/kirim klaviatura oqimi qo‘shildi. Warehouse formasi asl ruxsat/validatsiya/idempotency yo‘lidan foydalanadi. Oq fon saqlanadi. Build va mavjud testlar o‘tdi; uch ekranli real API regressiyasi PR/CI’da tekshiriladi.

2026-11-19 · PCRM-48 · Ma’lumot kiritish va ko‘rish foydalanuvchi talabiga ko‘ra jadval shakliga o‘tkazildi: kirim, material, ombor amallari va xarajatlar. Yagona EntryTable komponenti, native form yorliqlari, mobil gorizontal surish; qoldiq ham barcha ekranlarda jadval. Saqlash bir yozuv uchun, avvalgi ruxsat/validatsiya/idempotency saqlanadi. Build va 10 frontend testi o‘tdi; real API bilan uch ekranli CI tekshiruvi PR’da. Issue #54.

## PCRM-48 · Ombor sinovidan keyingi ruxsatlar

Mijoz sinovidan so‘ng kirim, ombor amallari, katalog va xarajatlar havolalari API ruxsatlariga moslandi. Ruxsatsiz manzil o‘rniga foydalanuvchiga mavjud bo‘lim ochiladi. Ishchiga ombor vakolati berilmagan bo‘lsa, sozlamalarda tushuntirish chiqadi. Chiqim, qaytarish va hisobdan chiqarish tablari alohida tekshiriladi. Narx va tasdiqlash ustunlari tegishli vakolat bo‘lganda ko‘rinadi.

Ishlab chiqarish ustasi, Bosh hisobchi va Ta’minotchi sinov rollari endi demo ma’lumotlarida yaratilmaydi. Avval yaratilganlarini tekshirish uchun `python backend/manage.py retire_warehouse_roles`, o‘chirish uchun `--apply` qo‘shiladi. Buyruq biriktirilgan yoki material ko‘rinishida ishlatilayotgan rol bo‘lsa, o‘chirishni to‘xtatadi. Administrator, Ombor mudiri va Ishchi rollari saqlanadi.

Dalil: frontend ssenariylari ruxsatsiz manzil, faqat chiqimga vakolat va faqat xarajatlarni o‘qish huquqini tekshiradi. Backend sinovi rollarni o‘chirish chegarasi va takroriy bajarilishini tekshiradi.
