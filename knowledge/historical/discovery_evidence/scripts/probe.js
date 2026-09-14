// DISCOVERY-ONLY PROBE — not test automation, not a baseline artifact.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://demowebshop.tricentis.com';
const email = 'qe.discovery.1789149299815@example.com';
const password = 'Discover!2345';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(`${BASE}/login`);
  await page.fill('#Email', email);
  await page.fill('#Password', password);
  await page.click('.login-button');
  await page.waitForTimeout(800);
  console.log('LOGIN URL:', page.url());

  await page.goto(`${BASE}/computing-and-internet`);
  await page.click('#add-to-cart-button-13');
  await page.waitForTimeout(1500);
  console.log('POST ADD-TO-CART NOTICE:', (await page.locator('#bar-notification').innerText().catch(()=>'N/A')));

  await page.goto(`${BASE}/cart`);
  await page.waitForTimeout(800);
  const html = await page.content();
  fs.writeFileSync(__dirname + '/cart_with_item.html', html);
  console.log('Saved cart_with_item.html, length', html.length);

  await page.close();
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
