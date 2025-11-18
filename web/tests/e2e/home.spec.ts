import { test, expect } from '@playwright/test';

test('home loads and map mounts', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Next/i);
  await expect(page.getByRole('img', { name: /next\.svg/i })).toBeVisible();
  // Map canvas check
  await expect(page.locator('canvas')).toBeVisible();
});
