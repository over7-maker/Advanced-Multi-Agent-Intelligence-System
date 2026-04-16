import { expect, test } from '@playwright/test';

/**
 * CAP-04: always-on UI contract (no env skip) — exercises real DOM beyond redirect-only checks.
 */
test.describe('command center interactive (public shell)', () => {
  test('login page exposes labeled credentials and primary action', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');

    // Stable contract: login page renders a form with at least two inputs.
    await expect(page.getByRole('heading', { name: /amas login/i })).toBeVisible({ timeout: 15000 });
    await expect(page.locator('form')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('input')).toHaveCount(2, { timeout: 15000 });

    // Primary action label is "Login" (see `components/Auth/Login.tsx`); loading state uses "Logging in...".
    await expect(page.getByRole('button', { name: /log ?in/i })).toBeVisible();
  });

  test('landing page serves branded shell', async ({ page }) => {
    await page.goto('/landing', { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');
    await expect(page.getByText(/AMAS/i).first()).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/orchestration/i).first()).toBeVisible({ timeout: 15000 });
  });
});
