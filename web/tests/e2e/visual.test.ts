import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('landing page visual snapshot', async ({ page }) => {
    await page.goto('/');
    // Hide dynamic/unpredictable content if any (none for now)
    await expect(page).toHaveScreenshot('landing-page.png', {
      fullPage: true,
    });
  });

  test('search results visual snapshot', async ({ page }) => {
    // Mock API for consistent results
    await page.route('**/api/v1/search*', async (route) => {
      const json = {
        intent: { location: 'Miami', qualities: ['beach'], dates: ['summer'] },
        count: 1,
        results: [
          { provider: 'Expedia', text: 'Beautiful beach resort', score: 10 }
        ]
      };
      await route.fulfill({ json });
    });

    await page.goto('/');
    await page.getByPlaceholder(/where do you want to go/i).fill('Miami');
    await page.getByRole('button', { name: /search/i }).click();
    
    // Wait for results to be visible before snapshot
    await expect(page.getByText(/refined options/i)).toBeVisible();
    
    await expect(page).toHaveScreenshot('search-results.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });
});
