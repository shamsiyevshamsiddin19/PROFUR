# Jamoa bilan kelishish va ishni yangilash

Har bir a’zo o‘z vazifasini boshqaradi. Boshqa odamning ekraniga, API’siga yoki ish tartibiga ta’sir qiladigan taklifni o‘sha odam bilan Jira vazifasi yoki PR ichida muhokama qiling. Og‘zaki yoki chatda kelishilgan qarorni ham tegishli Jira yoki PR’da qisqa yozib qo‘ying.

| Qanday qaror | Kim bilan kelishiladi |
|---|---|
| O‘z modulingiz ichidagi nomlash, fayl tuzilishi yoki UI tafsiloti | Vazifa egasi amaldagi standartga tayanib tanlaydi. AI tushuntiradi va tekshiradi. |
| Umumiy API maydoni, migratsiya, ruxsat yoki boshqa a’zoning vazifasiga ta’sir | Ta’sirlanadigan a’zo va Team Lead. Namunaviy javob yoki o‘zgarish diffini birga ko‘rib chiqing. |
| Partiya tanlash, tannarx, valyuta, loyiha doirasi yoki biznes jarayoni | Team Lead masalani PMga olib chiqadi. Tasdiq va sabab [qarorlar jurnalida](../docs/09-decisions/decision-log.md) qayd etiladi. |

## AI qanday maslahat beradi

AI yangi taklifni eshitganda avval amaldagi talab va mavjud kodni tekshiradi. Muammoni oddiy tilda tushuntiradi, haqiqiy tanlov bo‘lsa ikki yo‘lning foydasi va oqibatini aytadi, keyin bitta asosli tavsiya beradi. Javobda qaysi jamoadoshga ta’sir qilishi, qanday tekshirish va ishning xavfsiz boshlanadigan qismini ko‘rsatadi. AI foydalanuvchiga qisqa muhokama matnini tayyorlab berishi mumkin. Uni jamoaga yuborish va kelishish vazifa egasida qoladi.

Masalan, Ozodbek kirim API’sidagi `quantity` maydonini o‘zgartirmoqchi. AI avval Shamsiddinning formasini va amaldagi API shartnomasini tekshiradi. So‘ng ikki tomonga ham ta’sirini, yangi javob namunasini va o‘zgarishni bitta ketma-ketlikda chiqarish taklifini yozadi. Kelishuv va test dalili PR’da saqlanadi.

## Ma’lumot qachon yangilanadi

- **Ish boshida.** Tegishli Jira vazifasi, ochiq PR va rol faylidagi oxirgi qaydni solishtiring. Yangiroq dalil bo‘lsa, keyingi qadamni shunga qarab belgilang.
- **Ish o‘zgarganda.** Yangi qaror, bloklovchi sabab, test natijasi yoki topshirish zarurati chiqsa, o‘sha sessiyada rol faylini yangilang. Qaydga sana, Jira raqami, dalil va keyingi qadamni yozing. Kodga bog‘liq qayd shu PR bilan yuradi.
- **Jamoadoshga topshirishda.** Qaysi ish tayyorligi, qaysi PR yoki API javobidan foydalanishi va undan nima kerakligini aniq yozing.
- **PR birlashgach.** Merge va qabul sinovi dalilini tekshiring. Vazifa egasi keyingi ish sessiyasida yoki topshirish vaqtida rol faylidagi holatni yangilaydi. Kutilayotgan PM qarorini alohida ko‘rsating.

Qaydlar loyiha ustida ishlagan sessiyalarda yangilanadi. Jamoaviy holat kerak bo‘lsa, [AI boshlash sahifasidagi jamoa holati matnidan](START.md) foydalaning.
