# PROFUR — OQ-001–OQ-048: Team Lead javoblari

**Sana:** 2026-11-17  
**Holat:** **TAKLIF / PROPOSED** — PM va buyurtmachi hali tasdiqlamagan  
**Asos:** Team Lead bilan ChatGPT suhbatida berilgan javoblar; [savollar reyestri](open-questions.md); `Profur_CRM_MVP_TZ.pdf`.  
**Joriy ishlab chiqish chegarasi:** faqat TZdagi **1-qism — ombor/kirim-chiqim**, **responsive veb-sayt**. Qolgan qismlar kelgusida.

> Bu hujjat suhbatdagi tanlovlarni qayd etadi, **PM/buyurtmachi tasdiqlagan talablar** yoki yakuniy TZ o‘rnini bosmaydi. Ayrim savollarning javobi qisman noma’lum; ular pastda ochiq belgilangan. Avvalgi qarorlarga zid so‘nggi qarorlar (ayniqsa OQ-042/OQ-048) aniq qayd etilgan.

## A. Ombor, kirim-chiqim va tannarx

| ID | Team Lead javobi — dastlabki qaror | Izoh / hal qilinmagan jihat |
|---|---|---|
| OQ-001 | Har bir kirim partiyasi asl birlik narxi bilan alohida hisobga olinadi; o‘rtacha narxga majburiy birlashtirilmaydi. | Partiya qaysi chiqimga bog‘lanishi va loyihaga narx taqsimoti algoritmi PM bilan aniqlashtiriladi. |
| OQ-002 | Qoldiq materialni loyiha uchun rejalashtirganda emas, ombordan ishchiga amalda berilganda kamayadi. | Loyiha rezervi alohida ko‘rsatilishi zarur bo‘lsa, keyinchalik aniqlanadi. |
| OQ-003 | Foydalanilmagan material omborga qaytarilishi mumkin; ombor mas’uli tasdiqlagandan keyin qoldiq oshadi. | — |
| OQ-004 | Kirim sanasi va valyutasi saqlanadi; yetkazib beruvchi va hujjat raqami majburiy emas. | — |
| OQ-005 | Birliklar: list/dona, kg, litr, metr, m²; o‘lchamlar santimetrda. Faqat fizik jihatdan asosli avtomatik konvertatsiya. | Konvertatsiya uchun zarur o‘lcham/zichlik kabi parametrlar bo‘lmasa, konvertatsiya bajarilmaydi. |
| OQ-006 | Ombor qoldig‘i manfiy bo‘lishi taqiqlanadi; yetarli material bo‘lmasa chiqim rad etiladi. | — |
| OQ-007 | Yaroqsiz materialni hisobdan chiqarish so‘rovini ombor mas’uli yuboradi; admin sabab ko‘rsatilgan so‘rovni tasdiqlaydi. | — |
| OQ-008 | Material atributlari: nom, rang, uzunlik/eni, qalinlik; bir xil materialning har bir yangi kirimi mustaqil yozuv sifatida yuritiladi. | Material katalogi va kirim partiyasi o‘rtasidagi texnik aloqa loyihalashda ajratilsin. |
| OQ-009 | Dastlab bitta ombor ishlatiladi. | — |
| OQ-010 | Soliq, mahsulot, stanok va boshqa qo‘shimcha xarajatlar aniq loyihaga biriktiriladi. | Loyihalar moduli 1-qismdan keyin kelishi sababli integratsiya bosqichi aniq ko‘rsatiladi. |

## B. Buyurtma, model va material normalari

| ID | Team Lead javobi — dastlabki qaror | Izoh / hal qilinmagan jihat |
|---|---|---|
| OQ-011 | Bir modelning har xil o‘lcham variantlari uchun material normalari alohida saqlanadi. | — |
| OQ-012 | Model katalogi qayta ishlatiladi; buyurtma ichidagi model o‘zgarishi katalog yoki boshqa buyurtmalarga ta’sir qilmaydi. | — |
| OQ-013 | Material hisoblari ikki kasr xona aniqligida ko‘rsatiladi; foydalanuvchi 'yaxlitlanmasin' degan talabni ham bildirdi. | Ikki kasr xona va yaxlitlamaslik o‘rtasidagi ziddiyatni PM bilan aniqlashtirish zarur. |
| OQ-014 | Zarur material yetishmasa loyihani saqlash/ishlab chiqarishni boshlash bloklanadi va admin hamda mas’ulga xabar beriladi. Admin minimal qoldiq chegarasini belgilaydi. | — |
| OQ-015 | Model miqdorlari umumiy buyurtmadan oshsa saqlash taqiqlanadi. Kam bo‘lsa farq haqida ogohlantirish va tasdiqlash belgisi; ishlab chiqarishga o‘tishdan oldin miqdor teng bo‘lishi kerak. | Kam miqdorli loyihani ogohlantirishdan keyin saqlash tafsiloti PM bilan tasdiqlansin. |
| OQ-016 | Buyurtma summasi va mijoz to‘lovlari AQSH dollarida (USD) yuritiladi. | Ombor kirimlarida boshqa valyutalar bo‘lishi mumkin. |
| OQ-017 | Har bir qisman to‘lov miqdori, sanasi va qolgan qarz saqlanadi; deadline ixtiyoriy; muddati o‘tgan qarz haqida admin va mas’ulga xabar beriladi. | — |
| OQ-018 | Bekor qilingan buyurtma o‘chirilmaydi, tarixi saqlanadi; son o‘zgarsa kelgusidagi ehtiyoj qayta hisoblanadi, oldin bajarilgan ish va sarflar saqlanadi. Admin yoki loyiha mas’uli o‘zgartiradi. | — |
| OQ-019 | Mustaqil kalkulyator hisob va tarixni saqlaydi; bir tugma orqali hisobni buyurtmaga aylantirish mumkin, ombor tekshiruvi bajariladi. | — |

## C. Ishlab chiqarish va ishbay haq

| ID | Team Lead javobi — dastlabki qaror | Izoh / hal qilinmagan jihat |
|---|---|---|
| OQ-020 | Oldingi ishlab chiqarish bosqichi to‘liq tugamasdan, tayyor bo‘lgan miqdor keyingi bosqichga qisman o‘tkazilishi mumkin; detal turi va miqdori qayd etiladi. | — |
| OQ-021 | Arrachilar umumiy akkauntdan foydalansa ham har bir ish qaydida ishchining ismi tanlanadi; bajarilgan ish shaxsga yoziladi. | Bir xil akkauntda ism tanlash kuchsiz autentifikatsiya; PM xavfsizlik xavfini baholashi kerak. |
| OQ-022 | Ishbay stavkalar har ishlab chiqarish bosqichi bo‘yicha USDda belgilanadi; admin va loyiha mas’uli sozlaydi, o‘zgarishlar faqat kelgusi ishga ta’sir qiladi. | Aniq tariflar/sonlar TZda mavjud emas — PM/buyurtmachi beradi. |
| OQ-023 | Ishchida bir nechta loyiha vazifasi bo‘lishi mumkin; odatda bir vaqtda faqat bitta faol vazifa. Biriktirish va jadval sozlanadi. | — |
| OQ-024 | Tasdiqlangan ish qaydini ishchi bevosita o‘zgartirmaydi; sabab ko‘rsatib tuzatish so‘rovi yuboradi. Admin yoki loyiha mas’uli tasdiqlaydi; eski/yangi qiymat tarixi saqlanadi. | — |
| OQ-025 | Bosqichlardagi miqdorlar farq qilsa ogohlantirish, sabab va tarix bilan mavjud detallar davom etadi; admin/mas’ul xabardor bo‘ladi. Qisman o‘tkazish va yo‘qolishni ajratish kerak. | — |
| OQ-026 | Yaroqsiz, yo‘qolgan va qayta ishlangan detallar alohida kategoriyalanadi; admin yoki loyiha mas’uli tasdiqlaydi; qo‘shimcha xarajat loyihaga yoziladi. | — |
| OQ-027 | Normadan ortiq material so‘ralganda ishchi sabab kiritadi; admin yoki loyiha mas’uli tasdiqlamaguncha ombor bermaydi; jarayon tarixga yoziladi. | — |
| OQ-028 | Push va ilova ichidagi xabarnomalar talab qilinadi; internet uzilganda server xabarni navbatda saqlaydi, keyinchalik yetkazadi; o‘qilgan/o‘qilmagan holati bor. | Responsive veb-sayt tanlangani sababli push texnologiyasi va brauzer ruxsatlari qayta baholanadi. |
| OQ-029 | Ish va ishbay haq tarixi muddat cheklovisiz saqlanadi. Ishchi o‘zinikini, admin hammasini, loyiha mas’uli faqat o‘z loyihalari ishchilarinikini ko‘radi. | — |
| OQ-030 | Guruh ishbay haqi har ishchining amaldagi hissasiga mutanosib taqsimlanadi; admin yoki loyiha mas’uli tasdiqlaydi; taqsimot va tasdiqlovchi saqlanadi. | — |

## D. Upakovka, yetkazish va yakuniy foyda

| ID | Team Lead javobi — dastlabki qaror | Izoh / hal qilinmagan jihat |
|---|---|---|
| OQ-031 | Upakovka 3 ta ichki turga ajraladi; administrator turlarni qo‘shish, tahrirlash, faolsizlantirish huquqiga ega; tur model/o‘lcham bo‘yicha belgilanadi. | Uchta tur nomi noma’lum — PM/buyurtmachidan olinishi shart. |
| OQ-032 | Upakovka miqdor, sana, ishchi, model/o‘lcham va turi bo‘yicha qayd etiladi; admin/loyiha mas’uli tasdiqlaydi; qisman partiyalar mumkin; rasm ixtiyoriy. | — |
| OQ-033 | Qisman yetkazib berish mumkin; har jo‘natma sana, model/o‘lcham, miqdor, manzil, mas’ul, status bilan alohida; admin/loyiha mas’uli tasdiqlaydi; barcha jo‘natmalar tasdiqlangach loyiha yopiladi. | — |
| OQ-034 | Loyiha xarajati: material, ishbay haq, upakovka, yetkazib berish, yaroqsiz/qayta ish, boshqa loyiha xarajatlari. Tranzaksiya vaqtidagi kurs bo‘yicha USDga keltirish; rejadagi va haqiqiy tannarx/foyda ajratiladi. | Valyuta kursining manbasi va aniqligi PM bilan belgilanadi. |
| OQ-035 | Shartnoma summasiga asoslangan foyda va real pul oqimi alohida ko‘rsatiladi; jami summa, tushum va qarz ajratiladi. Yetkazilgan loyiha qarz bo‘lsa ham yopilishi mumkin, qarz ochiq qoladi. | — |
| OQ-036 | Yopilgan loyihani admin yoki loyiha mas’uli sabab ko‘rsatib qayta ochishi mumkin; eski tasdiqlangan yozuvlarni faqat tasdiqlanadigan tuzatish bilan o‘zgartirish; kim/qachon/sabab auditi. | — |

## E. Rollar, ruxsatlar va xavfsizlik

| ID | Team Lead javobi — dastlabki qaror | Izoh / hal qilinmagan jihat |
|---|---|---|
| OQ-037 | Admin istalgan nomdagi rollarni yaratadi, ko‘rish/yaratish/tahrirlash/tasdiqlash/o‘chirish ruxsatlarini boshqaradi, foydalanuvchiga bir nechta rol berishi mumkin. Foydalanuvchi ruxsatlari o‘zgarishi tarixini saqlash talab qilinmagan. | Xavfsizlik auditi qo‘shish tavsiya etilishi mumkin, lekin tasdiqlangan talab deb yozilmaydi. |
| OQ-038 | Admin barcha huquqlarga ega; ombor mas’uli material va kirim-chiqimni yuritadi, ayrim amallar tasdiqlanadi; loyiha mas’uli faqat tayinlangan loyihalarni boshqaradi/tasdiqlaydi; ishlab chiqarish nazoratchisi ish holatini kuzatadi, muammolarni qayd etadi; ishchi o‘z vazifa/ishbay hisobini ko‘radi va ishni qayd etadi. | — |
| OQ-039 | Ishchi faqat o‘ziga tayinlangan vazifalarni ko‘radi. Umumiy akkauntda ishchi ismi tanlanadi va har ish qaydidan oldin kimligi tasdiqlanadi. | — |
| OQ-040 | Faqat admin akkaunt yaratadi, parolni tiklaydi, rollarni o‘zgartiradi; akkaunt o‘chirilmaydi, faolsizlantiriladi; ish tarixi saqlanadi. | — |
| OQ-041 | Admin barcha loyiha moliyasi va ishbay haqlarni ko‘radi; loyiha mas’uli faqat o‘z loyihalari doirasida; omborchi material xarid narxi/qoldiq qiymatini, lekin foydani emas; ishlab chiqarish nazoratchisi miqdorlarni, lekin moliyani emas; ishchi faqat o‘z ishbay haqini ko‘radi. | — |

## F. Platforma, dizayn va operatsion talablar

| ID | Team Lead javobi — dastlabki qaror | Izoh / hal qilinmagan jihat |
|---|---|---|
| OQ-042 | Dastlab Android va iOS uchun ichki tarqatiladigan ishchi ilovasi hamda responsiv admin veb-paneli tanlangan; KEYINGI OQ-048 qaroriga ko‘ra alohida mobil ilova o‘rniga barcha qurilmalarga mos responsiv veb-sayt tanlandi. | Oxirgi tanlov avvalgi mobil ilova qarorini almashtiradi; TZda mobil ilova yozilgani uchun PM tasdig‘i talab qilinadi. |
| OQ-043 | Jami foydalanuvchilar, parallel foydalanuvchilar va faol loyihalar soni hozircha noma’lum. Arxitektura kelajakda kengaytirishga tayyor bo‘lishi kerak. | Aniq yuklama mezonlari keyin belgilanadi. |
| OQ-044 | Tizim to‘liq onlayn ishlaydi. Internet bo‘lmasa yangi ish qaydlari kiritilmaydi; oflayn ish qaydlarini saqlash/sinxronlash talab qilinmaydi. | OQ-028 serverda xabar navbati saqlanishi haqidagi qaror bilan zid emas. |
| OQ-045 | Interfeys: o‘zbek (lotin), rus va ingliz; har foydalanuvchi tilini mustaqil tanlaydi; barcha responsive veb-sahifalarda qo‘llanadi. | Standart dastlabki til alohida belgilanadi. |
| OQ-046 | Hosting: bulutli VPS/cloud; domen hozircha noma’lum; har kuni avtomatik backup; nosozlikdan tiklash maqsadi RTO = 4 soat. | RPO, backupni saqlash muddati va amaliy tiklash imkoniyati keyin aniqlanadi. |
| OQ-047 | Korxonaning haqiqiy xodimlari loyiha jamoasi bilan birgalikda alohida test muhitida sinov ma’lumotlari yordamida tekshiradi; qabul qiluvchi PM va buyurtmachi birgalikda; asosiy jarayonlar ishlashi va jiddiy xatolar qolmasligi kerak. | Jiddiy xato mezonlari va aniq test ssenariylari PM bilan rasmiylashtiriladi. |
| OQ-048 | HOZIRGI SCOPE: TZdagi MVP 1 ning faqat 1-qismi — kirim-chiqim va ombor nazorati ishlab chiqiladi. Barcha ekranlarga mos bitta responsive veb-sayt; alohida Android/iOS mobil ilovasi hozir qilinmaydi. TZdagi 2–4-qismlar keyingi bosqichlar. | TZdagi '4 qism' va '4 versiya'ni adashtirmaslik; joriy sprint faqat omborga qaratilgan; PM tasdig‘i kutiladi. |

## PM bilan tasdiqlanishi yoki aniqlashtirilishi kerak bo‘lgan masalalar

1. **OQ-001:** narxi turlicha bo‘lgan kirim partiyalarini chiqimga bog‘lash/tannarx tanlash algoritmi.
2. **OQ-013:** ikki kasr xona aniqligi va “yaxlitlanmasin” talabini muvofiqlashtirish.
3. **OQ-015:** umumiy miqdordan kam modelli buyurtmani saqlash mumkinligi bo‘yicha yakuniy qoida.
4. **OQ-022:** ishbay haqning aniq stavkalari.
5. **OQ-031:** upakovkaning uchta ichki turi nomi.
6. **OQ-034:** valyuta kursi manbasi.
7. **OQ-037/039:** dinamik ruxsatlar auditi va umumiy akkaunt identifikatsiyasi xavfsizligi.
8. **OQ-042/048:** TZda mobil ilova nazarda tutilgan, ammo oxirgi Team Lead qarori responsiv veb-sayt; PM bilan kelishish.
9. **OQ-043:** foydalanuvchi, parallel yuklama, faol loyihalar uchun sonli ko‘rsatkichlar.
10. **OQ-045:** standart dastlabki interfeys tili.
11. **OQ-046:** domen, RPO, zaxira nusxalar saqlash muddati va RTO=4 soat maqsadining amaliy bahosi.
12. **OQ-047:** qabul sinovlari va jiddiy xato mezonlarining yozma ro‘yxati.
13. **OQ-048:** dastlabki reliz faqat ombor bo‘lishini va keyingi bosqichlar taqvimini PM tasdiqlashi.

## Reliz chegarasi va Jira

- **Hozir:** 1-qism — 9 ta boshlang‘ich kategoriya va nomenklatura; kirim, birlik narxi, qoldiq, chiqim, qo‘shimcha xarajatlar, operatsiyalar tarixi. [PCRM-1 (Epic)](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-1); [PCRM-5–9 vazifalar](https://shamsiyevshamsiddin19.atlassian.net/jira/software/projects/PCRM/boards/34/backlog).
- **Keyingi qismlar:** buyurtmalar/model/normativlar, ishlab chiqarish/ishchilar, upakovka/yetkazish/yopilish — dastlabki ombor bosqichiga avtomatik kiritilmaydi.
- **Platforma:** telefon, planshet va kompyuter uchun responsive veb-sayt. To‘liq onlayn ish rejimi.
- **Qaror egasi:** Team Lead tomonidan taklif; **yakuniy tasdiqlovchi:** PM va buyurtmachi.
- **Status:** barcha 48 ta javob suhbatda bildirilgan, lekin **hali rasman tasdiqlanmagan**.
