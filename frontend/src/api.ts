import type { Language } from "./i18n";

export type User = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  roles: { code: string; name: string; permissions: string[] }[];
  role_codes: string[];
  is_superuser?: boolean;
};
export type Material = {
  id: number;
  name: string;
  display_name: string;
  unit: string;
  category: { id: number; name: string };
  color?: string;
  container_size?: string | null;
  allowed_roles?: string[];
  length_cm?: string | null;
  width_cm?: string | null;
  thickness_cm?: string | null;
  is_active?: boolean;
  quantity_on_hand?: string | null;
};
export type StockRow = {
  material: {
    id: number;
    display_name: string;
    unit: string;
    category: { id: number; name: string };
  };
  quantity_on_hand: string;
  open_batches: number;
  min_quantity: string | null;
  is_below_min: boolean;
  value_by_currency?: { currency: "USD"; amount: string }[];
};
export type StockBatch = {
  id: number;
  received_on: string;
  quantity: string;
  quantity_remaining: string;
  unit_price?: string;
  currency?: "USD";
};
export type StockMovement = {
  id: number;
  type: string;
  material: { id: number; display_name: string; unit: string };
  batch_id: number | null;
  quantity: string;
  quantity_on_hand_after: string;
  reference: { kind: string; id: number };
  reason: string;
  created_by: { id: number; name: string };
  created_at: string;
};
export type Receipt = {
  is_opening?: boolean;
  id: number;
  received_on: string;
  quantity: string;
  quantity_remaining?: string;
  total_amount?: string;
  currency?: "USD";
  unit_price?: string;
  quantity_on_hand_after?: string;
  supplier?: string;
  document_number?: string;
  note?: string;
  created_by?: { id: number; name: string };
  created_at?: string;
  material: { id?: number; display_name: string; unit: string };
};
export type Page<T> = { count: number; next: string | null; results: T[] };
export type ReceiptInput = {
  is_opening?: boolean;
  material_id: number;
  received_on: string;
  quantity: string;
  total_amount?: string;
  unit_price?: string;
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
  method: "POST" | "PATCH" = "POST",
) {
  const { csrfToken } = await request<{ csrfToken: string }>(
    "/api/auth/csrf/",
    language,
  );
  return request<T>(path, language, {
    method,
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

export function can(user: User, code: string) {
  return Boolean(
    user.is_superuser ||
    user.role_codes.includes("ADMIN") ||
    user.roles.some(
      (role) =>
        role.permissions.includes("*") || role.permissions.includes(code),
    ),
  );
}
export type Category = { id: number; name: string; is_active: boolean };
export type Allocation = {
  batch_id: number;
  quantity: string;
  unit_price?: string;
  returnable_quantity?: string;
  received_on: string;
};
export type Operation = {
  id: number;
  material: { id: number; display_name: string; unit: string };
  quantity: string;
  allocations: Allocation[];
  total_cost?: string;
  issued_on?: string;
  returned_on?: string;
  recipient_name?: string;
  project_id?: number | null;
  issue?: { id: number; recipient_name: string; quantity: string };
  reason?: string;
  note?: string;
  status?: "pending" | "approved" | "rejected";
  decision_note?: string;
  created_by: { id: number; name: string };
  created_at: string;
};
export type ExpenseType = {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
};
export type Expense = {
  id: number;
  expense_type: string;
  expense_type_name: string;
  amount: string;
  spent_on: string;
  project_id: number | null;
  note: string;
  created_by: number;
  reverses: number | null;
  reversal: { id: number; reason: string } | null;
};
export async function allPages<T>(
  path: string,
  lang: Language,
  signal?: AbortSignal,
): Promise<T[]> {
  const rows: T[] = [];
  let next: string | null = path;
  const seen = new Set<string>();
  const prefix = new URL(path, location.origin).pathname;
  while (next) {
    const url = new URL(next, location.origin);
    if (url.pathname !== prefix || seen.has(url.pathname + url.search))
      throw new ApiError(502, null);
    seen.add(url.pathname + url.search);
    const page: Page<T> = await request<Page<T>>(
      url.pathname + url.search,
      lang,
      { signal },
    );
    rows.push(...page.results);
    next = page.next;
  }
  return rows;
}
