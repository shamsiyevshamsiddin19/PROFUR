# PROFUR · Ombor uchun muhandislik rejasi

**17-noyabr 2026 · Taklif.** Doira — TZning 1-qismi, bitta ombor va telefon, planshet hamda kompyuterga mos veb-sayt. Interfeys noldan quriladi, UZ/RU/EN tanlovi saqlanadi. Manbalar — [OQ reyestri](../01-requirements/open-questions.md), [Jira Sprint 1](https://shamsiyevshamsiddin19.atlassian.net/jira/software/projects/PCRM/boards/34/backlog).

## Rasmlardan olinadigan mezon

Birinchi va to‘rtinchi rasmda foydalanuvchi ko‘radigan natija ortidagi farq ko‘rsatilgan. Yaxshi poydevor — aniq arxitektura, testlar, o‘qiladigan kod va nosozlikni aniqlash imkoniyati. Ikkinchi rasmda keyingi o‘zgarishlarning narxi ko‘rinadi. Har bir tezkor yamoq hisobni boshqa joyga ko‘chirsa, yangi talab kelganda bir xil qoidani bir nechta joyda tuzatish kerak bo‘ladi. Uchinchi rasmdan oladigan yondashuv — AI yordamida ishni tezlatish, talab, kod tekshiruvi va qabul mezonlarini jamoa boshqarishi.

**2026-11-18 qarori** — barcha pul summalari faqat USD ($), interfeys tillari uz/ru/en. [Qarorlar jurnali](../09-decisions/decision-log.md).

## Tuzilma va javobgarlik

Backend uchun taklif — Django + DRF + PostgreSQL, bitta ilova ichidagi alohida modullar. Katalog material va birliklarni yuritadi. Ombor moduli partiya, harakat, qoldiq va tasdiqlashni boshqaradi. Kirish va ruxsatlar serverda har bir amalda tekshiriladi. Xarajatlar loyiha havolasi bo‘yicha alohida qayd etiladi. API shartnomasi forma maydonlari, ruxsatlar va xato javoblarini belgilaydi. Frontend uchun React/TypeScript taklifi jamoa tajribasi bilan aniqlanadi.

Material bitta katalog yozuvi bo‘lib, turli narxda kelgan kirimlar alohida partiya bo‘ladi. Ombor harakati tarix manbasi. Ishlash tezligi uchun qoldiq alohida saqlansa, u harakat bilan ayni tranzaksiyada yangilanadi. Hisobda o‘nlik sonlar ishlatiladi, kirimning asl narxi va USD valyutasi saqlanadi. Xato operatsiya tasdiqlangan yozuvni o‘zgartirib yuborish o‘rniga sabab va asl yozuvga havolasi bor tuzatish harakati orqali aks etishi taklif qilinadi.

## Kod yozish va tekshirish standarti

- **SOLID.** API so‘rov shaklini tekshiradi va javob beradi. Ombor amali qoldiq, partiya va tasdiqlash qoidalarini bajaradi. Ma’lumotlar bazasi tranzaksiya va cheklovlarni ta’minlaydi. Yangi partiya tanlash usuli kerak bo‘lsa, o‘zgarish shu qoida doirasida qoladi. O‘zaro almashtiriladigan usullar bir xil shartlarga, jumladan manfiy qoldiq va asl narx qoidalariga rioya qiladi. Modullar faqat kerakli amallarni ochadi. Tashqi xizmatlar uchun zarur bo‘lganda kichik interfeys ishlatiladi. Abstraksiya amaldagi ehtiyojga qarab kiritiladi.
- **[PEP 8](https://peps.python.org/pep-0008/) va [PEP 257](https://peps.python.org/pep-0257/).** Python kodida to‘rt bo‘shliq bilan chekinish, ma’noli nomlar va tartibli importlar qo‘llanadi. Ochiq funksiyalar va modul chegaralarida tur annotatsiyalari yoziladi. Docstring amaldagi shartlar, qaytariladigan natija va muhim xatolarni tushuntiradi. [Ruff](https://docs.astral.sh/ruff/) qoidalari bitta loyiha konfiguratsiyasida yuritiladi. Format va lint CI’da tekshiriladi.
- **DRY, KISS va YAGNI.** Qoldiqni tekshirish kabi biznes qoidasi bitta joyda yuritiladi. Kirim va chiqimning umumiy qismi faqat xatti-harakatlari bir xil bo‘lsa ajratiladi. Modul va bog‘liqliklar joriy talabga qarab qo‘shiladi. React/TypeScript tanlansa, qat’iy turlash, lint va build ham CI tekshiruvida bo‘ladi.
- **PR qabul mezonlari.** Jamoa a’zosi kodni ko‘rib chiqadi. CI format, lint, avtomatik test va PostgreSQL migratsiyalarini tekshiradi. Qoldiq yoki ruxsatga ta’sir qiladigan o‘zgarishga tegishli qabul sinovi qo‘shiladi yoki yangilanadi. Maxfiy qiymatlar repozitoriy va jurnallarga yozilmaydi, foydalanuvchi tushunadigan xato javobi serverdan qaytadi.

## Qabul mezonlari

| Ssenariy | Tekshiruv natijasi | Mavjud vazifa |
|---|---|---|
| Bir material ikki xil narxda kirim qilinadi | Ikki partiya qoladi. Har biri asl birlik narxi va valyutasini saqlaydi. | PCRM-38, PCRM-40 |
| Qoldiq 10, ikki xodim bir vaqtda 7 tadan chiqaradi | Bitta chiqim o‘tadi, ikkinchisi qoldiq yetmasligi sabab rad etiladi. Qoldiq 3 va tarixda bitta chiqim. Sinov PostgreSQL’da alohida ulanishlar bilan bajariladi. | PCRM-42, PCRM-44, PCRM-50 |
| Internet uzilib, brauzer bir xil chiqim so‘rovini qayta yuboradi | Bir xil so‘rov kaliti bilan ikkinchi harakat yozilmaydi. Shu kalit bilan boshqa miqdor yuborilsa, so‘rov rad etiladi. | PCRM-44, PCRM-49, PCRM-50 |
| Qaytarish ikki marta tasdiqlanadi | Qoldiq faqat bir marta ortadi. Jami qaytarish asl chiqim miqdoridan oshmaydi. | PCRM-44, PCRM-50 |
| Ombor mas’uli hisobdan chiqarishga so‘rov beradi | Tasdiqlashgacha qoldiq saqlanadi. Ruxsatsiz API chaqiruvi rad etiladi. Muvaffaqiyatli harakatda kim, qachon va sabab qayd etiladi. | PCRM-44, PCRM-45, PCRM-50 |
| Mobil va desktopda kirim ochiladi | 320, 390, 768 va 1440 px kenglikda asosiy amal ko‘rinadi. Til almashganda matnlar boshqaruvni to‘sib qo‘ymaydi. | PCRM-41, PCRM-48, PCRM-50 |

## Ishni boshlash tartibi

1. [PCRM-31](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-31) doirasida PM bilan chiqim uchun partiya tanlash, narx va miqdor aniqligi, loyiha/ishchi havolasi va tasdiqlovchi rollar kelishiladi. Qarorlar yozilguncha tegishli model va formalar taklif holatida qoladi.
2. [PCRM-49](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-49) da model va API kelishuvi tayyorlanadi. Birinchi to‘liq oqim — material yaratish → kirim → qoldiqni ko‘rish. Bu oqim [PCRM-38](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-38)–[PCRM-43](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-43) ishlarini bir-biriga bog‘laydi.
3. [PCRM-37](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-37) doirasida PR uchun mas’ul tekshiruvchi, avtomatik testlar va PostgreSQL migratsiyasi tekshiruvi belgilanadi. AI yozgan o‘zgarish ham shu mezonlardan o‘tadi.
4. [PCRM-50](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-50) da real brauzer sinovi, xato jurnallarida so‘rov identifikatori va sinov muhitida zaxiradan tiklash natijasi qayd etiladi. Biznes tarixi va texnik xato jurnali alohida yuritiladi.

**Eng kichik topshiriladigan natija:** ombor mas’uli telefonidan kirim yozadi, tizim bir marta partiya yaratadi, qoldiq va tarixdan shu yozuvni ko‘rish mumkin. Bu yo‘l sinovdan o‘tgach, chiqim va tasdiqlash oqimlari unga ulanadi.
