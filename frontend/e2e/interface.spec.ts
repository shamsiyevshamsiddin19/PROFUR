import { expect, test, type Page } from "@playwright/test";

async function loginAsStorekeeper(page: Page, lang: "uz" | "ru" | "en" = "en") {
  await page.goto("/#receiving");
  await page.getByRole("combobox", { name: "Language" }).selectOption(lang);
  await page.locator('input[name="username"]').fill("browser_storekeeper");
  await page
    .locator('input[name="password"]')
    .fill("browser-test-only-password");
  await page.locator("form.login-form button.primary").click();
}

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
