# PostgreSQL Backup va Qayta Tiklash (Backup & Restore) Yo'riqnomasi

Ushbu yo'riqnoma PROFUR tizimining PostgreSQL ma'lumotlar bazasini xavfsiz zaxiralash, arxivlash va avariyaviy holatlarda ma'lumotlarni qayta tiklash tartibini belgilaydi.

---

## 1. Zaxira nusxa yaratish (Backup)

Baza zaxirasi PostgreSQL'ning rasmiy `pg_dump` vositasi orqali, siqilgan maxsus formatda (`custom format -F c`) olinadi. Ushbu format jadval tuzilmalari, indekslar, cheklovlar va blob ma'lumotlarni to'liq saqlaydi hamda tezkor tiklash imkonini beradi.

### Buyruq:
```bash
PGPASSWORD="${DB_PASSWORD}" pg_dump \
  -h "${DB_HOST:-localhost}" \
  -p "${DB_PORT:-5432}" \
  -U "${DB_USER:-profur_user}" \
  -F c \
  -b \
  -v \
  -f "/var/backups/profur/profur_db_$(date +%Y%m%d_%H%M%S).dump" \
  "${DB_NAME:-profur_db}"
```

### Parametrlar tavsifi:
* `-h` — Ma'lumotlar bazasi host manzili.
* `-p` — Port (standart: 5432).
* `-U` — Foydalanuvchi nomi (`profur_user`).
* `-F c` — Custom format (siqilgan binar format, `pg_restore` uchun qulay).
* `-b` — Katta obyektlarni (blobs) kiritish.
* `-v` — Jarayonning batafsil loglarini ko'rsatish (verbose).
* `-f` — Saqlanadigan zaxira fayl yo'li.

---

## 2. Zaxiradan ma'lumotlarni qayta tiklash (Restore)

Zaxira fayldan bazani tiklash uchun `pg_restore` utilitasi ishlatiladi.

### 2.1. Yangi yoki toza bazaga tiklash (Tavsiya etiladi):
```bash
# 1. Yangi toza baza yaratish (Postgres admin orqali)
psql -U postgres -h localhost -c "CREATE DATABASE profur_db OWNER profur_user;"

# 2. Zaxira faylini tiklash
PGPASSWORD="${DB_PASSWORD}" pg_restore \
  -h "${DB_HOST:-localhost}" \
  -p "${DB_PORT:-5432}" \
  -U "${DB_USER:-profur_user}" \
  -d "${DB_NAME:-profur_db}" \
  -v \
  "/var/backups/profur/profur_db_backup.dump"
```

### 2.2. Mavjud bazani tozalab tiklash (`--clean` rejimi):
```bash
PGPASSWORD="${DB_PASSWORD}" pg_restore \
  -h "${DB_HOST:-localhost}" \
  -p "${DB_PORT:-5432}" \
  -U "${DB_USER:-profur_user}" \
  -d "${DB_NAME:-profur_db}" \
  --clean \
  --if-exists \
  -v \
  "/var/backups/profur/profur_db_backup.dump"
```

---

## 3. Qayta tiklash tekshiruvi (Verification Drill)

Tiklash amali muvaffaqiyatli yakunlangach, quyidagi tekshiruvlar amalga oshiriladi:

1. **Jadvallar soni va migratsiyalar:**
```bash
python backend/manage.py migrate --check
```
2. **Katalog va boshlang'ich ma'lumotlar yaxlitligi:**
```sql
SELECT count(*) FROM catalog_category;       -- 9 ta standart kategoriya bo'lishi kerak
SELECT count(*) FROM expenses_expensetype;   -- 3 ta xarajat turi bo'lishi kerak
SELECT count(*) FROM inventory_stockbalance; -- Ombor qoldiqlari
```
3. **Tizim salomatligi:**
```bash
curl -f http://127.0.0.1:8000/api/health/
```

---

## 4. O'tkazilgan amaliy sinov (Drill Evidence) · 2026-11-18

Lokal PostgreSQL serverida quyidagi mashq o'tkazildi va muvaffaqiyatli tasdiqlandi:
* Baza `profur_db` dan `pg_dump` orqali `/tmp/profur_db_backup.dump` yaratildi.
* Test maqsadida yangi `profur_restore_drill_db` bazasi ochildi.
* `pg_restore` yordamida barcha jadvallar tiklandi.
* `catalog_category` (9 ta) va `expenses_expensetype` (3 ta) yozuvlari to'liq va o'zgarishsiz tiklanganligi tasdiqlandi.
* Test bazasi `DROP DATABASE` bilan tozalab tashlandi.
