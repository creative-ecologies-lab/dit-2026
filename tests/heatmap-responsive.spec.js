// @ts-check
const { test, expect } = require('@playwright/test');

const BASE_URL = 'https://aiskillsmap.noahratzan.com';

// Test viewports covering phone → desktop
const VIEWPORTS = [
  { name: 'iPhone SE',       width: 375,  height: 667  },
  { name: 'iPhone 14',       width: 390,  height: 844  },
  { name: 'Galaxy S21',      width: 412,  height: 915  },
  { name: 'Surface Duo',     width: 540,  height: 720  },
  { name: 'iPad Mini',       width: 768,  height: 1024 },
  { name: 'iPad Air',        width: 820,  height: 1180 },
  { name: 'Surface Pro 7',   width: 912,  height: 1368 },
  { name: 'iPad Pro',        width: 1024, height: 1366 },
  { name: 'Laptop',          width: 1280, height: 800  },
  { name: 'Desktop',         width: 1440, height: 900  },
  { name: 'Wide Desktop',    width: 1920, height: 1080 },
];

// Pages that contain a heatmap
const PAGES = [
  { name: 'Landing', path: '/' },
  // Results page requires a completed assessment, so skip in automated tests
];

for (const vp of VIEWPORTS) {
  for (const page of PAGES) {
    test(`${page.name} heatmap @ ${vp.name} (${vp.width}x${vp.height}): no overflow or broken words`, async ({ browser }) => {
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
      });
      const tab = await context.newPage();
      await tab.goto(`${BASE_URL}${page.path}`, { waitUntil: 'networkidle' });

      // Wait for heatmap to render
      const heatmap = tab.locator('.landing-heatmap');
      await expect(heatmap).toBeVisible({ timeout: 5000 });

      // Get the heatmap's bounding box
      const hmBox = await heatmap.boundingBox();

      // ── Check stage headers (EPIAS columns) ──
      const stageHeaders = tab.locator('.hm-stage-header');
      const stageCount = await stageHeaders.count();
      expect(stageCount).toBeGreaterThan(0);

      for (let i = 0; i < stageCount; i++) {
        const header = stageHeaders.nth(i);
        const box = await header.boundingBox();
        if (!box) continue;

        // Cell must not overflow the table
        expect(
          box.x + box.width,
          `Stage header ${i} overflows table right edge at ${vp.name}`
        ).toBeLessThanOrEqual(hmBox.x + hmBox.width + 2); // 2px tolerance

        // Check visible text — must not be clipped (scrollWidth > clientWidth)
        const overflow = await header.evaluate((el) => {
          return el.scrollWidth > el.clientWidth + 1;
        });
        expect(overflow, `Stage header ${i} text is clipped at ${vp.name}`).toBe(false);

        // Check that visible text is either a full word or a single letter (abbreviation),
        // never a broken fragment like "Practitio" or "Explo"
        const visibleText = await header.evaluate((el) => {
          // Get the visible span (whichever is displayed)
          const full = el.querySelector('.hm-stage-full');
          const abbr = el.querySelector('.hm-stage-abbr');
          if (full && getComputedStyle(full).display !== 'none') return full.textContent.trim();
          if (abbr && getComputedStyle(abbr).display !== 'none') return abbr.textContent.trim();
          return el.textContent.trim();
        });

        const VALID_FULL = ['Explorer', 'Practitioner', 'Integrator', 'Architect', 'Steward'];
        const VALID_ABBR = ['E', 'P', 'I', 'A', 'S'];
        const isValid = VALID_FULL.includes(visibleText) || VALID_ABBR.includes(visibleText);
        expect(isValid, `Stage header "${visibleText}" is a broken fragment at ${vp.name}`).toBe(true);
      }

      // ── Check level headers (SAE rows) ──
      const levelHeaders = tab.locator('.hm-level-header');
      const levelCount = await levelHeaders.count();
      expect(levelCount).toBeGreaterThan(0);

      for (let i = 0; i < levelCount; i++) {
        const header = levelHeaders.nth(i);
        const box = await header.boundingBox();
        if (!box) continue;

        // Cell must not overflow table
        expect(
          box.x + box.width,
          `Level header ${i} overflows table right edge at ${vp.name}`
        ).toBeLessThanOrEqual(hmBox.x + hmBox.width + 2);

        // Check for text clipping
        const overflow = await header.evaluate((el) => {
          return el.scrollWidth > el.clientWidth + 1;
        });
        expect(overflow, `Level header ${i} text is clipped at ${vp.name}`).toBe(false);

        // Check visible text: must be "L0"-"L5" alone, or "L0 Manual" / "L1 AI-Assisted" etc.
        // Never a broken fragment like "Full Automa"
        const levelNum = await header.locator('.hm-level-num').textContent();
        const levelName = header.locator('.hm-level-name');
        const nameVisible = await levelName.evaluate((el) => {
          return getComputedStyle(el).display !== 'none';
        }).catch(() => false);

        if (nameVisible) {
          const nameText = await levelName.textContent();
          const VALID_NAMES = ['Full Automation', 'Mostly Automated', 'Guided Automation',
                               'Partially Automated', 'AI-Assisted', 'Manual'];
          expect(
            VALID_NAMES.includes(nameText.trim()),
            `Level name "${nameText}" is a broken fragment at ${vp.name}`
          ).toBe(true);

          // Also check that the name isn't being word-broken mid-word
          const hasWordBreak = await levelName.evaluate((el) => {
            // Check if any word in the text is being split across lines
            const range = document.createRange();
            const text = el.firstChild;
            if (!text || text.nodeType !== Node.TEXT_NODE) return false;
            const words = el.textContent.trim().split(/\s+/);
            let offset = 0;
            for (const word of words) {
              const start = el.textContent.indexOf(word, offset);
              range.setStart(text, start);
              range.setEnd(text, start + word.length);
              const rects = range.getClientRects();
              if (rects.length > 1) return true; // Word spans multiple lines
              offset = start + word.length;
            }
            return false;
          });
          expect(
            hasWordBreak,
            `Level name word-breaks mid-word at ${vp.name}`
          ).toBe(false);
        }
      }

      // ── Check data cells don't overflow ──
      const dataCells = tab.locator('.hm-cell, .landing-heatmap td');
      const cellCount = await dataCells.count();
      for (let i = 0; i < cellCount; i++) {
        const cell = dataCells.nth(i);
        const box = await cell.boundingBox();
        if (!box) continue;
        expect(
          box.x + box.width,
          `Data cell ${i} overflows at ${vp.name}`
        ).toBeLessThanOrEqual(hmBox.x + hmBox.width + 2);
      }

      await context.close();
    });
  }
}
