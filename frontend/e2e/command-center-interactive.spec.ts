import { expect, test } from '@playwright/test';

/**
 * CAP-04: always-on UI contract (no env skip) — exercises real DOM beyond redirect-only checks.
 */
test.describe('command center interactive (public shell)', () => {
  test('login page exposes labeled credentials and primary action', async ({ page }) => {
    await page.goto('/login');
    // Allow both accessible label and placeholder-based fallback (some MUI variants render label differently in E2E).
    await expect(
      page.getByLabel(/username/i).or(page.getByPlaceholder(/username/i)).first()
    ).toBeVisible();
    await expect(
      page.getByLabel(/password/i).or(page.getByPlaceholder(/password/i)).first()
    ).toBeVisible();
    // Primary action label is "Login" (see `components/Auth/Login.tsx`); loading state uses "Logging in...".
    await expect(page.getByRole('button', { name: /log ?in/i })).toBeVisible();
  });

  test('landing page serves branded shell', async ({ page }) => {
    await page.goto('/landing');
    // Some shells start with a blocking overlay/spinner; wait for the main content to become visible.
    await expect(page.locator('body')).toBeAttached();
    await expect(page.getByText(/AMAS|multi-agent|orchestration/i).first()).toBeVisible();
  });
});
