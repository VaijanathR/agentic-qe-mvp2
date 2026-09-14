// DISCOVERY-ONLY SCRIPT — CP-MVP2-01 stateful browser discovery.
// Not an MVP2 baseline artifact. Not test automation. Temporary, scratchpad-only.
const { chromium } = require('playwright');
const fs = require('fs');

const BASE = 'https://demowebshop.tricentis.com';
const obs = [];
const shotDir = __dirname + '/shots';
fs.mkdirSync(shotDir, { recursive: true });
let shotN = 0;

function record(o) { obs.push(o); console.log('OBS:', JSON.stringify(o).slice(0, 300)); }

async function shot(page, name) {
  shotN++;
  const p = `${shotDir}/${String(shotN).padStart(2, '0')}_${name}.png`;
  try { await page.screenshot({ path: p, fullPage: true }); } catch (e) {}
  return p;
}

(async () => {
  const browser = await chromium.launch();
  const stamp = Date.now();
  const email = `qe.discovery.${stamp}@example.com`;
  const password = 'Discover!2345';

  // ---------- ANONYMOUS CONTEXT ----------
  const anonCtx = await browser.newContext();
  const anon = await anonCtx.newPage();

  // 1. Registration - submit empty form to see validation
  await anon.goto(`${BASE}/register`);
  await anon.click('#register-button');
  await anon.waitForTimeout(500);
  const emptyValidation = await anon.locator('.field-validation-error, .validation-summary-errors').allTextContents();
  record({
    capability: 'Registration', action: 'Submit registration form with all fields empty',
    result: emptyValidation.length ? emptyValidation.join(' | ') : 'No validation text captured',
    preconditions: 'Anonymous, /register', data: 'none', authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(anon, 'register_empty_validation');

  // Password mismatch
  await anon.fill('#FirstName', 'QE');
  await anon.fill('#LastName', 'Discovery');
  await anon.fill('#Email', email);
  await anon.fill('#Password', password);
  await anon.fill('#ConfirmPassword', 'Mismatch!999');
  await anon.click('#register-button');
  await anon.waitForTimeout(500);
  const mismatchValidation = await anon.locator('.field-validation-error, .validation-summary-errors').allTextContents();
  record({
    capability: 'Registration', action: 'Submit with mismatched password/confirm-password',
    result: mismatchValidation.length ? mismatchValidation.join(' | ') : 'No validation text captured',
    preconditions: 'Valid names/email, mismatched passwords', data: email, authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(anon, 'register_password_mismatch');

  // Valid registration
  await anon.fill('#ConfirmPassword', password);
  await anon.click('#register-button');
  await anon.waitForTimeout(800);
  const postRegUrl = anon.url();
  const postRegText = (await anon.locator('body').innerText()).slice(0, 600);
  record({
    capability: 'Registration', action: 'Submit valid registration (unique email, matching passwords)',
    result: `URL after submit: ${postRegUrl}. Page text snippet: ${postRegText.replace(/\s+/g, ' ').slice(0,300)}`,
    preconditions: 'Unique email, all required fields valid', data: email, authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(anon, 'register_success');

  // Is user auto-logged-in after registration? Check header for logout/account link
  const headerAfterReg = await anon.locator('.header-links, .account').innerText().catch(() => 'N/A');
  record({
    capability: 'Registration', action: 'Inspect header immediately after registration submit',
    result: headerAfterReg,
    preconditions: 'Just registered', data: email, authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });

  // Log out if auto logged in, to test explicit login next
  if (/logout/i.test(headerAfterReg)) {
    await anon.click('a[href="/logout"]').catch(() => {});
    await anon.waitForTimeout(500);
  }

  // 2. Login - invalid credentials
  await anon.goto(`${BASE}/login`);
  await anon.fill('#Email', email);
  await anon.fill('#Password', 'WrongPassword!1');
  await anon.click('.login-button');
  await anon.waitForTimeout(600);
  const badLoginMsg = await anon.locator('.validation-summary-errors, .message-error').allTextContents();
  record({
    capability: 'Login', action: 'Attempt login with correct email but wrong password',
    result: badLoginMsg.length ? badLoginMsg.join(' | ') : 'No visible error text captured; URL=' + anon.url(),
    preconditions: 'Registered email, wrong password', data: email, authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(anon, 'login_invalid_credentials');

  // Login - correct credentials (tests: can newly registered account log in immediately)
  await anon.fill('#Email', email);
  await anon.fill('#Password', password);
  await anon.click('.login-button');
  await anon.waitForTimeout(800);
  const loggedInUrl = anon.url();
  const headerAfterLogin = await anon.locator('.header-links').innerText().catch(() => 'N/A');
  record({
    capability: 'Login', action: 'Login with the just-registered email/password',
    result: `URL after login: ${loggedInUrl}. Header: ${headerAfterLogin.replace(/\s+/g,' ')}`,
    preconditions: 'Account created in previous step', data: email, authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(anon, 'login_success');

  // Password recovery
  await anon.goto(`${BASE}/passwordrecovery`);
  await anon.fill('#Email', email);
  await anon.click('button:has-text("Recover")');
  await anon.waitForTimeout(600);
  const recoveryMsg = await anon.locator('.result, .validation-summary-errors').allTextContents();
  record({
    capability: 'Password recovery', action: 'Submit password recovery for a valid registered email',
    result: recoveryMsg.length ? recoveryMsg.join(' | ') : anon.url(),
    preconditions: 'Valid registered email', data: email, authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(anon, 'password_recovery');

  // ---------- AUTHENTICATED SESSION CONTINUES (anon page is now logged in) ----------
  const authed = anon;

  // Account pages
  for (const path of ['/customer/info', '/customer/addresses', '/customer/orders']) {
    await authed.goto(`${BASE}${path}`);
    await authed.waitForTimeout(400);
    const txt = (await authed.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 400);
    record({
      capability: 'Account', action: `Navigate to ${path} while authenticated`,
      result: `URL: ${authed.url()} | Content snippet: ${txt}`,
      preconditions: 'Authenticated session', data: email, authRequired: true,
      evidence: 'OBSERVED_DIRECTLY'
    });
    await shot(authed, `account_${path.replace(/\//g, '_')}`);
  }

  // Search - valid keyword
  await authed.goto(`${BASE}/search`);
  await authed.fill('#q', 'computer');
  await authed.click('#search-button, input[value="Search"]').catch(async () => {
    await authed.press('#q', 'Enter');
  });
  await authed.waitForTimeout(600);
  const searchResultsCount = await authed.locator('.product-item').count();
  record({
    capability: 'Search', action: 'Search for keyword "computer"',
    result: `Result product cards found: ${searchResultsCount}. URL: ${authed.url()}`,
    preconditions: 'none', data: 'computer', authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });

  // Search - no results
  await authed.goto(`${BASE}/search`);
  await authed.fill('#q', 'zzzznoresultxyz123');
  await authed.click('input[value="Search"]').catch(() => {});
  await authed.waitForTimeout(600);
  const noResultsText = (await authed.locator('.search-results, .no-result, body').innerText()).replace(/\s+/g,' ').slice(0,300);
  record({
    capability: 'Search', action: 'Search for a keyword expected to match nothing',
    result: noResultsText,
    preconditions: 'none', data: 'zzzznoresultxyz123', authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'search_no_results');

  // Configurable product - dynamic pricing
  await authed.goto(`${BASE}/build-your-own-computer`);
  const priceBefore = await authed.locator('.product-price, #product-details-form .price-value-24').first().innerText().catch(() => 'N/A');
  // select a priced option
  const processorSelect = authed.locator('#product_attribute_1, select[id^="product_attribute_"]').first();
  await processorSelect.selectOption({ index: 1 }).catch(() => {});
  await authed.waitForTimeout(500);
  const priceAfter = await authed.locator('.product-price, #product-details-form .price-value-24').first().innerText().catch(() => 'N/A');
  record({
    capability: 'Configurable product / dynamic pricing', action: 'Change processor dropdown option on "Build your own computer"',
    result: `Price before: "${priceBefore}" | Price after selecting option: "${priceAfter}"`,
    preconditions: 'Product detail page loaded', data: 'processor option index 1', authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'configurable_product_price_change');

  // Add configurable product to cart, qty 2
  await authed.fill('#addtocart_1_EnteredQuantity, input.qty-input', '2').catch(() => {});
  await authed.click('#add-to-cart-button-1, button:has-text("Add to cart")').catch(() => {});
  await authed.waitForTimeout(1000);
  const addToCartNotice = await authed.locator('.bar-notification, .content').first().innerText().catch(() => 'N/A');
  record({
    capability: 'Cart', action: 'Add configurable product to cart with quantity 2',
    result: `Notification/content: ${addToCartNotice}`.replace(/\s+/g,' ').slice(0,300),
    preconditions: 'Logged in, product configured', data: 'qty=2', authRequired: true,
    evidence: 'OBSERVED_AFTER_STATE_CHANGE'
  });
  await shot(authed, 'add_to_cart');

  // View cart
  await authed.goto(`${BASE}/cart`);
  await authed.waitForTimeout(500);
  const cartRows = await authed.locator('.cart-item-row, tr.cart-item-row').count();
  const cartTotalsText = await authed.locator('.cart-total, .order-total').innerText().catch(() => 'N/A');
  const cartLineText = await authed.locator('.cart').innerText().catch(() => 'N/A');
  record({
    capability: 'Cart', action: 'View cart after adding configured product qty=2',
    result: `Rows: ${cartRows}. Totals block: ${cartTotalsText}`.replace(/\s+/g,' ').slice(0,400),
    preconditions: 'Item added previously', data: 'n/a', authRequired: true,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'cart_with_item');
  fs.writeFileSync(shotDir + '/cart_full_text.txt', cartLineText);

  // Update quantity to 3
  const qtyInput = authed.locator('.qty-input, input.qty').first();
  await qtyInput.fill('3').catch(() => {});
  await authed.click('input[name="updatecart"], button:has-text("Update cart")').catch(() => {});
  await authed.waitForTimeout(700);
  const cartAfterUpdate = await authed.locator('.cart').innerText().catch(() => 'N/A');
  record({
    capability: 'Cart', action: 'Update quantity from 2 to 3 and click Update cart',
    result: cartAfterUpdate.replace(/\s+/g,' ').slice(0,400),
    preconditions: 'Cart has 1 line item', data: 'qty=3', authRequired: true,
    evidence: 'OBSERVED_AFTER_STATE_CHANGE'
  });
  await shot(authed, 'cart_after_qty_update');

  // Remove item
  const removeCheckbox = authed.locator('.cart-item-row input[name="removefromcart"], input.remove-btn, input[type=checkbox][name*="Remove"]').first();
  await removeCheckbox.check().catch(() => {});
  await authed.click('input[name="updatecart"], button:has-text("Update cart")').catch(() => {});
  await authed.waitForTimeout(700);
  const cartAfterRemove = (await authed.locator('body').innerText()).replace(/\s+/g,' ').slice(0,300);
  record({
    capability: 'Cart', action: 'Check remove checkbox on line item and click Update cart',
    result: cartAfterRemove,
    preconditions: 'Cart had 1 line item', data: 'n/a', authRequired: true,
    evidence: 'OBSERVED_AFTER_STATE_CHANGE'
  });
  await shot(authed, 'cart_after_remove');

  // Checkout with EMPTY cart (authenticated)
  await authed.goto(`${BASE}/onepagecheckout`);
  await authed.waitForTimeout(500);
  record({
    capability: 'Checkout', action: 'Navigate directly to /onepagecheckout with an empty cart (authenticated)',
    result: `URL: ${authed.url()} | Snippet: ${(await authed.locator('body').innerText()).replace(/\s+/g,' ').slice(0,300)}`,
    preconditions: 'Authenticated, cart empty', data: 'n/a', authRequired: true,
    evidence: 'OBSERVED_DIRECTLY'
  });

  // Add a simple product for checkout walkthrough
  await authed.goto(`${BASE}/15-inch-laptop`);
  await authed.waitForTimeout(400);
  const laptopPageExists = !/404/.test(await authed.title());
  if (!laptopPageExists) {
    await authed.goto(`${BASE}/books`);
    await authed.waitForTimeout(400);
    await authed.locator('.product-item').first().locator('a').first().click().catch(()=>{});
    await authed.waitForTimeout(400);
  }
  await authed.click('button:has-text("Add to cart")').catch(() => {});
  await authed.waitForTimeout(1000);
  await shot(authed, 'second_product_added');

  await authed.goto(`${BASE}/cart`);
  // accept ToS checkbox if present
  await authed.check('#termsofservice').catch(() => {});
  await authed.click('#checkout, button:has-text("Checkout")').catch(() => {});
  await authed.waitForTimeout(1200);
  const checkoutStep1 = (await authed.locator('body').innerText()).replace(/\s+/g,' ').slice(0,500);
  record({
    capability: 'Checkout', action: 'Click Checkout from populated cart (authenticated)',
    result: `URL: ${authed.url()} | Content: ${checkoutStep1}`,
    preconditions: 'Authenticated, cart has 1 item, ToS checked if present', data: 'n/a', authRequired: true,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'checkout_step1');

  // Walk through checkout steps generically: fill any visible required text inputs, click continue buttons, capture each screen
  for (let step = 1; step <= 6; step++) {
    const url = authed.url();
    const heading = await authed.locator('.section.address-form, .checkout-page, h2, .title').first().innerText().catch(() => 'N/A');
    // Try filling a new address form if present
    const newAddressVisible = await authed.locator('#billing-address-select, .new-address-next-step-button').count();
    if (newAddressVisible) {
      const fields = {
        '#BillingNewAddress_FirstName': 'QE', '#BillingNewAddress_LastName': 'Discovery',
        '#BillingNewAddress_Email': email, '#BillingNewAddress_Company': 'QE Test',
        '#BillingNewAddress_Country': null, '#BillingNewAddress_City': 'Springfield',
        '#BillingNewAddress_Address1': '123 QE Street', '#BillingNewAddress_ZipPostalCode': '12345',
        '#BillingNewAddress_PhoneNumber': '5551234567'
      };
      for (const [sel, val] of Object.entries(fields)) {
        if (val) await authed.fill(sel, val).catch(() => {});
      }
      await authed.selectOption('#BillingNewAddress_CountryId', { index: 1 }).catch(() => {});
    }
    const continueBtn = authed.locator('.new-address-next-step-button, .shipping-method-next-step-button, .payment-method-next-step-button, .payment-info-next-step-button, .confirm-order-next-step-button, button:has-text("Continue")').first();
    const btnCount = await continueBtn.count();
    record({
      capability: 'Checkout', action: `Checkout walkthrough step ${step}: inspect screen and click Continue if available`,
      result: `URL: ${url} | Heading/snippet: ${heading.replace(/\s+/g,' ').slice(0,200)} | Continue button present: ${btnCount > 0}`,
      preconditions: 'Mid-checkout', data: 'n/a', authRequired: true,
      evidence: 'OBSERVED_DIRECTLY'
    });
    await shot(authed, `checkout_step_loop_${step}`);
    if (btnCount === 0) break;
    await continueBtn.click().catch(() => {});
    await authed.waitForTimeout(1200);
  }

  const finalCheckoutUrl = authed.url();
  const finalCheckoutText = (await authed.locator('body').innerText()).replace(/\s+/g,' ').slice(0,600);
  record({
    capability: 'Checkout', action: 'State after checkout walkthrough loop ends',
    result: `Final URL: ${finalCheckoutUrl} | Content: ${finalCheckoutText}`,
    preconditions: 'End of automated continue-clicking', data: 'n/a', authRequired: true,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'checkout_final_state');

  // Orders page after checkout attempt
  await authed.goto(`${BASE}/customer/orders`);
  await authed.waitForTimeout(500);
  const ordersText = (await authed.locator('body').innerText()).replace(/\s+/g,' ').slice(0,400);
  record({
    capability: 'Account/Orders', action: 'View Orders page after checkout attempt',
    result: ordersText,
    preconditions: 'Authenticated, checkout walkthrough attempted', data: 'n/a', authRequired: true,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'orders_after_checkout');

  // Wishlist - authenticated add
  await authed.goto(`${BASE}/books`);
  await authed.waitForTimeout(400);
  const wishlistBtn = authed.locator('.add-to-wishlist-button, button[onclick*="wishlist"]').first();
  const wishlistBtnCount = await wishlistBtn.count();
  if (wishlistBtnCount) {
    await wishlistBtn.click().catch(() => {});
    await authed.waitForTimeout(800);
  }
  record({
    capability: 'Wishlist', action: 'Attempt to add a book product to wishlist while authenticated (from category grid)',
    result: `Wishlist button found: ${wishlistBtnCount > 0}. Notification: ${(await authed.locator('.bar-notification').innerText().catch(()=>'N/A'))}`,
    preconditions: 'Authenticated', data: 'n/a', authRequired: true,
    evidence: wishlistBtnCount ? 'OBSERVED_AFTER_STATE_CHANGE' : 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'wishlist_add_attempt');

  await authed.goto(`${BASE}/wishlist`);
  await authed.waitForTimeout(400);
  const wishlistPageText = (await authed.locator('body').innerText()).replace(/\s+/g,' ').slice(0,400);
  record({
    capability: 'Wishlist', action: 'View wishlist page while authenticated after add attempt',
    result: wishlistPageText,
    preconditions: 'Authenticated', data: 'n/a', authRequired: true,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(authed, 'wishlist_authenticated_view');

  await anonCtx.close();

  // ---------- SEPARATE ANONYMOUS CONTEXT: guest checkout + anonymous wishlist ----------
  const guestCtx = await browser.newContext();
  const guest = await guestCtx.newPage();

  // Anonymous wishlist add
  await guest.goto(`${BASE}/books`);
  await guest.waitForTimeout(400);
  const guestWishlistBtn = guest.locator('.add-to-wishlist-button, button[onclick*="wishlist"]').first();
  const guestWishlistCount = await guestWishlistBtn.count();
  if (guestWishlistCount) {
    await guestWishlistBtn.click().catch(() => {});
    await guest.waitForTimeout(800);
  }
  const guestWishlistNotice = await guest.locator('.bar-notification, body').innerText().catch(() => 'N/A');
  record({
    capability: 'Wishlist', action: 'Attempt to add product to wishlist while ANONYMOUS (not logged in)',
    result: `Button found: ${guestWishlistCount>0}. Result text: ${guestWishlistNotice.replace(/\s+/g,' ').slice(0,300)} | URL after: ${guest.url()}`,
    preconditions: 'Anonymous/no session', data: 'n/a', authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(guest, 'anon_wishlist_add_attempt');

  // Anonymous cart add + guest checkout attempt
  await guest.goto(`${BASE}/books`);
  await guest.waitForTimeout(400);
  await guest.locator('.product-box-add-to-cart-button, button:has-text("Add to cart")').first().click().catch(() => {});
  await guest.waitForTimeout(1000);
  await shot(guest, 'anon_add_to_cart');

  await guest.goto(`${BASE}/cart`);
  await guest.check('#termsofservice').catch(() => {});
  await guest.click('#checkout, button:has-text("Checkout")').catch(() => {});
  await guest.waitForTimeout(1200);
  const guestCheckoutUrl = guest.url();
  const guestCheckoutText = (await guest.locator('body').innerText()).replace(/\s+/g,' ').slice(0,500);
  record({
    capability: 'Checkout', action: 'Click Checkout from populated cart while ANONYMOUS (guest, not logged in)',
    result: `URL: ${guestCheckoutUrl} | Content: ${guestCheckoutText}`,
    preconditions: 'Anonymous session, 1 item in cart', data: 'n/a', authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });
  await shot(guest, 'anon_checkout_attempt');

  // Check for a "Checkout as Guest" option specifically
  const guestOptionVisible = await guest.locator('text=/guest/i').count();
  record({
    capability: 'Checkout', action: 'Check for explicit "checkout as guest" option/button on the page reached above',
    result: `Elements matching /guest/i text: ${guestOptionVisible}`,
    preconditions: 'Same as previous step', data: 'n/a', authRequired: false,
    evidence: 'OBSERVED_DIRECTLY'
  });

  await guestCtx.close();
  await browser.close();

  fs.writeFileSync(__dirname + '/observations.json', JSON.stringify(obs, null, 2));
  fs.writeFileSync(__dirname + '/test_account.json', JSON.stringify({ email, password }, null, 2));
  console.log('DONE. Observations:', obs.length);
})().catch(e => {
  console.error('SCRIPT ERROR:', e);
  fs.writeFileSync(__dirname + '/observations.json', JSON.stringify(obs, null, 2));
  process.exit(1);
});
