import { test, expect } from '@playwright/test';
import { checkAccessibility } from './axe-util';

test.describe('Error State Regression', () => {
  test('displays error message on backend failure', async ({ page }) => {
    // 1. Mock a 500 error
    await page.route('**/api/v1/search*', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal Server Error' }),
      });
    });

    // 2. Navigate to home
    await page.goto('/');

    // 3. Perform search
    const searchInput = page.getByPlaceholder(/where do you want to go/i);
    await searchInput.fill('Trigger error');
    await page.getByRole('button', { name: /search/i }).click();

    // 4. Verify error message
    await expect(page.getByText(/something went wrong|connection issue/i)).toBeVisible();

    // 5. Accessibility audit
    await checkAccessibility(page, 'Error State Page');
  });
});
