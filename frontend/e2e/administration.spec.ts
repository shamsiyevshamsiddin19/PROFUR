import { expect, test } from "@playwright/test";

test.describe.configure({ retries: 0 });
test("admin manages users, roles and expense types; stock notifications remain private", async ({
  page,
}, info) => {
  await page.goto("/");
  await page.getByRole("combobox", { name: "Language" }).selectOption("en");
  await page.getByLabel("Username").fill("browser_storekeeper");
  await page.getByLabel("Password").fill("browser-test-only-password");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(
    page.getByRole("heading", { name: "Material receipts", exact: true }),
  ).toBeVisible();
  await page.goto("/#administration");
  await expect(
    page.getByRole("heading", { name: "Administration", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Add role", exact: true }).click();
  const dialog = page.getByRole("dialog");
  const suffix = info.project.name.replace(/\W/g, "_");
  const roleName = "Warehouse viewer " + suffix;
  const username = "phase1_" + suffix;
  await dialog.getByLabel("Role code").fill("VIEWER_" + suffix);
  await dialog.getByLabel("Name", { exact: true }).fill(roleName);
  await dialog.getByRole("checkbox", { name: /catalog.view_material/ }).check();
  await dialog.getByRole("checkbox", { name: /inventory.view_stock/ }).check();
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await page.getByRole("button", { name: "Add user", exact: true }).click();
  await dialog.getByLabel("Username", { exact: true }).fill(username);
  await dialog
    .getByLabel("Password", { exact: true })
    .fill("Warehouse-new-user-2026");
  await dialog
    .getByLabel("First name", { exact: true })
    .fill("Warehouse Viewer");
  await dialog.getByRole("checkbox", { name: roleName, exact: false }).check();
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await page
    .getByRole("textbox", { name: "Search users", exact: true })
    .fill(username);
  const record = page.locator(".admin-record").filter({ hasText: username });
  await expect(record).toHaveCount(1);
  await record.getByRole("button", { name: "Edit", exact: true }).click();
  await dialog.getByLabel("Phone", { exact: true }).fill("+998901234567");
  await dialog.getByRole("checkbox", { name: "Active", exact: true }).uncheck();
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(record).toContainText("Inactive");
  await record.getByRole("button", { name: "Edit", exact: true }).click();
  await expect(dialog.getByLabel("Phone", { exact: true })).toHaveValue(
    "+998901234567",
  );
  await dialog.getByRole("checkbox", { name: "Active", exact: true }).check();
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await record
    .getByRole("button", { name: "Reset password", exact: true })
    .click();
  await dialog
    .getByLabel("New password", { exact: true })
    .fill("Warehouse-reset-user-2026");
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(dialog).not.toBeVisible();

  await page.goto("/#expenses");
  await page
    .getByRole("button", { name: "Add expense type", exact: true })
    .click();
  await dialog
    .getByLabel("Type code", { exact: true })
    .fill("phase1_" + suffix);
  await dialog
    .getByLabel("Name · UZ", { exact: true })
    .fill("Boshqa " + suffix);
  await dialog
    .getByLabel("Name · RU", { exact: true })
    .fill("Прочие " + suffix);
  await dialog.getByLabel("Name · EN", { exact: true }).fill("Other " + suffix);
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(
    page.locator(".admin-record").filter({ hasText: "Other " + suffix }),
  ).toHaveCount(1);

  const csrf = await (await page.request.get("/api/auth/csrf/")).json();
  const headers = { "X-CSRFToken": csrf.csrfToken };
  const categories = await (
    await page.request.get("/api/v1/categories/")
  ).json();
  const material = await (
    await page.request.post("/api/v1/materials/", {
      headers,
      data: {
        name: "Alert " + suffix,
        category_id: categories.results[0].id,
        unit: "sheet",
      },
    })
  ).json();
  const minimum = await page.request.patch(`/api/v1/stock/${material.id}/`, {
    headers,
    data: { min_quantity: "5.00" },
  });
  expect(minimum.status()).toBe(200);
  await page.goto("/#notifications");
  const notification = page
    .locator(".admin-record")
    .filter({ hasText: "Alert " + suffix });
  await expect(notification).toContainText("0.00 / 5.00");
  await notification
    .getByRole("button", { name: "Mark as read", exact: true })
    .click();
  await expect(
    notification.getByRole("button", { name: "Mark as read", exact: true }),
  ).toHaveCount(0);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);

  // Restricted user can sign in with the new password, and cannot reach admin APIs.
  const logout = await page.request.post("/api/auth/logout/", { headers });
  expect(logout.status()).toBe(200);
  await page.goto("/");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("Warehouse-reset-user-2026");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(
    page.getByRole("heading", { name: "Material receipts", exact: true }),
  ).toBeVisible();
  await page.goto("/#administration");
  await expect(
    page.getByRole("button", { name: "Add user", exact: true }),
  ).toHaveCount(0);
  expect((await page.request.get("/api/auth/users/")).status()).toBe(403);
  expect(
    (await page.request.get("/api/v1/notifications/?unread=true")).status(),
  ).toBe(200);
});
