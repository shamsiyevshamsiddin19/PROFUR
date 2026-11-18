# Подсказка · PROFUR jamoasi

PROFUR’ning joriy doirasi — TZning 1-qismi. Jamoa ombor va kirim-chiqim uchun UZ/RU/EN tillaridagi responsive sayt quradi. Ekranlar noldan yaratiladi.

| Kim | Javobgarlik | Ish va holat yoziladigan fayl |
|---|---|---|
| Shamsiddin · Team Lead | Frontend, API integratsiyasi va PR tartibi | [Frontend](frontend.md) |
| [@ozodbek101](https://github.com/ozodbek101) | Katalog, kirim, qoldiq va API shartnomasi | [Katalog va qoldiq](backend-stock.md) |
| [Akbar (@thealiiheere)](https://github.com/thealiiheere) | Chiqim, qaytarish, hisobdan chiqarish, xarajatlar | [Ombor amallari](backend-operations.md) |
| [@jamoliddinusarov1-create](https://github.com/jamoliddinusarov1-create) | Login, ruxsatlar, CI va tizim sinovlari | [Integratsiya](integration.md) |

Jadval vazifa taqsimoti rejasini ko‘rsatadi. Amaldagi ijrochi, vazifa va sprint holati Jira’da tekshiriladi. [PCRM taxtasi](https://shamsiyevshamsiddin19.atlassian.net/jira/software/projects/PCRM/boards/34/backlog)

[AI bilan ish boshlash](START.md) — to‘rt a’zo uchun alohida tayyor matn.

## Parallel ishlash va birlashtirish

1. **Umumiy asos.** [@jamoliddinusarov1-create](https://github.com/jamoliddinusarov1-create) PCRM-37 doirasida lokal ishga tushirish yo‘riqnomasi, muhit sozlamalari namunalari, docker-compose va CI’ni tayyorladi ([feat/PCRM-37-setup-and-ci](https://github.com/shamsiyevshamsiddin19/PROFUR/tree/feat/PCRM-37-setup-and-ci), Ko‘rikda). Jamoadoshlar ushbu poydevor asosida o‘z ishlarini boshlashi mumkin. Ikki backendchi umumiy model va migratsiyalardagi o‘zgarishlarni kelishadi.
2. **Birinchi oqim.** Siz va [@ozodbek101](https://github.com/ozodbek101) material → kirim → qoldiq uchun API manzillari, maydonlar, javob va xato namunalarini kelishasiz. Shundan so‘ng formani namunaviy javoblar bilan, API’ni esa PostgreSQL bilan parallel qurasiz. [Akbar (@thealiiheere)](https://github.com/thealiiheere) xarajatlar ustida parallel ishlaydi.
3. **PR tartibi.** Bitta vazifaga bitta qisqa branch, masalan `feat/PCRM-40-receipt-api`. Ketma-ketlik — umumiy asos → katalog va kirim API’si → forma integratsiyasi. Mustaqil xarajatlar PR’i o‘z tekshiruvlaridan o‘tgach shu orada birlashishi mumkin. Bog‘liq PR tavsifida oldin qaysi PR birlashishi ko‘rsatiladi.
4. **Qabul.** Kamida bir jamoadosh PR’ni ko‘rib chiqadi. Tegishli testlar va migratsiya tekshiruvi o‘tgach birlashtiriladi. Birinchi qabul sinovida telefon orqali kirim yuboriladi, bitta partiya yaratiladi va ekranda qoldiq ko‘rinadi.

Biznes talablari va tasdiqlar [OQ reyestrida](../docs/01-requirements/open-questions.md), arxitektura va kod standarti [muhandislik rejasida](../docs/03-architecture/warehouse-engineering-plan.md). AI yordamchilari [AI ish tartibi](AI.md) bo‘yicha holatni yuritadi.

[Birgalikda ishlash tartibi](COLLABORATION.md) — kim bilan kelishish, AI qanday maslahat berishi va holatni qachon yangilash.

[AI bajarish qo‘llanmasi](EXECUTION.md) — har bir vazifani kod, sinov va PR’gacha yetkazish. Har bir rol faylida navbatdagi ishlarning ketma-ketligi bor.
