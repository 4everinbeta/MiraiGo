import { expect, test } from '@playwright/test'

test.describe('Clarification flow', () => {
  test('handles iterative follow-up answers, recap edits, and continue CTA handoff', async ({
    page,
  }) => {
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
          ],
        },
      })
    })

    const capturedBodies: Array<Record<string, unknown>> = []
    let searchTurn = 0

    await page.route('**/api/v1/search', async (route) => {
      const body = route.request().postDataJSON() as Record<string, unknown>
      capturedBodies.push(body)
      searchTurn += 1

      if (searchTurn === 1) {
        await route.fulfill({
          json: {
            search_id: 'search-1',
            query: body.query ?? '',
            requested_inventory: ['stay', 'flight'],
            applied_filters: {
              destination: 'Japan',
              origin: null,
              date_range: { start: '2026-06-01', end: '2026-06-10' },
              travelers: { adults: 2, children: 0, infants: 0 },
              stay_filters: { amenities: ['wifi'] },
              flight_filters: { nonstop: false },
            },
            provider_status: [],
            warnings: [],
            results: [],
            clarification_state: {
              destination: {
                slot: 'destination',
                value_label: 'Japan',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              timeline: {
                slot: 'timeline',
                value_label: 'June 2026',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              trip_length: {
                slot: 'trip_length',
                value_label: null,
                confidence: 0.1,
                ambiguous: true,
                explicit_unknown: false,
                source: 'extracted',
              },
              budget: {
                slot: 'budget',
                value_label: '$2,000',
                confidence: 0.8,
                ambiguous: false,
                explicit_unknown: false,
                source: 'extracted',
              },
              next_question: {
                slot: 'trip_length',
                prompt: 'How many days should this trip be?',
                helper_text: 'A rough estimate is fine.',
              },
              recap: {
                chips: [
                  {
                    slot: 'destination',
                    label: 'Destination',
                    value_label: 'Japan',
                    editable: true,
                    explicit_unknown: false,
                  },
                ],
                continue_label: 'Continue to Recommendations',
              },
              all_critical_slots_resolved: false,
            },
          },
        })
        return
      }

      if (searchTurn === 2) {
        await route.fulfill({
          json: {
            search_id: 'search-2',
            query: body.query ?? '',
            requested_inventory: ['stay', 'flight'],
            applied_filters: {
              destination: 'Japan',
              origin: null,
              date_range: { start: '2026-06-01', end: '2026-06-10' },
              travelers: { adults: 2, children: 0, infants: 0 },
              stay_filters: { amenities: ['wifi'] },
              flight_filters: { nonstop: false },
            },
            provider_status: [],
            warnings: [],
            results: [],
            clarification_state: {
              destination: {
                slot: 'destination',
                value_label: 'Japan',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              timeline: {
                slot: 'timeline',
                value_label: 'June 2026',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              trip_length: {
                slot: 'trip_length',
                value_label: '7 days',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              budget: {
                slot: 'budget',
                value_label: '$2,000',
                confidence: 0.8,
                ambiguous: false,
                explicit_unknown: false,
                source: 'extracted',
              },
              next_question: {
                slot: 'budget',
                prompt: 'What budget should we target?',
                helper_text: 'A rough range works.',
              },
              recap: {
                chips: [
                  {
                    slot: 'destination',
                    label: 'Destination',
                    value_label: 'Japan',
                    editable: true,
                    explicit_unknown: false,
                  },
                ],
                continue_label: 'Continue to Recommendations',
              },
              all_critical_slots_resolved: false,
            },
          },
        })
        return
      }

      if (searchTurn === 3) {
        await route.fulfill({
          json: {
            search_id: 'search-3',
            query: body.query ?? '',
            requested_inventory: ['stay', 'flight'],
            applied_filters: {
              destination: 'Seoul',
              origin: null,
              date_range: { start: '2026-06-01', end: '2026-06-10' },
              travelers: { adults: 2, children: 0, infants: 0 },
              stay_filters: { amenities: ['wifi'] },
              flight_filters: { nonstop: false },
            },
            provider_status: [],
            warnings: [],
            results: [],
            clarification_state: {
              destination: {
                slot: 'destination',
                value_label: 'Seoul',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              timeline: {
                slot: 'timeline',
                value_label: 'June 2026',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              trip_length: {
                slot: 'trip_length',
                value_label: '7 days',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              budget: {
                slot: 'budget',
                value_label: '$2,200',
                confidence: 1,
                ambiguous: false,
                explicit_unknown: false,
                source: 'user',
              },
              next_question: null,
              recap: {
                chips: [
                  {
                    slot: 'destination',
                    label: 'Destination',
                    value_label: 'Seoul',
                    editable: true,
                    explicit_unknown: false,
                  },
                  {
                    slot: 'trip_length',
                    label: 'Trip Length',
                    value_label: '7 days',
                    editable: true,
                    explicit_unknown: false,
                  },
                ],
                continue_label: 'Continue to Recommendations',
              },
              all_critical_slots_resolved: true,
            },
          },
        })
        return
      }

      await route.fulfill({
        json: {
          search_id: 'search-4',
          query: body.query ?? '',
          requested_inventory: ['stay', 'flight'],
          applied_filters: {
            destination: 'Seoul',
            origin: null,
            date_range: { start: '2026-06-01', end: '2026-06-10' },
            travelers: { adults: 2, children: 0, infants: 0 },
            stay_filters: { amenities: ['wifi'] },
            flight_filters: { nonstop: false },
          },
          provider_status: [],
          warnings: [],
          results: [
            {
              inventory_type: 'stay',
              provider: 'expedia',
              provider_label: 'Expedia',
              title: 'Seoul stay options',
              description: 'Redirect to partner',
              total_price: 0,
              currency: 'USD',
              redirect_url: 'https://example.com/stay',
              deep_link_label: 'View stays on Expedia',
              score: 80,
              price_known: false,
              price_label: 'Check live rates on Expedia',
              location_label: 'Seoul',
              amenities: ['wifi'],
              nightly_price: null,
              check_in: '2026-06-01',
              check_out: '2026-06-10',
            },
          ],
          clarification_state: null,
        },
      })
    })

    await page.goto('/')

    await page.getByLabel('Travel prompt').fill('Warm trip in June with moderate spend')
    await page.getByRole('button', { name: 'Submit travel intent' }).click()

    await expect(
      page.getByRole('heading', { name: 'How many days should this trip be?' })
    ).toBeVisible()

    await page.getByLabel('Your answer').fill('7 days')
    await page.getByRole('button', { name: 'Submit answer' }).click()
    await expect(page.getByRole('heading', { name: 'What budget should we target?' })).toBeVisible()

    await page.getByRole('button', { name: 'Edit Destination' }).click()
    await page.getByLabel('Update Destination').fill('Seoul')
    await page.getByRole('button', { name: 'Save Destination edit' }).click()

    await expect(
      page.getByRole('button', { name: 'Continue to Recommendations' })
    ).toBeVisible()
    await page.getByRole('button', { name: 'Continue to Recommendations' }).click()
    await expect(page.getByText(/seoul stay options/i)).toBeVisible()

    expect(capturedBodies).toHaveLength(4)
    expect(capturedBodies[0]).toMatchObject({
      query: 'Warm trip in June with moderate spend',
    })
    expect(capturedBodies[1]).toMatchObject({
      clarification_answer: {
        slot: 'trip_length',
        answer_text: '7 days',
        explicit_unknown: false,
      },
      destination: 'Japan',
      date_range: { start: '2026-06-01', end: '2026-06-10' },
    })
    expect(capturedBodies[2]).toMatchObject({
      recap_edit: {
        slot: 'destination',
        edited_value: 'Seoul',
        explicit_unknown: false,
      },
      date_range: { start: '2026-06-01', end: '2026-06-10' },
    })
    expect(capturedBodies[3]).toMatchObject({
      destination: 'Seoul',
      date_range: { start: '2026-06-01', end: '2026-06-10' },
    })
  })
})
