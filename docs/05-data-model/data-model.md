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

## Hali aniqlashtirilmagan masalalar

Tannarx usuli, zaxiraga olish va qoldiqni kamaytirish vaqti, umumiy akkaunt orqali ishni shaxsga bog‘lash, ishbay stavkalar, brak va qayta ishlash qoidalari. Ular aniqlashmaguncha jadvallar yakuniy tasdiqlanmaydi.
