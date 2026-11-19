# PROFUR jamoasi uchun ish tartibi

Har bir vazifadan oldin [Подсказка yo‘riqnomasi](Подсказка/README.md), [AI ish tartibi](Подсказка/AI.md) va tegishli a’zoning ish faylini o‘qing. Vazifa, ijrochi va sprintni Jira orqali tekshiring. Ombor qoidalari va arxitektura [docs](docs/README.md) bo‘limida yuritiladi.

Ish tugaganda yoki topshirilganda, tegishli rol faylidagi vazifa holati va dalilini yangilang. Kod o‘zgargan bo‘lsa, bu qaydni shu PR’ga kiriting. Ombor qoidasi, texnologiya yoki sprint holati faqat tegishli qaror yoki dalil asosida yangilanadi.

## Ishni boshlash

- GitHub hisobini yoki foydalanuvchi ko‘rsatgan rolni [jamoa ro‘yxati](Подсказка/README.md) bilan solishtiring. Ijrochi noma’lum bo‘lsa, Jira vazifasi egasini tekshiring. Ikki manba farq qilsa, o‘zgarish kiritishdan oldin farqni ayting.
- Joriy ish — TZning 1-qismi. Ombor sayti telefon, planshet va kompyuterga mos, tillar UZ/RU/EN. Eski maketlar va keyingi modullar joriy vazifaga kirmaydi. Qoidalar uchun [OQ reyestri](docs/01-requirements/open-questions.md), [qarorlar jurnali](docs/09-decisions/decision-log.md) va [muhandislik rejasi](docs/03-architecture/warehouse-engineering-plan.md)ni tekshiring. Takliflarni tasdiqlangan qaror sifatida qo‘llamang.
- Ish boshida joriy tarmoq va lokal o‘zgarishlarni tekshiring. Ochiq PR yoki davom etayotgan ish bo‘lsa, mavjud natijani saqlang. Mustaqil vazifaga Jira raqami bilan branch oching. Boshqa odamning o‘zgarishlarini bekor qilmang.
- Loyiha ishga tushirish yoki test buyruqlarini mavjud fayllardan aniqlang. Konfiguratsiya yoki test hali qo‘shilmagan bo‘lsa, buni aniq qayd eting. Natijani Jira vazifasi, o‘zgargan fayllar, bajarilgan tekshiruv va keyingi qadam bilan topshiring.

Chat yoki qo‘lda ish boshlash uchun [AI boshlash matnlari](Подсказка/START.md)dan foydalaning.

Yangi qaror yoki jamoadoshga ta’sir qiladigan o‘zgarishda [birgalikda ishlash tartibiga](Подсказка/COLLABORATION.md) amal qiling. AI variantlar va tavsiya beradi, kelishuv va qaror dalilga tayangan holda yoziladi.

## AI bilan amaliy bajarish

Jamoa a’zolari dastlabki tajribaga ega. Vazifa berilganda [bajarish qo‘llanmasi](Подсказка/EXECUTION.md) va o‘z rol faylidagi “Navbatdagi ish” bo‘limiga tayanib o‘qish → kodlash → tekshirish → PR → topshirish yo‘lini bajaring. Faqat reja yoki maslahat bilan to‘xtamang. Oddiy texnik tanlovlarda o‘zingiz qaror qilib sababini tushuntiring. Umumiy API, moliyaviy hisob va biznes qoidasiga tegadigan ochiq masalani tegishli egasi yoki PM bilan kelishish uchun qayd eting.

## PM tasdig‘i qaydi

2026-11-18 kuni Team Lead OQ-001–OQ-048 javoblari PM tomonidan tasdiqlanganini xabar qildi. Agent tasdiqlangan talablar bilan ishni davom ettiradi. Noma’lum qiymat yoki algoritm haqidagi izoh tegishli masala bo‘yicha aniqlashtiriladi. Tafsilotlar docs/09-decisions/decision-log.md da.

## Yagona valyuta va uch til

2026-11-18 kungi foydalanuvchi qarori — barcha pul summalari faqat USD ($). Interfeys tillari uz, ru, en. Bu qaror docs/09-decisions/decision-log.md da yozilgan va boshqa valyutalar/kurs haqidagi eski takliflarni almashtiradi. Har bir agent o‘z vazifasidagi eski API namunalari, shakllar va tekshiruvlarni shu qarorga moslashtiradi.

## Frontend uslubi · 2026-11-18

Foydalanuvchi oq fonni saqlash va tizim ranglari hamda dizayn kamchiliklarini yaxshilashni so‘radi. Joriy [vizual uslub](docs/07-ux-ui/visual-style.md): oq ish maydoni, safir ko‘k asosiy amallar, grafit matn va to‘q neytral navigatsiya. Avvalgi oltin palitra va rad etilgan login bezagi qaytarilmasin. UZ/RU/EN va USD saqlanadi.

## Vizual yangilanish · 2026-11-19

Foydalanuvchi avvalgi palitra/chap panelni oddiy deb topdi. Joriy standart: oq ish maydoni, zumrad aksent, to‘q yashil-grafit guruhlangan navigatsiya; sozlamalarda indigo/binafsha ham tanlanadi. Bu oldingi safir rangni majburiy standart sifatida qo‘llashni almashtiradi. Login dekorini qaytarmang. Tafsilotlar docs/07-ux-ui/visual-style.md da.
