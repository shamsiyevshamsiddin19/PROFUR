# Ishlab chiqish va jamoaviy ish rejasi

## Jamoa

- **PM:** ustoz; muddatlar va buyurtmachi bilan qarorlar.
- **Jamoa yetakchisi:** texnik reja, integratsiya, tekshiruv va muvofiqlashtirish.
- **Qolgan uch a'zo:** dastlabki tavsiya — server/ma'lumotlar bazasi, admin veb-ilovasi, ishchilar mobil ilovasi. Yakuniy taqsimot kelishilmagan.
- **Ish usuli:** AI yordamida kod yaratish; natijani inson ko‘rib chiqishi va testlardan o‘tkazishi shart.

## Jira bo‘yicha holat

- 4 ta yirik modul (Epic): PCRM-1–4.
- 24 ta asosiy foydalanuvchi vazifasi: PCRM-5–24, PCRM-27–30.
- PCRM-25 va PCRM-26 — takroriy vazifalar; sprintga kiritilmaydi.
- 7 ta tayyorgarlik vazifasi: PCRM-31–37.
- Sprint hali boshlanmagan.

## Taklif etilayotgan tartib

1. Muhim ochiq savollarni PM va buyurtmachi bilan aniqlashtirish.
2. Talablar hamda MVP chegarasini tasdiqlash.
3. Arxitektura, ma'lumotlar modeli va API kelishuvini tekshirish.
4. GitHub va AI yordamida kod yozish standartlarini belgilash.
5. Birinchi kichik to‘liq funksiya: omborga kirim → ma'lumotlar bazasi → qoldiq yangilanishi → testlar.
6. Veb va mobil qismlarni bosqichma-bosqich birlashtirish.
7. Haqiqiy foydalanuvchilar bilan sinov va ishga tushirish.

## AI yaratgan kodni qabul qilish

- Kod tasdiqlangan Jira vazifasiga mos bo‘lishi kerak.
- Maxfiy kalitlar va mijoz ma'lumotlari AIga yoki GitHubga joylanmaydi.
- Avtomatik test, inson tekshiruvi va ishga tushirish yo‘riqnomasi kerak.
- Asosiy `main` tarmog‘iga bevosita kod yozilmaydi; Pull Request orqali tekshiriladi.
- Test, xavfsizlik va biznes qoidalaridan o‘tgan o‘zgarishgina birlashtiriladi.
