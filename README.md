# PROFUR

PROFUR — mebel ishlab chiqarish korxonasi uchun ombor va kirim-chiqim boshqaruvi tizimi (MVP 1-bosqich: responsive veb-sayt).

## Jamoa va yo‘riqnomalar
- [Подсказка](Подсказка/README.md) — jamoa vazifalari, parallel ish va holat yuritish.
- [AI bilan ishlash tartibi](Подсказка/AI.md) — AI yordamchilari uchun qoidalar.
- [Loyiha hujjatlari](docs/README.md) — talablar, arxitektura, ma'lumotlar modeli va qarorlar.

---

## Mahalliy ishga tushirish (Local Setup)

Loyiha ustida ishlashni boshlash uchun quyidagi ketma-ketlikni bajaring:

### 1. Repozitoriyni olish va virtual muhit yaratish
```bash
git clone https://github.com/shamsiyevshamsiddin19/PROFUR.git
cd PROFUR

# Python virtual muhitini yaratish va faollashtirish (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate

# Bog'liqliklarni o'rnatish
pip install -r requirements.txt
```

### 2. Muhit sozlamalarini tayyorlash
Namuna fayldan nusxa olib `.env` yarating:
```bash
cp .env.example .env
```
Zarur bo‘lsa, `.env` ichidagi ma’lumotlar bazasi yoki kalit qiymatlarini tahrirlang.

### 3. Serverni ishga tushirish (Backend)
```bash
python backend/manage.py migrate
python backend/manage.py runserver
```
Tekshirish uchun brauzerda oching: `http://127.0.0.1:8000/api/health/`


### 4. Ma’lumotlar bazasini ishga tushirish (PostgreSQL)
Docker o‘rnatilgan bo‘lsa, PostgreSQL bazasini bitta buyruq bilan ko‘taring:
```bash
docker compose up -d
```
Bazani to‘xtatish uchun:
```bash
docker compose down
```

### 5. Kod sifati va formatlash tekshiruvi (Ruff)
Jamoamizda Python kodi uchun [Ruff](https://docs.astral.sh/ruff/) standart qilib belgilangan:
```bash
# Kodni tekshirish (linter)
ruff check .

# Kodni avtomatik to'g'rilash
ruff check --fix .

# Kodni formatlash (formatter)
ruff format .
```

### 6. Testlarni ishga tushirish (pytest)
```bash
pytest
```

### 7. Avtomatlashtirilgan tekshiruv (CI)

Har bir ochilgan Pull Request (PR) GitHub Actions orqali avtomatik tarzda quyidagilar bo‘yicha tekshiriladi:
- Ruff lint va formatlash tekshiruvi
- Ma’lumotlar bazasi migratsiyalari to‘liqligi (`makemigrations --check`)
- Avtomatlashtirilgan testlar


## Foydalanuvchi modeli bilan yangilash

Accounts ilovasi accounts.User modelini qo‘llaydi. Yangi muhitda migratsiyalar
toza PostgreSQL bazaga bajariladi. Oldin standart auth.User bilan migratsiya
qilingan bazada admin migratsiyasi tarixi yangi modelga mos kelmasligi mumkin.
Bunday bazada avval zaxira nusxa va mavjud ma’lumotlar tekshiriladi, ko‘chirish
rejasi Jamoliddin bilan kelishiladi. Lokal ishlab chiqish uchun yangi bo‘sh
baza tanlash mumkin. Eski baza ma’lumotlarini saqlang.

## Biznes endpointlari uchun ruxsat

Accounts ichidagi HasPermissionCode tekshiruvi ko‘rinishdagi required_permission
kodini Role.permissions ro‘yxati bilan solishtiradi. Ombor uchun aniq kodlar
docs/06-api-contract/warehouse-api-v1.md shartnomasida berilgan.

## Frontend — PCRM-48 va PCRM-41

Frontend uchun React, TypeScript va Vite tanlandi. Node.js 22.12+ kerak.
Frontend papkasida npm ci, keyin npm run dev orqali ishga tushiring.
Brauzer manzili http://127.0.0.1:5173. Django alohida 127.0.0.1:8000 da
ishlashi kerak. Vite /api so‘rovlarini Django’ga yo‘naltiradi, asl Host
sarlavhasini saqlaydi. Ishlab chiqarishda frontend va /api bir origin ostida
HTTPS orqali xizmat qilishi kerak.

Login uchun administrator bergan hisobdan foydalaning. Kod ichida tayyor
login yoki parol yo‘q. Tarjima tillari uz, ru va en, tanlov brauzerda saqlanadi.
Qayta yuboriladigan kirim faqat USD. Natijasi noma’lum qolgan so‘rov kaliti
va tanasi shu tab sessiyasida saqlanadi, sahifa qayta ochilsa ayni so‘rov takrorlanadi.

npm run build — TypeScript va ishlab chiqarish yig‘masi.
npm test — login CSRF/til, kirimni qayta yuborish hamda mavjud bo‘lmagan
katalog holati uchun avtomatik sinovlar.

Joriy bog‘liqlik — main’da katalog va kirim endpointlari hali mavjud emas.
Login haqiqiy accounts API’siga ulanadi. Material ro‘yxati va kirim API’si
tayyor bo‘lgach frontend shartnomadagi /api/v1 manzillaridan foydalanadi.
Bu API’lar 404 bersa, frontend xizmat mavjud emasligini ko‘rsatadi,
saqlash muvaffaqiyatini esa faqat server javobidan keyin ko‘rsatadi.
