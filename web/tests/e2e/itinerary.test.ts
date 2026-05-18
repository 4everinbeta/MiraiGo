import { test, expect } from '@playwright/test';
import { checkAccessibility } from './axe-util';

test.describe('Itinerary Flow', () => {
  test('generates proposals and loads live pricing for selected trip', async ({ page }) => {
    await page.route('**/api/v1/providers/status', async (route) => {
      await route.fulfill({
        json: {
          providers: [
            {
              provider: 'amadeus',
              label: 'Amadeus',
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
              reason: null,
            },
          ],
        },
      });
    });

    await page.route('**/api/v1/itinerary/propose', async (route) => {
      await route.fulfill({
        json: {
          session_id: 'session-1',
          proposals: [
            {
              proposal_id: 'proposal-1',
              destination: 'Vancouver Island',
              destination_region_key: 'vancouver-island',
              travel_window: { start: '2026-07-01', end: '2026-07-07' },
              duration_nights: 6,
              travelers: { adults: 2, children: 1, infants: 0 },
              needs_car: true,
              cost_estimate: {
                total_estimated: 6400,
                flight_estimated: 2100,
                stay_estimated: 3400,
                car_estimated: 900,
                currency_code: 'USD',
                confidence: 'medium',
              },
              rationale: 'Nature-first summer itinerary with coastal stays.',
              within_budget: true,
              over_budget_note: null,
            },
            {
              proposal_id: 'proposal-2',
              destination: 'New England',
              destination_region_key: 'new-england',
              travel_window: { start: '2026-07-01', end: '2026-07-07' },
              duration_nights: 6,
              travelers: { adults: 2, children: 1, infants: 0 },
              needs_car: true,
              cost_estimate: {
                total_estimated: 6900,
                flight_estimated: 1800,
                stay_estimated: 3800,
                car_estimated: 1300,
                currency_code: 'USD',
                confidence: 'medium',
              },
              rationale: 'Scenic road-trip itinerary with family-friendly hotels.',
              within_budget: true,
              over_budget_note: null,
            },
          ],
          clarification_state: [],
          clarification_questions: [],
          applied_inputs: {},
          warnings: [],
        },
      });
    });

    await page.route('**/api/v1/itinerary/price', async (route) => {
      await route.fulfill({
        json: {
          search_id: 'search-1',
          proposal_id: 'proposal-1',
          flight_results: [
            {
              inventory_type: 'flight',
              provider: 'amadeus',
              provider_label: 'Amadeus',
              title: 'SEA to YVR',
              description: 'Direct flight',
              total_price: 480,
              currency: 'USD',
              redirect_url: null,
              deep_link_label: null,
              score: 88,
              price_known: true,
              price_label: null,
              origin_code: 'SEA',
              destination_code: 'YVR',
              departure_at: '2026-07-01T09:00:00',
              arrival_at: '2026-07-01T10:00:00',
              carrier_codes: ['AS'],
              stops: 0,
              duration: 'PT2H',
            },
          ],
          stay_results: [
            {
              inventory_type: 'stay',
              provider: 'expedia',
              provider_label: 'Expedia',
              title: 'Hotels in Vancouver Island',
              description: 'Open Expedia to see live hotel inventory.',
              total_price: 0,
              currency: 'USD',
              redirect_url: 'https://example.com/stay',
              deep_link_label: 'View stays on Expedia',
              score: 50,
              price_known: false,
              price_label: 'Check live rates on Expedia',
              location_label: 'Vancouver Island',
              amenities: ['wifi'],
              nightly_price: null,
              check_in: '2026-07-01',
              check_out: '2026-07-07',
            },
          ],
          car_redirect_url: 'https://example.com/cars',
          car_redirect_label: 'Search car rentals',
          provider_status: [
            {
              provider: 'amadeus',
              label: 'Amadeus',
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
              reason: null,
            },
          ],
          warnings: [],
        },
      });
    });

    await page.goto('/');
    await page
      .getByLabel(/travel prompt/i)
      .fill(
        'Given a total budget of $6000-$7500 for a family of three this summer, what are the best travel options?'
      );
    await page.getByRole('button', { name: /submit travel intent/i }).click();

    await expect(page.getByTestId('itinerary-proposal-list')).toBeVisible();
    await expect(page.getByRole('button', { name: /select this trip/i }).first()).toBeVisible();
    await checkAccessibility(page, 'Itinerary proposal list');

    await page.getByRole('button', { name: /select this trip/i }).first().click();

    await expect(page.getByTestId('itinerary-pricing-result')).toBeVisible();
    await expect(page.locator('[data-testid="itinerary-pricing-result"] article').first()).toBeVisible();
    await checkAccessibility(page, 'Itinerary pricing result');
  });
});
