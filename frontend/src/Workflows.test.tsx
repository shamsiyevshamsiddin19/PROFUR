// @vitest-environment jsdom
import { afterEach, expect, test, vi } from "vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { Operations } from "./pages/Operations";
import { Expenses } from "./pages/Expenses";
import { App } from "./App";
import { csvCell } from "./pages/History";
import type { User } from "./api";

afterEach(() => {
  cleanup();
  sessionStorage.clear();
  localStorage.clear();
  location.hash = "";
  vi.unstubAllGlobals();
});
const user: User = {
  id: 3,
  username: "keeper",
  first_name: "",
  last_name: "",
  roles: [
    {
      code: "KEEPER",
      name: "Keeper",
      permissions: ["inventory.view_stock", "inventory.add_issue"],
    },
  ],
  role_codes: ["KEEPER"],
};
function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
const material = {
  id: 12,
  display_name: "MDF",
  unit: "sheet",
  category: { id: 1, name: "MDF" },
};
test("uncertain issue restores and retries the exact payload and key after remount", async () => {
  const posts: RequestInit[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string, init: RequestInit = {}) => {
      if (path === "/api/auth/csrf/") return json({ csrfToken: "fresh" });
      if (path === "/api/v1/stock/")
        return json({
          results: [{ material, quantity_on_hand: "10.00" }],
          next: null,
        });
      if (path === "/api/v1/stock/12/batches/")
        return json({
          results: [
            {
              id: 9,
              received_on: "2026-11-01",
              quantity: "10.00",
              quantity_remaining: "10.00",
            },
          ],
          next: null,
        });
      if (path === "/api/v1/issues/" && init.method === "POST") {
        posts.push(init);
        if (posts.length === 1) throw new TypeError("network lost");
        return json({ id: 23 }, 200);
      }
      if (path === "/api/v1/issues/") return json({ results: [], next: null });
      return json({}, 404);
    }),
  );
  const view = render(<Operations user={user} lang="en" />);
  await screen.findByRole("option", { name: "MDF · 10.00" });
  fireEvent.change(screen.getByRole("combobox", { name: "Material" }), {
    target: { value: "12" },
  });
  const qty = await screen.findByRole("spinbutton", { name: "Batch #9" });
  fireEvent.change(qty, { target: { value: "3" } });
  fireEvent.change(screen.getByLabelText("Recipient"), {
    target: { value: "Sardor" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Save" }));
  await screen.findByRole("button", { name: "Retry the same request" });
  expect(posts).toHaveLength(1);
  view.unmount();
  render(<Operations user={user} lang="en" />);
  fireEvent.click(
    await screen.findByRole("button", { name: "Retry the same request" }),
  );
  await waitFor(() => expect(posts).toHaveLength(2));
  expect(posts[1].body).toBe(posts[0].body);
  expect(new Headers(posts[1].headers).get("Idempotency-Key")).toBe(
    new Headers(posts[0].headers).get("Idempotency-Key"),
  );
  expect(JSON.parse(String(posts[1].body)).allocations).toEqual([
    { batch_id: 9, quantity: "3" },
  ]);
  await screen.findByText("Issue saved.");
  expect(sessionStorage.getItem("profur.pending.3.issues")).toBeNull();
});
test("permissionless user cannot access workflow screens through a direct hash", async () => {
  location.hash = "#operations";
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => json({ ...user, roles: [], role_codes: [] })),
  );
  render(<App />);
  await screen.findByText("Bu bo‘lim uchun ruxsatingiz yo‘q.");
  expect(screen.queryByRole("link", { name: "Ombor amallari" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Saqlash" })).toBeNull();
});
test("CSV values cannot execute spreadsheet formulas and quotes remain escaped", () => {
  expect(csvCell('=HYPERLINK("https://example.com")')).toBe(
    '"\'=HYPERLINK(""https://example.com"")"',
  );
  expect(csvCell("ordinary, value")).toBe('"ordinary, value"');
  expect(csvCell("  +SUM(1,2)")).toBe('"\'  +SUM(1,2)"');
});

test("expense form labels select their controls and an uncertain write reuses its key", async () => {
  const posts: RequestInit[] = [];
  const expenseUser: User = {
    ...user,
    roles: [
      {
        code: "ACCOUNTANT",
        name: "Accountant",
        permissions: [
          "expenses.view_expense",
          "expenses.add_expense",
          "expenses.view_expensetype",
        ],
      },
    ],
  };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string, init: RequestInit = {}) => {
      if (path === "/api/auth/csrf/") return json({ csrfToken: "fresh" });
      if (path === "/api/v1/expense-types/")
        return json({
          results: [{ id: 1, code: "tax", name: "Tax", is_active: true }],
          next: null,
        });
      if (path.startsWith("/api/v1/expenses/") && init.method === "POST") {
        posts.push(init);
        if (posts.length === 1) throw new TypeError("lost");
        return json({ id: 31 }, 200);
      }
      return json({ results: [], next: null });
    }),
  );
  const view = render(<Expenses lang="en" user={expenseUser} />);
  await waitFor(() =>
    expect(screen.getAllByRole("option", { name: "Tax" })).toHaveLength(2),
  );
  const form = screen.getByRole("button", { name: "Save" }).closest("form")!;
  fireEvent.change(
    within(form).getByLabelText("Expense type", { exact: true }),
    { target: { value: "tax" } },
  );
  fireEvent.change(
    within(form).getByLabelText("Amount · USD", { exact: true }),
    { target: { value: "12.50" } },
  );
  fireEvent.change(
    within(form).getByLabelText("Project number", { exact: true }),
    { target: { value: "7" } },
  );
  fireEvent.submit(form);
  await screen.findByRole("button", { name: "Retry the same request" });
  view.unmount();
  render(<Expenses lang="en" user={expenseUser} />);
  fireEvent.click(
    await screen.findByRole("button", { name: "Retry the same request" }),
  );
  await waitFor(() => expect(posts).toHaveLength(2));
  expect(posts[1].body).toBe(posts[0].body);
  expect(new Headers(posts[1].headers).get("Idempotency-Key")).toBe(
    new Headers(posts[0].headers).get("Idempotency-Key"),
  );
  expect(JSON.parse(String(posts[1].body))).toMatchObject({
    amount: "12.50",
    currency: "USD",
    project_id: 7,
    expense_type: "tax",
  });
  await screen.findByText("Saved.", { exact: true });
});
