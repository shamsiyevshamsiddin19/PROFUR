import { uxMessages } from "./ux-i18n";
import { appearanceMessages } from "./appearance-i18n";
import { adminMessages } from "./admin-i18n";
import { workflowMessages } from "./workflow-i18n";
export const languages = { uz: "O‘zbekcha", ru: "Русский", en: "English" };
export type Language = keyof typeof languages;

const messages = {
  ...workflowMessages,
  ...uxMessages,
  ...appearanceMessages,
  ...adminMessages,
  warehouse: ["Ombor", "Склад", "Warehouse"],
  receiving: ["Material kirimi", "Поступление материалов", "Material receipts"],
  materials: ["Materiallar", "Материалы", "Materials"],
  stock: ["Qoldiq", "Остатки", "Stock"],
  workspace: ["ISH MAYDONI", "РАБОЧЕЕ ПРОСТРАНСТВО", "WORKSPACE"],
  newReceipt: ["Yangi kirim", "Новое поступление", "New receipt"],
  intro: [
    "Omborga kelgan materialni hisobga oling.",
    "Учитывайте материалы, поступившие на склад.",
    "Record materials arriving at your warehouse.",
  ],
  details: ["Kirim ma’lumotlari", "Данные поступления", "Receipt details"],
  detailsHint: [
    "Har bir kirim alohida partiya sifatida saqlanadi.",
    "Каждое поступление сохраняется отдельной партией.",
    "Each receipt is recorded as a separate batch.",
  ],
  material: ["Material", "Материал", "Material"],
  select: ["Materialni tanlang", "Выберите материал", "Select a material"],
  quantity: ["Miqdor", "Количество", "Quantity"],
  date: ["Kirim sanasi", "Дата поступления", "Receipt date"],
  total: ["Jami summa", "Общая сумма", "Total amount"],
  currency: ["Valyuta", "Валюта", "Currency"],
  supplier: ["Yetkazib beruvchi", "Поставщик", "Supplier"],
  document: ["Hujjat raqami", "Номер документа", "Document number"],
  note: ["Izoh", "Примечание", "Notes"],
  optional: ["ixtiyoriy", "необязательно", "optional"],
  save: ["Kirimni saqlash", "Сохранить поступление", "Save receipt"],
  saving: ["Saqlanmoqda…", "Сохранение…", "Saving…"],
  summary: ["Kirim hisob-kitobi", "Расчёт поступления", "Receipt summary"],
  unitPrice: ["Birlik narxi", "Цена за единицу", "Unit price"],
  estimate: [
    "Dastlabki hisob. Yakuniy narxni tizim hisoblaydi.",
    "Предварительный расчёт. Итоговую цену рассчитает система.",
    "Preview. The system calculates the final unit price.",
  ],
  recent: ["So‘nggi kirimlar", "Последние поступления", "Recent receipts"],
  empty: ["Hozircha yozuvlar yo‘q", "Записей пока нет", "No records yet"],
  retry: ["Qayta tekshirish", "Проверить снова", "Try again"],
  unavailable: [
    "Bu xizmat hozircha ishlamayapti. Keyinroq qayta tekshiring.",
    "Сервис пока недоступен. Попробуйте позже.",
    "This service is not available yet. Please try again later.",
  ],
  network: [
    "Serverga ulanib bo‘lmadi. Ulanishni tekshiring.",
    "Не удалось подключиться к серверу. Проверьте соединение.",
    "Unable to reach the server. Check your connection.",
  ],
  loginTitle: [
    "Ish maydoningizga kiring.",
    "Войдите в рабочее пространство.",
    "Your workspace awaits.",
  ],
  loginHint: [
    "Omboringiz. Materiallaringiz. Hammasi bir joyda.",
    "Ваш склад. Ваши материалы. Всё в одном месте.",
    "Your warehouse. Your materials. All in one place.",
  ],
  username: ["Foydalanuvchi nomi", "Имя пользователя", "Username"],
  password: ["Parol", "Пароль", "Password"],
  login: ["Tizimga kirish", "Войти", "Sign in"],
  logout: ["Chiqish", "Выйти", "Sign out"],
  loading: ["Ulanmoqda…", "Подключение…", "Connecting…"],
  invalid: [
    "Ma’lumotlarni tekshiring.",
    "Проверьте введённые данные.",
    "Check the entered details.",
  ],
  credentials: [
    "Login yoki parol noto‘g‘ri.",
    "Неверное имя пользователя или пароль.",
    "Incorrect username or password.",
  ],
  forbidden: [
    "Bu amal uchun ruxsat yetarli emas.",
    "Недостаточно прав для этого действия.",
    "You do not have permission for this action.",
  ],
  success: ["Kirim saqlandi.", "Поступление сохранено.", "Receipt saved."],
  batch: ["Partiya", "Партия", "Batch"],
  remaining: ["Yangi qoldiq", "Новый остаток", "Updated stock"],
  search: ["Material qidirish", "Поиск материалов", "Search materials"],
  category: ["Kategoriya", "Категория", "Category"],
  unit: ["Birlik", "Единица", "Unit"],
  menu: ["Menyuni ochish", "Открыть меню", "Open menu"],
  close: ["Yopish", "Закрыть", "Close"],
  locked: [
    "Natija tasdiqlanmadi. Takror yozilmasligi uchun ayni so‘rovni qayta yuboring.",
    "Результат не подтверждён. Повторите тот же запрос, чтобы избежать дубля.",
    "The result could not be confirmed. Retry the same request to avoid a duplicate.",
  ],
  again: [
    "Ayni so‘rovni qayta yuborish",
    "Повторить тот же запрос",
    "Retry the same request",
  ],
  session: [
    "Sessiya tugagan. Qayta kiring.",
    "Сессия истекла. Войдите снова.",
    "Your session expired. Sign in again.",
  ],
  noMaterials: [
    "Kirim uchun avval faol material bo‘lishi kerak.",
    "Для поступления нужен активный материал.",
    "An active material is needed to record a receipt.",
  ],
  allMoney: [
    "Barcha hisoblar AQSH dollarida",
    "Все расчёты в долларах США",
    "All amounts in US dollars",
  ],
  batches: ["Partiyalar", "Партии", "Batches"],
  minLimit: ["Min. chegara", "Мин. остаток", "Min. limit"],
  lowStock: ["Kam qoldiq", "Мало на складе", "Low stock"],
  stockValue: ["Umumiy qiymati", "Общая стоимость", "Stock value"],
  belowMinFilter: [
    "Faqat kam qolganlar",
    "Только мало на складе",
    "Below minimum only",
  ],
} as const;

export type MessageKey = keyof typeof messages;
export function translate(language: Language, key: MessageKey): string {
  return messages[key][(["uz", "ru", "en"] as const).indexOf(language)];
}
export function initialLanguage(): Language {
  try {
    const value = localStorage.getItem("profur.language");
    if (value === "uz" || value === "ru" || value === "en") return value;
  } catch {
    /* Saqlash yopiq bo‘lsa standart til qo‘llanadi. */
  }
  return "uz";
}
export function unitLabel(unit: string, lang: Language) {
  const labels: Record<string, readonly string[]> = {
    sheet: ["list", "лист", "sheet"],
    piece: ["dona", "шт.", "pcs"],
    kg: ["kg", "кг", "kg"],
    liter: ["litr", "л", "L"],
    meter: ["metr", "м", "m"],
    m2: ["m²", "м²", "m²"],
  };
  return labels[unit]?.[["uz", "ru", "en"].indexOf(lang)] ?? unit;
}
