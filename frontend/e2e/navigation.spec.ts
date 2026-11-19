import { expect, test } from "@playwright/test";
for (const role of [
  "warehouse",
  "procurement",
  "production",
  "accountant",
  "worker",
] as const) {
  test(
    role + " sees only permitted menus and actions",
    async ({ page }, info) => {
      await page.goto("/");
      await page.getByRole("combobox", { name: "Language" }).selectOption("en");
      await page
        .getByLabel("Username", { exact: true })
        .fill("browser_" + role);
      await page
        .getByLabel("Password", { exact: true })
        .fill("browser-test-only-password");
      await page.getByRole("button", { name: "Sign in", exact: true }).click();
      await expect(
        page.getByRole("heading", { name: "Home", exact: true }),
      ).toBeVisible();
      const toggle = page.getByRole("button", {
        name: "Open menu",
        exact: true,
      });
      const mobile = await toggle.isVisible();
      if (mobile) await toggle.click();
      const nav = page.getByRole("navigation");
      const receives = role === "warehouse" || role === "procurement";
      await expect(
        nav.getByRole("link", { name: "Material receipts", exact: true }),
      ).toHaveCount(receives ? 1 : 0);
      await expect(
        nav.getByRole("link", { name: "Administration", exact: true }),
      ).toHaveCount(0);
      await expect(
        nav.getByRole("link", { name: "Expenses", exact: true }),
      ).toHaveCount(role === "accountant" ? 1 : 0);
      await expect(
        nav.getByRole("link", { name: "Stock", exact: true }),
      ).toHaveCount(
        ["warehouse", "procurement", "production"].includes(role) ? 1 : 0,
      );
      if (mobile) {
        // Keyboard focus stays inside the drawer, Escape restores the opener.
        await page
          .getByRole("button", { name: "Sign out", exact: true })
          .focus();
        await page.keyboard.press("Tab");
        await expect(page.locator("aside .brand")).toBeFocused();
        await page.keyboard.press("Escape");
        await expect(toggle).toBeFocused();
        await expect(page.locator(".workspace")).not.toHaveAttribute(
          "inert",
          "",
        );
      }
      await page.screenshot({
        path: info.outputPath(
          "role-home-" + role + "-" + info.project.name + ".png",
        ),
        fullPage: true,
      });
      const denied = await page.request.get("/api/auth/users/");
      expect(denied.status()).toBe(403);
      const csrf = await (await page.request.get("/api/auth/csrf/")).json();
      const writeDenied = await page.request.post("/api/v1/receipts/", {
        headers: { "X-CSRFToken": csrf.csrfToken },
        data: {},
      });
      expect(writeDenied.status()).toBe(receives ? 400 : 403);
      await page.goto("/#receiving");
      if (receives) {
        await expect(
          page.getByRole("heading", { name: "Material receipts", exact: true }),
        ).toBeVisible();
        await expect(
          page.getByRole("button", { name: "Save receipt", exact: true }),
        ).toHaveCount(1);
      } else {
        await expect(
          page.getByRole("link", { name: "Back to home", exact: true }),
        ).toBeVisible();
        await expect(
          page.getByRole("button", { name: "Save receipt", exact: true }),
        ).toHaveCount(0);
      }
      if (role === "production") {
        await page.goto("/#operations");
        await expect(
          page.getByRole("tab", { name: "Issue", exact: true }),
        ).toBeVisible();
        await expect(
          page.getByRole("tab", { name: "Return", exact: true }),
        ).toBeVisible();
        await expect(
          page.getByRole("tab", { name: "Write-off", exact: true }),
        ).toHaveCount(0);
      }
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
    },
  );
}
