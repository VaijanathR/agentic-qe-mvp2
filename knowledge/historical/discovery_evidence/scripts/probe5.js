// DISCOVERY-ONLY PROBE 5 — search, dynamic pricing, cart qty/price recalculation.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://demowebshop.tricentis.com';
const out = {};

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext()).newPage();

  // Search - valid keyword
  await page.goto(`${BASE}/search`);
  await page.fill('#Q', 'computer');
  await page.click('.search-button');
  await page.waitForTimeout(800);
  out.searchValidUrl = page.url();
  out.searchValidResultCount = await page.locator('.product-item').count();

  // Search - no results
  await page.goto(`${BASE}/search`);
  await page.fill('#Q', 'zzzznoresultxyz123');
  await page.click('.search-button');
  await page.waitForTimeout(800);
  out.searchNoResultText = (await page.locator('.search-results, .no-result, .product-grid, .page-body').first().innerText().catch(() => 'N/A')).replace(/\s+/g, ' ').slice(0, 300);
  out.searchNoResultCount = await page.locator('.product-item').count();

  // Configurable product dynamic pricing
  await page.goto(`${BASE}/build-your-own-computer`);
  await page.waitForTimeout(500);
  out.priceBeforeOptionChange = await page.locator('#product-details-form .product-price, .product-price').first().innerText().catch(() => 'N/A');
  // Select the higher-priced RAM option (2nd select, index 2 = 8GB [+60.00] typically)
  const selects = page.locator('select[id^="product_attribute_"]');
  const selCount = await selects.count();
  out.numConfigurableSelects = selCount;
  if (selCount > 0) {
    await selects.nth(0).selectOption({ index: 1 }).catch(() => {});
    await page.waitForTimeout(600);
  }
  out.priceAfterOptionChange = await page.locator('#product-details-form .product-price, .product-price').first().innerText().catch(() => 'N/A');

  // Add to cart with quantity 2
  await page.fill('input[id*="EnteredQuantity"]', '2').catch(() => {});
  await page.locator('input.add-to-cart-button').first().click().catch(() => {});
  await page.waitForTimeout(1500);
  out.addToCartNotice = (await page.locator('#bar-notification').innerText().catch(() => 'N/A')).replace(/\s+/g, ' ');

  await page.goto(`${BASE}/cart`);
  await page.waitForTimeout(600);
  out.cartTextAfterAdd = (await page.locator('.cart').innerText().catch(() => 'N/A')).replace(/\s+/g, ' ').slice(0, 500);

  // Update quantity to 5 and observe recalculated line total
  const qtyInput = page.locator('input.qty-input').first();
  await qtyInput.fill('5').catch(() => {});
  await page.click('input[name="updatecart"]').catch(() => {});
  await page.waitForTimeout(1000);
  out.cartTextAfterQtyUpdate = (await page.locator('.cart').innerText().catch(() => 'N/A')).replace(/\s+/g, ' ').slice(0, 500);

  // Remove the item and confirm empty-cart state
  await page.check('input[name="removefromcart"]').catch(() => {});
  await page.click('input[name="updatecart"]').catch(() => {});
  await page.waitForTimeout(1000);
  out.cartTextAfterRemove = (await page.locator('body').innerText().catch(() => 'N/A')).match(/Shopping Cart is empty|cart-item-row/gi);

  await browser.close();
  fs.writeFileSync(__dirname + '/probe5_results.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
})().catch(e => { console.error('PROBE5 ERROR:', e); fs.writeFileSync(__dirname + '/probe5_results.json', JSON.stringify(out, null, 2)); process.exit(1); });
