# Backend · Katalog, kirim va qoldiq

**Egasi** — [@ozodbek101](https://github.com/ozodbek101).

**Mas’uliyat** — Katalog va qoldiq modellari, migratsiyalar va kirim API’si.

## Ish tartibi

Avval frontend bilan kirim so‘rovi, javobi va xatolarini kelishing. Material va partiyani ajrating. Kirim va qoldiqni bitta tranzaksiyada yozing. Qoldiqni o‘zgartiradigan umumiy amalni Akbar (@thealiiheere) bilan kelishing va birgalikda tekshiring.

## Vazifalar va holat

`Reja` belgisi boshlang‘ich taqsimotni bildiradi. Ish holatini Jira va PR dalili bilan tekshiring.

| Jira | Natija | Holat | Dalil |
|---|---|---|---|
| [PCRM-38](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-38) | Kategoriya, material va partiya modellari | Reja | — |
| [PCRM-39](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-39) | Katalog API qismi. UI egasi frontend | Reja | — |
| [PCRM-40](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-40) | Kirim API’si va birlik narxi | Reja | — |
| [PCRM-42](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-42) | Qoldiq, minimal chegara va manfiy qoldiqni bloklash | Reja | — |
| [PCRM-49](https://shamsiyevshamsiddin19.atlassian.net/browse/PCRM-49) | ERD va API shartnomasini yig‘ish | Reja | — |

**Qabul mezoni** — Bir materialning ikki xil narxdagi kirimi alohida partiya bo‘ladi. API javobi, qoldiq va harakat tarixi mos keladi.

## Oxirgi qayd

Boshlang‘ich taqsimot. Keyingi ish qaydini [AI ish tartibi](AI.md) bo‘yicha kiriting.

## Navbatdagi ish

1. **PCRM-38** bilan boshlang. Main’dagi Django asosini oling. requirements.txt, settings.py, OQ-005 va OQ-008 hamda ma’lumotlar modelini tekshiring. Katalog va kirim partiyasini ajratish, birliklar, o‘lchamlar va majburiy maydonlar bo‘yicha kichik model taklifini docs/05-data-model ichidagi mavjud hujjatda yozing. Birinchi ishlaydigan kategoriya/material modeli, migratsiya va haqiqiy saqlash sinovini PR qiling.
2. **PCRM-39 / PCRM-49** doirasida kategoriya/material qidiruvi va kirim so‘rovining API manzili, maydonlari, majburiyligi, xato va javob namunalarini docs/06-api-contract ichidagi hujjatda aniqlang. Shamsiddin va Akbar uchun tayyor qismini yozing.
3. **PCRM-40** bilan kirimni bazaga saqlash, asl narx/valyuta, birlik narxi, qoldiq va tarixni bitta tranzaksiyada yozishni quring. Har xil narxdagi ikki partiya va takror so‘rov sinovini bajaring. Yaxlitlash yoki partiya tanlashdagi ochiq qarorni PMga qayd eting.
4. **PCRM-42** uchun mavjud qoldiq, minimal chegara va chiqim bilan umumiy qoldiq tekshiruvini Akbar bilan kelishing.

Boshlashda har bir band allaqachon kod yoki PR’da bajarilganini tekshiring. Akbarga model nomi, identifikator, migratsiya va qoldiq amalining kirish/chiqishini aniq topshiring.
