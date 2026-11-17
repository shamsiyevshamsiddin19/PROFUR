# Подсказка · PROFUR jamoasi

PROFUR’ning joriy doirasi — TZning 1-qismi. Jamoa ombor va kirim-chiqim uchun UZ/RU/EN tillaridagi responsive sayt quradi. Ekranlar noldan yaratiladi.

| Kim | Javobgarlik | Ish va holat yoziladigan fayl |
|---|---|---|
| Shamsiddin · Team Lead | Frontend, API integratsiyasi va PR tartibi | [Frontend](frontend.md) |
| 1-a’zo | Katalog, kirim, qoldiq va API shartnomasi | [Katalog va qoldiq](backend-stock.md) |
| 2-a’zo | Chiqim, qaytarish, hisobdan chiqarish, xarajatlar | [Ombor amallari](backend-operations.md) |
| 3-a’zo | Login, ruxsatlar, CI va tizim sinovlari | [Integratsiya](integration.md) |

Uch a’zoning ismi yoki GitHub logini ma’lum bo‘lganda tegishli faylga yoziladi. Jadval vazifa taqsimoti rejasini ko‘rsatadi. Amaldagi ijrochi, vazifa va sprint holati Jira’da tekshiriladi. [PCRM taxtasi](https://shamsiyevshamsiddin19.atlassian.net/jira/software/projects/PCRM/boards/34/backlog)

## Parallel ishlash va birlashtirish

1. **Umumiy asos.** 3-a’zo PCRM-37 doirasida lokal ishga tushirish yo‘riqnomasi, muhit sozlamalari namunalari va CI’ni tayyorlaydi. Ikki backendchi umumiy model va migratsiyalardagi o‘zgarishlarni kelishadi.
2. **Birinchi oqim.** Siz va 1-a’zo material → kirim → qoldiq uchun API manzillari, maydonlar, javob va xato namunalarini kelishasiz. Shundan so‘ng formani namunaviy javoblar bilan, API’ni esa PostgreSQL bilan parallel qurasiz. 2-a’zo xarajatlar ustida parallel ishlaydi.
3. **PR tartibi.** Bitta vazifaga bitta qisqa branch, masalan `feat/PCRM-40-receipt-api`. Ketma-ketlik — umumiy asos → katalog va kirim API’si → forma integratsiyasi. Mustaqil xarajatlar PR’i o‘z tekshiruvlaridan o‘tgach shu orada birlashishi mumkin. Bog‘liq PR tavsifida oldin qaysi PR birlashishi ko‘rsatiladi.
4. **Qabul.** Kamida bir jamoadosh PR’ni ko‘rib chiqadi. Tegishli testlar va migratsiya tekshiruvi o‘tgach birlashtiriladi. Birinchi qabul sinovida telefon orqali kirim yuboriladi, bitta partiya yaratiladi va ekranda qoldiq ko‘rinadi.

Biznes talablari va tasdiqlar [OQ reyestrida](../docs/01-requirements/open-questions.md), arxitektura va kod standarti [muhandislik rejasida](../docs/03-architecture/warehouse-engineering-plan.md). AI yordamchilari [AI ish tartibi](AI.md) bo‘yicha holatni yuritadi.
