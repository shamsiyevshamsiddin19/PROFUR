// @vitest-environment jsdom
import { afterEach, expect, test, vi } from "vitest";
import { cleanup, render, screen, within } from "@testing-library/react";
import { App } from "./App";
import { screenAllowed, operationAllowed } from "./navigation";
import type { User } from "./api";
const account = (code: string, permissions: string[]): User => ({
  id: 7,
  username: code,
  first_name: "",
  last_name: "",
  roles: [{ code, name: code, permissions }],
  role_codes: [code],
});
afterEach(() => {
  cleanup();
  localStorage.clear();
  location.hash = "";
  vi.unstubAllGlobals();
});
const view = "inventory.view_stock";
test.each([
  [
    "WAREHOUSE_MANAGER",
    [
      view,
      "catalog.view_material",
      "inventory.add_receipt",
      "inventory.add_issue",
      "inventory.approve_return",
    ],
    true,
    true,
    false,
  ],
  [
    "PRODUCTION_SUPERVISOR",
    [
      view,
      "catalog.view_material",
      "inventory.add_issue",
      "inventory.add_return",
    ],
    false,
    true,
    false,
  ],
  ["ACCOUNTANT", ["expenses.view_expense"], false, false, true],
  [
    "PROCUREMENT",
    [
      view,
      "catalog.view_material",
      "catalog.add_material",
      "inventory.add_receipt",
    ],
    true,
    false,
    false,
  ],
  ["WORKER", [], false, false, false],
  ["ADMIN", [], true, true, true],
] as const)(
  "%s sees only assigned sections",
  (code, permissions, receiving, operations, expenses) => {
    const user = account(code, [...permissions]);
    expect(screenAllowed(user, "receiving")).toBe(receiving);
    expect(screenAllowed(user, "operations")).toBe(operations);
    expect(screenAllowed(user, "expenses")).toBe(expenses);
    expect(screenAllowed(user, "administration")).toBe(code === "ADMIN");
  },
);
test("accountant starts at Home, sees expenses and never loads restricted stock or accounts", async () => {
  localStorage.setItem("profur.language", "en");
  const calls: string[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string) => {
      calls.push(path);
      return new Response(
        JSON.stringify(
          path === "/api/auth/me/"
            ? account("ACCOUNTANT", ["expenses.view_expense"])
            : { results: [], next: null, count: 0 },
        ),
        { headers: { "Content-Type": "application/json" } },
      );
    }),
  );
  render(<App />);
  await screen.findByRole("heading", { name: "Home" });
  const nav = within(screen.getByRole("navigation"));
  expect(nav.getByRole("link", { name: "Expenses" })).toBeTruthy();
  for (const name of [
    "Material receipts",
    "Warehouse operations",
    "Stock",
    "Administration",
  ])
    expect(nav.queryByRole("link", { name })).toBeNull();
  expect(calls).toEqual(["/api/auth/me/"]);
});
test("a forbidden deep link does not mount the restricted page", async () => {
  location.hash = "#administration";
  localStorage.setItem("profur.language", "en");
  const calls: string[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string) => {
      calls.push(path);
      return new Response(JSON.stringify(account("WORKER", [])), {
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
  render(<App />);
  await screen.findByRole("link", { name: "Back to home" });
  expect(calls).toEqual(["/api/auth/me/"]);
});
test("a return approver has no issue or write-off action", () => {
  const user = account("APPROVER", [view, "inventory.approve_return"]);
  expect(operationAllowed(user, "returns")).toBe(true);
  expect(operationAllowed(user, "issues")).toBe(false);
  expect(operationAllowed(user, "write-offs")).toBe(false);
});
