import { test, expect } from '@playwright/test'

test('user clicks a shortcut button and receives a response in the chat', async ({ page }) => {
  await page.goto('/')

  // ── 1. Shortcut buttons are visible in the empty state ────────────────────
  const main = page.getByRole('main')
  const shortcut = main.getByRole('button', { name: 'Which of my students need help?' })
  await expect(shortcut).toBeVisible()

  // ── 2. Click the shortcut button ─────────────────────────────────────────
  await shortcut.click()

  // ── 3. User message appears in the chat (button text sent as message) ─────
  await expect(main.getByText('Which of my students need help?')).toBeVisible()

  // ── 4. Shortcut buttons disappear once a conversation is active ───────────
  await expect(shortcut).not.toBeVisible()

  // ── 5. Mocked response arrives from the backend ───────────────────────────
  await expect(main.getByText(/Alice Chen/)).toBeVisible({ timeout: 10_000 })

  // ── 6. Input is empty (no text was placed in the textarea) ────────────────
  await expect(page.getByPlaceholder(/ask about your students/i)).toHaveValue('')

  // ── 7. Conversation appears in the sidebar ────────────────────────────────
  await expect(
    page.locator('[data-sidebar="menu-button"]', { hasText: 'Which of my students need help?' }).first()
  ).toBeVisible({ timeout: 5_000 })
})

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

  // Scope chat assertions to the main content area to avoid matching sidebar items
  const main = page.getByRole('main')

  // ── 4. User message appears in the chat ────────────────────────────────────
  await expect(main.getByText('Which students need the most support?')).toBeVisible()

  // ── 5. Mocked response arrives from the backend and renders in a bubble ────
  // Assert on a stable substring from the mock response in test_server.py
  await expect(main.getByText(/Alice Chen/)).toBeVisible({ timeout: 10_000 })

  // ── 6. Input is cleared after sending ──────────────────────────────────────
  await expect(input).toHaveValue('')

  // ── 7. Conversation appears in the sidebar (DB write + re-fetch confirmed) ─
  await expect(
    page.locator('[data-sidebar="menu-button"]', { hasText: 'Which students need the most support?' }).first()
  ).toBeVisible({ timeout: 5_000 })
})
