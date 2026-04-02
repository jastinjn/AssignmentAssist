import { test, expect } from '@playwright/test'

// Must match MOCK_RESPONSE in backend/test_server.py
const MOCK_RESPONSE =
  'Based on recent scores and comments, Alice Chen needs the most support — she scored below the class average on both Knowledge & Understanding and Analysis & Argument.'

test('user sends a message and receives a response in the chat', async ({ page }) => {
  await page.goto('/')

  // ── 1. Locate the chat input ───────────────────────────────────────────────
  const input = page.getByPlaceholder(/ask about your students/i)
  await expect(input).toBeVisible()

  // ── 2. Click the input and type a message ─────────────────────────────────
  await input.click()
  await input.fill('Which students need the most support?')

  // ── 3. Submit by pressing Enter ────────────────────────────────────────────
  await input.press('Enter')

  // ── 4. User message appears in the chat ────────────────────────────────────
  await expect(page.getByText('Which students need the most support?')).toBeVisible()

  // ── 5. Mocked response arrives from the backend and renders in a bubble ────
  await expect(page.getByText(MOCK_RESPONSE)).toBeVisible({ timeout: 10_000 })

  // ── 6. Input is cleared after sending ──────────────────────────────────────
  await expect(input).toHaveValue('')
})
