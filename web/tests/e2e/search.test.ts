import { test, expect } from '@playwright/test';
import { checkAccessibility } from './axe-util';

test.describe('Search Flow', () => {
  test('performs a successful search and displays results', async ({ page }) => {
    // 1. Mock the API response
    await page.route('**/api/v1/search*', async (route) => {
      const json = {
        intent: {
          location: 'Miami',
          qualities: ['beach', 'warm'],
          dates: ['December'],
          original_query: 'Beach trip to Miami in December'
        },
        count: 2,
        results: [
          { provider: 'Expedia', text: 'Beautiful beach resort in Miami', score: 20 },
          { provider: 'Booking.com', text: 'Warm coastal hotel', score: 15 }
        ]
      };
      await route.fulfill({ json });
    });

    // 2. Navigate to home
    await page.goto('/');

    // 3. Enter search query
    const searchInput = page.getByPlaceholder(/where do you want to go/i);
    await searchInput.fill('Beach trip to Miami in December');
    
    // 4. Click search
    await page.getByRole('button', { name: /search/i }).click();

    // 5. Verify results are displayed
    await expect(page.getByText(/refined options/i)).toBeVisible();
    await expect(page.getByText('Beautiful beach resort in Miami')).toBeVisible();
    await expect(page.getByText('Expedia')).toBeVisible();
    await expect(page.getByText(/Score \/\/ 20/i)).toBeVisible();

    // 6. Accessibility audit on results page
    await checkAccessibility(page, 'Search Results Page');
  });
});
