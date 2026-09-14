// DISCOVERY-ONLY PROBE 4 — confirm "Checkout as Guest" actually proceeds without login.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://demowebshop.tricentis.com';

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext()).newPage();
  await page.goto(`${BASE}/computing-and-internet`);
  await page.click('#add-to-cart-button-13');
  await page.waitForTimeout(1200);
  await page.goto(`${BASE}/cart`);
  await page.check('#termsofservice').catch(() => {});
  await page.click('#checkout');
  await page.waitForTimeout(1000);
  console.log('Guest interstitial URL:', page.url());
  await page.click('.checkout-as-guest-button');
  await page.waitForTimeout(1500);
  console.log('After Checkout-as-Guest click URL:', page.url());
  const text = (await page.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 500);
  console.log('Content snippet:', text);
  fs.writeFileSync(__dirname + '/guest_checkout_step1.html', await page.content());
  await browser.close();
})().catch(e => { console.error('PROBE4 ERROR:', e); process.exit(1); });
