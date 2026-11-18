import fs from "node:fs";
import { defineConfig, devices } from "@playwright/test";

const localChromium =
  !process.env.CI && fs.existsSync("/usr/bin/chromium")
    ? "/usr/bin/chromium"
    : undefined;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: "http://127.0.0.1:15173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    ...(localChromium
      ? { launchOptions: { executablePath: localChromium } }
      : {}),
  },
  projects: [
    { name: "mobile-chromium", use: { ...devices["Pixel 7"] } },
    {
      name: "tablet-chromium",
      use: { viewport: { width: 768, height: 1024 } },
    },
    {
      name: "desktop-chromium",
      use: { viewport: { width: 1280, height: 800 } },
    },
  ],
  webServer: [
    {
      command: `${process.env.E2E_PYTHON || "../.venv/bin/python"} e2e/backend.py`,
      url: "http://127.0.0.1:18110/api/health/",
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command:
        "npm run dev -- --config e2e/vite.config.ts --port 15173 --strictPort",
      url: "http://127.0.0.1:15173",
      reuseExistingServer: false,
    },
  ],
});
