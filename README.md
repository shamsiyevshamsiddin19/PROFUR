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

### 3. PostgreSQL bazasini ishga tushirish

`.env.example` dagi PostgreSQL sozlamalari uchun avval baza tayyor bo‘lsin:

```bash
docker compose up -d --wait
```

Docker bo‘lmasa, PostgreSQL 16+ da alohida baza va uning foydalanuvchisini tayyorlab, `.env` ni moslang. Ishlayotgan boshqa loyihaning bazasini ishlatmang. Mahalliy SQLite faqat tezkor preview uchun; parallel ombor amallari PostgreSQL’da tekshiriladi.

### 4. Backend va birinchi administrator

```bash
python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py notify_low_stock
python backend/manage.py runserver 127.0.0.1:8000
```

`createsuperuser` login/parolni interaktiv so‘raydi; kodda tayyor hisob yo‘q. Superuser PROFUR’ning Boshqaruv sahifasidan xodim va rollarni yaratishi mumkin. Sog‘liq tekshiruvi: `http://127.0.0.1:8000/api/health/`. Bazani to‘xtatish uchun `docker compose down`; volume’ni o‘chirish ish ma’lumotlarini yo‘qotadi, oddiy to‘xtatishda `-v` ishlatmang.

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

Joriy sayt haqiqiy Django API bilan katalog, kirim, qoldiq/partiya/minimum, chiqim, qaytarish va hisobdan chiqarish tasdig‘i, xarajat/teskari yozuv, tarix/CSV hamda shaxsiy xabarlarni bajaradi. Boshqaruv sahifasi faqat ADMIN/superuser uchun; boshqa rollar aynan berilgan permission kodlariga muvofiq ishlaydi. Xarajat turlarini boshqarish alohida ruxsat bilan ochiladi, xarajat yozuvlarini ko‘rish vakolati shart emas.

Brauzer sinovi: `frontend` ichida `npx playwright install chromium`, keyin `npm run test:e2e`. Python virtual muhit tashqarida bo‘lsa `E2E_PYTHON` bilan yo‘l ko‘rsating. Bu sinov alohida vaqtinchalik bazadan foydalanadi. PostgreSQL parallel sinovlari `pytest` bilan bajariladi. CI ham build, 3 ekranli Chromium va zaxirani alohida bazaga tiklashni tekshiradi.

[1-qism topshirish reyestri](docs/08-delivery/phase-one-acceptance.md) va [backup/restore](docs/08-delivery/backup-restore.md) joriy imkoniyatlar, hisob shartnomasi va jonli muhit qabuli chegarasini belgilaydi.
