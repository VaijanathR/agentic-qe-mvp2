// DISCOVERY-ONLY PROBE 3 — orders page, guest checkout, anonymous wishlist, cart-merge-on-login.
// Not test automation, not a baseline artifact.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://demowebshop.tricentis.com';
const email = 'qe.discovery.1789149299815@example.com';
const password = 'Discover!2345';
const out = {};

(async () => {
  const browser = await chromium.launch();

  // ---- A. Orders page for the account that just completed checkout ----
  const p1 = await (await browser.newContext()).newPage();
  await p1.goto(`${BASE}/login`);
  await p1.fill('#Email', email);
  await p1.fill('#Password', password);
  await p1.click('.login-button');
  await p1.waitForTimeout(800);
  await p1.goto(`${BASE}/customer/orders`);
  await p1.waitForTimeout(600);
  out.ordersPageText = (await p1.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 800);
  await p1.screenshot({ path: __dirname + '/shots_orders.png', fullPage: true }).catch(()=>{});
  await p1.close();

  // ---- B. Anonymous wishlist add attempt (confirm no wishlist button exists anywhere reachable) ----
  const anonCtx = await browser.newContext();
  const p2 = await anonCtx.newPage();
  await p2.goto(`${BASE}/computing-and-internet`);
  await p2.waitForTimeout(400);
  out.anonProductPageHasWishlistBtn = await p2.locator('text=/add to wishlist/i').count();
  out.anonProductPageButtons = await p2.locator('.add-to-cart input[type=button], .buttons input[type=button]').allTextContents().catch(()=>[]);

  // ---- C. Anonymous add-to-cart + guest checkout attempt ----
  await p2.click('#add-to-cart-button-13').catch(async () => {
    await p2.locator('input[value="Add to cart"]').first().click().catch(()=>{});
  });
  await p2.waitForTimeout(1200);
  out.anonAddToCartNotice = (await p2.locator('#bar-notification').innerText().catch(() => 'N/A')).replace(/\s+/g,' ');

  await p2.goto(`${BASE}/cart`);
  await p2.check('#termsofservice').catch(() => {});
  await p2.click('#checkout').catch(() => {});
  await p2.waitForTimeout(1200);
  out.anonCheckoutUrl = p2.url();
  out.anonCheckoutText = (await p2.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 600);
  fs.writeFileSync(__dirname + '/anon_checkout.html', await p2.content());
  await p2.screenshot({ path: __dirname + '/shots_anon_checkout.png', fullPage: true }).catch(()=>{});

  // ---- D. Cart persistence: does the anonymous cart merge into the account cart after login? ----
  await p2.goto(`${BASE}/login`);
  await p2.fill('#Email', email);
  await p2.fill('#Password', password);
  await p2.click('.login-button');
  await p2.waitForTimeout(1000);
  await p2.goto(`${BASE}/cart`);
  await p2.waitForTimeout(500);
  out.cartAfterLoginRowCount = await p2.locator('tr.cart-item-row').count();
  out.cartAfterLoginText = (await p2.locator('.cart').innerText().catch(() => 'N/A')).replace(/\s+/g, ' ').slice(0, 500);
  await p2.close();

  // ---- E. Registration with invalid email format ----
  const p3 = await (await browser.newContext()).newPage();
  await p3.goto(`${BASE}/register`);
  await p3.fill('#FirstName', 'QE');
  await p3.fill('#LastName', 'Bad');
  await p3.fill('#Email', 'not-an-email');
  await p3.fill('#Password', 'Discover!2345');
  await p3.fill('#ConfirmPassword', 'Discover!2345');
  await p3.click('#register-button');
  await p3.waitForTimeout(600);
  out.invalidEmailValidation = await p3.locator('.field-validation-error, .validation-summary-errors').allTextContents();

  // ---- F. Registration with an email that is already registered ----
  await p3.fill('#Email', email);
  await p3.click('#register-button');
  await p3.waitForTimeout(600);
  out.duplicateEmailValidation = await p3.locator('.field-validation-error, .validation-summary-errors').allTextContents();
  await p3.close();

  await browser.close();
  fs.writeFileSync(__dirname + '/probe3_results.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
})().catch(e => { console.error('PROBE3 ERROR:', e); fs.writeFileSync(__dirname + '/probe3_results.json', JSON.stringify(out, null, 2)); process.exit(1); });
