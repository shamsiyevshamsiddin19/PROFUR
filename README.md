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
```

### 2. Muhit sozlamalarini tayyorlash
Namuna fayldan nusxa olib `.env` yarating:
```bash
cp .env.example .env
```
Zarur bo‘lsa, `.env` ichidagi ma’lumotlar bazasi yoki kalit qiymatlarini tahrirlang.

### 3. Ma’lumotlar bazasini ishga tushirish (PostgreSQL)
Docker o‘rnatilgan bo‘lsa, PostgreSQL bazasini bitta buyruq bilan ko‘taring:
```bash
docker compose up -d
```
Bazani to‘xtatish uchun:
```bash
docker compose down
```

### 4. Kod sifati va formatlash tekshiruvi (Ruff)
Jamoamizda Python kodi uchun [Ruff](https://docs.astral.sh/ruff/) standart qilib belgilangan:
```bash
# Ruff o'rnatish
pip install ruff

# Kodni tekshirish (linter)
ruff check .

# Kodni avtomatik to'g'rilash
ruff check --fix .

# Kodni formatlash (formatter)
ruff format .
```

### 5. Avtomatlashtirilgan tekshiruv (CI)
Har bir ochilgan Pull Request (PR) GitHub Actions orqali avtomatik tarzda quyidagilar bo‘yicha tekshiriladi:
- Ruff lint va formatlash tekshiruvi
- Ma’lumotlar bazasi migratsiyalari to‘liqligi (`makemigrations --check`)
- Avtomatlashtirilgan testlar
