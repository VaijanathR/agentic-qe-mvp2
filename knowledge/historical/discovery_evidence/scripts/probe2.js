// DISCOVERY-ONLY PROBE 2 — checkout walkthrough, not test automation, not a baseline artifact.
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

  await page.goto(`${BASE}/cart`);
  await page.check('#termsofservice').catch(e => console.log('terms check failed', e.message));
  await page.click('#checkout');
  await page.waitForTimeout(1500);
  console.log('STEP0 URL:', page.url());
  fs.writeFileSync(__dirname + '/checkout_00.html', await page.content());

  // Fill billing address (new address form) before attempting to advance
  await page.selectOption('#BillingNewAddress_CountryId', { label: 'United States' }).catch(e => console.log('country select failed', e.message));
  await page.fill('#BillingNewAddress_City', 'Springfield').catch(()=>{});
  await page.fill('#BillingNewAddress_Address1', '123 QE Street').catch(()=>{});
  await page.fill('#BillingNewAddress_ZipPostalCode', '12345').catch(()=>{});
  await page.fill('#BillingNewAddress_PhoneNumber', '5551234567').catch(()=>{});
  await page.waitForTimeout(300);
  await page.selectOption('#BillingNewAddress_StateProvinceId', { index: 1 }).catch(()=>{});
  await page.waitForTimeout(300);
  fs.writeFileSync(__dirname + '/checkout_00_filled.html', await page.content());

  for (let i = 1; i <= 10; i++) {
    await page.waitForTimeout(800);
    const url = page.url();
    console.log(`--- STEP ${i} URL: ${url}`);
    const html = await page.content();
    fs.writeFileSync(`${__dirname}/checkout_${String(i).padStart(2,'0')}.html`, html);

    // Try common nopCommerce one-page-checkout continue buttons
    const selectors = [
      '.new-address-next-step-button',
      '#billing-buttons-container input[type=submit]',
      '.shipping-address-next-step-button',
      '#shipping-buttons-container input[type=submit]',
      '.shipping-method-next-step-button',
      '#shipping-method-buttons-container input[type=submit]',
      '.payment-method-next-step-button',
      '#payment-method-buttons-container input[type=submit]',
      '.payment-info-next-step-button',
      '#payment-info-buttons-container input[type=submit]',
      '.confirm-order-next-step-button',
      '#confirm-order-buttons-container input[type=submit]'
    ];
    // Generically fill any empty, visible, required text inputs (e.g. credit card fields) with dummy data
    const requiredInputs = await page.locator('input[data-val-required]:visible').all();
    for (const inp of requiredInputs) {
      const val = await inp.inputValue().catch(() => '');
      if (!val) await inp.fill('1234567890').catch(() => {});
    }
    // Pick first non-default option on any visible required select still at default
    const requiredSelects = await page.locator('select[data-val-required]:visible').all();
    for (const sel of requiredSelects) {
      const val = await sel.inputValue().catch(() => '');
      if (val === '0' || val === '') await sel.selectOption({ index: 1 }).catch(() => {});
    }

    let clicked = false;
    for (const sel of selectors) {
      const loc = page.locator(`${sel}:visible`);
      if (await loc.count()) {
        console.log('  clicking (visible):', sel);
        await loc.first().click({ timeout: 5000 }).catch(e => console.log('  click failed', e.message.split('\n')[0]));
        clicked = true;
        break;
      }
    }
    if (!clicked) {
      console.log('  No known continue-button selector matched. Stopping loop.');
      break;
    }
    await page.waitForTimeout(2000);
    const errs = await page.locator('.field-validation-error, .validation-summary-errors').allTextContents();
    if (errs.some(t => t.trim())) console.log('  VALIDATION ERRORS:', errs.filter(t=>t.trim()));
  }

  console.log('FINAL URL:', page.url());
  fs.writeFileSync(__dirname + '/checkout_final.html', await page.content());
  await page.close();
  await browser.close();
})().catch(e => { console.error('PROBE2 ERROR:', e); process.exit(1); });
