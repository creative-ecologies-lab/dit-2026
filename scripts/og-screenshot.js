const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    const svgContent = fs.readFileSync(
        path.join(__dirname, '..', 'assessment', 'static', 'trees', 'org', 'r3_c3_h3.svg'),
        'utf-8'
    );

    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });

    const groundY = 285;
    const svgH = 540;
    const groundPct = (groundY / svgH * 100).toFixed(1);

    await page.setContent(`
        <html>
        <body style="margin:0; display:flex; align-items:center; justify-content:center; width:1200px; height:630px; overflow:hidden; background: linear-gradient(to bottom, #2a4a70 0%, #4a7aa0 ${groundPct}%, #3a3020 ${groundPct}%, #2e2618 75%, #221c12 100%);">
            <div style="width:900px; height:916px; margin-top:10px;">
                ${svgContent}
            </div>
        </body>
        </html>
    `);

    await page.waitForTimeout(500);
    await page.screenshot({
        path: path.join(__dirname, '..', 'assessment', 'static', 'og-tree.png'),
        type: 'png'
    });
    console.log('Saved assessment/static/og-tree.png');
    await browser.close();
})();
