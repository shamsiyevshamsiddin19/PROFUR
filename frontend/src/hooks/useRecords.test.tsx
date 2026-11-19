// @vitest-environment jsdom
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { useRecords } from "./useRecords";
afterEach(() => vi.unstubAllGlobals());
const page = (id: number, next: string | null = null) =>
  new Response(JSON.stringify({ results: [id], next, count: 1 }), {
    headers: { "Content-Type": "application/json" },
  });
test("changing a filter after loading more never appends an old page to new results", async () => {
  const calls: string[] = [];
  let late!: (response: Response) => void;
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string) => {
      calls.push(path);
      if (path.includes("page=2"))
        return new Promise<Response>((resolve) => {
          late = resolve;
        });
      return path.includes("filter=A")
        ? page(1, "/items/?filter=A&page=2")
        : page(9);
    }),
  );
  const { result, rerender } = renderHook(
    ({ path }) => useRecords<number>(path, "en"),
    { initialProps: { path: "/items/?filter=A" } },
  );
  await waitFor(() => expect(result.current.data).toEqual([1]));
  act(() => result.current.more());
  await waitFor(() => expect(calls).toHaveLength(2));
  rerender({ path: "/items/?filter=B" });
  await waitFor(() => expect(result.current.data).toEqual([9]));
  await act(async () => {
    late(page(2));
  });
  expect(result.current.data).toEqual([9]);
  expect(calls).toEqual([
    "/items/?filter=A",
    "/items/?filter=A&page=2",
    "/items/?filter=B",
  ]);
});
