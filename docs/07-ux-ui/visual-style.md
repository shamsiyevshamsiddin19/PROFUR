# PROFUR interfeys uslubi

2026-11-18 kuni Team Lead yuborgan «Warehouse Inventory System» tasvirining vizual uslubi tanlandi va «boshla unda» topshirig‘i bilan amalga oshirish boshlandi. Eski Figma maketi ishlatilmaydi. Mavjud React komponentlari PROFUR ombor talablariga mos qoladi.

## Ranglar

| Vazifa | Rang |
|---|---|
| Chap navigatsiya | `#142231` — to‘q ko‘kimtir |
| Ish maydoni | `#f3f5f7` — och kulrang |
| Shakl, jadval va yuqori panel | `#ffffff` |
| Asosiy matn | `#202b38` |
| Ikkilamchi matn | `#687585` |
| Asosiy tugma va faol bo‘lim aksenti | `#e7b554` — vazmin oltin |
| Och fondagi oltin matn | `#79540f` |
| Ajratgich | `#e6eaef` |

Asosiy ranglar `frontend/src/styles.css` ichidagi CSS o‘zgaruvchilarida. Butun ilovani yana to‘liq dark uslubga almashtirmang. Yangi komponentlarni shu palitra bilan yarating.

## Komponentlar

- Chap menyu: ixcham SVG ikonka, faol bo‘limda oltin belgi, pastda foydalanuvchi va chiqish.
- Ish maydoni: och fon, kenglikdan foydalanadigan mazmun, oq yuqori panel va til tanlash.
- Shakllar: oq yuza, nozik ajratgich, yumshoq 7–10 px burchak, aniq fokus, mavjud kutish/xato holatlari.
- Jadvallar: och sarlavha, ixcham qatorlar, yengil hover, uzun jadval uchun o‘z konteynerida gorizontal surish.
- Kirim: material tanlash, USD summa, miqdor, sana va mustaqil hisob-kitob paneli.
- Telefon: menyu ochiladigan panelga aylanadi; kirim formasi va hisob-kitob ketma-ket joylashadi. Matn va tugmalar bir-birini bosmasin.
- Tillar uz/ru/en; barcha summalar USD. Refensdagi Google Sheets brendi, noutbuk maketi, demo statistika va mahsulotlar kiritilmaydi.

Joriy o‘zgarish faqat mavjud ekranlarning ko‘rinishiga tegishli. Kirim backendiga ulanish va hali yo‘q chiqim/tarix ekranlari alohida vazifalardir.
