import { expect, test } from "@playwright/test";

test("keyboard entry, empty filters and real table scrolling remain usable", async ({
  page,
}, info) => {
  test.setTimeout(60000);
  await page.goto("/");
  await page
    .getByRole("combobox", { name: "Language", exact: true })
    .selectOption("en");
  await page
    .getByLabel("Username", { exact: true })
    .fill("browser_storekeeper");
  await page
    .getByLabel("Password", { exact: true })
    .fill("browser-test-only-password");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Material receipts", exact: true }),
  ).toBeVisible();
  await page.goto("/#materials");
  await page.getByRole("heading", { name: "Materials", exact: true }).click();
  await page.keyboard.press("/");
  const search = page.getByRole("textbox", {
    name: "Search materials",
    exact: true,
  });
  await expect(search).toBeFocused();
  await search.fill("No matching material " + info.project.name);
  await search.press("/");
  await expect(search).toHaveValue(
    "No matching material " + info.project.name + "/",
  );
  await expect(page.locator(".empty")).toBeVisible();
  await page
    .locator(".empty")
    .getByRole("button", { name: "Clear filters", exact: true })
    .click();
  await expect(search).toHaveValue("");
  await page.getByRole("heading", { name: "Materials", exact: true }).click();
  await page.keyboard.press("Control+k");
  await expect(search).toBeFocused();

  const csrf = await (await page.request.get("/api/auth/csrf/")).json();
  const headers = { "X-CSRFToken": csrf.csrfToken };
  const categories = await (
    await page.request.get("/api/v1/categories/")
  ).json();
  const created = await page.request.post("/api/v1/materials/", {
    headers,
    data: {
      name: "Keyboard " + info.project.name,
      category_id: categories.results[0].id,
      unit: "sheet",
    },
  });
  expect(created.status()).toBe(201);
  const material = await created.json();
  await page.goto("/#receiving");
  const entry = page.getByRole("table", {
    name: "New record entry",
    exact: true,
  });
  await expect(entry.getByRole("columnheader")).toHaveCount(8);
  await expect(entry.getByRole("row")).toHaveCount(2);
  await expect(entry.getByLabel("Quantity", { exact: true })).toBeEditable();
  await page
    .getByRole("combobox", { name: "Material", exact: true })
    .selectOption(String(material.id));
  const quantity = page.getByRole("spinbutton", {
    name: "Quantity",
    exact: true,
  });
  const total = page.getByRole("spinbutton", {
    name: "Total amount",
    exact: true,
  });
  await quantity.fill("2");
  await total.fill("60");
  // A narrow viewport scrolls inside the entry table, never the whole page.
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await entry.getByRole("columnheader").first().scrollIntoViewIfNeeded();
  await page.screenshot({
    path: info.outputPath("tabular-entry-" + info.project.name + ".png"),
    fullPage: true,
  });
  await quantity.focus();
  await page.keyboard.down("Enter");
  await expect(total).toBeFocused();
  // Holding Enter must not skip filled fields and reach the save button.
  await page.keyboard.down("Enter");
  await expect(total).toBeFocused();
  await page.keyboard.up("Enter");
  await total.press("Enter");
  await expect(page.getByRole("textbox", { name: /Supplier/ })).toBeFocused();
  // Advancing from the last field must not activate Save on a held key.
  const note = page.getByRole("textbox", { name: /Notes/ });
  await note.fill("Keyboard verification");
  await note.focus();
  await page.keyboard.down("Enter");
  await expect(
    page.getByRole("button", { name: "Save receipt", exact: true }),
  ).toBeFocused();
  await page.keyboard.down("Enter");
  await page.keyboard.up("Enter");
  await expect(
    page.getByRole("button", { name: "Save receipt", exact: true }),
  ).toBeEnabled();
  await expect(note).toHaveValue("Keyboard verification");
  // Enter has advanced the form without creating a financial record.
  const before = await (
    await page.request.get("/api/v1/receipts/?material=" + material.id)
  ).json();
  expect(
    before.results.filter(
      (row: { material: { id: number } }) => row.material.id === material.id,
    ),
  ).toHaveLength(0);
  const response = page.waitForResponse(
    (res) =>
      res.url().endsWith("/api/v1/receipts/") &&
      res.request().method() === "POST",
  );
  await page.getByRole("textbox", { name: /Supplier/ }).press("Control+Enter");
  const saved = await response;
  expect(saved.status()).toBe(201);
  const receipt = await saved.json();
  expect(receipt.quantity_on_hand_after).toBe("2.00");
  // Enough real rows to exercise sticky headers and a genuinely overflowing viewport.
  for (let i = 0; i < 24; i++) {
    const result = await page.request.post("/api/v1/receipts/", {
      headers: { ...headers, "Idempotency-Key": crypto.randomUUID() },
      data: {
        material_id: material.id,
        quantity: "1.00",
        total_amount: "30.00",
        currency: "USD",
        received_on: receipt.received_on,
      },
    });
    expect(result.status()).toBe(201);
  }
  await page.goto("/#history");
  await expect(page.locator("tbody tr")).toHaveCount(20);
  const viewport = page.locator(".table-wrap");
  await expect(viewport).toHaveAttribute("tabindex", "0");
  await viewport.hover();
  const header = viewport.locator("th").first();
  await page.mouse.wheel(0, 800);
  await expect
    .poll(() => viewport.evaluate((node) => node.scrollTop))
    .toBeGreaterThan(0);
  const a = await header.boundingBox(),
    b = await viewport.boundingBox();
  expect(a && b && Math.abs(a.y - b.y)).toBeLessThan(3);
  const horizontal = await viewport.evaluate(
    (node) => node.scrollWidth > node.clientWidth + 1,
  );
  if (horizontal) {
    await expect(page.locator(".table-scroll-hint")).toBeVisible();
    await page.mouse.wheel(900, 0);
    await expect
      .poll(() => viewport.evaluate((node) => node.scrollLeft))
      .toBeGreaterThan(0);
    await expect(page.locator(".table-region")).toHaveClass(/scroll-left/);
  }
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: info.outputPath("warehouse-usability-" + info.project.name + ".png"),
    fullPage: true,
  });
});
