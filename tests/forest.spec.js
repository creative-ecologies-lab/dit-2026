// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Forest page (/tree/forest)', () => {

  test('loads with Forest view by default', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const forestBtn = page.locator('.forest-toggle-btn', { hasText: 'The Forest' });
    await expect(forestBtn).toHaveClass(/active/);
    const svg = page.locator('#viewForest svg');
    await expect(svg).toBeVisible();
  });

  test('shows participant count', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const subtitle = page.locator('.forest-subtitle');
    await expect(subtitle).toContainText('participants');
  });

  test('toggles to Trees view', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    await page.click('.forest-toggle-btn:has-text("The Trees")');
    const treesView = page.locator('#viewTrees');
    await expect(treesView).toHaveClass(/active/);
    // SVG exists and has tree content
    const svg = page.locator('#viewTrees svg');
    const treeCount = await svg.locator('.forest-tree-g').count();
    expect(treeCount).toBeGreaterThan(0);
  });

  test('toggles back to Forest view', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    await page.click('.forest-toggle-btn:has-text("The Trees")');
    await page.click('.forest-toggle-btn:has-text("The Forest")');
    const forestView = page.locator('#viewForest');
    await expect(forestView).toHaveClass(/active/);
  });

  test('wind slider updates label', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const slider = page.locator('#forestWind');
    const label = page.locator('#forestWindValue');
    await expect(label).toHaveText('calm');
    await slider.fill('50');
    await slider.dispatchEvent('input');
    // Wait for smooth wind to catch up
    await page.waitForTimeout(500);
    const text = await label.textContent();
    expect(text).not.toBe('calm');
  });

  test('Chance button shows "at risk" count', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    await page.click('#rollDice');
    // Wait for night animation + result
    await page.waitForTimeout(3000);
    const result = page.locator('#diceResult');
    const text = await result.textContent();
    expect(text.trim()).toMatch(/at risk|all safe/);
  });

  test('info popup toggles on click', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const popup = page.locator('#chancePopup');
    await expect(popup).not.toBeVisible();
    await page.click('#chanceInfo');
    await expect(popup).toBeVisible();
    // Click elsewhere to dismiss
    await page.click('body');
    await expect(popup).not.toBeVisible();
  });

  test('balance stats are visible', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const stats = page.locator('.forest-stats');
    await expect(stats).toBeVisible();
    const statItems = page.locator('.forest-stat');
    const count = await statItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('show all toggle hides/shows empty trees', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    await page.click('.forest-toggle-btn:has-text("The Trees")');
    await page.waitForTimeout(200);

    const checkbox = page.locator('#showAllTrees');
    // Default: unchecked, empties hidden
    await expect(checkbox).not.toBeChecked();
    const hiddenEmpty = page.locator('[data-empty][style*="display: none"]');
    const hiddenCount = await hiddenEmpty.count();
    expect(hiddenCount).toBeGreaterThan(0);

    // Check the box — empties should appear
    await checkbox.check();
    await page.waitForTimeout(100);
    const visibleEmpty = page.locator('[data-empty]:not([style*="display: none"])');
    const visibleCount = await visibleEmpty.count();
    expect(visibleCount).toBeGreaterThan(0);
  });
});

test.describe('Trees in forest view have correct structure', () => {

  test('forest SVG contains tree groups with data-ratio', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const trees = page.locator('.forest-tree-g');
    const count = await trees.count();
    expect(count).toBeGreaterThan(0);
    // Check first tree has data-ratio
    const ratio = await trees.first().getAttribute('data-ratio');
    expect(ratio).not.toBeNull();
  });

  test('trees SVG has no roots visible (mini-roots stripped)', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const forestSvg = page.locator('#viewForest svg');
    const roots = forestSvg.locator('.mini-roots');
    const count = await roots.count();
    expect(count).toBe(0);
  });

  test('trees grid SVG has roots visible', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    await page.click('.forest-toggle-btn:has-text("The Trees")');
    await page.waitForTimeout(200);
    const treesSvg = page.locator('#viewTrees svg');
    const roots = treesSvg.locator('.mini-roots');
    const count = await roots.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Results page (/tree/v2/results)', () => {

  test('shows community views when no assessment data', async ({ page }) => {
    await page.goto('/tree/v2/results', { waitUntil: 'networkidle' });
    // No sessionStorage data — should show community toggle
    const forestTab = page.locator('[data-view="forest"]');
    await expect(forestTab).toBeVisible();
    // Your Tree tab should be hidden
    const yourTreeTab = page.locator('[data-view="yourTree"]');
    await expect(yourTreeTab).toBeHidden();
  });

  test('3-way toggle switches views', async ({ page }) => {
    await page.goto('/tree/v2/results', { waitUntil: 'networkidle' });
    // Click Trees tab
    await page.click('[data-view="trees"]');
    const community = page.locator('#viewCommunity');
    await expect(community).toBeVisible();
    // Click Forest tab
    await page.click('[data-view="forest"]');
    await expect(community).toBeVisible();
  });
});

test.describe('Wind animation mechanics', () => {

  test('trees sway at moderate wind', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const slider = page.locator('#forestWind');
    await slider.fill('40');
    await slider.dispatchEvent('input');
    await page.waitForTimeout(300);

    // Check that at least one tree has a transform
    const tree = page.locator('.forest-tree-g').first();
    const transform = await tree.getAttribute('transform');
    expect(transform).not.toBeNull();
    expect(transform).not.toBe('');
  });

  test('calm reset restores trees after 2 seconds', async ({ page }) => {
    await page.goto('/tree/forest', { waitUntil: 'networkidle' });
    const slider = page.locator('#forestWind');

    // Wind up
    await slider.fill('80');
    await slider.dispatchEvent('input');
    await page.waitForTimeout(1000);

    // Back to calm — wait for smooth wind ramp + 2s calm reset
    await slider.fill('0');
    await slider.dispatchEvent('input');
    await page.waitForTimeout(4000);

    // Trees should be reset (transform empty or very small rotation)
    const tree = page.locator('.forest-tree-g').first();
    const transform = await tree.getAttribute('transform');
    const isReset = !transform || transform === '' || transform.includes('rotate(0');
    expect(isReset).toBeTruthy();
  });
});
