import { test, expect } from '@playwright/test';
import { checkAccessibility } from './axe-util';

test.describe('Error State Regression', () => {
  test('displays error message on backend failure', async ({ page }) => {
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

    await page.route('**/api/v1/search', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal Server Error' }),
      });
    });

    await page.goto('/');
    await page.getByLabel(/travel prompt/i).fill('Trip to Barcelona');
    await page.getByRole('button', { name: /submit travel intent/i }).click();
    await expect(page.getByText(/search request failed/i)).toBeVisible();
    await checkAccessibility(page, 'Error State Page');
  });
});
