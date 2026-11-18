import { useState } from "react";
import { ApiError, write } from "../api";
import type { Language } from "../i18n";

type Pending = { path: string; body: unknown; key: string };
export function useIdempotentWrite<T>(
  scope: string,
  userId: number,
  lang: Language,
) {
  const storage = `profur.pending.${userId}.${scope}`;
  const [pending, setPending] = useState<Pending | null>(() => {
    try {
      const value = JSON.parse(sessionStorage.getItem(storage) || "null");
      return value &&
        typeof value.key === "string" &&
        value.path === `/api/v1/${scope}/`
        ? value
        : null;
    } catch {
      return null;
    }
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function submit(body: unknown): Promise<T | null> {
    if (busy) return null;
    const operation = pending || {
      path: `/api/v1/${scope}/`,
      body,
      key: crypto.randomUUID(),
    };
    setBusy(true);
    setError(null);
    try {
      // Natija noma'lum bo'lsa yangilanishdan keyin ham ayni kalit tiklanadi.
      sessionStorage.setItem(storage, JSON.stringify(operation));
      setPending(operation);
      const result = await write<T>(
        operation.path,
        lang,
        operation.body,
        operation.key,
      );
      sessionStorage.removeItem(storage);
      setPending(null);
      return result;
    } catch (err) {
      setError(err);
      if (err instanceof ApiError && err.status < 500 && err.status !== 409) {
        sessionStorage.removeItem(storage);
        setPending(null);
      }
      // 409 biznes rad javobi ham aniq natija; forma to'g'rilanadi.
      if (err instanceof ApiError && err.status === 409) {
        sessionStorage.removeItem(storage);
        setPending(null);
      }
      return null;
    } finally {
      setBusy(false);
    }
  }
  return { submit, busy, error, pending };
}
