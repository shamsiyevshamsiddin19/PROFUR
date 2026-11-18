# PROFUR interfeys uslubi

2026-11-18 kuni Team Lead yuborgan «Warehouse Inventory System» tasvirining vizual uslubi tanlandi va «boshla unda» topshirig‘i bilan amalga oshirish boshlandi. Eski Figma maketi ishlatilmaydi. Mavjud React komponentlari PROFUR ombor talablariga mos qoladi.

## Ranglar

| Vazifa | Rang |
|---|---|
| Chap navigatsiya | `#101f32` — chuqur ko‘kimtir |
| Ish maydoni | `#f4f6f9` — och sovuq kulrang |
| Asosiy yuza | `#ffffff` |
| Maydonlar | `#fbfcfe` |
| Hisob-kitob paneli | `#fffcf5` — iliq oq |
| Asosiy matn | `#1c2b3e` |
| Ikkilamchi matn | `#647187` |
| Asosiy tugma | `#e1ac45` — oltin |
| Oltin matn | `#77500b` |
| Ajratgich | `#e1e6ee` |
| Xato | `#a7302a`, och yuza `#fff1ef` |
| Muvaffaqiyat | `#216342`, och yuza `#edf8f0` |
| Ogohlantirish | `#79520d`, och yuza `#fff8e7` |

Barcha ranglar `frontend/src/tokens.css`da saqlanadi. Komponent uslublarida tayyor CSS o‘zgaruvchilarini ishlating; alohida hex yoki nomlangan rang yozmang. `styles.css` joylashuv va shaklni, `tokens.css` esa ranglarni boshqaradi. Brauzer paneli uchun `index.html`dagi `theme-color` navigatsiya rangiga mos bo‘lishi kerak.

Faol, hover, fokus, disabled, autofill, matn tanlash, surish paneli va soyalar ham yagona palitradan foydalanadi. Disabled holatni faqat shaffoflik bilan belgilanmaydi: alohida neytral yuza va matn qo‘llanadi. Gold aksent dekor va asosiy amal uchun, holat xabarlari esa o‘z semantik ranglari uchun ishlatiladi.

Asosiy tekshirilgan matn/yuza juftliklari kamida 4.5:1 kontrastga ega: asosiy/ikkilamchi matn, placeholder, tugma, menyu, xato/muvaffaqiyat/ogohlantirish. Bu butun ilovaning accessibility auditi o‘rnini bosmaydi. Butun ilovani yana to‘liq dark uslubga almashtirmang.

## Komponentlar

- Chap menyu: ixcham SVG ikonka, faol bo‘limda oltin belgi, pastda foydalanuvchi va chiqish.
- Ish maydoni: och fon, kenglikdan foydalanadigan mazmun, oq yuqori panel va til tanlash.
- Shakllar: oq yuza, nozik ajratgich, yumshoq 7–10 px burchak, aniq fokus, mavjud kutish/xato holatlari.
- Jadvallar: och sarlavha, ixcham qatorlar, yengil hover, uzun jadval uchun o‘z konteynerida gorizontal surish.
- Kirim: material tanlash, USD summa, miqdor, sana va mustaqil hisob-kitob paneli.
- Telefon: menyu ochiladigan panelga aylanadi; kirim formasi va hisob-kitob ketma-ket joylashadi. Matn va tugmalar bir-birini bosmasin.
- Tillar uz/ru/en; barcha summalar USD. Refensdagi Google Sheets brendi, noutbuk maketi, demo statistika va mahsulotlar kiritilmaydi.

Joriy o‘zgarish faqat mavjud ekranlarning ko‘rinishiga tegishli. Kirim backendiga ulanish va hali yo‘q chiqim/tarix ekranlari alohida vazifalardir.
