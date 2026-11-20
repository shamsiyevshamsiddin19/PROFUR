import { expect, test } from "@playwright/test";

const cases = [
  {
    account: "worker",
    start: "settings",
    hidden: ["receipts", "stock", "issues", "expenses", "expense-types"],
  },
  {
    account: "issuer",
    start: "operations",
    hidden: ["receipts", "returns", "write-offs", "expenses", "expense-types"],
  },
  {
    account: "expense_reader",
    start: "expenses",
    hidden: ["receipts", "stock", "issues", "expense-types"],
  },
];

for (const { account, start, hidden } of cases) {
  test(`${account} only sees and requests permitted work`, async ({ page }) => {
    const fetched = new Set<string>();
    page.on("request", (request) =>
      fetched.add(new URL(request.url()).pathname),
    );
    await page.goto("/#receiving");
    await page.getByRole("combobox", { name: "Language" }).selectOption("en");
    await page.getByLabel("Username").fill("browser_" + account);
    await page.getByLabel("Password").fill("browser-test-only-password");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page).toHaveURL(new RegExp("#" + start + "$"));
    await expect(
      page.getByRole("main").getByRole("link", { name: "Add material" }),
    ).toHaveCount(0);
    if (account === "worker") {
      await expect(
        page.getByText(/No warehouse work is assigned/),
      ).toBeVisible();
      await expect(page.locator("nav a")).toHaveCount(1);
    } else if (account === "issuer") {
      await expect(page.getByRole("tab")).toHaveCount(1);
      await expect(page.getByRole("tab", { name: "Issue" })).toBeVisible();
      await expect(
        page.getByRole("columnheader", { name: "Actions" }),
      ).toHaveCount(0);
    } else {
      await expect(
        page.getByRole("heading", { name: "Expenses", level: 1 }),
      ).toBeVisible();
      await expect(
        page.getByRole("combobox", { name: "Expense type" }),
      ).toHaveCount(0);
    }
    await page.goto("/#administration");
    await expect(page).toHaveURL(new RegExp("#" + start + "$"));
    for (const resource of hidden)
      expect(fetched.has(`/api/v1/${resource}/`)).toBe(false);
    expect(fetched.has("/api/auth/users/")).toBe(false);
    expect((await page.request.get("/api/auth/users/")).status()).toBe(403);
  });
}
