import { useEffect, useState } from "react";
import { allPages, request, type Page } from "../api";
import type { Language } from "../i18n";

export function useRecords<T>(
  path: string | null,
  lang: Language,
  revision = 0,
  loadAll = false,
) {
  const key = JSON.stringify([path, lang, revision, loadAll]);
  const [pagination, setPagination] = useState({
    key,
    cursor: null as string | null,
  });
  const cursor = pagination.key === key ? pagination.cursor : null;
  const [state, setState] = useState({
    key,
    data: [] as T[],
    next: null as string | null,
    error: null as unknown,
    loading: Boolean(path),
  });
  const [nonce, setNonce] = useState(0);
  useEffect(() => {
    setPagination((current) =>
      current.key === key ? current : { key, cursor: null },
    );
  }, [key]);
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    setState((old) => ({
      key,
      data: old.key === key ? old.data : [],
      next: null,
      error: null,
      loading: true,
    }));
    const url = new URL(cursor || path, location.origin);
    const expected = new URL(path, location.origin).pathname;
    if (url.pathname !== expected) {
      setState({
        key,
        data: [],
        next: null,
        error: new Error("Invalid pagination URL"),
        loading: false,
      });
      return () => controller.abort();
    }
    const result = loadAll
      ? allPages<T>(url.pathname + url.search, lang, controller.signal).then(
          (results) => ({ results, next: null, count: results.length }),
        )
      : request<Page<T>>(url.pathname + url.search, lang, {
          signal: controller.signal,
        });
    result
      .then((page) => {
        if (!controller.signal.aborted)
          setState((old) => ({
            key,
            data:
              cursor && old.key === key
                ? [...old.data, ...page.results]
                : page.results,
            next: page.next,
            error: null,
            loading: false,
          }));
      })
      .catch((error) => {
        if (!controller.signal.aborted)
          setState((old) => ({ ...old, error, loading: false }));
      });
    return () => controller.abort();
  }, [key, path, lang, cursor, nonce, loadAll]);
  const current =
    state.key === key && path
      ? state
      : { data: [], next: null, error: null, loading: Boolean(path) };
  return {
    data: current.data,
    next: current.next,
    error: current.error,
    loading: current.loading,
    more: () => {
      if (!current.loading && current.next)
        setPagination({ key, cursor: current.next });
    },
    reload: () => {
      setPagination({ key, cursor: null });
      setNonce((n) => n + 1);
    },
  };
}
