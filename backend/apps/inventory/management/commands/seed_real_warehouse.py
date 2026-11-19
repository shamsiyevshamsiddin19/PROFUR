"""PROFUR mebel ishlab chiqarish ombori uchun haqiqiy, boyitilgan ma'lumotlar bazasini to'ldiruvchi buyruq.

Ushbu buyruq PostgreSQL (profur_db) bazasini quyidagilar bilan to'ldiradi:
1. Rollar va foydalanuvchilar (admin, omborchi, usta, taminotchi, hisobchi).
2. Mebel xomashyo kategoriyalari (LDSP, MDF, Furnitura, Kromka, Yelim, Ko'zgular va h.k.).
3. 35 dan ortiq real mebel materiallari (o'lchamlari sm da, ranglari va birliklari bilan).
4. 50 dan ortiq kirim partiyalari (har xil sanalar, yetkazib beruvchilar va hujjat raqamlari).
5. 20 dan ortiq chiqimlar (haqiqiy mebel loyihalariga biriktirilgan holda).
6. Qaytarish va hisobdan chiqarish so'rovlari (tasdiqlangan va kutilayotgan).
7. Minimal qoldiq chegaralari va kam qoldiq haqidagi tizimli xabarnomalar.
8. Turli xildagi qo'shimcha xarajatlar (loyiha va umumiy xarajatlar, bekor qilingan yozuvlar).
"""

from datetime import date, timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Role, User
from apps.catalog.models import Category, Material, Unit
from apps.expenses.models import Expense, ExpenseType
from apps.inventory.models import (
    Batch,
    Currency,
    MovementType,
    RequestStatus,
    StockBalance,
    StockIssue,
    StockIssueAllocation,
    StockMovement,
    StockNotification,
    StockReturn,
    StockReturnAllocation,
    WriteOff,
    WriteOffAllocation,
)
from apps.inventory.services import (
    Allocation,
    approve_return,
    approve_write_off,
    issue_stock,
    receive,
    request_return,
    request_write_off,
    set_min_quantity,
    sync_low_stock,
)


class Command(BaseCommand):
    help = "PostgreSQL bazasini real mebel ombori ma'lumotlari bilan to'ldiradi."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Eski ombor va harakatlar ma'lumotlarini tozalab, keyin to'ldirish.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Ombor ma'lumotlarini yaratish boshlandi..."))

        # ---------------------------------------------------------
        # 1. FOYDALANUVCHILAR VA ROLLAR
        # ---------------------------------------------------------
        self.stdout.write("1. Rollar va foydalanuvchilar sozlanmoqda...")

        role_admin, _ = Role.objects.get_or_create(
            code="ADMIN",
            defaults={
                "name": "Administrator",
                "description": "Barcha vakolatlar va to'liq tizim boshqaruvi",
                "permissions": ["*"],
                "is_system": True,
            },
        )
        role_wh, _ = Role.objects.get_or_create(
            code="WAREHOUSE_MANAGER",
            defaults={
                "name": "Ombor mudiri",
                "description": "Kirim, chiqim, partiyalar va qoldiqlar ustidan to'liq nazorat",
                "permissions": [
                    "catalog.view_material",
                    "inventory.view_stock",
                    "inventory.view_purchase_price",
                    "inventory.add_receipt",
                    "inventory.add_issue",
                    "inventory.add_return",
                    "inventory.approve_return",
                    "inventory.add_write_off",
                    "inventory.approve_write_off",
                    "inventory.change_min_quantity",
                ],
                "is_system": True,
            },
        )
        role_prod, _ = Role.objects.get_or_create(
            code="PRODUCTION_SUPERVISOR",
            defaults={
                "name": "Ishlab chiqarish ustasi",
                "description": "Sexda mebel ishlab chiqarish uchun material talab qilish va qaytarish",
                "permissions": [
                    "catalog.view_material",
                    "inventory.view_stock",
                    "inventory.add_issue",
                    "inventory.add_return",
                ],
                "is_system": True,
            },
        )
        role_acc, _ = Role.objects.get_or_create(
            code="ACCOUNTANT",
            defaults={
                "name": "Bosh hisobchi",
                "description": "Moliyaviy xarajatlar va ombor qiymatini nazorat qilish",
                "permissions": [
                    "catalog.view_material",
                    "inventory.view_stock",
                    "inventory.view_purchase_price",
                    "expenses.view_expense",
                    "expenses.add_expense",
                    "expenses.reverse_expense",
                    "expenses.view_expensetype",
                ],
                "is_system": True,
            },
        )
        role_proc, _ = Role.objects.get_or_create(
            code="PROCUREMENT",
            defaults={
                "name": "Ta'minotchi",
                "description": "Yangi materiallar nomenklaturasi va kirim partiyalarini ro'yxatdan o'tkazish",
                "permissions": [
                    "catalog.view_material",
                    "catalog.add_material",
                    "catalog.change_material",
                    "catalog.add_category",
                    "inventory.view_stock",
                    "inventory.add_receipt",
                ],
                "is_system": True,
            },
        )

        # Admin user
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Shamsiddin",
                "last_name": "Shamsiyev",
                "email": "shamsiddin@profur.uz",
                "phone": "+998 90 123-45-67",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        admin_user.set_password("admin123")
        admin_user.save()
        admin_user.roles.set([role_admin])

        # Omborchi
        omborchi_user, _ = User.objects.get_or_create(
            username="omborchi",
            defaults={
                "first_name": "Davronbek",
                "last_name": "Toirov",
                "email": "davron@profur.uz",
                "phone": "+998 93 987-65-43",
                "is_active": True,
            },
        )
        omborchi_user.set_password("ombor123")
        omborchi_user.save()
        omborchi_user.roles.set([role_wh])

        # Ishlab chiqarish ustasi
        usta_user, _ = User.objects.get_or_create(
            username="usta",
            defaults={
                "first_name": "Rustam",
                "last_name": "Yusupov",
                "email": "rustam@profur.uz",
                "phone": "+998 97 111-22-33",
                "is_active": True,
            },
        )
        usta_user.set_password("usta123")
        usta_user.save()
        usta_user.roles.set([role_prod])

        # Hisobchi
        hisobchi_user, _ = User.objects.get_or_create(
            username="hisobchi",
            defaults={
                "first_name": "Nodira",
                "last_name": "Karimova",
                "email": "nodira@profur.uz",
                "phone": "+998 90 777-88-99",
                "is_active": True,
            },
        )
        hisobchi_user.set_password("hisobchi123")
        hisobchi_user.save()
        hisobchi_user.roles.set([role_acc])

        # Ta'minotchi
        taminot_user, _ = User.objects.get_or_create(
            username="taminotchi",
            defaults={
                "first_name": "Bobur",
                "last_name": "Aliyev",
                "email": "bobur@profur.uz",
                "phone": "+998 99 444-55-66",
                "is_active": True,
            },
        )
        taminot_user.set_password("taminot123")
        taminot_user.save()
        taminot_user.roles.set([role_proc])

        # ---------------------------------------------------------
        # 2. XARAJAT TURLARI
        # ---------------------------------------------------------
        self.stdout.write("2. Xarajat turlari sozlanmoqda...")
        exp_types_data = [
            ("soliq", "Soliq va majburiy to'lovlar", "Налоги и сборы", "Taxes and duties"),
            ("stanok", "Stanok va asboblar ta'miri", "Ремонт станков", "Machine & Tool Maintenance"),
            ("transport", "Transport va logistika", "Транспорт и доставка", "Transportation & Delivery"),
            ("kommunal", "Kommunal to'lovlar (Elektr/Gaz)", "Коммунальные услуги", "Utilities"),
            ("asboblar", "Mayda asboblar va fitinglar", "Расходные инструменты", "Consumables & Tools"),
            ("ijara", "Ombor va sex binosi ijarasi", "Аренда склада и цеха", "Facility Rent"),
            ("ovqat", "Sex xodimlari tushligi", "Питание сотрудников", "Staff Meals"),
            ("paketlash", "Qadoqlash materiallari (Streych/Karton)", "Упаковочные материалы", "Packaging Materials"),
        ]
        created_exp_types = {}
        for code, uz, ru, en in exp_types_data:
            obj, _ = ExpenseType.objects.get_or_create(
                code=code,
                defaults={"name_uz": uz, "name_ru": ru, "name_en": en, "is_active": True},
            )
            created_exp_types[code] = obj

        # ---------------------------------------------------------
        # 3. KATEGORIYALAR VA MATERIALLAR
        # ---------------------------------------------------------
        self.stdout.write("3. Mebel materiallari katalogi yaratilmoqda...")

        cat_ldsp, _ = Category.objects.get_or_create(name="DSP va LDSP plitalari")
        cat_mdf, _ = Category.objects.get_or_create(name="MDF va Akril panellar")
        cat_kromka, _ = Category.objects.get_or_create(name="DSP kromka va qoplamalar")
        cat_furn, _ = Category.objects.get_or_create(name="Furnituralar va mexanizmlar")
        cat_fastener, _ = Category.objects.get_or_create(name="Mahkamlagichlar va fitinglar")
        cat_chem, _ = Category.objects.get_or_create(name="Yelim va kimyoviy vositalar")
        cat_glass, _ = Category.objects.get_or_create(name="Shisha va ko'zgular")
        cat_prof, _ = Category.objects.get_or_create(name="Profil va karkas tizimlari")
        cat_tutqich, _ = Category.objects.get_or_create(name="Mebel tutqichlari va oyoqlar")

        materials_spec = [
            # LDSP
            (cat_ldsp, "LDSP Kronospan Oq Premium", "Oq", Decimal("280.0"), Decimal("207.0"), Decimal("1.8"), Unit.SHEET, Decimal("25.0")),
            (cat_ldsp, "LDSP Kastamonu Dub Bardolino", "Dub", Decimal("280.0"), Decimal("207.0"), Decimal("1.8"), Unit.SHEET, Decimal("20.0")),
            (cat_ldsp, "LDSP Egger Grafit Matt", "Grafit", Decimal("280.0"), Decimal("207.0"), Decimal("1.8"), Unit.SHEET, Decimal("15.0")),
            (cat_ldsp, "LDSP Yulduz Yong'oq Venge", "Venge", Decimal("275.0"), Decimal("183.0"), Decimal("1.6"), Unit.SHEET, Decimal("15.0")),
            (cat_ldsp, "LDSP Kronospan Qora Matt", "Qora", Decimal("280.0"), Decimal("207.0"), Decimal("1.8"), Unit.SHEET, Decimal("10.0")),
            (cat_ldsp, "LDSP Kastamonu Krem Shokolad", "Krem", Decimal("280.0"), Decimal("207.0"), Decimal("1.8"), Unit.SHEET, Decimal("10.0")),
            (cat_ldsp, "LDSP Egger Beton Chiqindi", "Kulrang", Decimal("280.0"), Decimal("207.0"), Decimal("1.8"), Unit.SHEET, Decimal("12.0")),
            
            # MDF
            (cat_mdf, "MDF AGT Oq Yaltiroq Gloss 601", "Oq Gloss", Decimal("280.0"), Decimal("122.0"), Decimal("1.8"), Unit.SHEET, Decimal("15.0")),
            (cat_mdf, "MDF AGT Supramat Qora Qaymoq", "Qora Matt", Decimal("280.0"), Decimal("122.0"), Decimal("1.8"), Unit.SHEET, Decimal("10.0")),
            (cat_mdf, "MDF Bo'yaladigan Shliflangan", "Xom", Decimal("280.0"), Decimal("207.0"), Decimal("1.6"), Unit.SHEET, Decimal("15.0")),
            (cat_mdf, "MDF Akril Panel Oltin Jilo", "Oltin", Decimal("280.0"), Decimal("122.0"), Decimal("1.8"), Unit.SHEET, Decimal("8.0")),
            (cat_mdf, "DVP Orqa devor Oq", "Oq", Decimal("280.0"), Decimal("207.0"), Decimal("0.3"), Unit.SHEET, Decimal("30.0")),
            (cat_mdf, "DVP Orqa devor Venge", "Venge", Decimal("275.0"), Decimal("183.0"), Decimal("0.3"), Unit.SHEET, Decimal("25.0")),

            # KROMKA
            (cat_kromka, "PVX Kromka 22×1 mm Oq", "Oq", Decimal("20000.0"), Decimal("2.2"), Decimal("0.1"), Unit.METER, Decimal("500.0")),
            (cat_kromka, "PVX Kromka 22×2 mm Dub Bardolino", "Dub", Decimal("10000.0"), Decimal("2.2"), Decimal("0.2"), Unit.METER, Decimal("400.0")),
            (cat_kromka, "PVX Kromka 22×2 mm Grafit", "Grafit", Decimal("10000.0"), Decimal("2.2"), Decimal("0.2"), Unit.METER, Decimal("300.0")),
            (cat_kromka, "PVX Kromka 45×2 mm Qora Matt", "Qora", Decimal("10000.0"), Decimal("4.5"), Decimal("0.2"), Unit.METER, Decimal("200.0")),
            (cat_kromka, "Melamin kromka yelimli 20mm Venge", "Venge", Decimal("5000.0"), Decimal("2.0"), Decimal("0.04"), Unit.METER, Decimal("150.0")),

            # FURNITURA
            (cat_furn, "Blum Movento 500mm yashirin tortma", "Kumush", None, None, None, Unit.PIECE, Decimal("40.0")),
            (cat_furn, "Blum Clip-Top 110° dovodchikli petlya", "Nikel", None, None, None, Unit.PIECE, Decimal("120.0")),
            (cat_furn, "Blum Aventos HF bukiluvchi fasad lifti", "Kulrang", None, None, None, Unit.PIECE, Decimal("10.0")),
            (cat_furn, "Samet Star dovodchikli petlya 110°", "Nikel", None, None, None, Unit.PIECE, Decimal("150.0")),
            (cat_furn, "GTV Teleskopik napravlyayushchiy 450mm", "Qora", None, None, None, Unit.PIECE, Decimal("80.0")),
            (cat_furn, "Gazlift pnevmatik 100N", "Kumush", None, None, None, Unit.PIECE, Decimal("50.0")),

            # FASTENERS
            (cat_fastener, "Minifiks Rastex ekssentrik korpus + shtok", "Sink", None, None, None, Unit.PIECE, Decimal("500.0")),
            (cat_fastener, "Konfirmat mebel vinti 7×50 mm", "Sink", None, None, None, Unit.PIECE, Decimal("1000.0")),
            (cat_fastener, "Samorez o'yuvchi 4×16 mm sariq", "Sariq", None, None, None, Unit.PIECE, Decimal("2000.0")),
            (cat_fastener, "Samorez mebel vinti 4×30 mm", "Qora", None, None, None, Unit.PIECE, Decimal("1500.0")),
            (cat_fastener, "Yog'och shkant qayin 8×35 mm", "Yog'och", None, None, None, Unit.PIECE, Decimal("800.0")),

            # KIMYO VA YELIM
            (cat_chem, "Termo-yelim Kleiberit 707.6 Oq", "Oq", None, None, None, Unit.KG, Decimal("50.0")),
            (cat_chem, "Termo-yelim Kleiberit 707.9 Jigar", "Jigarrang", None, None, None, Unit.KG, Decimal("30.0")),
            (cat_chem, "Kontakt yelim Cosmofen CA 12 tezyurar", "Shaffof", None, None, None, Unit.PIECE, Decimal("25.0")),
            (cat_chem, "PVA Mebel yelimi D3 suvga chidamli", "Oq", None, None, None, Unit.LITER, Decimal("20.0")),

            # SHISHA VA KO'ZGU
            (cat_glass, "Ko'zgu Kumush 4mm fasad uchun", "Kumush", Decimal("250.0"), Decimal("160.0"), Decimal("0.4"), Unit.SQUARE_METER, Decimal("15.0")),
            (cat_glass, "Ko'zgu Bronza 4mm dekorativ", "Bronza", Decimal("250.0"), Decimal("160.0"), Decimal("0.4"), Unit.SQUARE_METER, Decimal("10.0")),

            # PROFIL VA TUTQICHLAR
            (cat_prof, "Alyuminiy G-profil tutqich 300 sm", "Qora Matt", Decimal("300.0"), Decimal("4.0"), Decimal("2.0"), Unit.METER, Decimal("40.0")),
            (cat_prof, "Alyuminiy Shkaf-kupe relsi 300 sm", "Kumush", Decimal("300.0"), Decimal("8.0"), Decimal("4.5"), Unit.METER, Decimal("30.0")),
            (cat_tutqich, "Mebel tutqichi qora chiziqli 160 mm", "Qora Matt", Decimal("19.2"), Decimal("1.2"), Decimal("2.8"), Unit.PIECE, Decimal("60.0")),
            (cat_tutqich, "Mebel oyog'i metall xrom 100 mm sozlanuvchi", "Xrom", Decimal("10.0"), Decimal("5.0"), Decimal("5.0"), Unit.PIECE, Decimal("50.0")),
        ]

        created_materials = []
        for cat, name, color, l_cm, w_cm, th_cm, unit, min_q in materials_spec:
            mat, _ = Material.objects.get_or_create(
                category=cat,
                name=name,
                color=color,
                length_cm=l_cm,
                width_cm=w_cm,
                thickness_cm=th_cm,
                unit=unit,
                defaults={"is_active": True},
            )
            created_materials.append((mat, min_q))

        self.stdout.write(f"Jami {len(created_materials)} ta material tayyorlandi.")

        # ---------------------------------------------------------
        # 4. KIRIM PARTIYALARI (BATCHES)
        # ---------------------------------------------------------
        self.stdout.write("4. Haqiqiy kirim partiyalari yaratilmoqda...")

        suppliers = [
            ("Kronospan Uzbekistan MChJ", "KR-2026/"),
            ("Egger Central Asia Distribution", "EG-88/"),
            ("Kastamonu Samarqand Plant", "KS-91/"),
            ("Blum Eurasia / MebelPlast MChJ", "BL-55/"),
            ("Samet Furnitura Tashkent", "SH-77/"),
            ("Kleiberit Adhesives CIS", "KL-10/"),
            ("GTV Hardware Distribution", "GTV-44/"),
            ("Toshkent Oyna Zavodi AJ", "TOZ-02/"),
            ("Alutex Alyuminiy Profillari", "ALU-19/"),
        ]

        today = date.today()
        created_batches = []

        # Har bir material uchun 1 tadan 3 tagacha partiya kiritiladi
        # Sanalari oxirgi 60 kun davomida
        for idx, (mat, min_q) in enumerate(created_materials):
            # Asosiy birlik narxlari taxminiy
            base_prices = {
                Unit.SHEET: Decimal(random.randint(32, 75)),
                Unit.METER: Decimal(random.randint(2, 12)),
                Unit.PIECE: Decimal(random.randint(1, 45)),
                Unit.KG: Decimal(random.randint(4, 18)),
                Unit.LITER: Decimal(random.randint(5, 15)),
                Unit.SQUARE_METER: Decimal(random.randint(12, 28)),
            }
            price_base = base_prices.get(mat.unit, Decimal("10.0"))

            # Kiritiladigan partiyalar soni
            num_batches = 2 if idx % 2 == 0 else 3
            for b_idx in range(num_batches):
                days_ago = 55 - (b_idx * 16) - random.randint(0, 5)
                received_date = today - timedelta(days=max(2, days_ago))
                
                # Partiya miqdori
                qty_mult = {
                    Unit.SHEET: Decimal(random.randint(20, 60)),
                    Unit.METER: Decimal(random.randint(150, 600)),
                    Unit.PIECE: Decimal(random.randint(100, 1500)),
                    Unit.KG: Decimal(random.randint(40, 150)),
                    Unit.LITER: Decimal(random.randint(20, 80)),
                    Unit.SQUARE_METER: Decimal(random.randint(15, 45)),
                }
                qty = qty_mult.get(mat.unit, Decimal("50.0"))

                # Bir oz narx o'zgarishi (partiya bo'yicha)
                unit_p = (price_base + Decimal(b_idx * 1.5)).quantize(Decimal("0.01"))
                total_amt = (qty * unit_p).quantize(Decimal("0.01"))

                supplier_name, prefix = suppliers[idx % len(suppliers)]
                doc_num = f"{prefix}{random.randint(1000, 9999)}"

                batch, balance = receive(
                    material=mat,
                    received_on=received_date,
                    quantity=qty,
                    total_amount=total_amt,
                    user=omborchi_user,
                    currency=Currency.USD,
                    supplier=supplier_name,
                    document_number=doc_num,
                    note=f"{mat.name} partiyasi #{b_idx + 1}",
                )
                created_batches.append(batch)

            # Minimal qoldiq belgilash
            set_min_quantity(mat, min_q)

        self.stdout.write(f"Jami {len(created_batches)} ta partiya qabul qilindi.")

        # ---------------------------------------------------------
        # 5. HAQIQIY CHIQIMLAR (ISSUES)
        # ---------------------------------------------------------
        self.stdout.write("5. Real mebel loyihalariga chiqimlar amalga oshirilmoqda...")

        projects = [
            (101, "Toshkent City - A blok ofis mebellari", "Alisher Usta"),
            (102, "Hilton mehmonxonasi - lyuks xonadon shkaflari", "Jasur Montajchi"),
            (103, "IT Park rezidenti kovorking stollari", "Bobur Sbornik"),
            (104, "Koshona restorani - bar stoykasi va panellari", "Rustam Usta"),
            (105, "Prezident maktabi - laboratoriya mebellari", "Jamshid Duradgor"),
            (106, "Chilonzor kottej - oshxona garnituri", "Dilshod Usta"),
            (107, "Yunusobod 19-mavze - shkaf-kupe va yotoqxona", "Alisher Usta"),
            (108, "Mirzo Ulug'bek - bolalar mebel to'plami", "Jasur Montajchi"),
            (109, "Samarqand mehmonxona majmuasi - vestibyul", "Rustam Usta"),
            (110, "Buxoro shahar klinika qabulxonasi", "Bobur Sbornik"),
        ]

        created_issues = []
        # Har bir loyiha uchun bir nechta materialdan chiqim qilamiz
        for prj_idx, (p_id, p_desc, recipient) in enumerate(projects):
            # Loyihaga mos 3-5 ta material tanlaymiz
            sample_materials = random.sample(created_materials, 4)
            issue_date = today - timedelta(days=35 - (prj_idx * 3))

            for mat, _ in sample_materials:
                # Materialning mavjud partiyalarini topamiz
                avail_batches = Batch.objects.filter(material=mat, quantity_remaining__gt=0).order_by("received_on")
                if not avail_batches.exists():
                    continue

                b = avail_batches.first()
                # Chiqim miqdori partiyaning 20% - 40% miqdorida
                max_take = b.quantity_remaining
                if max_take <= 2:
                    continue

                take_qty = (max_take * Decimal("0.35")).quantize(Decimal("1.00"))
                if take_qty <= 0:
                    take_qty = Decimal("1.00")

                allocations = [Allocation(batch_id=b.id, quantity=take_qty)]
                try:
                    issue, _ = issue_stock(
                        material=mat,
                        allocations=allocations,
                        issued_on=issue_date,
                        recipient_name=recipient,
                        user=omborchi_user,
                        project_id=p_id,
                        note=f"{p_desc} uchun berildi",
                    )
                    created_issues.append((issue, b, take_qty))
                except Exception as e:
                    # Qoldiq yetmagan bo'lsa davom etamiz
                    pass

        self.stdout.write(f"Jami {len(created_issues)} ta chiqim hujjati yaratildi.")

        # ---------------------------------------------------------
        # 6. QAYTARISHLAR (RETURNS)
        # ---------------------------------------------------------
        self.stdout.write("6. Qaytarish amallari bajarilmoqda...")
        # 3 ta chiqimdan qisman qaytarish qilamiz (2 tasi tasdiqlangan, 1 tasi kutilayotgan)
        for r_idx in range(min(3, len(created_issues))):
            iss, b, taken = created_issues[r_idx]
            if taken >= 3:
                ret_qty = Decimal("1.00") if taken < 10 else Decimal("2.00")
                ret_date = iss.issued_on + timedelta(days=3)
                alloc = [Allocation(batch_id=b.id, quantity=ret_qty)]

                st_return = request_return(
                    issue=iss,
                    allocations=alloc,
                    returned_on=ret_date,
                    user=usta_user,
                    reason=f"Loyiha #{iss.project_id} da ortib qolgan material",
                )
                if r_idx < 2:
                    # Tasdiqlaymiz
                    approve_return(return_id=st_return.id, user=admin_user, note="Qoldiq omborga qabul qilindi")
                # 3-chisi kutilayotgan holatda qoladi

        # ---------------------------------------------------------
        # 7. HISOBDAN CHIQARISHLAR (WRITE-OFFS)
        # ---------------------------------------------------------
        self.stdout.write("7. Hisobdan chiqarish (brak/shikastlanish) so'rovlari yaratilmoqda...")
        # 2 ta tasdiqlangan, 1 ta kutilayotgan hisobdan chiqarish
        damage_specs = [
            ("Yuk tushirishda kran ilmog'i tegib cheti yorilgan", True),
            ("Sex ichida ko'chirish vaqtida tushib darz ketgan", True),
            ("Namlik va chang sababli chetlari yaroqsiz holga kelgan", False),
        ]

        for d_idx, (reason, do_approve) in enumerate(damage_specs):
            target_mat, _ = created_materials[d_idx * 3]
            avail = Batch.objects.filter(material=target_mat, quantity_remaining__gt=2).first()
            if avail:
                wo_qty = Decimal("1.00")
                wo_alloc = [Allocation(batch_id=avail.id, quantity=wo_qty)]
                wo = request_write_off(
                    material=target_mat,
                    allocations=wo_alloc,
                    reason=reason,
                    user=omborchi_user,
                )
                if do_approve:
                    approve_write_off(write_off_id=wo.id, user=admin_user, note="Komissiya xulosasi: yaroqsiz")

        # ---------------------------------------------------------
        # 8. QO'SHIMCHA XARAJATLAR (EXPENSES)
        # ---------------------------------------------------------
        self.stdout.write("8. Qo'shimcha xarajatlar kiritilmoqda...")
        expenses_data = [
            ("soliq", Decimal("850.00"), today - timedelta(days=45), None, "Oktyabr oyi daromad va ijtimoiy soliq to'lovi"),
            ("soliq", Decimal("1240.00"), today - timedelta(days=15), None, "QQS va foyda solig'i oylik avansi"),
            ("stanok", Decimal("180.00"), today - timedelta(days=40), 101, "Formatka pichog'i charxlash va yangi disk sotib olish"),
            ("stanok", Decimal("320.00"), today - timedelta(days=22), 104, "Kromka stanogi teni va roliklarini almashtirish"),
            ("transport", Decimal("220.00"), today - timedelta(days=38), 101, "Fura yuk tushirish va kran xizmati"),
            ("transport", Decimal("150.00"), today - timedelta(days=25), 102, "Mebellarni Hilton mehmonxonasiga yetkazish logistikasi"),
            ("transport", Decimal("95.00"), today - timedelta(days=10), 106, "Chilonzor kottejiga qismlarni eltish xarajati"),
            ("kommunal", Decimal("410.00"), today - timedelta(days=32), None, "Sex va ombor elektr energiyasi to'lovi (sentyabr)"),
            ("kommunal", Decimal("460.00"), today - timedelta(days=5), None, "Sex va ombor elektr energiyasi to'lovi (oktyabr)"),
            ("asboblar", Decimal("135.00"), today - timedelta(days=28), 103, "Freza va spiral sverlolar to'plami"),
            ("asboblar", Decimal("75.00"), today - timedelta(days=14), 105, "Pnevmatik pistolet va shlang ta'miri"),
            ("ijara", Decimal("2200.00"), today - timedelta(days=30), None, "Asosiy ombor va ishlab chiqarish binosi oylik ijarasi"),
            ("ovqat", Decimal("380.00"), today - timedelta(days=20), None, "Usta va yig'uvchilarning tushlik ovqati ta'minoti"),
            ("paketlash", Decimal("190.00"), today - timedelta(days=18), 102, "Fasadlar uchun havoli plenka (puzirchataya) va karton"),
            ("transport", Decimal("300.00"), today - timedelta(days=8), None, "Xomashyo olib kelish furasiga to'lov (bekor qilinadi)"),
        ]

        created_expenses = []
        for code, amt, dt, prj, note in expenses_data:
            exp_type = created_exp_types.get(code)
            if exp_type:
                exp = Expense.objects.create(
                    expense_type=exp_type,
                    amount=amt,
                    spent_on=dt,
                    project_id=prj,
                    note=note,
                    created_by=hisobchi_user,
                )
                created_expenses.append(exp)

        # 1 ta xarajatni bekor qilish (reversal)
        if created_expenses:
            last_exp = created_expenses[-1]
            Expense.objects.create(
                expense_type=last_exp.expense_type,
                amount=-last_exp.amount,
                spent_on=today - timedelta(days=7),
                project_id=last_exp.project_id,
                note=f"Hujjatdagi xato summa sababli bekor qilindi (Asl: #{last_exp.id})",
                created_by=hisobchi_user,
                reverses=last_exp,
            )

        # ---------------------------------------------------------
        # 9. KAM QOLDIQ VA XABARNOMALARNI SINXRONLASH
        # ---------------------------------------------------------
        self.stdout.write("9. Minimal qoldiq xabarnomalari yangilanmoqda...")
        for pk in StockBalance.objects.values_list("pk", flat=True).iterator():
            bal = StockBalance.objects.select_for_update().get(pk=pk)
            sync_low_stock(bal)

        # Natijalar xulosasi
        self.stdout.write(self.style.SUCCESS("\n========================================================"))
        self.stdout.write(self.style.SUCCESS("✅ POSTGRESQL (profur_db) BAZASI MUVAFFAQIYATLI TO'LDIRILDI!"))
        self.stdout.write(self.style.SUCCESS("========================================================"))
        self.stdout.write(f"👥 Foydalanuvchilar: {User.objects.count()} ta")
        self.stdout.write(f"🏷 Kategoriyalar: {Category.objects.count()} ta")
        self.stdout.write(f"📦 Materiallar (Katalog): {Material.objects.count()} ta")
        self.stdout.write(f"🚚 Kirim partiyalari (Batches): {Batch.objects.count()} ta")
        self.stdout.write(f"📤 Chiqimlar (Issues): {StockIssue.objects.count()} ta")
        self.stdout.write(f"🔄 Qaytarishlar (Returns): {StockReturn.objects.count()} ta")
        self.stdout.write(f"🗑 Hisobdan chiqarishlar (Write-offs): {WriteOff.objects.count()} ta")
        self.stdout.write(f"📊 Harakatlar tarixi (Movements): {StockMovement.objects.count()} ta")
        self.stdout.write(f"🔔 Kam qoldiq xabarlari (Notifications): {StockNotification.objects.count()} ta")
        self.stdout.write(f"💰 Qo'shimcha xarajatlar (Expenses): {Expense.objects.count()} ta")
        self.stdout.write(self.style.SUCCESS("========================================================"))
        self.stdout.write("🔑 Kirish ma'lumotlari:")
        self.stdout.write("   • admin / admin123 (Administrator - Barcha huquqlar)")
        self.stdout.write("   • omborchi / ombor123 (Ombor mudiri)")
        self.stdout.write("   • usta / usta123 (Ishlab chiqarish ustasi)")
        self.stdout.write("   • hisobchi / hisobchi123 (Bosh hisobchi)")
        self.stdout.write("   • taminotchi / taminot123 (Ta'minot mutaxassisi)")

