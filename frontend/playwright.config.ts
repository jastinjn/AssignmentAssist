import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: 'http://localhost:5174',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      // Real FastAPI backend with Runner patched — no OpenAI calls
      command: 'uv run python test_server.py',
      cwd: '../backend',
      url: 'http://localhost:8001/api/chat/histories',
      reuseExistingServer: !process.env['CI'],
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      // Vite dev server on a dedicated E2E port, proxying /api to the test backend
      command: 'npm run dev -- --port 5174',
      url: 'http://localhost:5174',
      reuseExistingServer: !process.env['CI'],
      env: { API_TARGET: 'http://localhost:8001' },
    },
  ],
})
