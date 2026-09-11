# Agentic QE MVP2 — Draft Software Requirements Specification (SRS)

**Checkpoint:** CP-MVP2-01 — Application Discovery & Approved SRS
**Document status:** `DRAFT — REQUIRES HUMAN APPROVAL` (this is **not** the Approved SRS)
**System Under Test:** Demo Web Shop — https://demowebshop.tricentis.com/ (third-party, public, shared nopCommerce demo instance)
**Discovery basis:** One static (HTTP-fetch) discovery pass and three stateful (real browser, session-aware) discovery passes performed on 2026-09-11, including a dedicated wishlist-eligibility sweep.
**Author:** Agentic session (Claude Code), on behalf of the user (vaijanath.ruge@gmail.com)

---

## Evidence Hierarchy (used throughout this document)

Every requirement below cites an **Evidence Strength** using this fixed hierarchy, strongest first:

1. **APPROVED BASELINE** — a previously human-approved requirement or architecture document. *No such baseline exists yet for MVP2; this tier is not used anywhere in this draft.*
2. **DIRECT SYSTEM EVIDENCE** — behavior directly observed via a live, stateful, JS-executing browser session against the real SUT during this discovery effort.
3. **CURRENT TESTING ARTIFACT** — the specific capture (script output, saved HTML, JSON result, screenshot) produced during this discovery effort that substantiates a Direct System Evidence claim.
4. **HISTORICAL EVIDENCE** — findings from the earlier static (non-stateful, non-JS) HTTP-fetch discovery pass in this same effort; lower confidence, and superseded wherever a later stateful check contradicts or refines it (this is called out explicitly where it occurs).
5. **AGENT INFERENCE** — the agent's own interpretation, extrapolation, or hypothesis, not directly observed. Never sufficient on its own to justify a requirement; always flagged.

**Important:** Evidence Strength describes *how well the underlying fact is observed*. It is independent of **Status**, which for every requirement in this document is fixed at `DRAFT — REQUIRES HUMAN APPROVAL` — even a requirement backed by strong Direct System Evidence is not yet an approved business requirement until a human/business owner ratifies it.

**Classification** (applied per requirement, per the checkpoint instructions):
- **OBSERVED** — behavior directly seen during discovery
- **DERIVED/CANDIDATE** — a requirement statement inferred from observed behavior, proposed for approval
- **INFERENCE** — the agent's own reasoning/extrapolation beyond what was directly seen
- **OPEN QUESTION** — evidence is incomplete or ambiguous; explicitly not asserted as fact
- **REQUIRES HUMAN APPROVAL** — applies to every requirement in this document without exception

---

## 1. Purpose

This document translates the CP-MVP2-01 application-discovery evidence (static + stateful browser discovery of the Demo Web Shop) into a structured, traceable set of **draft** candidate requirements for MVP2. It exists to give a human/business reviewer a concrete basis for approving, amending, or rejecting scope before any knowledge base (CP-MVP2-02), test case generation (CP-MVP2-03), test data generation (CP-MVP2-04), or automation (CP-MVP2-05) work begins. Per the MVP2 core principles, **the Approved SRS — not this draft — is the eventual source of truth**; this draft is the proposal that must be reviewed to produce that baseline.

## 2. MVP2 Scope

Based on discovery evidence, the following capability areas were directly exercised and are proposed as in-scope for MVP2:

- Customer registration and authentication
- Password recovery (UI-level only — see §12 limitations)
- Product search and category browsing
- Product configuration (attribute selection, including mandatory-attribute enforcement)
- Shopping cart management
- Wishlist (product-detail-page capability — see §6.8 for important scope caveats)
- Guest checkout and authenticated checkout
- Shipping method selection and payment method selection
- Order confirmation and order history
- Basic customer account areas (Customer info, Addresses, Orders)

This scope reflects **what was observed to exist and largely function**, not a business decision about what MVP2 *should* cover — that decision is reserved for the human approver (see §15).

## 3. Out of Scope / POST-MVP — PARKED

Carried over from the approved MVP2 architecture (README.md) and reinforced by discovery:

- Security testing and penetration testing — **POST-MVP — PARKED** (per existing project governance)
- Full application/site coverage (only the capability areas in §2 were investigated)
- Multiple applications, CI/CD integration, distributed browser grid, multi-VM orchestration, large-scale parallel execution — **POST-MVP — PARKED** (per existing project governance)
- Admin/back-office functionality (not investigated; no admin URL was discovered or accessed)
- Email delivery/content verification for password recovery (UI acceptance only was observed — see §12)
- Deep verification of "Downloadable products," "Back in stock subscriptions," and "Reward points" account areas — menu presence only was observed, not their functional behavior (**PARKED pending further discovery**)
- Cross-browser and mobile-responsive verification (all discovery was performed on headless Chromium only)
- Any load, concurrency, or performance-threshold testing (see §9)
- Treating the specific test account, order number, or product IDs used during discovery as reusable fixtures (see §10, §13)
- A canonical Gift Card wishlist test scenario — **PARKED** until the required-field interaction (recipient/sender name & email) blocking the wishlist-add attempt is further investigated (see §6.8)

## 4. Actors and Personas

| Persona | Basis | Evidence Strength |
|---|---|---|
| **Anonymous / Guest shopper** | Directly observed browsing, searching, adding to cart, adding to wishlist (on eligible products), and completing checkout as a guest, all without an account | DIRECT SYSTEM EVIDENCE |
| **Registered / Authenticated customer** | Directly observed registering, logging in, managing cart/wishlist, completing checkout, and viewing order history | DIRECT SYSTEM EVIDENCE |
| **Admin / site operator** | Not investigated — inferred to exist only because the platform is nopCommerce and a placeholder string ("edit this in the admin site") appeared in the login page copy | AGENT INFERENCE — **OUT OF SCOPE** for MVP2 unless a human approver adds it |

No role-based tiers (e.g., manager, support agent) or B2B personas were observed anywhere in the storefront.

## 5. Business Journeys

These are the **candidate** high-value E2E journeys, now updated with stateful confirmation. None are approved; all require human sign-off before being used to drive later checkpoints.

| Journey ID | Journey | Evidence Strength | Notes |
|---|---|---|---|
| J-01 | Registration → auto-login → Browse/Search → Add to cart → Authenticated checkout → Order confirmation → Order history | DIRECT SYSTEM EVIDENCE | Fully walked end-to-end in this discovery; produced a real (non-reusable) order number |
| J-02 | Anonymous browse → Add to cart → "Checkout as Guest" → Billing/Shipping/Payment → Order confirmation | DIRECT SYSTEM EVIDENCE | Confirmed as a first-class, explicitly-offered path, not merely a fallback |
| J-03 | Login → Configurable product (mandatory attribute) → blocked Add to Cart → correct selection → Cart → Checkout | DIRECT SYSTEM EVIDENCE | Good candidate for both positive and negative test design once approved |
| J-04 | Cart quantity edge cases (increase, decrease to 0) | DIRECT SYSTEM EVIDENCE | Smaller, focused journey; qty=0 silently empties the cart |
| J-05 | Product-detail wishlist add (on an eligible product) → view on Wishlist page → Add to cart from Wishlist | DIRECT SYSTEM EVIDENCE for add + view; **OPEN QUESTION** for "Add to cart from Wishlist" (button observed present on the wishlist page but the action itself was not exercised) | Must not be scoped using a Computers/Apparel/Books/Jewelry product, since the control was not observed on those; must not use Gift Cards as the canonical example (see §6.8) |

## 6. Functional Requirements

Every requirement below carries: ID, Statement, Rationale, Evidence Basis, Evidence Strength, Acceptance Criteria, Actor, Related Journey, Classification, and Status. **Status is `DRAFT — REQUIRES HUMAN APPROVAL` for every requirement without exception.**

### 6.1 Registration

| Field | REQ-REG-01 | REQ-REG-02 | REQ-REG-03 | REQ-REG-04 | REQ-REG-05 |
|---|---|---|---|---|---|
| Statement | The system shall require First name, Last name, Email, Password, and Confirm password on registration, rejecting submission with field-specific messages when any are blank | The system shall reject registration when Password and Confirm password do not match | The system shall reject registration when the Email field is not a validly formatted email address | The system shall reject registration when the supplied email is already associated with an existing account | Upon successful registration, the system shall automatically authenticate the new user without a separate login step |
| Rationale | Prevents incomplete customer records; baseline data-quality gate | Prevents account lockout from a typo'd password | Prevents undeliverable/invalid contact email on file | Prevents duplicate accounts per email | Reduces friction — new customer reaches an authenticated state immediately |
| Evidence Basis | Empty-form submission to `/register` returned: "First name is required. / Last name is required. / Email is required. / Password is required." (shown twice) | Submission with mismatched passwords returned: "The password and confirmation password do not match." | Submission with `not-an-email` returned: "Wrong email" | Submission with an email already used by the discovery test account returned: "The specified email already exists" | Post-submission page (`/registerresult/1`) header immediately showed the account email and a "Log out" link, with no intervening login prompt |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (CURRENT TESTING ARTIFACT: `discover.js` run, `01_register_empty_validation.png`) | DIRECT SYSTEM EVIDENCE (`02_register_password_mismatch.png`) | DIRECT SYSTEM EVIDENCE (`probe3_results.json` → `invalidEmailValidation`) | DIRECT SYSTEM EVIDENCE (`probe3_results.json` → `duplicateEmailValidation`) | DIRECT SYSTEM EVIDENCE (`03_register_success.png`) |
| Acceptance Criteria | Given all fields blank, when Register is submitted, then all five required-field messages are shown and no account is created | Given valid names/email and mismatched passwords, when submitted, then the mismatch message is shown and no account is created | Given a malformed email, when submitted, then "Wrong email" is shown and no account is created | Given an email already on file, when submitted, then the duplicate-email message is shown and no account is created | Given a unique email and matching valid passwords, when submitted, then the resulting page shows the user as logged in without requiring a separate login |
| Actor | Guest (pre-registration) | Guest | Guest | Guest | Guest → becomes Authenticated |
| Journey | J-01 | J-01 | J-01 | J-01 | J-01 |
| Classification | DERIVED/CANDIDATE (from OBSERVED behavior) | DERIVED/CANDIDATE | DERIVED/CANDIDATE | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (REG-OQ-01):** Whether auto-login-after-registration is an intended business decision or an artifact of this specific demo configuration (nopCommerce's registration mode is admin-configurable) is unknown. A human approver should confirm this is the desired behavior for whatever target system MVP2 ultimately governs, rather than assuming this demo's behavior is the intended design.

### 6.2 Authentication / Login

| Field | REQ-AUTH-01 | REQ-AUTH-02 | REQ-AUTH-03 |
|---|---|---|---|
| Statement | The system shall authenticate a user given a correct, registered email and password combination | The system shall reject login with an incorrect password using a generic error that does not disclose which field was wrong | A newly registered account shall be able to log in explicitly and successfully immediately after registration, with no observed verification gate |
| Rationale | Core access-control function | Avoids leaking account-enumeration information | Confirms no hidden onboarding blocker exists between registration and usable login |
| Evidence Basis | Logging in with the discovery account's correct email/password redirected to `/` with the header showing the account email and "Log out" | Login attempt with correct email + wrong password returned: "Login was unsuccessful. Please correct the errors and try again. / The credentials provided are incorrect" | The discovery account was explicitly logged out after registration, then logged back in successfully on the very next action, with no email-verification prompt encountered |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`05_login_success.png`) | DIRECT SYSTEM EVIDENCE (`04_login_invalid_credentials.png`) | DIRECT SYSTEM EVIDENCE (same session as REQ-REG-05) |
| Acceptance Criteria | Given valid credentials, when submitted, then the user reaches an authenticated state | Given an incorrect password, when submitted, then a generic incorrect-credentials message is shown and no session is created | Given a just-registered account, when the user logs out and back in with the same credentials, then login succeeds without additional steps |
| Actor | Guest → Authenticated | Guest | Guest → Authenticated |
| Journey | J-01, J-03 | J-01 | J-01 |
| Classification | DERIVED/CANDIDATE | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**HISTORICAL EVIDENCE (not re-verified statefully):** A "Remember me" checkbox is present on the login form (static discovery pass). Its actual session-persistence effect was not exercised in the stateful pass — captured here as HISTORICAL EVIDENCE only, not a confirmed requirement basis.

### 6.3 Password Recovery

| Field | REQ-PWR-01 |
|---|---|
| Statement | The system shall accept a password-recovery request for a registered email via `/passwordrecovery` without displaying an error |
| Rationale | Enables account-access self-service |
| Evidence Basis | Submitting the discovery account's email on the recovery form completed without any validation error being shown |
| Evidence Strength | DIRECT SYSTEM EVIDENCE for the UI-acceptance behavior only |
| Acceptance Criteria | Given a valid registered email, when password recovery is submitted, then the UI shows an acceptance state and no error |
| Actor | Guest |
| Journey | Supporting flow to J-01/J-02 |
| Classification | DERIVED/CANDIDATE (UI acceptance only) |
| Status | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (PWR-OQ-01):** Whether an actual recovery email is sent, its content, the reset-link/token behavior, and whether the reset flow itself works were **not** verified — no mailbox access was available during discovery. This must not be assumed functional; it requires dedicated follow-up before any password-reset requirement is treated as confirmed.

### 6.4 Search

| Field | REQ-SRCH-01 | REQ-SRCH-02 |
|---|---|---|
| Statement | The system shall return matching product results for a valid keyword search | The system shall display an explicit "no results" message when a search matches nothing |
| Rationale | Core product-discovery function | Prevents an ambiguous blank-results experience |
| Evidence Basis | Searching "computer" returned 4 result cards at `/search?Q=computer&As=false&Cid=0&Isc=false&Mid=0&Pf=&Pt=&Sid=false` | Searching a nonsense keyword returned the exact text: "No products were found that matched your criteria." |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`probe5_results.json`) | DIRECT SYSTEM EVIDENCE (`probe5_results.json`) |
| Acceptance Criteria | Given a keyword matching existing products, when searched, then at least one result card is displayed | Given a keyword matching nothing, when searched, then the "No products were found..." message is shown and zero result cards render |
| Actor | Guest, Authenticated | J-01, J-02 |
| Journey | J-01, J-02 | J-01, J-02 |
| Classification | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**HISTORICAL EVIDENCE:** Advanced search options (category incl. subcategory toggle, price range, manufacturer filter, "search in description" checkbox) were observed only in the static discovery pass; their actual filtering effect was not stress-tested statefully. Listed here as HISTORICAL EVIDENCE, not confirmed via direct interaction — any requirement built on these specific filters should be re-verified before approval.

### 6.5 Product Browsing

| Field | REQ-BRW-01 |
|---|---|
| Statement | The system shall organize the catalog into at least the following top-level categories, each independently browsable: Books, Computers, Electronics, Apparel & Shoes, Digital Downloads, Jewelry, Gift Cards |
| Rationale | Establishes the catalog navigation structure that all other browsing/search/cart/wishlist requirements assume |
| Evidence Basis | All 7 categories were directly navigated to and rendered product grids during both the original discovery pass and the wishlist sweep | 
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`wishlist_sweep_results.json` covers all 7 category grid pages) |
| Acceptance Criteria | Given the main navigation, when any of the 7 category links is selected, then a grid of products for that category renders |
| Actor | Guest, Authenticated |
| Journey | J-01, J-02 |
| Classification | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL |

**HISTORICAL EVIDENCE (not re-verified statefully):** Category-grid sort options (Position/Name A-Z/Z-A/Price Low-High/High-Low/Created on), page-size options (4/8/12), and price-bucket filters (Under $25 / $25–$50 / Over $50) were observed only via the static pass. No stateful test of actually applying a sort/filter and confirming the result set changed was performed.

### 6.6 Product Configuration

| Field | REQ-CFG-01 |
|---|---|
| Statement | For a configurable product that declares a mandatory attribute, the system shall block "Add to Cart" and display a specific message identifying the missing attribute until it is selected |
| Rationale | Prevents incomplete/invalid orders for build-to-order products |
| Evidence Basis | Attempting to add "Build your own computer" to the cart without selecting an HDD option returned the blocking message "Please select HDD" and the item was not added |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`probe5_results.json` → `addToCartNotice`) |
| Acceptance Criteria | Given a configurable product with a mandatory attribute left unselected, when Add to Cart is attempted, then a message naming the missing attribute is shown and the cart is not modified |
| Actor | Guest, Authenticated |
| Journey | J-03 |
| Classification | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (CFG-OQ-01):** Whether selecting a priced attribute option visibly updates the displayed price before Add to Cart was **inconclusive** in this discovery — one dropdown selection produced no visible price change, but the priced attribute(s) on this product may be controls other than the dropdown tested (e.g., radio buttons or checkboxes not yet exercised). **No requirement is stated for dynamic price recalculation on attribute change** until this is re-confirmed; asserting it now would exceed the evidence.

### 6.7 Cart

| Field | REQ-CART-01 | REQ-CART-02 | REQ-CART-03 | REQ-CART-04 |
|---|---|---|---|---|
| Statement | The system shall allow a product to be added to the cart, confirming the addition to the user | Updating a line item's quantity shall recalculate that line's subtotal and the cart's total accordingly | Setting a line item's quantity to 0 and applying the update shall remove that line item without a confirmation prompt | The system shall allow explicit removal of a cart line item via a remove control, and shall show an "empty cart" state with no active checkout when the cart has no items |
| Rationale | Core cart function | Ensures pricing accuracy as quantities change | Documents actual (not assumed) zero-quantity behavior, relevant to negative-path test design | Core cart function; prevents proceeding to checkout with nothing to purchase |
| Evidence Basis | Adding "Computing and Internet" produced an AJAX notice: "The product has been added to your shopping cart" | Cart at qty=1 showed unit 10.00/subtotal 10.00/total 10.00; after updating to qty=3, subtotal became 30.00 and cart total became 30.00, unit price unchanged | Setting quantity to 0 and clicking "Update shopping cart" resulted in the cart returning to "Your Shopping Cart is empty!" with no dialog | Checking the line-item remove checkbox and updating returned the cart to its empty state; navigating to an empty cart shows "Your Shopping Cart is empty!" with the checkout breadcrumb (Cart→Address→Shipping→Payment→Confirm→Complete) but no active checkout action |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`probe6_results.json`) | DIRECT SYSTEM EVIDENCE (`probe6_results.json`) | DIRECT SYSTEM EVIDENCE (`probe6_results.json` → `qty0_result`) | DIRECT SYSTEM EVIDENCE (`probe.js`/`probe2.js` cart captures) |
| Acceptance Criteria | Given a product page, when Add to Cart is used, then a success notice appears and the cart item count increments | Given a cart with 1 unit at price P, when quantity is changed to N, then subtotal = P×N and cart total reflects it | Given a cart line item, when its quantity is set to 0 and Update is applied, then the line item no longer appears and no prompt is shown | Given an empty cart, when the cart page is viewed, then an empty-state message is shown and no checkout can proceed |
| Actor | Guest, Authenticated | Guest, Authenticated | Guest, Authenticated | Guest, Authenticated |
| Journey | J-01, J-02 | J-04 | J-04 | J-01, J-02, J-04 |
| Classification | DERIVED/CANDIDATE | DERIVED/CANDIDATE | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**Cart persistence across authentication — carefully worded per known evidence limits.**

| Field | REQ-CART-05 |
|---|---|
| Statement | An item added to the cart during an anonymous session shall remain present in the cart after the same browser session subsequently authenticates |
| Rationale | Avoids losing shopper intent when a guest chooses to log in mid-shopping |
| Evidence Basis | An item added to the cart anonymously was still present in the cart immediately after logging in, within the same browser session |
| Evidence Strength | DIRECT SYSTEM EVIDENCE for the observed outcome only (`probe3_results.json` → `cartAfterLoginRowCount`, `cartAfterLoginText`) |
| Acceptance Criteria | Given an anonymous cart with 1+ items, when the user logs in within the same session, then those items remain visible in the cart afterward |
| Actor | Guest → Authenticated |
| Journey | J-01 (guest-to-account transition) |
| Classification | DERIVED/CANDIDATE, narrowly scoped to the observed outcome |
| Status | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (CART-OQ-01) — explicit caution:** This discovery **did not** establish the underlying mechanism. It is **not confirmed** whether this is a true "cart merge" (combining two previously-distinct carts, e.g. if the account already had its own separate saved cart) versus simple session/cookie continuity (the same anonymous cart simply continuing to be addressed after login, with no separate account cart involved). REQ-CART-05 is deliberately worded to the observed outcome only. **Do not generalize this into a "cart merge" requirement** without a dedicated test where the account has a pre-existing distinct cart before the anonymous item is added.

### 6.8 Wishlist

> **Scope framing (read before the table):** Wishlist is a real, functioning, product-detail-page capability. It is **not available on every product**, and it is **never available from category grid/listing pages**. The exact catalog-wide rule determining which products expose it is **not known** and must not be invented. The requirements below are deliberately scoped to what was directly observed, not generalized to "all products."

| Field | REQ-WISH-01 | REQ-WISH-02 | REQ-WISH-03 |
|---|---|---|---|
| Statement | On product detail pages where an "Add to Wishlist" control is present, the system shall allow the current user (anonymous or authenticated) to add that product to their wishlist | A successful wishlist addition shall show a confirmation notice and the item shall subsequently appear on the `/wishlist` page with its price and a remove/add-to-cart action | The wishlist shall be usable by anonymous users, including a persistent, shareable wishlist URL, without requiring an account |
| Rationale | Lets shoppers save items of interest, on the subset of products where this is offered | Confirms the action has a real, durable effect rather than being cosmetic | Reduces friction for wishlist usage prior to registration |
| Evidence Basis | An "Add to Wishlist" control was directly found and successfully clicked on sampled products in **Electronics** (Digital SLR Camera) and **Digital Downloads** (Music 2/Music Album 1); the same control was **not found** on sampled products in Computers, Apparel, Books, or Jewelry, nor on any of the 7 category grid pages | After clicking Add to Wishlist on the two products above, `/wishlist` showed both items ("Digital SLR Camera - Black" 670.00, "Music 2" 10.00) with Remove and Add to cart actions | The `/wishlist` page (in an anonymous session) displayed a "Your wishlist URL for sharing" link in the form `https://demowebshop.tricentis.com/wishlist/<guid>` |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`wishlist_sweep_results.json` — 7 categories × product-detail + grid × anonymous + authenticated = 28 checks) | DIRECT SYSTEM EVIDENCE (`wishlist_confirm.js` / `wishlist_confirm.html`) | DIRECT SYSTEM EVIDENCE (`wishlist_confirm.js` output) |
| Acceptance Criteria | Given a product detail page that exposes an Add to Wishlist control, when clicked, then a wishlist-add confirmation is shown | Given an item was just added to the wishlist, when `/wishlist` is viewed, then that item appears with correct price and available actions | Given no account, when a user adds items to the wishlist and views `/wishlist`, then a shareable URL for that wishlist is displayed |
| Actor | Guest, Authenticated | Guest, Authenticated | Guest |
| Journey | J-05 | J-05 | J-05 |
| Classification | DERIVED/CANDIDATE, explicitly scoped to "where the control is present" | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (WISH-OQ-01):** The catalog-wide rule for which products expose "Add to Wishlist" is unknown. Only one product per category was sampled (7 categories); within a category, other products may or may not follow the same pattern as the one sampled. **No requirement in this document should be read as "wishlist is available for [category] products"** — only for the specific sampled products named above.

**OPEN QUESTION (WISH-OQ-02) — Gift Cards parked:** An "Add to Wishlist" control **is** visible and clickable on the sampled Gift Card product, but clicking it surfaced product-specific required-field validation errors (recipient/sender name and email) instead of a wishlist-add confirmation. It is **not known** whether the wishlist-add succeeds once those fields are populated, or whether gift-card products are incompatible with the wishlist action entirely. **Per explicit instruction, Gift Cards must not be used as the canonical wishlist example until this is further investigated** (tracked as PARKED in §3).

**OPEN QUESTION (WISH-OQ-03):** "Add to cart from Wishlist" — a button captioned "Add to cart" was observed present on the `/wishlist` page line items, but actually invoking it and confirming the resulting cart state was not exercised in this discovery. No requirement is stated for this action yet.

### 6.9 Guest Checkout

| Field | REQ-GCO-01 | REQ-GCO-02 |
|---|---|---|
| Statement | The system shall allow an anonymous user with items in their cart to complete checkout via an explicit "Checkout as Guest" option, without creating an account | Guest checkout shall use the same step sequence and screens as authenticated checkout (Billing → Shipping Address → Shipping Method → Payment Method → Payment Info → Confirm → Completed) |
| Rationale | Reduces purchase friction for shoppers unwilling to register | Avoids maintaining two divergent checkout implementations conceptually, and simplifies later automation scoping |
| Evidence Basis | Clicking Checkout as an anonymous user with 1 cart item routed to `/login/checkoutasguest?returnUrl=%2Fcart`, an interstitial offering "Checkout as a guest or register" with a "Checkout as Guest" button; clicking it loaded `/onepagecheckout` with the header still showing "Register / Log in" (i.e., genuinely anonymous) | The guest session's `/onepagecheckout` rendered the same Billing Address step structure (empty, since no saved address existed) as the authenticated flow |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`probe3_results.json` → `anonCheckoutUrl`/`anonCheckoutText`; `probe4.js` output) | DIRECT SYSTEM EVIDENCE (`guest_checkout_step1.html`) |
| Acceptance Criteria | Given an anonymous cart with items, when Checkout is initiated, then a guest-or-register interstitial appears with a working "Checkout as Guest" option that proceeds without login | Given a guest proceeding through checkout, then the same named steps appear as for an authenticated user, with an empty (not pre-filled) address form |
| Actor | Guest | Guest |
| Journey | J-02 | J-02 |
| Classification | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

### 6.10 Authenticated Checkout

| Field | REQ-ACO-01 | REQ-ACO-02 | REQ-ACO-03 |
|---|---|---|---|
| Statement | For an authenticated user with items in the cart, the system shall provide a checkout sequence of: Billing Address → Shipping Address → Shipping Method → Payment Method → Payment Information → Confirm Order → Order Completed | If the account has a previously saved address, the checkout's address steps shall offer that saved address for reuse via a selection control, rather than forcing re-entry | The Billing/Shipping address form shall require First name, Last name, Email, Country, City, Address 1, Zip/postal code, and Phone number, with Company, Address 2, and Fax number optional |
| Rationale | Establishes the canonical checkout path for the majority of transactions | Reduces repeat-purchase friction | Ensures sufficient address data is captured for fulfillment |
| Evidence Basis | A full authenticated checkout was walked end-to-end, capturing HTML at each step, ending in a real order-confirmation screen and a corresponding entry in Order History | After a billing address was saved in one checkout attempt, a subsequent checkout's Shipping Address step showed a `shipping-address-select` dropdown pre-populated with that saved address | Directly observed `data-val-required` markers and matching inline required-field messages on First name, Last name, Email, Country, City, Address1, Zip/postal code, and Phone number; Company, Address2, and Fax number carried no such marker |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`checkout_00.html` through `checkout_final.html`, `probe2_run.log`) | DIRECT SYSTEM EVIDENCE (`checkout_02.html`) | DIRECT SYSTEM EVIDENCE (`checkout_00.html` field markup) |
| Acceptance Criteria | Given an authenticated user with a non-empty cart, when Checkout is initiated, then all six named steps are presented in order and a completed order results | Given an account with a saved address, when a checkout address step is reached, then that address is offered via a dropdown instead of a blank form | Given the address form, when required fields are left blank, then progression to the next step is blocked |
| Actor | Authenticated | Authenticated | Guest, Authenticated |
| Journey | J-01 | J-01 | J-01, J-02 |
| Classification | DERIVED/CANDIDATE | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (ACO-OQ-01):** The exact inline validation message text shown when a required checkout field is left blank was not cleanly isolated (progression was blocked, but the specific error copy at that moment was not captured). Needed before this becomes a precise, testable acceptance criterion.

### 6.11 Shipping

| Field | REQ-SHIP-01 |
|---|---|
| Statement | At the Shipping Method step, the system shall present multiple shipping method options for the customer to choose from |
| Rationale | Allows the customer to select a fulfillment speed/cost tradeoff |
| Evidence Basis | Three shipping methods were presented: Ground, Next Day Air, 2nd Day Air |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`checkout_03.html`) — **for the existence of the options only** |
| Acceptance Criteria | Given the Shipping Method step, when reached, then at least the observed method(s) are selectable |
| Actor | Guest, Authenticated |
| Journey | J-01, J-02 |
| Classification | DERIVED/CANDIDATE (existence of the choice), **explicitly not extended to cost** |
| Status | DRAFT — REQUIRES HUMAN APPROVAL |

**IMPORTANT — cost explicitly NOT generalized:** In the one discovery run performed, all three shipping methods showed **$0.00** for the specific cart contents (a single $10.00 book) and address used. **This is recorded as a session-specific observation only.** No requirement in this document states "shipping is free" or defines any shipping-cost rule, threshold, or calculation model. Whether shipping cost varies by weight, destination, order value, or method is an **OPEN QUESTION (SHIP-OQ-01)** requiring dedicated follow-up (e.g., a heavier/multi-item cart or a non-US address) before any cost-related requirement can be drafted.

### 6.12 Payment

| Field | REQ-PAY-01 | REQ-PAY-02 | REQ-PAY-03 |
|---|---|---|---|
| Statement | At the Payment Method step, the system shall present multiple payment method options | Selecting a payment method may add a method-specific fee that is reflected in the order total shown at Confirm Order | Selecting "Cash On Delivery" as the payment method shall not require entry of any card/payment details at the Payment Information step |
| Rationale | Supports customers without card-based payment | Ensures total price transparency including payment surcharges | Matches the nature of a pay-on-delivery method |
| Evidence Basis | Four payment methods were observed: Cash On Delivery (COD), Check / Money Order, Credit Card, Purchase Order | With COD selected, the Confirm Order totals showed: Sub-Total 10.00, Shipping 0.00, Payment method additional fee **7.00**, (Tax present but not isolated), Order Total **17.00** | The Payment Information step for COD displayed only the text "You will pay by COD" with no form fields |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`checkout_04.html`) | DIRECT SYSTEM EVIDENCE (`checkout_06.html`) — **specific to this one cart/session, not a general fee schedule** | DIRECT SYSTEM EVIDENCE (`checkout_05.html`) |
| Acceptance Criteria | Given the Payment Method step, when reached, then at least the four observed methods are selectable | Given COD is selected for this specific $10.00 cart, then the order total includes a $7.00 addition, as observed | Given COD is selected, when the Payment Information step is reached, then no payment-detail form is required |
| Actor | Guest, Authenticated | Guest, Authenticated | Guest, Authenticated |
| Journey | J-01, J-02 | J-01, J-02 | J-01, J-02 |
| Classification | DERIVED/CANDIDATE | DERIVED/CANDIDATE, narrowly scoped to the observed session | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**IMPORTANT — fees NOT generalized:** The $7.00 (COD) and $5.00 (Check/Money Order) fee amounts, and the $0.00 shown for Credit Card, are recorded strictly as **this session's observed values** for this specific cart. **No general fee schedule, percentage rule, or pricing model should be inferred or hard-coded** from these numbers (**PAY-OQ-01**, open question).

### 6.13 Order Confirmation

| Field | REQ-CONF-01 | REQ-CONF-02 |
|---|---|---|
| Statement | Upon completing checkout, the system shall display a success message and generate a unique order number | The order-confirmation total shall reflect the sum of item subtotal, shipping cost, any payment-method fee, and applicable tax |
| Rationale | Gives the customer positive, referenceable proof of purchase | Ensures the customer is charged the price they were shown |
| Evidence Basis | The completed-order screen showed: "Your order has been successfully processed!" together with a generated order number | The Confirm Order screen's total (17.00) equaled the visible Sub-Total (10.00) + Shipping (0.00) + Payment method fee (7.00), consistent with tax being 0.00 for this order/jurisdiction |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`checkout_final.html`) | DIRECT SYSTEM EVIDENCE (`checkout_06.html`) |
| Acceptance Criteria | Given a completed checkout, then a success message and a unique order number are shown | Given the line items, shipping, payment fee and tax for an order, then the confirmed total equals their sum | 
| Actor | Guest, Authenticated | Guest, Authenticated |
| Journey | J-01, J-02 | J-01, J-02 |
| Classification | DERIVED/CANDIDATE | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL | DRAFT — REQUIRES HUMAN APPROVAL |

**Explicit non-fixture note:** The specific order number produced during this discovery session is **discovery evidence only**. It must **not** be hard-coded into any future requirement, test case, or automation as an expected value or reusable fixture (see §10).

### 6.14 Order History

| Field | REQ-OHIST-01 |
|---|---|
| Statement | A completed order shall appear in the authenticated customer's Order History, showing order number, status, date, and total |
| Rationale | Lets customers track and reference past purchases |
| Evidence Basis | After completing checkout, `/customer/orders` displayed the order with its number, a "Pending" status, the order date/time, and the matching total |
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`probe3_results.json` → `ordersPageText`) |
| Acceptance Criteria | Given a just-completed order, when Order History is viewed, then that order appears with number, status, date, and total |
| Actor | Authenticated |
| Journey | J-01 |
| Classification | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (OHIST-OQ-01):** Whether a guest-checkout order is retrievable anywhere (e.g., via an order-lookup-by-email/order-number mechanism) was not investigated, since guest checkout was not carried through to a completed order in this discovery (it was confirmed to *reach* the checkout form, not to *complete* an order as a guest).

### 6.15 Customer Account

| Field | REQ-ACCT-01 |
|---|---|
| Statement | An authenticated customer shall be able to access Customer Info, Addresses, and Orders sections of their account |
| Rationale | Baseline self-service account management |
| Evidence Basis | `/customer/info`, `/customer/addresses`, and `/customer/orders` all loaded successfully for the authenticated discovery session, with `/customer/addresses` showing the address saved during checkout | 
| Evidence Strength | DIRECT SYSTEM EVIDENCE (`discover.js` account-page captures; `probe3_results.json`) |
| Acceptance Criteria | Given an authenticated session, when each of the three account URLs is visited, then the corresponding page loads without redirect to login |
| Actor | Authenticated |
| Journey | Supporting flow to J-01 |
| Classification | DERIVED/CANDIDATE |
| Status | DRAFT — REQUIRES HUMAN APPROVAL |

**OPEN QUESTION (ACCT-OQ-01):** The account menu also lists "Downloadable products," "Back in stock subscriptions," "Reward points," and "Change password." Only their presence in the menu was observed — **their functional behavior was not exercised** and no requirement is drafted for them.

## 7. Negative and Exceptional Requirements

These consolidate the negative/exceptional behaviors already evidenced above into their own explicit list, per the checkpoint's negative-path priority.

| ID | Statement | Evidence Basis | Evidence Strength | Status |
|---|---|---|---|---|
| NEG-01 | Registration with all fields blank is rejected with per-field required messages | See REQ-REG-01 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-02 | Registration with mismatched passwords is rejected | See REQ-REG-02 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-03 | Registration with a malformed email is rejected | See REQ-REG-03 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-04 | Registration with a duplicate email is rejected | See REQ-REG-04 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-05 | Login with a correct email but wrong password is rejected with a generic message | See REQ-AUTH-02 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-06 | Checkout cannot proceed from an empty cart | See REQ-CART-04 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-07 | Setting cart quantity to 0 silently removes the line item (no confirmation dialog) — flagged as a UX/business-rule point worth explicit sign-off, since silent destructive actions are sometimes considered a defect rather than a feature | See REQ-CART-03 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-08 | Add to Cart is blocked with a specific message when a mandatory product attribute is unselected | See REQ-CFG-01 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL |
| NEG-09 | Attempting to add a Gift Card product to the wishlist without its recipient/sender fields populated surfaces those fields' validation errors instead of confirming the wishlist action | See §6.8 WISH-OQ-02 | DIRECT SYSTEM EVIDENCE | DRAFT — REQUIRES HUMAN APPROVAL — **classification: OPEN QUESTION**, not a confirmed rule, pending further investigation |

## 8. Business Rules

Explicitly observed, system-enforced rules (not inferred policy):

1. A registration email must be unique across accounts (REQ-REG-04).
2. A configurable product may declare mandatory attributes that block cart addition until satisfied (REQ-CFG-01).
3. Cart line subtotal = unit price × quantity, recalculated on every quantity update (REQ-CART-02).
4. Setting a cart line's quantity to 0 is treated as removal, not an error (REQ-CART-03).
5. Checkout is unavailable from an empty cart (REQ-CART-04).
6. Checkout is available both to authenticated customers and to anonymous guests via an explicit guest path (REQ-GCO-01).
7. A selected payment method may add a fee to the order total (REQ-PAY-02) — the specific fee values observed are session-specific, not a stated general rule (see §6.12 caution).
8. The Add to Wishlist control's availability is product-specific — it is not present on every product nor on any category grid page (REQ-WISH-01, WISH-OQ-01).

## 9. Performance / NFR Requirements

**No performance SLAs, thresholds, or numeric targets are defined in this draft.** Per explicit instruction, no numbers are invented here.

| Item | Status |
|---|---|
| Page load time thresholds | TBD — HUMAN APPROVAL REQUIRED |
| Search response time | TBD — HUMAN APPROVAL REQUIRED |
| Checkout step transition time | TBD — HUMAN APPROVAL REQUIRED |
| Concurrent-user targets | TBD — HUMAN APPROVAL REQUIRED |
| Error-rate thresholds | TBD — HUMAN APPROVAL REQUIRED |
| Availability/uptime expectations | TBD — HUMAN APPROVAL REQUIRED (this is a third-party shared demo instance — see §11) |

**Observed-but-not-a-requirement note:** All discovery interactions (page loads, AJAX add-to-cart, checkout step transitions) completed within ordinary interactive browser automation timeouts (a few seconds each) during this session, with no timeouts or failures attributable to system slowness. This is an **anecdotal AGENT INFERENCE-adjacent observation from a single session on a shared public demo instance**, not a measured baseline, and must not be used to derive any NFR threshold. Formal performance work is explicitly scoped to CP-MVP2-08 (JMeter) per the project's checkpoint plan, not this document.

## 10. Data Requirements / Test Data Considerations

- Registration requires a **unique** email per account; any future test-data strategy must generate unique emails per run rather than reusing fixed values.
- The specific discovery test account (`qe.discovery.<timestamp>@example.com`) and the specific order number produced during checkout in this session are **discovery evidence only** and **must not** be hard-coded as expected values, fixtures, or golden data in any future test case, test data set, or automation script.
- Product identifiers referenced in this document (e.g., the sampled Electronics/Digital Downloads/Gift Card products) are **examples from this discovery session**, not a guaranteed-stable catalog reference — catalog contents on a shared public demo instance could change.
- Address, phone, and other PII-shaped fields used during discovery were synthetic placeholder values; any future test data generation should likewise use clearly synthetic data, not real personal information.
- **OPEN QUESTION (DATA-OQ-01):** No data-reset or isolation policy for this shared public demo instance is known. Whether accounts/orders created by testing persist indefinitely, are visible to other users of the same public instance, or are periodically reset is unconfirmed and should be established before committing to a repeatable automated test-data strategy.

## 11. Environment and Shared Demo-Instance Assumptions

- The SUT (`https://demowebshop.tricentis.com/`) is a **third-party, publicly shared** nopCommerce demo instance, not an environment MVP2 controls.
- Other, unrelated users/testers may be interacting with the same instance concurrently; observed state (e.g., product prices, catalog contents) could change outside MVP2's control.
- No SLA, uptime guarantee, or environment-reset schedule is published or known for this instance.
- All discovery in this document was performed on 2026-09-11 using headless Chromium via Playwright; no cross-browser or mobile-viewport verification was performed.
- Given the shared/public nature of the instance, any future automated test suite must be designed defensively (e.g., not assuming exclusive ownership of catalog state) — this is a design consideration for CP-MVP2-05, flagged here for awareness, not solved by this document.

## 12. Evidence and Discovery Limitations

- An initial discovery pass used static HTTP fetches (no JavaScript execution, no session/cookies). Several of its conclusions were later **superseded** by the stateful pass — most notably, the static pass characterized all "Build your own computer" attributes as dropdowns; the stateful pass found only 2 actual `<select>` elements, with at least one mandatory attribute (HDD) implemented as a different control type. Wherever a static-pass finding was superseded, this document uses the stateful finding.
- Wishlist eligibility was sampled at **one product per category** (7 categories) — not exhaustive of the catalog. See WISH-OQ-01.
- Dynamic price recalculation on configurable-product attribute change was tested once and was inconclusive (see CFG-OQ-01).
- Password-recovery email delivery could not be verified (no mailbox access).
- Several customer-account sub-areas (Downloadable products, Back in stock subscriptions, Reward points, Change password) were not functionally exercised.
- Guest checkout was confirmed to be *reachable and to render the checkout form*; it was **not** carried through to a completed order and order-confirmation in this discovery (only the authenticated path was carried to completion). This is a gap, not a negative finding.
- Cart-persistence-across-login was observed as an outcome; the underlying mechanism (merge vs. session continuity) is unresolved (CART-OQ-01).
- All findings derive from a single browser (headless Chromium), a single session, and a limited time window — no repeated-trial confirmation was performed for any observation.

## 13. Open Questions / TBD Items

| ID | Question | Blocking for |
|---|---|---|
| REG-OQ-01 | Is auto-login-after-registration an intended design decision? | REQ-REG-05 approval |
| PWR-OQ-01 | Does password recovery actually deliver a working reset email/link? | REQ-PWR-01 completeness |
| CFG-OQ-01 | Does any configurable-product attribute visibly change price on selection? | Any future dynamic-pricing requirement |
| CART-OQ-01 | Is anonymous→authenticated cart continuity a true merge or session continuity? | REQ-CART-05 precision |
| WISH-OQ-01 | What is the catalog-wide rule for wishlist-control eligibility? | Any broader wishlist requirement than REQ-WISH-01–03 |
| WISH-OQ-02 | Does Gift Card wishlist-add succeed once recipient/sender fields are populated? | Using Gift Cards as a wishlist example (currently PARKED) |
| WISH-OQ-03 | Does "Add to cart" from the Wishlist page work as expected? | Any Wishlist→Cart requirement |
| ACO-OQ-01 | What is the exact inline validation message for a blank required checkout field? | Precise negative-path acceptance criteria |
| SHIP-OQ-01 | Does shipping cost ever vary (by weight/destination/order value)? | Any shipping-cost requirement |
| PAY-OQ-01 | Are the observed payment-method fees fixed, or do they vary by cart/context? | Any payment-fee requirement |
| OHIST-OQ-01 | Can a guest-checkout order be retrieved/tracked afterward? | Guest-checkout order-history requirement |
| ACCT-OQ-01 | What do Downloadable products / Back in stock subscriptions / Reward points / Change password actually do? | Any account-area requirement beyond REQ-ACCT-01 |
| DATA-OQ-01 | What is the data-reset/isolation policy for this shared demo instance? | Test-data strategy (CP-MVP2-04) |
| NFR-OQ-01 (all of §9) | What are the approved performance thresholds? | All NFR/performance requirements |

## 14. Requirement Traceability Placeholder

Population of this matrix is **out of scope for this checkpoint** (it depends on CP-MVP2-03 test cases and CP-MVP2-05 automation, neither of which exist yet). The structure is defined here so later checkpoints have a consistent target:

| Requirement ID | Business Journey | Test Case ID (TBD — CP-MVP2-03) | Automation ID (TBD — CP-MVP2-05) | Evidence Artifact(s) |
|---|---|---|---|---|
| REQ-REG-01 … REQ-ACCT-01 | J-01 … J-05 | *(not yet created)* | *(not yet created)* | See each requirement's Evidence Basis column above |

## 15. SRS Approval / Baseline Metadata

| Field | Value |
|---|---|
| Document status | **DRAFT — REQUIRES HUMAN APPROVAL** |
| Baseline status | **NOT BASELINED** — no Approved SRS exists yet for MVP2 |
| Version | 0.1 (initial draft) |
| Checkpoint | CP-MVP2-01 — Application Discovery & Approved SRS (discovery portion complete; approval portion pending) |
| Prepared by | Agentic session (Claude Code), for vaijanath.ruge@gmail.com |
| Date prepared | 2026-09-11 |
| Approver(s) | **TBD** — no human/business approver has yet reviewed or signed off on this draft |
| Approval date | **TBD** |
| Next checkpoint | CP-MVP2-02 (Knowledge Base + RAG) — **must not begin** until this draft is reviewed and an Approved SRS is produced |
| Evidence hierarchy tier of this document as a whole | Below APPROVED BASELINE by definition — the document is composed of DIRECT SYSTEM EVIDENCE, CURRENT TESTING ARTIFACTS, HISTORICAL EVIDENCE, and clearly flagged AGENT INFERENCE, none of which become an Approved Baseline without human sign-off |

---

*End of Draft MVP2 SRS. This document does not authorize any subsequent checkpoint work.*
