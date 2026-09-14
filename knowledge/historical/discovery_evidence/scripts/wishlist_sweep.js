// DISCOVERY-ONLY — wishlist presence sweep across catalog categories. Not automation, not a baseline artifact.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://demowebshop.tricentis.com';
const email = 'qe.discovery.1789149299815@example.com';
const password = 'Discover!2345';

const products = [
  { category: 'Computers', url: '/desktop-pc' },
  { category: 'Computers-grid', url: '/desktops' },
  { category: 'Electronics', url: '/digital-slr-camera' },
  { category: 'Electronics-grid', url: '/camera-photo' },
  { category: 'Apparel', url: '/blue-jeans' },
  { category: 'Apparel-grid', url: '/apparel-shoes' },
  { category: 'Digital Downloads', url: '/music-album-1' },
  { category: 'Digital Downloads-grid', url: '/digital-downloads' },
  { category: 'Books', url: '/computing-and-internet' },
  { category: 'Books-grid', url: '/books' },
  { category: 'Jewelry', url: '/diamond-tennis-bracelet' },
  { category: 'Jewelry-grid', url: '/jewelry' },
  { category: 'Gift Cards', url: '/25-virtual-gift-card' },
  { category: 'Gift Cards-grid', url: '/gift-cards' },
];

const WISHLIST_SELECTORS = [
  'text=/add to wishlist/i',
  '[onclick*="wishlist" i]',
  '.add-to-wishlist-button',
  'a[href*="addwishlist" i]',
  'input[value*="wishlist" i]',
];

async function checkPage(page, label) {
  await page.waitForTimeout(400);
  let found = null;
  for (const sel of WISHLIST_SELECTORS) {
    const loc = page.locator(sel);
    const c = await loc.count().catch(() => 0);
    if (c > 0) { found = { sel, count: c }; break; }
  }
  const buttons = await page.locator('.buttons input[type=button], .add-to-cart input[type=button]').evaluateAll(
    els => els.map(e => e.value || e.textContent)
  ).catch(() => []);
  let clickResult = 'N/A - no wishlist control found';
  if (found) {
    try {
      const loc = page.locator(found.sel).first();
      await loc.click({ timeout: 3000 });
      await page.waitForTimeout(1000);
      const notice = await page.locator('#bar-notification, .content').first().innerText().catch(() => 'no notice text');
      clickResult = `Clicked OK. Notice/result: ${notice.replace(/\s+/g, ' ').slice(0, 200)}. URL after click: ${page.url()}`;
    } catch (e) {
      clickResult = `Found but click failed: ${e.message.split('\n')[0]}`;
    }
  }
  return {
    label,
    url: page.url(),
    visibleButtonsOnPage: buttons,
    wishlistControlFound: !!found,
    wishlistSelectorMatched: found ? found.sel : null,
    clickResult,
  };
}

(async () => {
  const browser = await chromium.launch();
  const results = [];

  // Anonymous pass
  const anonCtx = await browser.newContext();
  const anonPage = await anonCtx.newPage();
  for (const p of products) {
    await anonPage.goto(`${BASE}${p.url}`).catch(e => results.push({ category: p.category, error: `nav failed: ${e.message}` }));
    const r = await checkPage(anonPage, `${p.category} (ANONYMOUS) - ${p.url}`);
    results.push({ category: p.category, state: 'anonymous', url: p.url, ...r });
  }
  await anonCtx.close();

  // Authenticated pass
  const authCtx = await browser.newContext();
  const authPage = await authCtx.newPage();
  await authPage.goto(`${BASE}/login`);
  await authPage.fill('#Email', email);
  await authPage.fill('#Password', password);
  await authPage.click('.login-button');
  await authPage.waitForTimeout(800);
  for (const p of products) {
    await authPage.goto(`${BASE}${p.url}`).catch(e => results.push({ category: p.category, error: `nav failed: ${e.message}` }));
    const r = await checkPage(authPage, `${p.category} (AUTHENTICATED) - ${p.url}`);
    results.push({ category: p.category, state: 'authenticated', url: p.url, ...r });
  }
  await authCtx.close();

  await browser.close();
  fs.writeFileSync(__dirname + '/wishlist_sweep_results.json', JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
})().catch(e => { console.error('SWEEP ERROR:', e); process.exit(1); });
