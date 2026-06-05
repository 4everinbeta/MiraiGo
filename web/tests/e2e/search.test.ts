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

    await page.route('**/api/v1/orchestrator/turn', async (route) => {
      const json = {
        session_id: 'session-search',
        response_type: 'packages',
        markdown: 'Here is your travel suggestion packages.',
        open_questions: [],
        candidate_destinations: [],
        packages: [],
        itineraries: [],
        disclaimers: [],
        executed_agents: ['presenter'],
        search_response: {
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
          recommendation_packages: [
            {
              bundle_id: 'pkg-1',
              destination: 'Barcelona',
              score: 92,
              rationale: ['Matches your key constraints with the strongest available inventory.'],
              rationale_text: 'Matches your key constraints with the strongest available inventory.',
              reason_tags: ['timeline match', 'budget fit', 'top provider score 90'],
              hard_constraint_status: { destination: true, timeline: true, budget: true },
              fallback_level: 'high-fit',
            },
          ],
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
        }
      };
      await route.fulfill({ json });
    });

    await page.goto('/');
    await page.getByLabel(/travel prompt/i).fill('Barcelona trip');
    await page.getByRole('button', { name: /submit travel intent/i }).click();
    await expect(page.getByText(/top suggestions/i)).toBeVisible();
    await expect(page.getByText(/high fit/i)).toBeVisible();
    await expect(page.getByText(/hotels in barcelona/i)).toBeVisible();
    await expect(page.getByText(/flight results/i)).toBeVisible();
    await checkAccessibility(page, 'Search Results Page');
  });

  test('allows sorting and filtering stay results', async ({ page }) => {
    await page.route('**/api/v1/providers/status', async (route) => {
      await route.fulfill({
        json: {
          providers: [
            {
              provider: 'expedia',
              label: 'Expedia',
              configured: true,
              healthy: true,
              inventory_types: ['stay'],
              reason: null,
            },
          ],
        },
      });
    });

    await page.route('**/api/v1/orchestrator/turn', async (route) => {
      const json = {
        session_id: 'session-search-2',
        response_type: 'packages',
        markdown: 'Here are stay options.',
        open_questions: [],
        candidate_destinations: [],
        packages: [],
        itineraries: [],
        disclaimers: [],
        executed_agents: ['presenter'],
        search_response: {
          search_id: 'search-2',
          query: 'stays in Paris',
          requested_inventory: ['stay'],
          applied_filters: {
            destination: 'Paris',
          },
          provider_status: [
            {
              provider: 'expedia',
              label: 'Expedia',
              configured: true,
              healthy: true,
              inventory_types: ['stay'],
              reason: null,
            },
          ],
          warnings: [],
          recommendation_packages: [],
          results: [
            {
              inventory_type: 'stay',
              provider: 'expedia',
              provider_label: 'Expedia',
              title: 'Luxury Stay Paris',
              description: 'Luxury hotel in center',
              total_price: 500,
              currency: 'USD',
              redirect_url: 'https://example.com/stay1',
              deep_link_label: 'View Stay',
              score: 95,
              price_known: true,
              price_label: '$500/night',
              location_label: 'Paris',
              amenities: ['Gym', 'Pool'],
              nightly_price: 500,
              check_in: '2026-05-03',
              check_out: '2026-05-08',
              rating: '4.9',
            },
            {
              inventory_type: 'stay',
              provider: 'expedia',
              provider_label: 'Expedia',
              title: 'Cozy Stay Paris',
              description: 'Cozy apartment',
              total_price: 150,
              currency: 'USD',
              redirect_url: 'https://example.com/stay2',
              deep_link_label: 'View Stay',
              score: 90,
              price_known: true,
              price_label: '$150/night',
              location_label: 'Paris',
              amenities: ['WiFi', 'Pool'],
              nightly_price: 150,
              check_in: '2026-05-03',
              check_out: '2026-05-08',
              rating: '4.8',
            },
            {
              inventory_type: 'stay',
              provider: 'expedia',
              provider_label: 'Expedia',
              title: 'Budget Stay Paris',
              description: 'Budget room',
              total_price: 300,
              currency: 'USD',
              redirect_url: 'https://example.com/stay3',
              deep_link_label: 'View Stay',
              score: 85,
              price_known: true,
              price_label: '$300/night',
              location_label: 'Paris',
              amenities: ['WiFi'],
              nightly_price: 300,
              check_in: '2026-05-03',
              check_out: '2026-05-08',
              rating: '3.5',
            },
          ],
        }
      };
      await route.fulfill({ json });
    });

    await page.goto('/');
    await page.getByLabel(/travel prompt/i).fill('stays in Paris');
    await page.getByRole('button', { name: /submit travel intent/i }).click();

    // Verify initial load has all stays
    await expect(page.getByText('Luxury Stay Paris')).toBeVisible();
    await expect(page.getByText('Cozy Stay Paris')).toBeVisible();
    await expect(page.getByText('Budget Stay Paris')).toBeVisible();

    // 1. Filter by amenities (WiFi checkbox)
    const wifiCheckbox = page.locator('[data-testid="amenity-wifi-checkbox"]');
    await wifiCheckbox.click();
    // WiFi stays should be visible, others hidden
    await expect(page.getByText('Cozy Stay Paris')).toBeVisible();
    await expect(page.getByText('Budget Stay Paris')).toBeVisible();
    await expect(page.getByText('Luxury Stay Paris')).toBeHidden();

    // 2. Filter by max price threshold (set price slider to 200)
    const priceSlider = page.locator('[data-testid="stays-price-slider"]');
    await priceSlider.fill('200');
    // Cozy Stay is 150 (visible), Budget Stay is 300 (hidden)
    await expect(page.getByText('Cozy Stay Paris')).toBeVisible();
    await expect(page.getByText('Budget Stay Paris')).toBeHidden();

    // 3. Filter by rating threshold (set to 4.0+ Stars button)
    // First, let's reset the WiFi checkbox and price slider so everything is visible
    await wifiCheckbox.click(); // uncheck wifi
    await priceSlider.fill('500'); // reset max price
    await expect(page.getByText('Luxury Stay Paris')).toBeVisible();
    await expect(page.getByText('Cozy Stay Paris')).toBeVisible();
    await expect(page.getByText('Budget Stay Paris')).toBeVisible();

    // Now click 4.0+ Stars rating threshold button
    const starsButton = page.getByRole('button', { name: '4.0+ Stars' });
    await starsButton.click();
    // Luxury (4.9) and Cozy (4.8) should be visible, Budget (3.5) should be hidden
    await expect(page.getByText('Luxury Stay Paris')).toBeVisible();
    await expect(page.getByText('Cozy Stay Paris')).toBeVisible();
    await expect(page.getByText('Budget Stay Paris')).toBeHidden();

    // 4. Sort Stays (by Price: Low to High)
    const sortSelect = page.locator('[data-testid="stays-sort-select"]');
    await sortSelect.selectOption('price');
    
    // Cozy (150) should come before Luxury (500)
    const staysContainer = page.locator('.grid.gap-4').first();
    const textContent = await staysContainer.innerText();
    const cozyIndex = textContent.indexOf('Cozy Stay Paris');
    const luxuryIndex = textContent.indexOf('Luxury Stay Paris');
    expect(cozyIndex).toBeLessThan(luxuryIndex);
  });
});
