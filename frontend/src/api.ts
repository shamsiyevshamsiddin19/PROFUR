import type { Language } from "./i18n";

export type User = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  roles: { code: string; name: string; permissions: string[] }[];
  role_codes: string[];
};
export type Material = {
  id: number;
  name: string;
  display_name: string;
  unit: string;
  category: { id: number; name: string };
  quantity_on_hand?: string;
};
export type Receipt = {
  id: number;
  received_on: string;
  quantity: string;
  total_amount: string;
  currency: "USD";
  unit_price: string;
  quantity_on_hand_after?: string;
  material: { display_name: string; unit: string };
};
export type Page<T> = { count: number; next: string | null; results: T[] };
export type ReceiptInput = {
  material_id: number;
  received_on: string;
  quantity: string;
  total_amount: string;
  currency: "USD";
  supplier: string;
  document_number: string;
  note: string;
};

export class ApiError extends Error {
  constructor(
    public status: number,
    public data: unknown,
  ) {
    super(String(status));
  }
}

// CSRF token har bir yozishda olinadi: login tokenni aylantiradi.
export async function request<T>(
  path: string,
  language: Language,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  headers.set("Accept-Language", language);
  if (init.body) headers.set("Content-Type", "application/json");
  const response = await fetch(path, {
    ...init,
    headers,
    credentials: "same-origin",
  });
  const type = response.headers.get("content-type") ?? "";
  const data: unknown = type.includes("application/json")
    ? await response.json()
    : null;
  if (!response.ok) throw new ApiError(response.status, data);
  if (data === null) throw new ApiError(502, null);
  return data as T;
}
export async function write<T>(
  path: string,
  language: Language,
  body: unknown,
  key?: string,
) {
  const { csrfToken } = await request<{ csrfToken: string }>(
    "/api/auth/csrf/",
    language,
  );
  return request<T>(path, language, {
    method: "POST",
    body: JSON.stringify(body),
    headers: {
      "X-CSRFToken": csrfToken,
      ...(key ? { "Idempotency-Key": key } : {}),
    },
  });
}
export function fieldErrors(error: unknown): Record<string, string> {
  if (
    !(error instanceof ApiError) ||
    !error.data ||
    typeof error.data !== "object"
  )
    return {};
  const data = error.data as { error?: { fields?: Record<string, unknown> } };
  const fields = data.error?.fields ?? (error.data as Record<string, unknown>);
  return Object.fromEntries(
    Object.entries(fields).map(([key, value]) => {
      const first = Array.isArray(value) ? value[0] : value;
      const text =
        typeof first === "string"
          ? first
          : first && typeof first === "object" && "message" in first
            ? String(first.message)
            : "";
      return [key, text];
    }),
  );
}
