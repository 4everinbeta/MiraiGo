import { test, expect } from '@playwright/test';
import { checkAccessibility } from './axe-util';

test.describe('Search Flow', () => {
  test('performs a successful search and displays results', async ({ page }) => {
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
      const json = {
        search_id: 'search-1',
        query: 'Barcelona trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Barcelona',
          origin: 'Denver',
          date_range: { start: '2026-05-03', end: '2026-05-08' },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [
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
        warnings: [],
        results: [
          {
            inventory_type: 'stay',
            provider: 'expedia',
            provider_label: 'Expedia',
            title: 'Hotels in Barcelona',
            description: 'Open Expedia to see live hotel inventory and current partner pricing.',
            total_price: 0,
            currency: 'USD',
            redirect_url: 'https://example.com/stay',
            deep_link_label: 'View stays on Expedia',
            score: 50,
            price_known: false,
            price_label: 'Check live rates on Expedia',
            location_label: 'Barcelona',
            amenities: ['wifi'],
            nightly_price: null,
            check_in: '2026-05-03',
            check_out: '2026-05-08',
          },
          {
            inventory_type: 'flight',
            provider: 'duffel',
            provider_label: 'Duffel',
            title: 'DEN to BCN',
            description: 'Flight option',
            total_price: 640,
            currency: 'USD',
            redirect_url: null,
            deep_link_label: null,
            score: 90,
            price_known: true,
            price_label: null,
            origin_code: 'DEN',
            destination_code: 'BCN',
            departure_at: '2026-05-03T09:30:00',
            arrival_at: '2026-05-03T20:15:00',
            carrier_codes: ['TP'],
            stops: 1,
            duration: 'PT10H45M',
          },
        ],
      };
      await route.fulfill({ json });
    });

    await page.goto('/');
    await page.getByLabel(/travel prompt/i).fill('Barcelona trip');
    await page.getByRole('button', { name: /submit travel intent/i }).click();
    await expect(page.getByText(/hotels in barcelona/i)).toBeVisible();
    await expect(page.getByText(/flight results/i)).toBeVisible();
    await checkAccessibility(page, 'Search Results Page');
  });
});
