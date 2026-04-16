import { expect, test } from '@playwright/test';

/**
 * CAP-04: always-on UI contract (no env skip) — exercises real DOM beyond redirect-only checks.
 */
test.describe('command center interactive (public shell)', () => {
  test('login page exposes labeled credentials and primary action', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByLabel(/username/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    // Primary action label is "Login" (see `components/Auth/Login.tsx`); loading state uses "Logging in...".
    await expect(page.getByRole('button', { name: /log ?in/i })).toBeVisible();
  });

  test('landing page serves branded shell', async ({ page }) => {
    await page.goto('/landing');
    await expect(page.locator('body')).toBeVisible();
    await expect(page.getByText(/AMAS|multi-agent|orchestration/i).first()).toBeVisible();
  });
});
