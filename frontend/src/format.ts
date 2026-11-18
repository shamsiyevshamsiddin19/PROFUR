import { ApiError } from "./api";
import type { Language, MessageKey } from "./i18n";

export function localDate() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tashkent",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}
export function errorKey(error: unknown): MessageKey {
  if (!(error instanceof ApiError)) return "network";
  if (error.status === 404 || error.status >= 500) return "unavailable";
  if (error.status === 403) return "forbidden";
  return "invalid";
}
export function money(value: string, lang: Language) {
  return new Intl.NumberFormat(lang === "uz" ? "uz-UZ" : lang, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number(value));
}
