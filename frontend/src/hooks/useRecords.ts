import { useEffect, useState } from "react";
import { request, type Page } from "../api";
import type { Language } from "../i18n";

export function useRecords<T>(
  path: string | null,
  lang: Language,
  revision = 0,
) {
  const [data, setData] = useState<T[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [cursor, setCursor] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);
  useEffect(() => {
    setCursor(null);
    setData([]);
  }, [path, lang, revision]);
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    const url = new URL(cursor || path, location.origin);
    const expected = new URL(path, location.origin).pathname;
    if (url.pathname !== expected) return () => controller.abort();
    request<Page<T>>(url.pathname + url.search, lang, {
      signal: controller.signal,
    })
      .then((page) => {
        if (controller.signal.aborted) return;
        setData((old) => (cursor ? [...old, ...page.results] : page.results));
        setNext(page.next);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [path, lang, revision, cursor, nonce]);
  return {
    data,
    next,
    error,
    loading,
    more: () => setCursor(next),
    reload: () => {
      setCursor(null);
      setNonce((n) => n + 1);
    },
  };
}
