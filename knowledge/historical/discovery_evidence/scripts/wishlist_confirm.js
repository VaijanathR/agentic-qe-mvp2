// DISCOVERY-ONLY — confirm wishlist page actually reflects additions. Not automation.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://demowebshop.tricentis.com';

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext()).newPage();

  await page.goto(`${BASE}/digital-slr-camera`);
  await page.locator('text=/add to wishlist/i').first().click();
  await page.waitForTimeout(1000);

  await page.goto(`${BASE}/music-album-1`);
  await page.locator('text=/add to wishlist/i').first().click();
  await page.waitForTimeout(1000);

  await page.goto(`${BASE}/wishlist`);
  await page.waitForTimeout(600);
  const text = (await page.locator('body').innerText()).replace(/\s+/g, ' ');
  const rowCount = await page.locator('tr.wishlist-item-row, .wishlist-content tr').count().catch(() => 0);
  fs.writeFileSync(__dirname + '/wishlist_confirm.html', await page.content());
  console.log('ANON wishlist page rowCount(approx):', rowCount);
  console.log('ANON wishlist page text snippet:', text.slice(0, 500));

  await browser.close();
})().catch(e => { console.error('ERROR:', e); process.exit(1); });
