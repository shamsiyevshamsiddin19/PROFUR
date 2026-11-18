import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: "http://127.0.0.1:15173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "mobile-chromium", use: { ...devices["Pixel 7"] } }],
  webServer: [
    {
      command: `${process.env.E2E_PYTHON || "python3"} e2e/backend.py`,
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
