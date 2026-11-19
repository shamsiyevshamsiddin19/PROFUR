# Umumiy foydalanish va rol bo‘yicha tekshiruv · 2026-11-19

Doira: 1-qismning mavjud ekranlari, jadvalda kiritish, menyu, ruxsatlar va serverdagi joriy rollar. Yangi modul yoki moliyaviy algoritm qo‘shilmaydi.

## Topilgan va tuzatilgan holatlar

| Holat | Natija |
|---|---|
| Hamma kirim oynasidan boshlagan, jumladan kirim ruxsatisiz foydalanuvchi | Bosh sahifa kundalik ishlar va ruxsatga mos havolalarni ko‘rsatadi. |
| Kirim menyusi faqat qoldiqni ko‘rish ruxsati bilan ham chiqqan | Kirim uchun add_receipt, katalogni va qoldiqni ko‘rish kerak; bevosita URL ham tekshiriladi. |
| Ombor amallari ichida foydalanuvchiga tegishli bo‘lmagan tablar ko‘ringan | Faqat yaratish yoki tegishli tasdiqlash ruxsati mavjud tablar chiqadi. |
| Kichik ekranda jadval tashqi blokining minimal eni butun sahifani cho‘zgan | Minimal en jadvalda qoldirildi; konteyner ekran ichida suriladi. |
| Mobil menyu ochilganda klaviatura fokusining orqa sahifaga o‘tishi mumkin bo‘lgan | Fokus menyuda, orqa sahifa inert, Escape yopadi, fokus ochish tugmasiga qaytadi. |
| Ko‘proq yuklanganidan keyin filtr o‘zgarsa eski cursor yana qo‘llanishi mumkin bo‘lgan | So‘rov/til/revision bilan bog‘langan pagination; eski javob yangi natijaga qo‘shilmaydi. |
| Xarajatni faqat ko‘ruvchi foydalanuvchi ham xarajat turlarini so‘ragan | Turlar so‘rovi va yaratish formasi tegishli ruxsat bilan; teskari yozuv uchun turlar majburiy emas. |
| Boshqa sessiyada rol o‘zgarsa menyu eskicha qolgan | Oyna qayta faollashganda va har 60 soniyada /me yangilanadi; server har so‘rovda ruxsatni tekshiradi. |

## Serverda o‘qilgan amaldagi rollar

| Rol | Ko‘rinadigan ishlar |
|---|---|
| ADMIN | Barcha mavjud bo‘limlar va administrator amallari. |
| WAREHOUSE_MANAGER | Materiallarni ko‘rish, kirim, qoldiq/narx, chiqim/qaytarish/hisobdan chiqarish va tasdiqlash, minimal chegara, tarix/xabarlar. |
| PRODUCTION_SUPERVISOR | Materiallar va qoldiqni ko‘rish, chiqim va qaytarish. Kirim, narx, tasdiqlash, hisobdan chiqarish va boshqaruv yo‘q. |
| ACCOUNTANT | Material/qoldiq/narx/tarix, xarajat ko‘rish/yaratish/teskari yozuv, xarajat turlarini ko‘rish. Kirim va ombor amallari yo‘q. |
| PROCUREMENT | Material yaratish/tahrirlash, kategoriya yaratish, kirim va qoldiqni ko‘rish. Narxlarni ko‘rish, chiqim/tasdiqlash, xarajat va boshqaruv yo‘q. |
| WORKER | Hozirgi ruxsatlar ro‘yxati bo‘sh: bosh sahifa va shaxsiy ko‘rinish sozlamalari. Ish bo‘limini administrator biriktiradi. |

Bir necha rol biriktirilsa mavjud server qoidasi bo‘yicha ruxsatlar birlashadi. ADMIN kodi va superuser — serverdagi to‘liq vakolat; yangi maxsus rol avtomatik ADMIN bo‘lmaydi. Bu ish serverdagi rol ruxsatlarini kengaytirmaydi.

Tekshiruvlar: frontend rol matritsasi, taqiqlangan URL’da yopiq sahifa so‘rovlari yo‘qligi, filtr/cursor regressiyasi; haqiqiy API bilan production/accountant/worker login, taqiqlangan POST va admin GET uchun 403; uch ekranli navigatsiya va ombor oqimi. Yakuniy PR/CI dalili topshirishda yoziladi.

P1/P3/P5 ochiq biznes qarorlari va buyurtmachi qabuli bu texnik tekshiruv bilan yopilmaydi.
