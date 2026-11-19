import { expect, test } from "@playwright/test";
test("appearance preferences persist without changing warehouse currency or permissions", async ({
  page,
}, info) => {
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
  await page.goto("/#settings");
  if (info.project.name === "mobile-chromium")
    await page.setViewportSize({ width: 320, height: 800 });
  await expect(
    page.getByRole("heading", { name: "Settings", exact: true }),
  ).toBeVisible();
  await page.getByRole("radio", { name: "Indigo", exact: true }).check();
  await page.getByRole("button", { name: "Compact", exact: true }).click();
  await page.getByRole("checkbox", { name: /Reduce motion/ }).check();
  await page.reload();
  await expect(
    page.getByRole("radio", { name: "Indigo", exact: true }),
  ).toBeChecked();
  await expect(
    page.getByRole("button", { name: "Compact", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("html")).toHaveAttribute("data-motion", "reduced");
  await expect(page.locator("html")).toHaveAttribute("data-accent", "indigo");
  await expect(page.locator("html")).toHaveAttribute("data-density", "compact");
  await page
    .getByRole("combobox", { name: "Interface language", exact: true })
    .selectOption("ru");
  await expect(
    page.getByRole("heading", { name: "Настройки", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("combobox", { name: "Language", exact: true })
    .selectOption("en");
  await page
    .getByRole("button", { name: "Reset appearance", exact: true })
    .click();
  await expect(
    page.getByRole("radio", { name: "Emerald", exact: true }),
  ).toBeChecked();
  await expect(page.locator("html")).toHaveAttribute(
    "data-density",
    "comfortable",
  );
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  if (info.project.name === "desktop-chromium")
    await expect(
      page.getByRole("link", { name: "Settings", exact: true }),
    ).toBeInViewport({ ratio: 1 });
  await page.screenshot({
    path: info.outputPath("settings-" + info.project.name + ".png"),
    fullPage: true,
  });
});
