import { expect, test, type Page } from "@playwright/test";

async function login(page: Page, user: string, screen: string) {
  await page.goto("/#" + screen);
  await page.getByRole("combobox", { name: "Language" }).selectOption("en");
  await page.getByLabel("Username").fill(user);
  await page.getByLabel("Password").fill("browser-test-only-password");
  await page.getByRole("button", { name: "Sign in" }).click();
}

test("unit price, immediate worker issue, cut piece and admin review reach the monthly report", async ({
  browser,
  page,
}, info) => {
  const material = `E2E PVC ${info.project.name}`;
  await login(page, "browser_storekeeper", "receiving");
  await expect(
    page.getByRole("heading", { name: "Material receipts", exact: true }),
  ).toBeVisible();
  const csrf = (await (await page.request.get("/api/auth/csrf/")).json())
    .csrfToken;
  const category = (
    await (await page.request.get("/api/v1/categories/?search=PVC")).json()
  ).results[0];
  const created = await page.request.post("/api/v1/materials/", {
    headers: { "X-CSRFToken": csrf },
    data: {
      name: material,
      category_id: category.id,
      unit: "sheet",
      length_cm: "200",
      width_cm: "100",
      allowed_roles: ["BROWSER_SAWYER"],
    },
  });
  expect(created.status()).toBe(201);
  const sheet = await created.json();
  await page.reload();
  await page
    .getByRole("combobox", { name: "Material", exact: true })
    .selectOption(String(sheet.id));
  await page
    .getByRole("combobox", { name: "Price entry method" })
    .selectOption("unit_price");
  await page
    .getByRole("spinbutton", { name: "Quantity", exact: true })
    .fill("3");
  await page
    .getByRole("spinbutton", { name: "Unit price", exact: true })
    .fill("28");
  await expect(page.locator("output")).toContainText("84");
  await page.getByRole("button", { name: "Save receipt" }).click();
  await expect(page.getByText(/Receipt saved/)).toBeVisible();

  const worker = await browser.newContext(info.project.use);
  const workerPage = await worker.newPage();
  try {
    await login(workerPage, "browser_sawyer", "operations");
    await expect(
      workerPage.getByRole("heading", { level: 1, name: "Take stock" }),
    ).toBeVisible();
    await workerPage
      .getByRole("combobox", { name: "Material", exact: true })
      .selectOption(String(sheet.id));
    await workerPage
      .getByRole("spinbutton", { name: "Quantity", exact: true })
      .fill("1");
    await workerPage
      .getByRole("spinbutton", { name: "Project number", exact: true })
      .fill("42");
    await workerPage.getByRole("button", { name: "Save", exact: true }).click();
    await expect(
      workerPage.getByText("Issue saved.", { exact: true }),
    ).toBeVisible();
    const issued = await (
      await workerPage.request.get(`/api/v1/issues/?material=${sheet.id}`)
    ).json();
    expect(issued.count).toBe(1);
    expect(issued.results[0].total_cost).toBeUndefined();
    const balance = await (
      await workerPage.request.get(`/api/v1/stock/${sheet.id}/`)
    ).json();
    expect(balance.quantity_on_hand).toBe("2.00");
    await workerPage.goto("/#offcuts");
    await workerPage
      .getByRole("combobox", { name: "Original issue" })
      .selectOption(String(issued.results[0].id));
    await workerPage
      .getByRole("spinbutton", { name: "Length (mm)" })
      .fill("600");
    await workerPage
      .getByRole("spinbutton", { name: "Width (mm)" })
      .fill("400");
    await workerPage.getByRole("button", { name: "Save", exact: true }).click();
    await expect(
      workerPage
        .locator("section.recent")
        .getByRole("row")
        .filter({ hasText: material }),
    ).toContainText("600.00");
  } finally {
    await worker.close();
  }

  await page.goto("/#reviews");
  const issue = page
    .getByRole("row")
    .filter({ hasText: material })
    .filter({ hasText: "Take stock" });
  await expect(issue).toContainText("Pending");
  await issue
    .getByRole("button", { name: "Mark reviewed", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Save", exact: true })
    .click();
  await expect(issue).toContainText("Reviewed");
  await page.goto("/#report");
  const report = page.getByRole("row").filter({ hasText: material });
  await expect(report).toContainText("$84.00");
  await expect(report).toContainText("$28.00");
});
