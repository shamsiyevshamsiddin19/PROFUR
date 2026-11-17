# PROFUR CRM MVP — Savollar va dastlabki javoblar reyestri

**Holat:** Dastlabki nusxa — PM va buyurtmachi tasdig‘i kutilmoqda  
**Sana:** 2026-11-17  
**Manba:** `Profur_CRM_MVP_TZ.pdf` (9 sahifa), jamoa yetakchisining rollar va ruxsatlarga oid qo‘shimcha talabi  
**Jira:** [PCRM-31](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-31)

Quyida 48 ta savol va Team Lead tomonidan suhbatda berilgan **dastlabki javoblar** bir jadvalda keltirilgan. Batafsil izohlar va aniqlashtirishlar [48 ta javob hujjatida](oq-001-048-team-lead-answers.md) bor. **JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA** holati foydalanuvchi qarori qayd qilinganini, ammo PM va buyurtmachi tasdiqlamagani va ayrim kichik tafsilotlar ochiq qolishi mumkinligini anglatadi. TZdan tashqari funksiyalar PM tasdig‘isiz MVP doirasiga avtomatik qo‘shilmaydi.

**Ustuvorlik:** P0 — arxitektura yoki hisob-kitobga bevosita ta’sir qiladi; P1 — asosiy biznes jarayoniga ta’sir qiladi; P2 — UX, infratuzilma yoki operatsion qaror.

## A. Ombor, kirim-chiqim va tannarx

| ID | Ustuvorlik | Buyurtmachiga savol | Team Lead javobi | Izoh / aniqlashtirish | Holat |
|---|---|---|---|---|---|
| OQ-001 | P0 | Bir xil material turli narxda kirim qilinganda xarajat qaysi usulda hisoblanadi: FIFO, o‘rtacha tannarx yoki boshqa qoida? | Har bir kirim partiyasi asl birlik narxi bilan alohida hisobga olinadi; o‘rtacha narxga majburiy birlashtirilmaydi. | Partiya qaysi chiqimga bog‘lanishi va loyihaga narx taqsimoti algoritmi PM bilan aniqlashtiriladi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-002 | P0 | Material loyiha uchun rejalashtirilganda band qilinadimi, ishchi ombordan olganda qoldiq kamayadimi yoki real ishlatilganda? | Qoldiq materialni loyiha uchun rejalashtirganda emas, ombordan ishchiga amalda berilganda kamayadi. | Loyiha rezervi alohida ko‘rsatilishi zarur bo‘lsa, keyinchalik aniqlanadi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-003 | P0 | Ishchi olgan, lekin ishlatmagan materialni omborga qaytarish qanday qayd etiladi? | Foydalanilmagan material omborga qaytarilishi mumkin; ombor mas’uli tasdiqlagandan keyin qoldiq oshadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-004 | P1 | Material kirimida yetkazib beruvchi, hujjat raqami, sana va valyutani qayd etish talab qilinadimi? | Kirim sanasi va valyutasi saqlanadi; yetkazib beruvchi va hujjat raqami majburiy emas. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-005 | P0 | List, dona, kg, m² birliklari orasida konvertatsiya qoidalari qanday? Sm va mm uchun yagona birlik qaysi? | Birliklar: list/dona, kg, litr, metr, m²; o‘lchamlar santimetrda. Faqat fizik jihatdan asosli avtomatik konvertatsiya. | Konvertatsiya uchun zarur o‘lcham/zichlik kabi parametrlar bo‘lmasa, konvertatsiya bajarilmaydi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-006 | P1 | Qoldiq manfiy bo‘lishi mumkinmi yoki chiqim bloklanadimi? | Ombor qoldig‘i manfiy bo‘lishi taqiqlanadi; yetarli material bo‘lmasa chiqim rad etiladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-007 | P1 | Omborda buzilgan/yaroqsiz material qanday hisobdan chiqariladi? | Yaroqsiz materialni hisobdan chiqarish so‘rovini ombor mas’uli yuboradi; admin sabab ko‘rsatilgan so‘rovni tasdiqlaydi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-008 | P1 | Material nomenklaturasini qanday noyob aniqlaymiz: nom, tur, rang, razmer, qalinlik? | Material atributlari: nom, rang, uzunlik/eni, qalinlik; bir xil materialning har bir yangi kirimi mustaqil yozuv sifatida yuritiladi. | Material katalogi va kirim partiyasi o‘rtasidagi texnik aloqa loyihalashda ajratilsin. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-009 | P1 | Bir nechta ombor yoki ombor joylashuvi bormi? | Dastlab bitta ombor ishlatiladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-010 | P1 | Nalog, produkta, stanok kabi qo‘shimcha xarajatlar aniq loyiha bilan bog‘lanadimi yoki umumiy sex xarajatimi? | Soliq, mahsulot, stanok va boshqa qo‘shimcha xarajatlar aniq loyihaga biriktiriladi. | Loyihalar moduli 1-qismdan keyin kelishi sababli integratsiya bosqichi aniq ko‘rsatiladi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |

## B. Zakaz, model va norma

| ID | Ustuvorlik | Buyurtmachiga savol | Team Lead javobi | Izoh / aniqlashtirish | Holat |
|---|---|---|---|---|---|
| OQ-011 | P0 | Bitta modelning turli razmerlariga material normalari alohida kiritiladimi? | Bir modelning har xil o‘lcham variantlari uchun material normalari alohida saqlanadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-012 | P1 | Model shablon sifatida keyingi zakazlarda qayta ishlatiladimi yoki har zakazda qayta yaratiladimi? | Model katalogi qayta ishlatiladi; buyurtma ichidagi model o‘zgarishi katalog yoki boshqa buyurtmalarga ta’sir qilmaydi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-013 | P1 | Norma 10 ta tumba uchun kiritilib, buyurtma soniga ko‘paytirilganda qoldiqlar qanday yaxlitlanadi? | Material hisoblari ikki kasr xona aniqligida ko‘rsatiladi; foydalanuvchi 'yaxlitlanmasin' degan talabni ham bildirdi. | Ikki kasr xona va yaxlitlamaslik o‘rtasidagi ziddiyatni PM bilan aniqlashtirish zarur. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-014 | P0 | Skladda material yetarli bo‘lmasa, modelni saqlashga yoki loyihani ishlab chiqarishga yuborishga ruxsat bormi? | Zarur material yetishmasa loyihani saqlash/ishlab chiqarishni boshlash bloklanadi va admin hamda mas’ulga xabar beriladi. Admin minimal qoldiq chegarasini belgilaydi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-015 | P1 | Model miqdorlari loyiha umumiy sonidan oshsa nima bo‘ladi? | Model miqdorlari umumiy buyurtmadan oshsa saqlash taqiqlanadi. Kam bo‘lsa farq haqida ogohlantirish va tasdiqlash belgisi; ishlab chiqarishga o‘tishdan oldin miqdor teng bo‘lishi kerak. | Kam miqdorli loyihani ogohlantirishdan keyin saqlash tafsiloti PM bilan tasdiqlansin. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-016 | P1 | Zakaz summasi/to‘lovlar bitta valyutada saqlanadimi? | Buyurtma summasi va mijoz to‘lovlari AQSH dollarida (USD) yuritiladi. | Ombor kirimlarida boshqa valyutalar bo‘lishi mumkin. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-017 | P1 | Qisman to‘lov uchun aniq summa va sana kiritiladimi yoki faqat holat va shartmi? | Har bir qisman to‘lov miqdori, sanasi va qolgan qarz saqlanadi; deadline ixtiyoriy; muddati o‘tgan qarz haqida admin va mas’ulga xabar beriladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-018 | P1 | Zakaz bekor qilinsa yoki modellar soni o‘zgartirilsa, rezerv/sarf/qilingan ish qanday qayta hisoblanadi? | Bekor qilingan buyurtma o‘chirilmaydi, tarixi saqlanadi; son o‘zgarsa kelgusidagi ehtiyoj qayta hisoblanadi, oldin bajarilgan ish va sarflar saqlanadi. Admin yoki loyiha mas’uli o‘zgartiradi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-019 | P1 | Mustaqil kalkulyatorda hisob natijasini saqlash yoki zakazga o‘tkazish kerakmi? | Mustaqil kalkulyator hisob va tarixni saqlaydi; bir tugma orqali hisobni buyurtmaga aylantirish mumkin, ombor tekshiruvi bajariladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |

## C. Ishchilar, ishlab chiqarish va ishbay haq

| ID | Ustuvorlik | Buyurtmachiga savol | Team Lead javobi | Izoh / aniqlashtirish | Holat |
|---|---|---|---|---|---|
| OQ-020 | P0 | Oldingi bosqich to‘liq tugamasdan keyingi bosqich qisman boshlanishi mumkinmi? | Oldingi ishlab chiqarish bosqichi to‘liq tugamasdan, tayyor bo‘lgan miqdor keyingi bosqichga qisman o‘tkazilishi mumkin; detal turi va miqdori qayd etiladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-021 | P0 | 3 arrachi bitta akkauntdan foydalansa, bajarilgan ish kimga yoziladi? | Arrachilar umumiy akkauntdan foydalansa ham har bir ish qaydida ishchining ismi tanlanadi; bajarilgan ish shaxsga yoziladi. | Bir xil akkauntda ism tanlash kuchsiz autentifikatsiya; PM xavfsizlik xavfini baholashi kerak. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-022 | P0 | Ishbay haqning har rol/detal uchun stavkasi qancha, stavka vaqtga qarab o‘zgaradimi? | Ishbay stavkalar har ishlab chiqarish bosqichi bo‘yicha USDda belgilanadi; admin va loyiha mas’uli sozlaydi, o‘zgarishlar faqat kelgusi ishga ta’sir qiladi. | Aniq tariflar/sonlar TZda mavjud emas — PM/buyurtmachi beradi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-023 | P1 | Bir ishchiga bir vaqtning o‘zida bir nechta loyiha vazifasi berilishi mumkinmi? | Ishchida bir nechta loyiha vazifasi bo‘lishi mumkin; odatda bir vaqtda faqat bitta faol vazifa. Biriktirish va jadval sozlanadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-024 | P1 | Ishchi bajarilgan detal sonini keyinchalik tahrirlay oladimi, kim tasdiqlaydi? | Tasdiqlangan ish qaydini ishchi bevosita o‘zgartirmaydi; sabab ko‘rsatib tuzatish so‘rovi yuboradi. Admin yoki loyiha mas’uli tasdiqlaydi; eski/yangi qiymat tarixi saqlanadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-025 | P0 | Detallar soni farq qilganda jarayon bloklanadimi yoki izoh bilan davom etadimi? | Bosqichlardagi miqdorlar farq qilsa ogohlantirish, sabab va tarix bilan mavjud detallar davom etadi; admin/mas’ul xabardor bo‘ladi. Qisman o‘tkazish va yo‘qolishni ajratish kerak. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-026 | P1 | Yaroqsiz detal, qayta ishlash yoki yo‘qolgan detal qanday kategoriyalanadi? | Yaroqsiz, yo‘qolgan va qayta ishlangan detallar alohida kategoriyalanadi; admin yoki loyiha mas’uli tasdiqlaydi; qo‘shimcha xarajat loyihaga yoziladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-027 | P1 | Arrachi normadan ortiq material olayotganda faqat ogohlantiriladimi yoki admin ruxsati kerakmi? | Normadan ortiq material so‘ralganda ishchi sabab kiritadi; admin yoki loyiha mas’uli tasdiqlamaguncha ombor bermaydi; jarayon tarixga yoziladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-028 | P1 | Notification kanali push, ilova ichida yoki ikkalasimi? Internet yo‘q bo‘lsa nima qiladi? | Push va ilova ichidagi xabarnomalar talab qilinadi; internet uzilganda server xabarni navbatda saqlaydi, keyinchalik yetkazadi; o‘qilgan/o‘qilmagan holati bor. | Responsive veb-sayt tanlangani sababli push texnologiyasi va brauzer ruxsatlari qayta baholanadi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-029 | P1 | Ishchi qaysi tugallangan vazifalarni va qancha muddatlik tarixni ko‘rishi mumkin? | Ish va ishbay haq tarixi muddat cheklovisiz saqlanadi. Ishchi o‘zinikini, admin hammasini, loyiha mas’uli faqat o‘z loyihalari ishchilarinikini ko‘radi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-030 | P1 | Bir ishlab chiqarish bosqichini guruh bajarishi va bir necha shaxsga ishbay haq taqsimlanishi kerakmi? | Guruh ishbay haqi har ishchining amaldagi hissasiga mutanosib taqsimlanadi; admin yoki loyiha mas’uli tasdiqlaydi; taqsimot va tasdiqlovchi saqlanadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |

## D. Upakovka, yetkazish va yakuniy foyda

| ID | Ustuvorlik | Buyurtmachiga savol | Team Lead javobi | Izoh / aniqlashtirish | Holat |
|---|---|---|---|---|---|
| OQ-031 | P0 | Upakovka kategoriyasining 3 ta ichki turi qanday nomlanadi? | Upakovka 3 ta ichki turga ajraladi; administrator turlarni qo‘shish, tahrirlash, faolsizlantirish huquqiga ega; tur model/o‘lcham bo‘yicha belgilanadi. | Uchta tur nomi noma’lum — PM/buyurtmachidan olinishi shart. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-032 | P1 | Upakovka tugallanishi qanday tasdiqlanadi: son, sana, mas’ul yoki boshqa mezon? | Upakovka miqdor, sana, ishchi, model/o‘lcham va turi bo‘yicha qayd etiladi; admin/loyiha mas’uli tasdiqlaydi; qisman partiyalar mumkin; rasm ixtiyoriy. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-033 | P1 | Yetkazib berish bir necha partiyada bo‘lsa, har bir jo‘natma alohida qayd etiladimi? | Qisman yetkazib berish mumkin; har jo‘natma sana, model/o‘lcham, miqdor, manzil, mas’ul, status bilan alohida; admin/loyiha mas’uli tasdiqlaydi; barcha jo‘natmalar tasdiqlangach loyiha yopiladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-034 | P0 | Yakuniy foyda tarkibida material, ishbay haq, soliq, stanok, yetkazish va boshqa xarajatlardan qaysilari qatnashadi? | Loyiha xarajati: material, ishbay haq, upakovka, yetkazib berish, yaroqsiz/qayta ish, boshqa loyiha xarajatlari. Tranzaksiya vaqtidagi kurs bo‘yicha USDga keltirish; rejadagi va haqiqiy tannarx/foyda ajratiladi. | Valyuta kursining manbasi va aniqligi PM bilan belgilanadi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-035 | P1 | Foyda zakazning kelishilgan summasi asosidami yoki real kelib tushgan to‘lovlar asosidami? | Shartnoma summasiga asoslangan foyda va real pul oqimi alohida ko‘rsatiladi; jami summa, tushum va qarz ajratiladi. Yetkazilgan loyiha qarz bo‘lsa ham yopilishi mumkin, qarz ochiq qoladi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-036 | P1 | Yopilgan loyihani qayta ochish mumkinmi va kimga ruxsat beriladi? | Yopilgan loyihani admin yoki loyiha mas’uli sabab ko‘rsatib qayta ochishi mumkin; eski tasdiqlangan yozuvlarni faqat tasdiqlanadigan tuzatish bilan o‘zgartirish; kim/qachon/sabab auditi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |

## E. Rollar, permissions va xavfsizlik

| ID | Ustuvorlik | Buyurtmachiga savol | Team Lead javobi | Izoh / aniqlashtirish | Holat |
|---|---|---|---|---|---|
| OQ-037 | P0 | Admin yangi rollarni istalgan nomda yaratib, permissionlarni o‘zi sozlay oladimi? | Admin istalgan nomdagi rollarni yaratadi, ko‘rish/yaratish/tahrirlash/tasdiqlash/o‘chirish ruxsatlarini boshqaradi, foydalanuvchiga bir nechta rol berishi mumkin. Foydalanuvchi ruxsatlari o‘zgarishi tarixini saqlash talab qilinmagan. | Xavfsizlik auditi qo‘shish tavsiya etilishi mumkin, lekin tasdiqlangan talab deb yozilmaydi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-038 | P0 | Admin, ombor mas’uli, ishlab chiqarish boshqaruvchisi va ishchilarning aniq permissionlari qanday? | Admin barcha huquqlarga ega; ombor mas’uli material va kirim-chiqimni yuritadi, ayrim amallar tasdiqlanadi; loyiha mas’uli faqat tayinlangan loyihalarni boshqaradi/tasdiqlaydi; ishlab chiqarish nazoratchisi ish holatini kuzatadi, muammolarni qayd etadi; ishchi o‘z vazifa/ishbay hisobini ko‘radi va ishni qayd etadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-039 | P0 | Ishchi faqat o‘ziga biriktirilgan vazifalarni ko‘radimi, guruh akkaunti bundan mustasnomi? | Ishchi faqat o‘ziga tayinlangan vazifalarni ko‘radi. Umumiy akkauntda ishchi ismi tanlanadi va har ish qaydidan oldin kimligi tasdiqlanadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-040 | P1 | Foydalanuvchi yaratilishi, parolni tiklash, akkauntni bloklash va rollarni almashtirishni kim bajaradi? | Faqat admin akkaunt yaratadi, parolni tiklaydi, rollarni o‘zgartiradi; akkaunt o‘chirilmaydi, faolsizlantiriladi; ish tarixi saqlanadi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-041 | P1 | Moliyaviy hisobot va ishbay oylikni qaysi rollar ko‘rishi mumkin? | Admin barcha loyiha moliyasi va ishbay haqlarni ko‘radi; loyiha mas’uli faqat o‘z loyihalari doirasida; omborchi material xarid narxi/qoldiq qiymatini, lekin foydani emas; ishlab chiqarish nazoratchisi miqdorlarni, lekin moliyani emas; ishchi faqat o‘z ishbay haqini ko‘radi. | — | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |

## F. Platforma, dizayn va operatsion talablar

| ID | Ustuvorlik | Buyurtmachiga savol | Team Lead javobi | Izoh / aniqlashtirish | Holat |
|---|---|---|---|---|---|
| OQ-042 | P1 | Ishchilar uchun Android, iOS yoki ikkala platforma shartmi? | Dastlab Android va iOS uchun ichki tarqatiladigan ishchi ilovasi hamda responsiv admin veb-paneli tanlangan; KEYINGI OQ-048 qaroriga ko‘ra alohida mobil ilova o‘rniga barcha qurilmalarga mos responsiv veb-sayt tanlandi. | Oxirgi tanlov avvalgi mobil ilova qarorini almashtiradi; TZda mobil ilova yozilgani uchun PM tasdig‘i talab qilinadi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-043 | P1 | Bir vaqtning o‘zida nechta ishchi/admin va nechta faol loyiha bo‘lishi kutilmoqda? | Jami foydalanuvchilar, parallel foydalanuvchilar va faol loyihalar soni hozircha noma’lum. Arxitektura kelajakda kengaytirishga tayyor bo‘lishi kerak. | Aniq yuklama mezonlari keyin belgilanadi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-044 | P1 | Internet uzilsa, mobil ilova offline ishlashi va keyin sinxronlashi shartmi? | Tizim to‘liq onlayn ishlaydi. Internet bo‘lmasa yangi ish qaydlari kiritilmaydi; oflayn ish qaydlarini saqlash/sinxronlash talab qilinmaydi. | OQ-028 serverda xabar navbati saqlanishi haqidagi qaror bilan zid emas. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-045 | P1 | CRMning interfeys tili qaysi: o‘zbek, rus yoki bir necha tilmi? | Interfeys: o‘zbek (lotin), rus va ingliz; har foydalanuvchi tilini mustaqil tanlaydi; barcha responsive veb-sahifalarda qo‘llanadi. | Standart dastlabki til alohida belgilanadi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-046 | P2 | Qaysi hosting, domen, backup va recovery talablari bor? | Hosting: bulutli VPS/cloud; domen hozircha noma’lum; har kuni avtomatik backup; nosozlikdan tiklash maqsadi RTO = 4 soat. | RPO, backupni saqlash muddati va amaliy tiklash imkoniyati keyin aniqlanadi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-047 | P2 | Tizimni qabul qilish uchun real sexdagi sinov ssenariylari va mezonlari qanday? | Korxonaning haqiqiy xodimlari loyiha jamoasi bilan birgalikda alohida test muhitida sinov ma’lumotlari yordamida tekshiradi; qabul qiluvchi PM va buyurtmachi birgalikda; asosiy jarayonlar ishlashi va jiddiy xatolar qolmasligi kerak. | Jiddiy xato mezonlari va aniq test ssenariylari PM bilan rasmiylashtiriladi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |
| OQ-048 | P1 | Qaysi funksiyalar birinchi ishlab chiqarish pilotiga majburiy, qaysi biri keyingi bosqichga qoldirilishi mumkin? | HOZIRGI SCOPE: TZdagi MVP 1 ning faqat 1-qismi — kirim-chiqim va ombor nazorati ishlab chiqiladi. Barcha ekranlarga mos bitta responsive veb-sayt; alohida Android/iOS mobil ilovasi hozir qilinmaydi. TZdagi 2–4-qismlar keyingi bosqichlar. | TZdagi '4 qism' va '4 versiya'ni adashtirmaslik; joriy sprint faqat omborga qaratilgan; PM tasdig‘i kutiladi. | JAVOB BERILGAN — PM TASDIG‘I KUTILMOQDA |

## Ishlash tartibi

1. Team Lead savollarni PMga yuboradi; PM buyurtmachidan qaror oladi.
2. Har bir javob uchun **Decision**, **Decision owner**, **Date**, **Impact**, **Affected requirements/Jira issues** qayd etiladi.
3. Javoblar tasdiqlanmaguncha tegishli texnik qarorlar `PROPOSED` holatida qoladi.
4. P0 savollar loyiha arxitekturasi va hisoblash formulalarini yakunlashdan avval yopilishi lozim.
5. Qarorlarni `docs/09-decisions/decision-log.md`ga ko‘chiring.

## Qaror qayd qilish shabloni

```text
Savol ID:
Qaror:
Tanlangan variant:
Sababi:
Tasdiqlagan shaxs:
Tasdiqlangan sana:
Ta'sir qiladigan talablar:
Ta'sir qiladigan Jira vazifalari:
Holat: TASDIQLANGAN / RAD ETILGAN / KEYINGA QOLDIRILGAN
```
