import { Page, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

export async function checkAccessibility(page: Page, testName: string) {
  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();

  // If there are violations, we'll log them clearly for debugging
  if (accessibilityScanResults.violations.length > 0) {
    console.error(`Accessibility violations found in "${testName}":`);
    console.error(JSON.stringify(accessibilityScanResults.violations, null, 2));
  }

  expect(accessibilityScanResults.violations).toEqual([]);
}
