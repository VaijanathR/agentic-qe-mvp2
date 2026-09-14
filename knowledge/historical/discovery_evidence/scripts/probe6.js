// DISCOVERY-ONLY PROBE 6 — cart quantity-based price recalculation, isolated and minimal.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://demowebshop.tricentis.com';
const out = {};

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext()).newPage();

  await page.goto(`${BASE}/computing-and-internet`);
  await page.click('#add-to-cart-button-13');
  await page.waitForTimeout(1200);

  await page.goto(`${BASE}/cart`);
  await page.waitForTimeout(500);
  out.qty1_unitPrice = await page.locator('.product-unit-price').first().innerText().catch(() => 'N/A');
  out.qty1_subtotal = await page.locator('.product-subtotal').first().innerText().catch(() => 'N/A');
  out.qty1_cartTotal = await page.locator('.cart-total .product-price').first().innerText().catch(() => 'N/A');

  await page.fill('input.qty-input', '3');
  await page.click('input[name="updatecart"]');
  await page.waitForTimeout(1200);
  out.qty3_unitPrice = await page.locator('.product-unit-price').first().innerText().catch(() => 'N/A');
  out.qty3_subtotal = await page.locator('.product-subtotal').first().innerText().catch(() => 'N/A');
  out.qty3_cartTotal = await page.locator('.cart-total .product-price').first().innerText().catch(() => 'N/A');

  // Negative: try quantity 0
  await page.fill('input.qty-input', '0');
  await page.click('input[name="updatecart"]');
  await page.waitForTimeout(1200);
  out.qty0_result = (await page.locator('body').innerText()).match(/Shopping Cart is empty|cart-item-row|error/i)?.[0] || 'no-match';
  out.qty0_rowCount = await page.locator('tr.cart-item-row').count();

  await browser.close();
  fs.writeFileSync(__dirname + '/probe6_results.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
})().catch(e => { console.error('PROBE6 ERROR:', e); fs.writeFileSync(__dirname + '/probe6_results.json', JSON.stringify(out, null, 2)); process.exit(1); });
