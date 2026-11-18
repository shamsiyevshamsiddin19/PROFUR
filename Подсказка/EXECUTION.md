# AI agenti bilan vazifani oxirigacha bajarish

## Ishni olish

Foydalanuvchi rolidagi navbatdagi vazifani bajarishni so‘raganda, AI repo, rol fayli, Jira va mavjud PR’larni tekshirib, hali bajarilmagan birinchi ishni oladi. GitHub loginini bilsa roldan foydalanadi, bilmasa bir marta loginni so‘raydi. Tasdiqlangan vazifa doirasidagi oddiy qaytariladigan texnik tanlovlarni o‘zi qiladi va sababini qisqa aytadi. Har bir fayl yoki funksiya uchun alohida ruxsat so‘rash shart emas.

AI avval lokal o‘zgarishlarni ko‘radi, masofaviy main’ni fetch qiladi va farqni tekshiradi. Ishlayotgan branchga main yangiliklari kerak bo‘lsa, lokal ishni saqlagan holda birlashtiradi. Tayyor asosni qayta yaratmaydi. Vazifaga oid branch yoki PR mavjud bo‘lsa, egasi va holatini tekshirib o‘sha ishni davom ettiradi. Qolgan a’zoning vazifasini olishdan oldin kelishuv kerak.

## Har bir vazifada chiqadigan natija

1. Talab va qabul mezonini o‘qing. Tegishli model, sozlama, test va API shartnomasi mavjudligini tekshiring.
2. Joriy vazifaning eng kichik to‘liq ishlaydigan qismini tanlang. O‘zgarish kerak bo‘lgan fayllar va bog‘liqlikni aytib, kodlashni davom ettiring.
3. So‘rovdan bazagacha haqiqiy yo‘lni ishlating. Forma yoki API xatolarini ham boshqaring. Biznes hisob-kitobini serverda bajaring.
4. Tegishli test, Ruff va migratsiya tekshiruvini bajaring. Muvaffaqiyatsiz tekshiruvni sababini topib tuzating. Tashqi xizmatga kira olmasangiz, qaysi tekshiruv bajarilmaganini dalili bilan yozing.
5. Rol fayliga natija, tekshiruv, branch va keyingi qadamni qo‘shing. Shu o‘zgarishlar bilan commit va push qiling, PR tayyorlang. PR’da Jira raqami, bog‘liq ish, qabul ssenariysi va kim ko‘rishi kerakligi yoziladi.
6. CI natijasini tekshiring. O‘zgarishingizdan kelgan xatoni tuzating va qayta tekshiring. PR’ni jamoadosh ko‘rigiga topshiring. Main’ga merge jamoaning kelishilgan tartibi bo‘yicha bajariladi.
7. Topshirishda a’zoga uch narsani sodda ayting — nima ishlaydi, qayerdan tekshiradi, keyin nima qiladi. Keyingi mustaqil vazifani ham ko‘rsating.

## Umumiy qismlar

| Qism | Asosiy egasi | Birgalikda ishlash |
|---|---|---|
| Muhit, accounts, umumiy Django sozlamalari va CI | Jamoliddin | Yangi app qo‘shgan kishi kerakli sozlama diffini o‘z PR’ida ko‘rsatadi. |
| catalog va inventory’dagi kirim/qoldiq | Ozodbek | Akbar inventory ichida chiqim/qaytarishni shu modelga ulaydi. |
| inventory’dagi chiqim/qaytarish va expenses | Akbar | Ozodbekning modeli va migratsiyasi bilan moslikni tekshiradi. |
| frontend va kirim shakli | Shamsiddin | API javobi o‘zgarsa tegishli backendchi bilan kelishadi. |

accounts, catalog, inventory va expenses joriy modul taklifidir. Repo yoki tasdiqlangan qarorda boshqa nom mavjud bo‘lsa, mavjud tuzilmani tekshirib foydalaning. Bir xil maqsadli ikkinchi app yaratishdan oldin muvofiqlikni tekshiring.

## Bog‘liqlik bo‘lsa

API hali tayyor bo‘lmasa, kelishilgan javob namunalari asosida frontendni davom ettirish mumkin. Autentifikatsiya hali tayyor bo‘lmasa, katalogning ruxsat talabi va sinovini accounts egasi bilan kelishib tayyorlash mumkin. Kutilayotgan PM qarorini taxmin bilan yopmang. Masalani, ta’sirlanadigan vazifani va taklif variantini yozing, keyin shu qarorga bog‘liq bo‘lmagan ishga o‘ting.

GitHub/Jira holatini tekshirish uchun ulanish bo‘lmasa, lokal ishni davom ettiring. Masofaga yuborish yoki tekshirish bajarilmagan bo‘lsa, topshirishda aniq yozing. AI agentlari umumiy GitHub/Jira qaydlari va foydalanuvchi bergan xabarlar orqali kelishuvni kuzatadi. Tashqi xabar yuborish uchun foydalanuvchi topshirig‘i kerak.
