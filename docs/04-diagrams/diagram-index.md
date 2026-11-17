# Diagrammalar ro‘yxati

**Holat:** Dastlabki chizmalar. Rollar va jarayonlar PM tomonidan tasdiqlangach takomillashtiriladi.

## Foydalanish holatlari — umumiy ko‘rinish

```mermaid
flowchart LR
  A[Admin] --> B[Omborni boshqarish]
  A --> C[Zakaz va modellarni boshqarish]
  A --> D[Ishlab chiqarishni kuzatish]
  A --> E[Loyihani yopish va hisobot]
  I[Ishchi] --> F[O‘z vazifalarini ko‘rish]
  I --> G[Vazifani qabul qilish]
  I --> H[Ish va material sarfini qayd etish]
```

## Ishlab chiqarish jarayoni

```mermaid
flowchart TD
  P[Loyiha va modellarni yaratish] --> A[Arra]
  A --> B[Freza]
  B --> C[Shkurka]
  C --> D[Kraska]
  D --> E[Zbor]
  E --> F[Upakovka]
  F --> G[Yetkazish va xarajatni kiritish]
  G --> H[Loyihani yopish va tarixga o‘tkazish]
```

## Keyingi chizmalar

- Rollar tasdiqlangach to‘liq UML foydalanish holatlari diagrammasi.
- Tizimning asosiy qismlari va ularning aloqalari.
- Ombor qoidalari aniqlashgach ma'lumotlar bazasi aloqalari (ER diagramma).
- Material kirimi, chiqimi, detal nomuvofiqligi va loyiha yopilishi uchun ketma-ketlik diagrammalari.
