import { expect, test } from "@playwright/test";

// Bitta vaqtinchalik bazani o‘zgartiradigan ssenariy qayta urinishda takrorlanmaydi.
test.describe.configure({ retries: 0 });

test("mobile warehouse workflow persists receipts, issues, approvals and expenses through the real API", async ({
  page,
}, testInfo) => {
  await page.goto("/#receiving");
  await page.getByRole("combobox", { name: "Language" }).selectOption("en");
  await page.getByLabel("Username").fill("browser_storekeeper");
  await page.getByLabel("Password").fill("browser-test-only-password");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(
    page.getByRole("heading", { name: "Material receipts" }),
  ).toBeVisible();

  const materialName = `Warehouse ${testInfo.project.name}`;
  const csrf = await (await page.request.get("/api/auth/csrf/")).json();
  const categories = await (
    await page.request.get("/api/v1/categories/?search=LMDF")
  ).json();
  const created = await page.request.post("/api/v1/materials/", {
    data: {
      name: materialName,
      category_id: categories.results[0].id,
      unit: "sheet",
    },
    headers: { "X-CSRFToken": csrf.csrfToken },
  });
  expect(created.status()).toBe(201);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Material receipts", exact: true }),
  ).toBeVisible();
  const material = page.getByRole("combobox", {
    name: "Material",
    exact: true,
  });
  await expect(
    material.locator("option").filter({ hasText: materialName }),
  ).toHaveCount(1);
  await material.selectOption({ label: `${materialName} · sheet` });
  await page
    .getByRole("spinbutton", { name: "Quantity", exact: true })
    .fill("15");
  await page
    .getByRole("spinbutton", { name: "Total amount", exact: true })
    .fill("450.00");
  const response = page.waitForResponse(
    (res) =>
      res.url().endsWith("/api/v1/receipts/") &&
      res.request().method() === "POST",
  );
  const save = page.getByRole("button", { name: "Save receipt" });
  await save.scrollIntoViewIfNeeded();
  await expect(save).toBeInViewport();
  await save.click();
  const saved = await response;
  expect(saved.status()).toBe(201);
  const batch = await saved.json();
  expect(batch.currency).toBe("USD");
  expect(batch.quantity_on_hand_after).toBe("15.00");
  expect(batch.unit_price).toBe("30.000000");

  // Bir xil so‘rov haqiqiy serverga qaytariladi: ikkinchi partiya yaratilmasin.
  const original = saved.request();
  const retry = await page.request.post("/api/v1/receipts/", {
    data: original.postDataJSON(),
    headers: {
      "X-CSRFToken": original.headers()["x-csrftoken"],
      "Idempotency-Key": original.headers()["idempotency-key"],
    },
  });
  expect(retry.status()).toBe(200);
  expect((await retry.json()).id).toBe(batch.id);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Material receipts" }),
  ).toBeVisible();
  const receipts = await page.request.get(
    `/api/v1/receipts/?material=${batch.material.id}`,
  );
  const result = await receipts.json();
  expect(result.count).toBe(1);
  expect(result.results[0].id).toBe(batch.id);
  const catalogue = await page.request.get(
    `/api/v1/materials/${batch.material.id}/`,
  );
  expect((await catalogue.json()).quantity_on_hand).toBe("15.00");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);

  // Shu haqiqiy sessiyada qolgan ombor oqimi ham bajariladi.
  await page.goto("/#operations");
  await expect(
    page
      .getByRole("table", { name: "New record entry", exact: true })
      .getByLabel("Recipient", { exact: true }),
  ).toBeEditable();
  await page
    .getByRole("combobox", { name: "Material", exact: true })
    .selectOption({ label: `${materialName} · 15.00` });
  await page.getByLabel("Recipient", { exact: true }).fill("Sardor");
  const batchQuantity = page.getByRole("spinbutton", {
    name: `Batch #${batch.id}`,
    exact: true,
  });
  await batchQuantity.fill("7");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("Issue saved.", { exact: true })).toBeVisible();
  const issues = await (
    await page.request.get(`/api/v1/issues/?material=${batch.material.id}`)
  ).json();
  expect(issues.count).toBe(1);
  expect(issues.results[0].quantity).toBe("7.00");
  await page.getByRole("tab", { name: "Return", exact: true }).click();
  await page
    .getByRole("combobox", { name: "Original issue", exact: true })
    .selectOption(String(issues.results[0].id));
  await batchQuantity.fill("2");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByText("Request saved. Awaiting approval.", { exact: true }),
  ).toBeVisible();
  await expect(batchQuantity).toHaveAttribute("max", "5.00");
  await page
    .getByRole("row")
    .filter({ hasText: materialName })
    .getByRole("button", { name: "Approve", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Approve", exact: true })
    .click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(
    page
      .getByRole("row")
      .filter({ hasText: materialName })
      .getByText("Approved", { exact: true }),
  ).toBeVisible();
  await page.getByRole("tab", { name: "Write-off", exact: true }).click();
  await page
    .getByRole("combobox", { name: "Material", exact: true })
    .selectOption({ label: `${materialName} · 10.00` });
  await page.getByLabel("Reason", { exact: true }).fill("Damaged sheet");
  await batchQuantity.fill("1");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByText("Request saved. Awaiting approval.", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("row")
    .filter({ hasText: materialName })
    .getByRole("button", { name: "Approve", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Approve", exact: true })
    .click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  const stock = await (
    await page.request.get(`/api/v1/stock/${batch.material.id}/`)
  ).json();
  expect(stock.quantity_on_hand).toBe("9.00");

  const projectId =
    100 +
    ["mobile-chromium", "tablet-chromium", "desktop-chromium"].indexOf(
      testInfo.project.name,
    );
  await page.goto("/#expenses");
  await expect(
    page
      .getByRole("table", { name: "New record entry", exact: true })
      .getByRole("columnheader"),
  ).toHaveCount(5);
  await page
    .locator("form")
    .getByLabel("Expense type", { exact: true })
    .selectOption("tax");
  await page.getByLabel("Amount · USD", { exact: true }).fill("12.50");
  await page
    .locator("form")
    .getByLabel("Project number", { exact: true })
    .fill(String(projectId));
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("Saved.", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Reverse expense", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByLabel("Reason", { exact: true })
    .fill("Duplicate expense");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Reverse expense", exact: true })
    .click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  const expenseRows = await (
    await page.request.get(`/api/v1/expenses/?project_id=${projectId}`)
  ).json();
  expect(expenseRows.count).toBe(2);
  expect(
    expenseRows.results.map((row: { amount: string }) => row.amount).sort(),
  ).toEqual(["-12.50", "12.50"]);

  await page.goto("/#stock");
  await page
    .getByRole("combobox", { name: "Category", exact: true })
    .selectOption({ label: "LMDF" });
  await page.getByRole("button", { name: materialName, exact: true }).click();
  await page
    .getByRole("dialog")
    .getByLabel("Min. limit", { exact: true })
    .fill("10");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Apply", exact: true })
    .click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(
    page
      .getByRole("row")
      .filter({ hasText: materialName })
      .getByText("Low stock", { exact: true }),
  ).toBeVisible();
  const minimum = await (
    await page.request.get(`/api/v1/stock/${batch.material.id}/`)
  ).json();
  expect(minimum.min_quantity).toBe("10.00");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);

  await page.goto("/#history");
  await expect(
    page.getByRole("heading", { name: "Movement history" }),
  ).toBeVisible();
  await expect(
    page
      .getByRole("row")
      .filter({ hasText: "Write-off #" })
      .filter({ hasText: materialName }),
  ).toBeVisible();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download CSV", exact: true }).click();
  expect((await download).suggestedFilename()).toBe("PROFUR-movements.csv");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
