# PROFUR CRM MVP — Ochiq savollar reyestri

**Holat:** Dastlabki nusxa — PM va buyurtmachi tasdig‘i kutilmoqda  
**Sana:** 2026-11-17  
**Manba:** `Profur_CRM_MVP_TZ.pdf` (9 sahifa), jamoa yetakchisining rollar va ruxsatlarga oid qo‘shimcha talabi  
**Jira:** [PCRM-31](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-31)

Bu hujjatda 48 savol keltirilgan. Team Leadning 48 ta **dastlabki javobi** [alohida hujjatda](oq-001-048-team-lead-answers.md) saqlangan. Jadvaldagi **OCHIQ** holati PM/buyurtmachi tomonidan **rasmiy tasdiq yo‘qligini** bildiradi, javob umuman berilmaganligini emas. TZda ko‘rsatilmagan funksiyalar avtomatik ravishda MVPga kiritilmaydi.

**Ustuvorlik:** P0 — arxitektura yoki hisob-kitobga bevosita ta’sir qiladi; P1 — asosiy biznes jarayoniga ta’sir qiladi; P2 — UX, infratuzilma yoki operatsion qaror.

## A. Ombor, kirim-chiqim va tannarx

| ID | Ustuvorlik | Buyurtmachiga savol | Nima uchun kerak? | Holat |
|---|---|---|---|---|
| OQ-001 | P0 | Bir xil material turli narxda kirim qilinganda xarajat qaysi usulda hisoblanadi: FIFO, o‘rtacha tannarx yoki boshqa qoida? | Loyiha sarfi va foyda hisobi | OCHIQ |
| OQ-002 | P0 | Material loyiha uchun rejalashtirilganda band qilinadimi, ishchi ombordan olganda qoldiq kamayadimi yoki real ishlatilganda? | Qoldiq va sarf ikki marta kamaymasligi | OCHIQ |
| OQ-003 | P0 | Ishchi olgan, lekin ishlatmagan materialni omborga qaytarish qanday qayd etiladi? | Real sarf va qaytarish hisobi | OCHIQ |
| OQ-004 | P1 | Material kirimida yetkazib beruvchi, hujjat raqami, sana va valyutani qayd etish talab qilinadimi? | Kirim maydonlarini aniqlash | OCHIQ |
| OQ-005 | P0 | List, dona, kg, m² birliklari orasida konvertatsiya qoidalari qanday? Sm va mm uchun yagona birlik qaysi? | Hisob aniqligi | OCHIQ |
| OQ-006 | P1 | Qoldiq manfiy bo‘lishi mumkinmi yoki chiqim bloklanadimi? | Ombor tekshiruvlari | OCHIQ |
| OQ-007 | P1 | Omborda buzilgan/yaroqsiz material qanday hisobdan chiqariladi? | Real xarajat va qoldiq | OCHIQ |
| OQ-008 | P1 | Material nomenklaturasini qanday noyob aniqlaymiz: nom, tur, rang, razmer, qalinlik? | Takroriy materiallarni oldini olish | OCHIQ |
| OQ-009 | P1 | Bir nechta ombor yoki ombor joylashuvi bormi? | Ma’lumotlar modeli | OCHIQ |
| OQ-010 | P1 | Nalog, produkta, stanok kabi qo‘shimcha xarajatlar aniq loyiha bilan bog‘lanadimi yoki umumiy sex xarajatimi? | Foyda hisobiga taqsimlash | OCHIQ |

## B. Zakaz, model va norma

| ID | Ustuvorlik | Buyurtmachiga savol | Nima uchun kerak? | Holat |
|---|---|---|---|---|
| OQ-011 | P0 | Bitta modelning turli razmerlariga material normalari alohida kiritiladimi? | ModelVariant va norma modeli | OCHIQ |
| OQ-012 | P1 | Model shablon sifatida keyingi zakazlarda qayta ishlatiladimi yoki har zakazda qayta yaratiladimi? | Model katalogi | OCHIQ |
| OQ-013 | P1 | Norma 10 ta tumba uchun kiritilib, buyurtma soniga ko‘paytirilganda qoldiqlar qanday yaxlitlanadi? | List/dona hisobining aniqligi | OCHIQ |
| OQ-014 | P0 | Skladda material yetarli bo‘lmasa, modelni saqlashga yoki loyihani ishlab chiqarishga yuborishga ruxsat bormi? | Ogohlantirish va bloklash farqi | OCHIQ |
| OQ-015 | P1 | Model miqdorlari loyiha umumiy sonidan oshsa nima bo‘ladi? | Miqdor validatsiyasi | OCHIQ |
| OQ-016 | P1 | Zakaz summasi/to‘lovlar bitta valyutada saqlanadimi? | Moliyaviy aniqlik | OCHIQ |
| OQ-017 | P1 | Qisman to‘lov uchun aniq summa va sana kiritiladimi yoki faqat holat va shartmi? | To‘lovlar modeli | OCHIQ |
| OQ-018 | P1 | Zakaz bekor qilinsa yoki modellar soni o‘zgartirilsa, rezerv/sarf/qilingan ish qanday qayta hisoblanadi? | Ma’lumotlar izchilligi | OCHIQ |
| OQ-019 | P1 | Mustaqil kalkulyatorda hisob natijasini saqlash yoki zakazga o‘tkazish kerakmi? | Kalkulyator chegarasi | OCHIQ |

## C. Ishchilar, ishlab chiqarish va ishbay haq

| ID | Ustuvorlik | Buyurtmachiga savol | Nima uchun kerak? | Holat |
|---|---|---|---|---|
| OQ-020 | P0 | Oldingi bosqich to‘liq tugamasdan keyingi bosqich qisman boshlanishi mumkinmi? | Workflow/state modeli | OCHIQ |
| OQ-021 | P0 | 3 arrachi bitta akkauntdan foydalansa, bajarilgan ish kimga yoziladi? | Ishbay haq va audit | OCHIQ |
| OQ-022 | P0 | Ishbay haqning har rol/detal uchun stavkasi qancha, stavka vaqtga qarab o‘zgaradimi? | Oylik hisoblash | OCHIQ |
| OQ-023 | P1 | Bir ishchiga bir vaqtning o‘zida bir nechta loyiha vazifasi berilishi mumkinmi? | Task assignment | OCHIQ |
| OQ-024 | P1 | Ishchi bajarilgan detal sonini keyinchalik tahrirlay oladimi, kim tasdiqlaydi? | Audit va xato tuzatish | OCHIQ |
| OQ-025 | P0 | Detallar soni farq qilganda jarayon bloklanadimi yoki izoh bilan davom etadimi? | Nomuvofiqlik workflow | OCHIQ |
| OQ-026 | P1 | Yaroqsiz detal, qayta ishlash yoki yo‘qolgan detal qanday kategoriyalanadi? | Bosqich hisobi | OCHIQ |
| OQ-027 | P1 | Arrachi normadan ortiq material olayotganda faqat ogohlantiriladimi yoki admin ruxsati kerakmi? | Ruxsat va ogohlantirish oqimi | OCHIQ |
| OQ-028 | P1 | Notification kanali push, ilova ichida yoki ikkalasimi? Internet yo‘q bo‘lsa nima qiladi? | Mobil arxitektura | OCHIQ |
| OQ-029 | P1 | Ishchi qaysi tugallangan vazifalarni va qancha muddatlik tarixni ko‘rishi mumkin? | Worker history va data scope | OCHIQ |
| OQ-030 | P1 | Bir ishlab chiqarish bosqichini guruh bajarishi va bir necha shaxsga ishbay haq taqsimlanishi kerakmi? | Team vs individual work log | OCHIQ |

## D. Upakovka, yetkazish va yakuniy foyda

| ID | Ustuvorlik | Buyurtmachiga savol | Nima uchun kerak? | Holat |
|---|---|---|---|---|
| OQ-031 | P0 | Upakovka kategoriyasining 3 ta ichki turi qanday nomlanadi? | TZ §7 dagi ochiq nuqta | OCHIQ |
| OQ-032 | P1 | Upakovka tugallanishi qanday tasdiqlanadi: son, sana, mas’ul yoki boshqa mezon? | Yopilish sharti | OCHIQ |
| OQ-033 | P1 | Yetkazib berish bir necha partiyada bo‘lsa, har bir jo‘natma alohida qayd etiladimi? | Delivery data model | OCHIQ |
| OQ-034 | P0 | Yakuniy foyda tarkibida material, ishbay haq, soliq, stanok, yetkazish va boshqa xarajatlardan qaysilari qatnashadi? | Moliyaviy formula | OCHIQ |
| OQ-035 | P1 | Foyda zakazning kelishilgan summasi asosidami yoki real kelib tushgan to‘lovlar asosidami? | Foyda va cashflow farqi | OCHIQ |
| OQ-036 | P1 | Yopilgan loyihani qayta ochish mumkinmi va kimga ruxsat beriladi? | History va audit | OCHIQ |

## E. Rollar, permissions va xavfsizlik

| ID | Ustuvorlik | Buyurtmachiga savol | Nima uchun kerak? | Holat |
|---|---|---|---|---|
| OQ-037 | P0 | Admin yangi rollarni istalgan nomda yaratib, permissionlarni o‘zi sozlay oladimi? | Team Lead taklifi, TZdan tashqari | OCHIQ |
| OQ-038 | P0 | Admin, ombor mas’uli, ishlab chiqarish boshqaruvchisi va ishchilarning aniq permissionlari qanday? | Roles & Permissions Matrix | OCHIQ |
| OQ-039 | P0 | Ishchi faqat o‘ziga biriktirilgan vazifalarni ko‘radimi, guruh akkaunti bundan mustasnomi? | Obyekt darajasidagi access | OCHIQ |
| OQ-040 | P1 | Foydalanuvchi yaratilishi, parolni tiklash, akkauntni bloklash va rollarni almashtirishni kim bajaradi? | Authentication/authorization | OCHIQ |
| OQ-041 | P1 | Moliyaviy hisobot va ishbay oylikni qaysi rollar ko‘rishi mumkin? | Maxfiy ma’lumotlar | OCHIQ |

## F. Platforma, dizayn va operatsion talablar

| ID | Ustuvorlik | Buyurtmachiga savol | Nima uchun kerak? | Holat |
|---|---|---|---|---|
| OQ-042 | P1 | Ishchilar uchun Android, iOS yoki ikkala platforma shartmi? | Mobile stack | OCHIQ |
| OQ-043 | P1 | Bir vaqtning o‘zida nechta ishchi/admin va nechta faol loyiha bo‘lishi kutilmoqda? | Performance va hosting | OCHIQ |
| OQ-044 | P1 | Internet uzilsa, mobil ilova offline ishlashi va keyin sinxronlashi shartmi? | Offline architecture | OCHIQ |
| OQ-045 | P1 | CRMning interfeys tili qaysi: o‘zbek, rus yoki bir necha tilmi? | UI/UX | OCHIQ |
| OQ-046 | P2 | Qaysi hosting, domen, backup va recovery talablari bor? | Deployment va ishonchlilik | OCHIQ |
| OQ-047 | P2 | Tizimni qabul qilish uchun real sexdagi sinov ssenariylari va mezonlari qanday? | UAT va acceptance | OCHIQ |
| OQ-048 | P1 | Qaysi funksiyalar birinchi ishlab chiqarish pilotiga majburiy, qaysi biri keyingi bosqichga qoldirilishi mumkin? | Scope va release plan | OCHIQ |

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
