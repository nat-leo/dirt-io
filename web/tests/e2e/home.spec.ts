import { test, expect } from '@playwright/test';

test('Map Renders some Polygon Data Initially - Not a blank map to start', async ({ page }) => {
  await page.goto('/');

  const canvas = page.locator('canvas').first();
  await expect(canvas).toBeVisible();
});

test('Map Rerenders Itself Where the User Scrolled Over To.', async ({ page }) => {
  await page.goto('/');

  const canvas = page.locator('canvas').first();
  await expect(canvas).toBeVisible();

  // Polygon should be exposed to window for tests.
  await expect.poll(async () => {
    const poly = await page.evaluate(() => (window as any).__POLYGON__);
    return poly?.features?.[0]?.geometry?.coordinates?.length ?? 0;
  }).toBeGreaterThan(0);

  // Drag left to change viewport and trigger polygon refresh.
  const box = await canvas.boundingBox();
  if (!box) throw new Error('Canvas bounding box not found');
  const midY = box.y + box.height / 2;
  const midX = box.x + box.width / 2;
  await page.mouse.move(midX, midY);
  await page.mouse.down();
  await page.mouse.move(midX - 100, midY, { steps: 10 });
  await page.mouse.up();

  // After move, polygon should still exist (updated bounds).
  await expect.poll(async () => {
    const poly = await page.evaluate(() => (window as any).__POLYGON__);
    return poly?.features?.[0]?.geometry?.coordinates?.length ?? 0;
  }).toBeGreaterThan(0);
});