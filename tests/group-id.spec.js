// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Group ID page (/group-id)', () => {

  test('loads with version dropdown defaulting to v2', async ({ page }) => {
    await page.goto('/group-id', { waitUntil: 'networkidle' });
    const select = page.locator('#versionSelect');
    await expect(select).toBeVisible();
    await expect(select).toHaveValue('v2');
  });

  test('version dropdown has v1 and v2 options', async ({ page }) => {
    await page.goto('/group-id', { waitUntil: 'networkidle' });
    const select = page.locator('#versionSelect');
    const options = select.locator('option');
    await expect(options).toHaveCount(2);
    await expect(options.nth(0)).toHaveValue('v2');
    await expect(options.nth(1)).toHaveValue('v1');
  });

  test('entering a group ID generates a QR code', async ({ page }) => {
    await page.goto('/group-id', { waitUntil: 'networkidle' });
    const input = page.locator('#cohortInput');
    await input.fill('test-group');
    await page.click('#cohortGoBtn');
    // Wait for content to appear
    await page.waitForSelector('#cohortContent:not([style*="display: none"])', { timeout: 5000 });
    const qrSvg = page.locator('#qrCode svg');
    await expect(qrSvg).toBeVisible();
  });

  test('mobile responsive check (375x667)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/group-id', { waitUntil: 'networkidle' });
    const input = page.locator('#cohortInput');
    await expect(input).toBeVisible();
    const select = page.locator('#versionSelect');
    await expect(select).toBeVisible();
    // Verify the page doesn't overflow horizontally
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(bodyWidth).toBeLessThanOrEqual(375);
  });

});
