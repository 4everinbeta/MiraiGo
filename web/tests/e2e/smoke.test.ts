import { test, expect } from '@playwright/test';
import { checkAccessibility } from './axe-util';

test('smoke test - landing page loads', async ({ page }) => {
  await page.route('**/api/v1/providers/status', async (route) => {
    await route.fulfill({
        json: {
          providers: [
            {
              provider: 'duffel',
              label: 'Duffel',
              configured: true,
              healthy: true,
              inventory_types: ['flight'],
              reason: null,
            },
            {
              provider: 'expedia',
              label: 'Expedia',
              configured: true,
              healthy: true,
              inventory_types: ['stay'],
              reason: 'Redirect-only hotel handoff. Live rates open on Expedia.',
            },
          ],
        },
    });
  });
  await page.goto('/');
  await expect(page).toHaveTitle(/MiraiGo/i);
  await expect(page.getByText(/miraigo mvp/i)).toBeVisible();
  await expect(page.getByText(/what this version does/i)).toBeVisible();
  await expect(page.getByRole('button', { name: /submit travel intent/i })).toBeVisible();
});

test('smoke test - accessibility audit', async ({ page }) => {
  await page.route('**/api/v1/providers/status', async (route) => {
    await route.fulfill({
        json: {
          providers: [
            {
              provider: 'duffel',
              label: 'Duffel',
              configured: false,
              healthy: false,
              inventory_types: ['flight'],
              reason: 'Duffel access token is not configured.',
            },
            {
              provider: 'expedia',
              label: 'Expedia',
              configured: true,
              healthy: true,
              inventory_types: ['stay'],
              reason: 'Redirect-only hotel handoff. Live rates open on Expedia.',
            },
          ],
        },
    });
  });
  await page.goto('/');
  await checkAccessibility(page, 'Landing Page Smoke Test');
});
