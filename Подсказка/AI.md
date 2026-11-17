# AI yordamchisi uchun ish tartibi

1. **Boshlash.** Rol fayli, Jira vazifasi, tegishli `docs` hujjati va joriy branchni o‘qing. Ochiq PR’larni tekshiring. Bir vazifa bo‘yicha mavjud ishni topib, o‘sha ishni davom ettiring.
2. **Bajarish.** Vazifada ko‘rsatilgan fayllar va modul chegarasida ishlang. API shartnomasi, qoldiq va migratsiyaga tegadigan o‘zgarishni tegishli egasi bilan kelishish uchun PR’da ko‘rsating. Mavjud SOLID, PEP 8 va test qoidalariga amal qiling.
3. **Yangilash.** Ish holati o‘zgarsa, tegishli rol faylidagi qatorni yangilang va oxirgi qaydga sana, natija, tekshiruv, PR yoki commit havolasi va keyingi qadamni yozing. Kod bilan bog‘liq qaydni shu PR tarkibida kiriting. Bir vazifani boshqa a’zoning faylida takroriy statusga aylantirmang.
4. **Tekshirish.** PR ochilgan va ko‘rib chiqishga tayyor bo‘lsa — `Ko‘rikda`. PR birlashgan va qabul mezoni dalili mavjud bo‘lsa — `Bajarildi`. Dalil tekshirilmaganda oxirgi ma’lum holatni qoldiring. PM qarori yoki bog‘liqlik sabab ish yurmasa, bloklovchi sababni yozing.
5. **Holat so‘ralganda.** To‘rtta rol fayli, Jira va ochiq yoki yaqinda birlashgan PR’larni solishtiring. Qisqa hisobotda har bir rol uchun nima tugaganini, nima ketayotganini va keyingi qadamni dalili bilan ayting. Tafovut bo‘lsa, Jira’dagi ish holati va GitHub’dagi kod holatini alohida ko‘rsating.

Ish statuslari: `Reja` → `Jarayonda` → `Ko‘rikda` → `Bajarildi`. Bog‘liqlik chiqsa `Bloklangan` va sababi. Vazifa yoki sprint boshqaruvi uchun Jira’dagi haqiqiy holatga tayaning.

Qayd shakli:

`YYYY-MM-DD · PCRM-XX · holat · nima o‘zgardi · tekshiruv / PR · keyingi qadam yoki bloklovchi sabab`

Jira yoki GitHub ulanishi bo‘lmasa, oxirgi lokal qayd qachon yozilganini ko‘rsating va masofaviy holatni tekshirilmagan deb belgilang. Status so‘rovi yoki faylni o‘qishning o‘zi loyiha holatini o‘zgartirmaydi. Qaydlar loyiha ustida ish olib borilgan va tekshiriladigan dalil mavjud bo‘lgan sessiyada yangilanadi.

Yangi g‘oya, umumiy API yoki biznes qoidasiga o‘zgarish chiqsa, [qarorni kelishish tartibini](COLLABORATION.md) o‘qing. Tavsiya, ta’sirlanadigan jamoadosh va tekshiruvni qisqa yozing. Dalilsiz kelishuv yoki tasdiq qayd etmang.
