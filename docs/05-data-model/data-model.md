# Ma'lumotlar modeli — dastlabki tushunchalar

Bu ro‘yxat hali yakuniy ma'lumotlar bazasi jadvallari emas.

## Taklif etilgan obyektlar

| Yo‘nalish | Obyektlar |
|---|---|
| Foydalanuvchilar | Foydalanuvchi, Rol, Ruxsat, RolRuxsati |
| Ombor | MaterialKategoriyasi, Material, MaterialKirimi, OmborHarakati |
| Zakaz | Loyiha, To‘lov, Model, ModelRazmeri, MaterialNormasi |
| Ishlab chiqarish | Ishchi, IshVazifasi, IshQaydi, IshlabChiqarishBosqichi, Nomuvofiqlik |
| Yakunlash | Xarajat, UpakovkaQaydi, Yetkazish, LoyihaYopilishi |

**Izoh:** Adminning dinamik rol va ruxsatlar yaratishi hali tasdiqlanmagan.

## Asosiy aloqalar

- Bitta loyihaga bir nechta model, to‘lov, vazifa va xarajat tegishli bo‘lishi mumkin.
- Bitta modelda turli razmer va material normalari bo‘lishi mumkin.
- Ombor harakati materialga, zarur bo‘lsa loyiha va ishchiga bog‘lanadi.
- Ish qaydi ishchi yoki guruh, vazifa, bosqich va detal miqdoriga bog‘lanadi.
- Loyiha yopilgach barcha tarixiy yozuvlar saqlanadi.

## Katalog modeli · PCRM-38

**18-noyabr 2026 · Taklif, kodda amalga oshirilgan.** Manba: OQ-005, OQ-008, OQ-014, talablar reyestridagi 9 turdagi kategoriya. Django ilovasi — `backend/apps/catalog`, jadval nomlari `catalog_*`.

Katalog «qanday material bor»ligini saqlaydi. Narx, miqdor va kirim sanasi katalogga yozilmaydi. Har bir kirim keyin PCRM-40 doirasida alohida partiya bo‘lib, `Material`ga havola qiladi (OQ-008: katalog va partiya ajratiladi).

| Model | Maydon | Turi | Majburiy | Izoh |
|---|---|---|---|---|
| `Category` | `name` | matn, 100 | ha | Noyob. 9 ta boshlang‘ich nom hujjatlarda yo‘q, shuning uchun migratsiya ularni yaratmaydi — admin qo‘shadi. |
| | `is_active` | mantiqiy | ha, `true` | O‘chirish o‘rniga faolsizlantiriladi. |
| `Material` | `category` | `Category`ga havola | ha | Materiali bor kategoriyani o‘chirish bazada bloklanadi. |
| | `name` | matn, 200 | ha | |
| | `color` | matn, 50 | yo‘q, bo‘sh qator | |
| | `length_cm`, `width_cm`, `thickness_cm` | o‘nlik son, 10,2 | yo‘q | O‘lchamlar santimetrda (OQ-005). Berilsa, 0 dan katta. |
| | `unit` | tanlov | ha | `sheet` list, `piece` dona, `kg`, `liter` litr, `meter` metr, `m2` m². |
| | `is_active` | mantiqiy | ha, `true` | Tarixi bor material o‘chirilmaydi. |
| Ikkalasi | `created_at`, `updated_at` | sana-vaqt | avtomatik | |

**Noyoblik.** Bir kategoriyada `name + color + length_cm + width_cm + thickness_cm + unit` jamlanmasi takrorlanmaydi. Bo‘sh o‘lcham ham teng qiymat sifatida solishtiriladi (PostgreSQL 15+, `NULLS NOT DISTINCT`). Shuning uchun o‘lchamsiz ikkita bir xil «Kley, kg» yaratilmaydi.

**Keyingi vazifalarga qoldirildi.** Minimal qoldiq chegarasi (OQ-014) — PCRM-42. Partiya, asl narx va valyuta — PCRM-40. Birliklar orasidagi konvertatsiya — zarur o‘lcham yoki zichlik ma’lumoti bor bo‘lgandagina, alohida vazifada (OQ-005).

**Tasdiqlash kerak.** OQ-005 da «list/dona» bitta band sifatida yozilgan. Model ularni ikki xil birlik qilib saqlaydi: list — plita, dona — furnitura. PM boshqacha qaror qilsa, tanlovlar ro‘yxati bir migratsiya bilan o‘zgaradi.

## Hali aniqlashtirilmagan masalalar

Tannarx usuli, zaxiraga olish va qoldiqni kamaytirish vaqti, umumiy akkaunt orqali ishni shaxsga bog‘lash, ishbay stavkalar, brak va qayta ishlash qoidalari. Ular aniqlashmaguncha jadvallar yakuniy tasdiqlanmaydi.
