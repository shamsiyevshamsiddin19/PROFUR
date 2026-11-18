import { expect, test, type Page } from "@playwright/test";

async function loginAsStorekeeper(page: Page, lang: "uz" | "ru" | "en" = "en") {
  await page.goto("/");
  await page.getByRole("combobox", { name: "Language" }).selectOption(lang);
  await page.locator('input[name="username"]').fill("browser_storekeeper");
  await page
    .locator('input[name="password"]')
    .fill("browser-test-only-password");
  await page.locator("form.login-form button.primary").click();
}

test("receipt flow persists one USD batch through the real API", async ({
  page,
}) => {
  await loginAsStorekeeper(page, "en");
  await expect(
    page.getByRole("heading", { name: "Material receipts" }),
  ).toBeVisible();

  const material = page.getByRole("combobox", {
    name: "Material",
    exact: true,
  });
  await expect(material.locator("option")).toHaveCount(3);
  await material.selectOption({ label: "Browser MDF · sheet" });
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
  expect(Number(batch.quantity_on_hand_after)).toBeGreaterThanOrEqual(15);
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
  const receipts = await page.request.get("/api/v1/receipts/");
  const result = await receipts.json();
  expect(result.count).toBeGreaterThanOrEqual(1);
  const found = result.results.find((r: { id: number }) => r.id === batch.id);
  expect(found).toBeDefined();
  const catalogue = await page.request.get(
    `/api/v1/materials/${batch.material.id}/`,
  );
  expect(
    Number((await catalogue.json()).quantity_on_hand),
  ).toBeGreaterThanOrEqual(15);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});

test("multilingual language switching dynamically updates interface in uz, ru, and en", async ({
  page,
}) => {
  await loginAsStorekeeper(page, "uz");

  // O'zbekcha sarlavha
  await expect(
    page.getByRole("heading", { name: "Material kirimi" }),
  ).toBeVisible();

  // Rus tiliga o'tkazamiz
  await page.getByRole("combobox", { name: "Language" }).selectOption("ru");
  await expect(
    page.getByRole("heading", { name: "Поступление материалов" }),
  ).toBeVisible();

  // Ingliz tiliga o'tkazamiz
  await page.getByRole("combobox", { name: "Language" }).selectOption("en");
  await expect(
    page.getByRole("heading", { name: "Material receipts" }),
  ).toBeVisible();
});

test("long material names render cleanly without layout overflow across viewports", async ({
  page,
}) => {
  await loginAsStorekeeper(page, "en");
  await expect(
    page.getByRole("heading", { name: "Material receipts" }),
  ).toBeVisible();

  const material = page.getByRole("combobox", {
    name: "Material",
    exact: true,
  });
  // Uzun nomli materialni tanlaymiz
  await material.selectOption({
    label:
      "Akril panel yuqori zichlikdagi namlikka chidamli maxsus qoplama 2800x1220x18mm · sheet",
  });

  // Gorizontal siljish (overflow) yo'qligini tekshiramiz
  const noOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth <= window.innerWidth,
  );
  expect(noOverflow).toBe(true);
});
