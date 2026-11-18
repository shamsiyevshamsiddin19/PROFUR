import { expect, test } from "@playwright/test";

test("mobile login and receipt persist one USD batch through the real API", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("combobox", { name: "Language" }).selectOption("en");
  await page.getByLabel("Username").fill("browser_storekeeper");
  await page.getByLabel("Password").fill("browser-test-only-password");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(
    page.getByRole("heading", { name: "Material receipts" }),
  ).toBeVisible();

  const material = page.getByRole("combobox", { name: "Material", exact: true });
  await expect(material.locator("option")).toHaveCount(2);
  await material.selectOption({ label: "Browser MDF · sheet" });
  await page.getByRole("spinbutton", { name: "Quantity", exact: true }).fill("15");
  await page.getByRole("spinbutton", { name: "Total amount", exact: true }).fill("450.00");
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
  const receipts = await page.request.get("/api/v1/receipts/");
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
});
