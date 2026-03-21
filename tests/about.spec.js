// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('About page (/about)', () => {

  test('page loads with h1 visible', async ({ page }) => {
    await page.goto('/about', { waitUntil: 'networkidle' });
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    await expect(h1).toContainText('About This Project');
  });

  test('heatmap table renders with .hm-cell elements', async ({ page }) => {
    await page.goto('/about', { waitUntil: 'networkidle' });
    const table = page.locator('table.landing-heatmap');
    await expect(table).toBeVisible();
    const cells = page.locator('.hm-cell');
    const count = await cells.count();
    expect(count).toBeGreaterThan(0);
  });

  test('feedback category toggle works', async ({ page }) => {
    await page.goto('/about', { waitUntil: 'networkidle' });
    const bugBtn = page.locator('.about-fb-cat[data-cat="bug"]');
    const generalBtn = page.locator('.about-fb-cat[data-cat="general"]');

    // General is active by default
    await expect(generalBtn).toHaveClass(/active/);
    await expect(bugBtn).not.toHaveClass(/active/);

    // Click Bug
    await bugBtn.click();
    await expect(bugBtn).toHaveClass(/active/);
    await expect(generalBtn).not.toHaveClass(/active/);
  });

  test('feedback empty submit shows error message', async ({ page }) => {
    await page.goto('/about', { waitUntil: 'networkidle' });
    const submitBtn = page.locator('#aboutFbSubmit');
    const status = page.locator('#aboutFbStatus');

    await submitBtn.click();
    await expect(status).toContainText('Please enter a message');
  });

  test('nav has About link, no Assess link', async ({ page }) => {
    await page.goto('/about', { waitUntil: 'networkidle' });
    const aboutLink = page.locator('.nav-links a[href="/about"]');
    await expect(aboutLink).toBeVisible();
    await expect(aboutLink).toHaveClass(/active/);

    const assessLink = page.locator('.nav-links a[href="/assess"]');
    await expect(assessLink).toHaveCount(0);
  });

  test('mobile viewport: page scrolls, content visible', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/about', { waitUntil: 'networkidle' });

    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();

    // Feedback section should exist (may need scroll)
    const feedbackCard = page.locator('.about-feedback-card');
    await feedbackCard.scrollIntoViewIfNeeded();
    await expect(feedbackCard).toBeVisible();
  });

});
