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


## Qabul va joylashtirish chegarasi

OQ-046: zaxira har kuni olinishi, tiklash maqsadi 4 soat bo‘lishi kerak. Retention/RPO qiymatlari aniqlashtiriladi. Yuqoridagi buyruqlar yo‘riqnoma; production’da rejalashtirilgan backup ishlayotgani yoki ushbu ko‘rikda restore bajarilgani haqidagi dalil emas. Muallif qayd etgan lokal drill natijasi bilan production qabuli alohida tekshiriladi. Real bazada qo‘shimcha kategoriya/xarajat turlari bo‘lishi mumkin; 9/3 soni boshlang‘ich muhitga tegishli.

## Avtomatik vosita va kundalik timer

Repo ichidagi vositalar `DB_NAME/USER/PASSWORD/HOST/PORT` yoki PostgreSQL `PG*` muhit parametrlarini oladi. Parol buyruq satriga yozilmaydi. PostgreSQL client vositalari va Python 3.11+ kerak.

```bash
python3 ops/backup.py --directory /var/backups/profur
python3 ops/restore_drill.py /var/backups/profur/profur-TIMESTAMP.dump
```

Restore mashqi original bazaga yozmaydi. Undan olingan arxivni tasodifiy `profur_drill_*` bazaga tiklaydi va o‘z bazasini tozalaydi. Bu mashq akkauntiga vaqtinchalik baza yaratish huquqi kerak; oddiy kundalik backup akkauntiga bu huquq shart emas. Arxiv yonidagi JSON manifest SHA-256 bilan birga saqlansin. Rejalashtirilgan sinov/CI dalili [topshirish reyestrida](phase-one-acceptance.md).

VPS o‘rnatish: repo `/opt/profur`, `profur` xizmat foydalanuvchisi, PostgreSQL client, `/var/backups/profur` jildi shu foydalanuvchiga tegishli (0700), `/etc/profur/backup.env` faqat xizmat/root o‘qiydigan (0600) bo‘lishi kerak. `ops/systemd/profur-backup.service` va `.timer` fayllarini `/etc/systemd/system/` ga o‘rnating, `systemctl daemon-reload`, avval `systemctl start profur-backup.service` bilan natijani tekshiring, keyin `systemctl enable --now profur-backup.timer`. Jadval har kuni 02:00 UTC (07:00 Toshkent), o‘tkazib yuborilgan ish keyingi ishga tushishda bajariladi. Holat `systemctl list-timers profur-backup.timer` va `journalctl -u profur-backup.service` orqali tekshiriladi. Nosozlik xabarini server monitoringiga ulang.

Retention qiymati kelishilmagani sababli vosita eski zaxiralarni o‘chirmaydi. Serverdan tashqari nusxa, disk sig‘imi nazorati va real ma’lumot hajmidagi 4 soatlik RTO mashqi production qabulida tekshiriladi. Ushbu fayllar tayyorligi timer jonli serverda o‘rnatilganiga dalil emas.

PostgreSQL client va server asosiy versiyalari mos bo‘lsin. `PG_BIN=/usr/lib/postgresql/16/bin` kabi parametr barcha `pg_dump`, `pg_restore`, `psql`, `createdb`, `dropdb` yo‘lini belgilaydi. CI PostgreSQL 16 uchun aynan `postgres:16-alpine` client konteynerini ishlatadi; yangi client chiqargan `transaction_timeout` buyrug‘ini eski serverda e’tiborsiz qoldirish ishlatilmaydi.
