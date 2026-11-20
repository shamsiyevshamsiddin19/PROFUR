# PROFUR interfeys uslubi

## Joriy yo‘nalish · 2026-11-18

Foydalanuvchi fonni oq saqlab, tizim ranglari va dizayndagi kamchiliklarni tuzatishni so‘radi. Joriy yechim — oq ish maydoni, grafit matn, safir ko‘k asosiy amallar va to‘q neytral navigatsiya. Bu avvalgi oltin rangli palitrani almashtiradi. Kirish sahifasidagi rad etilgan qutilar tasvirini qaytarmang.

## Ko‘rikda topilgan va tuzatilgan kamchiliklar

- 8–11 px yordamchi matnlar telefonda juda mayda edi. Yordamchi matnlar odatda 12 px, maydonlar 14 px, bo‘lim sarlavhalari 16 px bo‘ldi. Navigatsiya guruhi kabi qisqa metama’lumotlar bundan mustasno.
- Oltin rang amal, bezak va ma’lumotda birday ishlatilgan. Ko‘k asosiy amal va faol navigatsiya uchun; yashil/qizil/ambar natija holatlari uchun ajratildi. USD belgisi neytral.
- Maydon chegarasi va oq yuza kontrasti past edi. Yangi chegarada 3.11:1, ko‘k fokusda 6.16:1 kontrast tekshirildi.
- Kirim hisob-kitobidagi dekorativ shakl va takrorlangan sarlavha/valyuta yozuvlari kamaytirildi. Asosiy e’tibor material, miqdor va summada.
- Kichik ekranda uzun yorliqlar yonma-yon maydonlarni notekis ko‘rsatgan. Ixtiyoriy maydon yorliqlari tekislandi, 320 px da sana maydonining ichki bo‘shlig‘i tuzatildi.
- Mobil menyu kirish-chiqishdan keyin ochiq qolishi mumkin edi. Holat tozalanadi; desktopda ortiqcha qoraytiruvchi qatlam ko‘rsatilmaydi. Avtomatik regressiya sinovi bor.

## Palitra

| Vazifa | Qiymat |
|---|---|
| Fon va asosiy yuza | `#ffffff` |
| Asosiy matn | `#182230` |
| Ikkilamchi matn | `#5d6b7d` |
| Asosiy amal | `#2956d7`, ustidagi matn `#ffffff` |
| Hover | `#2147b5` |
| Och ko‘k yuza | `#edf2ff` |
| Hisob-kitob yuza | `#f8faff` |
| Navigatsiya | `#131e30` |
| Faol navigatsiya | `#243c67` |
| Maydon chegarasi | `#8793a5` |
| Strukturaviy ajratgich | `#e4e8ef` |
| Xato / muvaffaqiyat / ogohlantirish | `#a7302a` / `#216342` / `#79520d` |

Manba — `frontend/src/tokens.css`. Komponentda yangi tarqoq hex rang yozmang. Brauzer `theme-color`i oq. Yordamchi yuza yoki ikonka rangini asosiy amal rangidan balandroq urg‘uda ishlatmang.

## Komponent qoidalari

- Bir sahifada asosiy sarlavha, qisqa izoh va mazmunning aniq tartibi bo‘lsin. Takroriy brand/sarlavha va vazifasiz dekor qo‘shmang.
- Yorliq va maydon orasida 8 px; guruhlar orasida 20–24 px masofa saqlang. Ixtiyoriylik yorliq bilan yonma-yon ko‘rsatiladi.
- Maydon va asosiy tugma kamida 44 px balandlikda; ikonka tugmalar 40×40 px. Telefon va uzun tarjimalarda tekshiring.
- Fokus ko‘rinadigan bo‘lsin. Xato faqat rang bilan emas, matn va maydonning aria atributlari bilan ham ko‘rsatilsin. Disabled holat alohida neytral rangda.
- Tashqi panellar nozik strukturaviy chiziqda; foydalanuvchi yozadigan maydon chegarasi kuchliroq. Har bir elementga qalin border bermang.
- Jadvallar oq yuza, neytral sarlavha va sokin hoverda. Gorizontal surish jadval konteynerida, butun sahifada emas.
- Login markazdagi forma bo‘lib qoladi. Yangi dekorativ tasvir qo‘shmang.
- UZ/RU/EN va USD saqlanadi. Faqat haqiqiy API ma’lumotlari ko‘rsatiladi.

## O‘rganilgan manbalar va tekshiruv

[Atlassian rang tamoyillari](https://atlassian.design/foundations/color/) — neytral, asosiy amal va status ranglarini vazifasiga qarab ajratish.

[W3C matn kontrasti](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — oddiy matn uchun 4.5:1 chegara. Tekshirilgan juftliklar: asosiy matn 16.03:1; ikkilamchi matn 5.43:1; oq matnli ko‘k tugma 6.16:1.

[W3C boshqaruv kontrasti](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) — muhim boshqaruv belgilari uchun 3:1. Har bir dekorativ chiziq bu talabga kirmaydi.

[W3C bosish maydoni](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — kamida 24×24 px yoki tegishli masofa; PROFUR asosiy boshqaruvlari buning ustida tanlandi.

Bu to‘liq WCAG muvofiqligi auditi emas. Brauzerda 320/768 px va desktop, uch til, mobil menyu va maydon joylashuvi tekshirildi. Build hamda 4 frontend sinovi bajariladi.

## 2026-11-19 · Rang, navigatsiya va sozlamalar yangilanishi

Foydalanuvchi oldingi ranglar/chap panelni oddiy deb baholadi. Asosiy oq ish maydoni saqlandi; standart aksent zumrad (#087d68), navigatsiya to‘q yashil-grafit. Sidebar ombor, nazorat va boshqaruv guruhlariga ajratildi. Faol sahifa ikonka, chegara va fon bilan belgilanadi; rangning o‘zi yagona belgi emas. Profil pastda alohida joylashgan. Past ekranlarda menyu o‘z ichida aylanadi.

`#settings`: zumrad/indigo/binafsha aksent, keng/ixcham qatorlar, kamaytirilgan animatsiya, uz/ru/en til tanlovi va qayta tiklash. Ko‘rinish sozlamalari ushbu brauzerda `profur.appearance` bilan saqlanadi; server yoki boshqa xodim sozlamasini o‘zgartirmaydi. Brauzer saqlashni taqiqlasa sessiyadagi tanlov ishlaydi va holat tushuntiriladi. USD va ombor ma’lumotlari axborot sifatida ko‘rsatiladi. Ruxsatlar serverdagi shartnoma bo‘yicha qoladi.

2026-11-19 foydalanuvchi tuzatishi: chap paneldagi “Asosiy ombor / Ombor boshqaruvi” kartasi olib tashlandi. Uning o‘rniga dekor yoki takroriy yozuv qo‘shilmang.

## 2026-11-19 · UI/UX tahlilidan amaliy yaxshilash

Oq canvas bo‘yicha foydalanuvchining avvalgi qarori saqlandi. Sidebar guruhlari 11px; barcha jadvallar va raqamli maydonlarda tabular raqamlar; asosiy tugmada semantik token bilan nozik ichki yorug‘lik. Jadvalni o‘rash `TableViewport` da: sarlavha jadvalning o‘z scroll hududida yopishadi, faqat haqiqiy gorizontal overflow bo‘lsa chet soyasi va uch tilli surish ko‘rsatmasi chiqadi. Scroll hududi kerak bo‘lganda klaviaturadan fokuslanadi, ekran/baza o‘zgarsa ResizeObserver bilan yangilanadi. Stock mobil kartalari sahifada tabiiy davom etadi.

`/`, Ctrl+K yoki Cmd+K joriy sahifadagi mavjud qidiruvga fokus beradi. Matn yozish, IME va ochiq dialog ichidagi tugmalarni tortib olmaydi. Kirimda input ichidagi Enter maydonni tekshirib keyingisiga o‘tkazadi; Ctrl/Cmd+Enter native forma validatsiyasi va mavjud saqlash/ruxsat/idempotency orqali yozadi. Select, tugma va oddiy textarea xatti-harakati saqlanadi. Bo‘sh katalog/qoldiq/xarajat/tarixda filtrni tozalash, kerakli bo‘limga o‘tish yoki ruxsatli yaratish amali taklif qilinadi. Jonli birlik narxi avvaldan mavjud bo‘lgani uchun qayta qurilmadi.


## Jadvalda kiritish va ko‘rish · 2026-11-19

Foydalanuvchi qarori: kirim, material tafsilotlari, chiqim/qaytarish/hisobdan chiqarish va xarajat maydonlari ustun sarlavhasi hamda kiritish qatoridan iborat `EntryTable` bilan beriladi. Bir saqlash — bir yozuv; bu ommaviy saqlash yoki mavjud moliyaviy yozuvni bevosita tahrirlash imkoniyati emas. 650 px gacha kirim maydonlari va jadval yozuvlari ekran kengligiga sig‘adigan ikki ustunga joylashadi. Har qiymat o‘z sarlavhasi bilan chiqadi. Uzun matn qatorga o‘tadi va jadval yon tomonga surilmaydi. Maydon yorliqlari ekran o‘quvchiga bog‘langan, xato tegishli katakda, saqlash amali esa doimo jadval tashqarisida ko‘rinadi. Tab bilan kataklar orasida yuriladi; kirimdagi Enter/Ctrl+Enter oqimi saqlanadi. Oq fon, aksent tanlovi, USD, uz/ru/en va server validatsiyasi o‘zgarmaydi.
