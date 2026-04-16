import { expect, test } from '@playwright/test';
import type { Page } from '@playwright/test';

type A11yScanResult = {
  unlabeledInteractive: string[];
};

async function scanBasicA11y(page: import('@playwright/test').Page): Promise<A11yScanResult> {
  return page.evaluate(() => {
    const interactive = Array.from(
      document.querySelectorAll<HTMLElement>(
        'button, a[href], input, select, textarea, [role="button"], [role="link"]',
      ),
    );
    const unlabeledInteractive: string[] = [];

    for (const el of interactive) {
      if (el.getAttribute('aria-hidden') === 'true') continue;
      // MUI Select: focusable combobox is elsewhere; nativeInput is an implementation detail.
      if (
        el.tagName === 'INPUT' &&
        (el.className || '').toString().includes('MuiSelect-nativeInput')
      ) {
        continue;
      }
      const ariaLabel = (el.getAttribute('aria-label') || '').trim();
      const title = (el.getAttribute('title') || '').trim();
      const text = (el.textContent || '').trim();
      const labelledBy = (el.getAttribute('aria-labelledby') || '').trim();
      let labelledByText = '';
      if (labelledBy) {
        labelledByText = labelledBy
          .split(/\s+/)
          .map((id) => document.getElementById(id)?.textContent?.trim() || '')
          .join(' ')
          .trim();
      }
      // MUI TextField + native <label for="…">: the visible label is not input.textContent; use DOM .labels.
      let labelFromDom = '';
      if (
        el instanceof HTMLInputElement ||
        el instanceof HTMLTextAreaElement ||
        el instanceof HTMLSelectElement
      ) {
        const ls = el.labels;
        if (ls && ls.length > 0) {
          labelFromDom = Array.from(ls)
            .map((l) => l.textContent?.trim() || '')
            .join(' ')
            .trim();
        }
      }
      const hasName = Boolean(ariaLabel || title || text || labelledByText || labelFromDom);
      if (!hasName) {
        const tag = el.tagName.toLowerCase();
        const id = (el.id || '').trim();
        const cls = (el.className || '').toString().trim().split(/\s+/).filter(Boolean).slice(0, 3).join('.');
        unlabeledInteractive.push(`${tag}${id ? `#${id}` : ''}${cls ? `.${cls}` : ''}`);
      }
    }

    return { unlabeledInteractive };
  });
}

/** Some Playwright builds omit `page.accessibility`; keep a DOM-based fallback for CI parity. */
async function assertSemanticSurfacePresent(page: Page, route: string): Promise<void> {
  const acc = (page as unknown as { accessibility?: { snapshot: () => Promise<unknown> } }).accessibility;
  if (acc && typeof acc.snapshot === 'function') {
    const snapshot = await acc.snapshot();
    expect(snapshot, `accessibility snapshot empty for ${route}`).toBeTruthy();
    return;
  }
  const semanticCount = await page.locator('main, [role="main"], nav, h1, h2, button, a[href], input').count();
  expect(semanticCount, `expected semantic/interactive elements on ${route}`).toBeGreaterThan(0);
}

test.describe('command-center accessibility sweep', () => {
  test('core routes render with accessibility tree + labeled controls', async ({ page }) => {
    const routes = ['/login', '/tasks', '/engage', '/services', '/jobs', '/live-system'];

    for (const route of routes) {
      await page.goto(route);
      await expect(page.locator('body')).toBeVisible();

      // Route may redirect to login when unauthenticated; still enforce accessibility checks on final page.
      await assertSemanticSurfacePresent(page, route);

      const scan = await scanBasicA11y(page);
      expect(
        scan.unlabeledInteractive,
        `Unlabeled interactive elements on route ${route}: ${scan.unlabeledInteractive.join(', ')}`,
      ).toEqual([]);
    }
  });
});
