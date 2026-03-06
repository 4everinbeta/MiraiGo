import { test, expect } from '@playwright/test';
import { checkAccessibility } from './axe-util';

test('smoke test - landing page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/MiraiGo/i);
});

test('smoke test - accessibility audit', async ({ page }) => {
  await page.goto('/');
  await checkAccessibility(page, 'Landing Page Smoke Test');
});
