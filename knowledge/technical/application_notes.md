# Technical / Application Notes — Demo Web Shop

**source_type:** `technical_note` (authority tier 3 — supporting only; can never redefine what an Approved SRS requirement means). Every fact below is drawn directly from the Approved SRS (`requirements/MVP2_SRS_v1.0_APPROVED.md`) or from the persisted historical discovery evidence in `knowledge/historical/discovery_evidence/`. Nothing here is a new technical claim beyond what those sources already establish.

## Platform
- The SUT is a third-party, publicly shared **nopCommerce** demo instance (Approved SRS §11). MVP2 does not control this environment.
- No SLA, uptime guarantee, or reset schedule is published or known (Approved SRS §11; DATA-OQ-01 parked).

## Checkout engine (from historical captures)
- Authenticated and guest checkout both render through the same one-page checkout engine at `/onepagecheckout` (source: `knowledge/historical/discovery_evidence/captures/checkout_00.html` … `checkout_final.html`, `guest_checkout_step1.html`).
- An anonymous user initiating checkout is first routed through `/login/checkoutasguest`, which offers an explicit "Checkout as Guest" control alongside a returning-customer login form (source: `knowledge/historical/discovery_evidence/captures/anon_checkout.html`).
- Checkout step transitions are AJAX-driven within the same URL (no per-step page navigation) — see REQ-ACO-01/REQ-GCO-02.

## Discovery method (for anyone re-running or extending discovery)
- All CP-MVP2-01 discovery used headless Chromium via Playwright, single browser, single session, on 2026-09-11 (Approved SRS §11, §12).
- The probe scripts in `knowledge/historical/discovery_evidence/scripts/` show the exact selectors and navigation sequence used; they are historical-tier artifacts, not a maintained automation library.

## Explicit non-facts (do not infer beyond this document)
- No page-load/response-time figures are recorded as facts (Approved SRS §9 — performance thresholds are TBD, not derived from discovery).
- No statement here should be read as describing any system other than this specific shared demo instance on the date discovery was performed.
