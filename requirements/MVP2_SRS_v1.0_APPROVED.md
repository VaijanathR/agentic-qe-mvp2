# Agentic QE MVP2 — Software Requirements Specification (SRS)

**Version:** 1.0
**Status:** `APPROVED BASELINE`
**Checkpoint:** CP-MVP2-01 — Application Discovery & Approved SRS (governance/refinement pass complete)
**System Under Test:** Demo Web Shop — https://demowebshop.tricentis.com/ (third-party, public, shared nopCommerce demo instance)
**Supersedes (for baseline purposes only):** `requirements/MVP2_SRS_DRAFT.md` (retained, unmodified, as the discovery-evidence record this baseline was governed from)
**Baseline date:** 2026-09-11
**Approver:** Human Owner (vaijanath.ruge@gmail.com), via explicit governance decisions issued in the CP-MVP2-01 baseline-approval session

---

## Evidence Hierarchy (unchanged from draft; still governs every claim in this document)

1. **APPROVED BASELINE** — a previously human-approved requirement or architecture document. *This document itself becomes an Approved Baseline only from the moment §15 is executed; it does not retroactively upgrade the evidentiary strength of any individual observation below it.*
2. **DIRECT SYSTEM EVIDENCE** — behavior directly observed via a live, stateful, JS-executing browser session against the real SUT during CP-MVP2-01 discovery.
3. **CURRENT TESTING ARTIFACT** — the specific capture (script output, saved HTML, JSON result, screenshot) that substantiates a Direct System Evidence claim.
4. **HISTORICAL EVIDENCE** — findings from the earlier static (non-stateful) discovery pass; lower confidence, superseded wherever a stateful check contradicted it.
5. **AGENT INFERENCE** — the agent's own interpretation or extrapolation, never sufficient alone to justify a requirement; always flagged where used.

**Governance distinction (unchanged principle, now exercised):** Evidence Strength describes how well a fact is observed. **Approval Status** describes whether a human business owner has ratified a requirement. This pass exercises that distinction: requirements in §6–§7 that support the five frozen journeys are now marked `APPROVED — BASELINED v1.0`; unresolved items remain `PARKED — NOT IN BASELINE` regardless of how strong or weak their underlying evidence is. **No `PARKED` item in this document has been silently upgraded to approved, and no `APPROVED` requirement asserts more than its cited evidence supports.**

**Non-generalization rule (stated once, applies throughout):** Per governance decision, no requirement or acceptance criterion in this document states a specific product ID, order number, shipping price, payment fee amount, or catalog-availability count as a business rule. Where such values appear, they appear **only** inside an "Evidence Basis" cell, explicitly as an illustrative example from one discovery session — never inside a "Statement" or "Acceptance Criteria" cell.

---

## 1. Purpose

This is the **Approved SRS baseline (v1.0)** for MVP2, produced by a governance/refinement pass over `MVP2_SRS_DRAFT.md` using only the discovery evidence already gathered in CP-MVP2-01 (no new discovery was performed). It records the Human Owner's explicit scope-freeze decisions and is now, per §15, the **immutable source of truth** for CP-MVP2-02 onward.

## 2. MVP2 Approved Scope

### 2.1 Approved Journeys (frozen)
- **J-01** — Registration → Login → Browse/Search → Cart → Authenticated Checkout → Order → Order History
- **J-02** — Anonymous Browse → Cart → Guest Checkout → Order
- **J-03** — Configurable Product → Missing Mandatory Attribute → Correct Selection → Cart → Checkout
- **J-04** — Cart Quantity / Remove / Empty-cart behavior
- **J-05** — Eligible Product Detail → Wishlist → Wishlist Page

No other journey is in MVP2 scope unless added through the change-control process in §15.

### 2.2 Approved Capability Areas
Registration; Authentication/Login; Password Recovery (**UI-acceptance only** — see §3); Search; Product Browsing; Product Configuration (mandatory-attribute enforcement); Cart; Wishlist (**product-detail-page scoped** — see §6.8); Guest Checkout; Authenticated Checkout; Shipping (method **selection**, not cost rules); Payment (method **selection** and total-inclusion, not fee rules); Order Confirmation; Order History; Customer Account (Customer Info / Addresses / Orders only).

### 2.3 Approved Negative/Exceptional Behaviors
NEG-01 through NEG-08 (§7). NEG-09 (Gift Card wishlist validation interaction) is **not** approved — it remains parked with WISH-OQ-02.

### 2.4 Performance Scope (approved as scope; no thresholds approved)
MVP2 approved performance scope is the **measurement and validation** of: response time, throughput, error rate, behavior under a defined baseline load, and behavior under defined concurrency/load levels — with evidence capture and threshold validation as a process. **No numeric SLA or threshold is approved by this document.** See §9.

### 2.5 Explicitly Parked (do not block this baseline; do not treat as approved)
CFG-OQ-01 (dynamic pricing), CART-OQ-01 (cart merge semantics), WISH-OQ-01 (catalog-wide wishlist eligibility), WISH-OQ-02 (Gift Card wishlist behavior), WISH-OQ-03 (Wishlist → Add to Cart), SHIP-OQ-01 (shipping-cost calculation), PAY-OQ-01 (payment-fee calculation rules), OHIST-OQ-01 (guest order retrieval), ACCT-OQ-01 (untested account subareas), DATA-OQ-01 (shared-instance reset/isolation), PWR-OQ-01 (password-reset/email delivery), REG-OQ-01 (auto-login-on-registration design intent), ACO-OQ-01 (exact checkout validation copy), and all NFR numeric thresholds (§9). Full detail in §13.

## 3. Out of Scope / POST-MVP — PARKED

- Security testing and penetration testing — **POST-MVP — PARKED** (existing project governance).
- Full application/site coverage beyond the approved capability areas in §2.2.
- Multiple applications, CI/CD integration, distributed browser grid, multi-VM orchestration, large-scale parallel execution — **POST-MVP — PARKED** (existing project governance).
- Admin/back-office functionality — not investigated, not in scope.
- **End-to-end password reset (email delivery, reset token/link, password change completion) is explicitly excluded from MVP2 acceptance scope.** Only the UI-level "recovery request accepted" behavior (REQ-PWR-01) is approved; see PWR-OQ-01.
- Functional verification of "Downloadable products," "Back in stock subscriptions," and "Reward points" account areas (menu presence only was observed) — **PARKED** (ACCT-OQ-01).
- Cross-browser and mobile-responsive verification (discovery used headless Chromium only).
- Gift Card wishlist behavior as a canonical example — **PARKED** (WISH-OQ-02) until the recipient/sender required-field interaction is resolved.
- Wishlist "Add to cart" action — **PARKED** (WISH-OQ-03), not exercised in discovery.
- Any numeric performance/SLA threshold — **PARKED**, requires separate Human/Project Target approval (§9).
- Treating any discovery-session-specific value (product ID, order number, shipping price, payment fee, discovery test-account identity) as a reusable fixture, golden value, or business rule (§10).

## 4. Actors and Personas

| Persona | Basis | Evidence Strength | Approval Status |
|---|---|---|---|
| **Anonymous / Guest shopper** | Directly observed browsing, searching, cart, wishlist (on eligible products), and guest checkout | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| **Registered / Authenticated customer** | Directly observed registration, login, cart/wishlist, authenticated checkout, order history | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| **Admin / site operator** | Not investigated; inferred only from platform identity and one placeholder string | AGENT INFERENCE | OUT OF SCOPE — not part of this baseline |

## 5. Business Journeys (Approved & Frozen)

| ID | Journey | Evidence Strength | Approval Status | Notes |
|---|---|---|---|---|
| J-01 | Registration → Login → Browse/Search → Cart → Authenticated Checkout → Order → Order History | DIRECT SYSTEM EVIDENCE (walked end-to-end; produced a real, non-reusable order) | **APPROVED — BASELINED v1.0** | Fully evidenced, no gaps |
| J-02 | Anonymous Browse → Cart → Guest Checkout → Order | DIRECT SYSTEM EVIDENCE for Browse/Cart/reaching-checkout-as-guest; **AGENT INFERENCE** for the final "→ Order" step (guest path was confirmed to load the identical `/onepagecheckout` engine used by the completed authenticated order, but was not itself carried through to a completed order in discovery) | **APPROVED — BASELINED v1.0 (scope); completion evidence gap noted — see §14 validation** | Frozen at the Human Owner's explicit direction with this gap disclosed, not hidden |
| J-03 | Configurable Product → Missing Mandatory Attribute → Correct Selection → Cart → Checkout | DIRECT SYSTEM EVIDENCE (blocking message observed; correct-selection completion to cart not separately re-verified after the block, but Add to Cart mechanics are otherwise confirmed via J-01/J-02) | **APPROVED — BASELINED v1.0** | Core negative+positive pairing |
| J-04 | Cart Quantity / Remove / Empty-cart behavior | DIRECT SYSTEM EVIDENCE | **APPROVED — BASELINED v1.0** | Fully evidenced |
| J-05 | Eligible Product Detail → Wishlist → Wishlist Page | DIRECT SYSTEM EVIDENCE | **APPROVED — BASELINED v1.0** | "Eligible" is load-bearing — see §6.8 |

## 6. Functional Requirements

All requirements below are `APPROVED — BASELINED v1.0` unless marked otherwise. Fields: ID, Statement, Rationale, Evidence Basis, Evidence Strength, Acceptance Criteria, Actor, Journey, Status.

### 6.1 Registration

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-REG-01 | Registration shall require First name, Last name, Email, Password, and Confirm password, rejecting submission with field-specific messages when any are blank | Baseline data-quality gate | Empty-form submission returned per-field "is required" messages | DIRECT SYSTEM EVIDENCE | Given all fields blank, when submitted, then all required-field messages show and no account is created | Guest | J-01 | APPROVED — BASELINED v1.0 |
| REQ-REG-02 | Registration shall reject mismatched Password/Confirm password | Prevents typo'd-password lockout | Mismatch returned "The password and confirmation password do not match." | DIRECT SYSTEM EVIDENCE | Given mismatched passwords, when submitted, then the mismatch message shows and no account is created | Guest | J-01 | APPROVED — BASELINED v1.0 |
| REQ-REG-03 | Registration shall reject a malformed email | Prevents undeliverable contact email | `not-an-email` returned "Wrong email" | DIRECT SYSTEM EVIDENCE | Given a malformed email, when submitted, then "Wrong email" shows and no account is created | Guest | J-01 | APPROVED — BASELINED v1.0 |
| REQ-REG-04 | Registration shall reject a duplicate email | Prevents duplicate accounts | Re-registering an existing email returned "The specified email already exists" | DIRECT SYSTEM EVIDENCE | Given an email already on file, when submitted, then the duplicate message shows and no account is created | Guest | J-01 | APPROVED — BASELINED v1.0 |
| REQ-REG-05 | Upon successful registration, the user shall be automatically authenticated with no separate login step | Reduces first-use friction | Post-registration page showed the account logged in immediately | DIRECT SYSTEM EVIDENCE | Given a valid unique-email registration, when submitted, then the resulting page shows an authenticated state | Guest → Authenticated | J-01 | APPROVED — BASELINED v1.0 (design-intent question REG-OQ-01 parked — does not block) |

### 6.2 Authentication / Login

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-AUTH-01 | Login shall succeed given correct, registered email/password | Core access control | Correct-credential login reached an authenticated home page | DIRECT SYSTEM EVIDENCE | Given valid credentials, when submitted, then an authenticated state is reached | Guest → Authenticated | J-01, J-03 | APPROVED — BASELINED v1.0 |
| REQ-AUTH-02 | Login shall reject an incorrect password with a generic message that does not disclose which field was wrong | Avoids account-enumeration leakage | Wrong-password attempt returned "The credentials provided are incorrect" | DIRECT SYSTEM EVIDENCE | Given an incorrect password, when submitted, then the generic message shows and no session is created | Guest | J-01 | APPROVED — BASELINED v1.0 |
| REQ-AUTH-03 | A newly registered account shall be able to log in explicitly immediately after registration | Confirms no hidden onboarding blocker | Discovery account was logged out then back in successfully, same session | DIRECT SYSTEM EVIDENCE | Given a just-registered account, when logged out and back in, then login succeeds | Guest → Authenticated | J-01 | APPROVED — BASELINED v1.0 |

*(HISTORICAL EVIDENCE only, not approved as a requirement: a "Remember me" checkbox is present on the login form; its session-persistence effect was not exercised statefully — retained in §12 as a limitation, not a requirement.)*

### 6.3 Password Recovery

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-PWR-01 | The system shall accept a password-recovery request for a registered email via the recovery form, without displaying an error, at the UI level | Confirms the request-acceptance UI works | Submitting the discovery account's email completed with no validation error shown | DIRECT SYSTEM EVIDENCE (UI acceptance only) | Given a valid registered email, when password recovery is submitted, then the UI shows acceptance and no error | Guest | Supporting flow to J-01/J-02 | APPROVED — BASELINED v1.0 (UI-acceptance scope only) |

**Governance decision:** Actual email delivery, reset-token/link validity, and password-change completion are **explicitly excluded from MVP2 acceptance scope** (PWR-OQ-01, parked, non-blocking — see §3, §13). No requirement in this baseline claims that password reset works end-to-end.

### 6.4 Search

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-SRCH-01 | Search shall return matching product results for a valid keyword | Core product-discovery function | A representative keyword search returned multiple result cards | DIRECT SYSTEM EVIDENCE | Given a keyword matching existing products, when searched, then at least one result renders | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |
| REQ-SRCH-02 | Search shall display an explicit "no results" message when nothing matches | Avoids an ambiguous blank-results experience | A nonsense keyword returned "No products were found that matched your criteria." | DIRECT SYSTEM EVIDENCE | Given a keyword matching nothing, when searched, then the no-results message shows and zero results render | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |

*(HISTORICAL EVIDENCE only, not approved as requirements: advanced-search filters — category/subcategory, price range, manufacturer, description-search — were observed statically; their filtering effect was not stress-tested statefully. Retained in §12, not stated as a requirement.)*

### 6.5 Product Browsing

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-BRW-01 | The catalog shall be organized into independently browsable top-level categories, including at minimum: Books, Computers, Electronics, Apparel & Shoes, Digital Downloads, Jewelry, and Gift Cards | Establishes the navigation structure other requirements assume | All 7 categories were directly navigated and rendered product grids across two discovery passes | DIRECT SYSTEM EVIDENCE | Given the main navigation, when any of the 7 category links is selected, then a product grid renders | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |

*(HISTORICAL EVIDENCE only, not approved as requirements: sort options, page-size options, and price-bucket filters on category grids — observed statically, not exercised statefully. Retained in §12.)*

### 6.6 Product Configuration

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-CFG-01 | For a configurable product with a mandatory attribute, Add to Cart shall be blocked with a message identifying the missing attribute until it is selected | Prevents incomplete build-to-order submissions | Attempting to add a configurable product without a required attribute selected returned a specific blocking message and the item was not added | DIRECT SYSTEM EVIDENCE | Given a configurable product with a mandatory attribute unselected, when Add to Cart is attempted, then a message names the missing attribute and the cart is unchanged | Guest, Authenticated | J-03 | APPROVED — BASELINED v1.0 |

**Parked, non-blocking:** CFG-OQ-01 — whether any configurable-product attribute visibly triggers dynamic price recalculation was inconclusive in discovery and is **not** asserted as a requirement (§13).

### 6.7 Cart

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-CART-01 | Adding a product to the cart shall confirm the addition to the user | Core cart function | AJAX confirmation notice observed on add | DIRECT SYSTEM EVIDENCE | Given a product page, when Add to Cart is used, then a success notice appears and cart count increments | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |
| REQ-CART-02 | Updating a line item's quantity shall recalculate that line's subtotal and the cart's total | Pricing accuracy | Quantity change from 1 to 3 units recalculated subtotal/total proportionally, unit price unchanged | DIRECT SYSTEM EVIDENCE | Given a cart line at unit price P and quantity 1, when quantity is changed to N, then subtotal = P×N and cart total reflects it | Guest, Authenticated | J-04 | APPROVED — BASELINED v1.0 |
| REQ-CART-03 | Setting a line item's quantity to 0 and applying the update shall remove that line item without a confirmation prompt | Documents actual zero-quantity behavior for negative-path design | Qty=0 + Update returned the cart to its empty state with no dialog | DIRECT SYSTEM EVIDENCE | Given a cart line, when quantity is set to 0 and Update is applied, then the line item no longer appears and no prompt is shown | Guest, Authenticated | J-04 | APPROVED — BASELINED v1.0 |
| REQ-CART-04 | The cart shall support explicit line-item removal, and shall show an empty-cart state with no active checkout when it has no items | Core cart function; prevents empty checkout | Checkbox-removal + update returned to empty state; empty-cart page showed "Your Shopping Cart is empty!" with the checkout breadcrumb but no active checkout action | DIRECT SYSTEM EVIDENCE | Given an empty cart, when viewed, then an empty-state message shows and checkout cannot proceed | Guest, Authenticated | J-01, J-02, J-04 | APPROVED — BASELINED v1.0 |
| REQ-CART-05 | An item added to the cart during an anonymous session shall remain present in the cart after that same browser session subsequently authenticates | Avoids losing shopper intent on guest-to-account transition | An anonymously added item was still present in the cart immediately after login, same session | DIRECT SYSTEM EVIDENCE (outcome only) | Given an anonymous cart with items, when the user logs in within the same session, then those items remain visible afterward | Guest → Authenticated | J-01 | APPROVED — BASELINED v1.0 (narrow wording only — see below) |

**Parked, non-blocking:** CART-OQ-01 — the underlying mechanism (true cart-merge vs. session/cookie continuity) is **not** established and REQ-CART-05 must not be read as a "cart merge" requirement (§13).

### 6.8 Wishlist

> **Governance framing:** Wishlist is **IN SCOPE for MVP2**, scoped strictly to what was observed: a product-detail-page capability, present only where the page exposes an Add to Wishlist control. It is **not assumed to exist on every product**, and it is **never available from category grid/listing pages**.

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-WISH-01 | On product detail pages that expose an Add to Wishlist control, the system shall allow the current user (anonymous or authenticated) to add that product to their wishlist | Lets shoppers save items of interest, on the subset of products where offered | Control found and successfully used on sampled Electronics and Digital Downloads products; **not found** on sampled Computers, Apparel, Books, or Jewelry products, nor on any of the 7 category grid pages | DIRECT SYSTEM EVIDENCE (28-check sweep) | Given a product detail page exposing Add to Wishlist, when clicked, then a wishlist-add confirmation shows | Guest, Authenticated | J-05 | APPROVED — BASELINED v1.0 |
| REQ-WISH-02 | A successful wishlist addition shall be reflected on the `/wishlist` page with the item's price and available actions | Confirms the action has a durable effect | Two added items appeared on the wishlist page with price, Remove, and Add to cart controls | DIRECT SYSTEM EVIDENCE | Given an item was just added to the wishlist, when the wishlist page is viewed, then that item appears with price and available actions | Guest, Authenticated | J-05 | APPROVED — BASELINED v1.0 |
| REQ-WISH-03 | The wishlist shall be usable by anonymous users, including a persistent, shareable wishlist URL, without requiring an account | Reduces pre-registration friction | Anonymous session's wishlist page displayed a shareable URL | DIRECT SYSTEM EVIDENCE | Given no account, when items are added and the wishlist page is viewed, then a shareable URL is displayed | Guest | J-05 | APPROVED — BASELINED v1.0 |

**Parked, non-blocking (do not generalize):**
- WISH-OQ-01 — the catalog-wide rule for which products expose Add to Wishlist is unknown; only one product per category was sampled. **No requirement here means "wishlist is available for [category]" — only for the specific sampled products.**
- WISH-OQ-02 — Gift Card wishlist behavior remains **PARKED**: the control is visible/clickable there, but the click surfaced the product's own required-field validation (recipient/sender name & email) instead of a wishlist confirmation. Gift Cards must **not** be used as a canonical wishlist example until resolved.
- WISH-OQ-03 — "Add to cart" from the wishlist page was seen present but not exercised; no requirement is stated for it.

### 6.9 Guest Checkout

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-GCO-01 | An anonymous user with cart items shall be able to initiate checkout via an explicit "Checkout as Guest" option, without creating an account | Reduces purchase friction for non-registering shoppers | Anonymous checkout click routed to a guest-or-register interstitial; "Checkout as Guest" proceeded to the checkout form while remaining anonymous | DIRECT SYSTEM EVIDENCE | Given an anonymous cart with items, when Checkout is initiated, then a working "Checkout as Guest" path proceeds without login | Guest | J-02 | APPROVED — BASELINED v1.0 |
| REQ-GCO-02 | Guest checkout shall present the same step sequence as authenticated checkout (Billing → Shipping Address → Shipping Method → Payment Method → Payment Info → Confirm → Completed) | Consistency of checkout mechanics regardless of authentication state | Guest session's checkout rendered the same Billing Address step structure as the authenticated flow | DIRECT SYSTEM EVIDENCE | Given a guest proceeding through checkout, then the same named steps appear as for an authenticated user | Guest | J-02 | APPROVED — BASELINED v1.0 |
| REQ-GCO-03 | Guest checkout shall culminate in order confirmation and a generated order number, consistent with the mechanism observed for authenticated checkout | Journey J-02 requires an "Order" outcome for guest shoppers | The guest flow was confirmed to load the identical `/onepagecheckout` engine and step structure used by the authenticated flow that *was* carried through to a completed order; the guest path itself was not separately carried to completion in discovery | **AGENT INFERENCE**, bridging from DIRECT SYSTEM EVIDENCE on the authenticated path (REQ-ACO/REQ-CONF) | Given a guest completes all checkout steps, then an order confirmation and order number are produced, consistent with the authenticated-path mechanism | Guest | J-02 | **APPROVED — BASELINED v1.0 (scope), evidence gap explicitly disclosed — see §14** |

### 6.10 Authenticated Checkout

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-ACO-01 | For an authenticated user with cart items, checkout shall proceed through: Billing Address → Shipping Address → Shipping Method → Payment Method → Payment Information → Confirm Order → Order Completed | Canonical checkout path | Full checkout walked end-to-end with HTML captured at each step, ending in order confirmation and a matching Order History entry | DIRECT SYSTEM EVIDENCE | Given an authenticated user with a non-empty cart, when checkout is initiated, then all six steps present in order and a completed order results | Authenticated | J-01 | APPROVED — BASELINED v1.0 |
| REQ-ACO-02 | If the account has a previously saved address, checkout's address steps shall offer it for reuse via a selection control rather than forcing re-entry | Reduces repeat-purchase friction | A subsequent checkout's Shipping Address step showed the previously saved address pre-populated in a selection dropdown | DIRECT SYSTEM EVIDENCE | Given an account with a saved address, when a checkout address step is reached, then that address is offered via selection instead of a blank form | Authenticated | J-01 | APPROVED — BASELINED v1.0 |
| REQ-ACO-03 | The Billing/Shipping address form shall require First name, Last name, Email, Country, City, Address 1, Zip/postal code, and Phone number; Company, Address 2, and Fax number shall be optional | Ensures sufficient fulfillment data | Required-field markers and matching inline messages observed on the named fields; no such marker on the optional fields | DIRECT SYSTEM EVIDENCE | Given the address form, when required fields are left blank, then progression to the next step is blocked | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |

**Parked, non-blocking:** ACO-OQ-01 — the exact inline validation message text for a blank required checkout field was not cleanly isolated; not stated as a precise acceptance criterion (§13).

### 6.11 Shipping

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-SHIP-01 | The Shipping Method step shall present multiple shipping method options for selection | Allows a fulfillment speed/cost tradeoff choice | Three shipping methods were presented (existence only; no cost rule asserted) | DIRECT SYSTEM EVIDENCE (existence of the choice only) | Given the Shipping Method step, when reached, then more than one method is selectable | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |

**Governance decision — explicitly not generalized:** The specific per-method cost observed in one discovery session (all methods showing the same session-specific value for one cart/address) is evidence only, **not** a "shipping is free" requirement. SHIP-OQ-01 (shipping-cost calculation) is **parked, non-blocking** (§13).

### 6.12 Payment

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-PAY-01 | The Payment Method step shall present multiple payment method options | Supports customers without card-based payment | Four payment methods were observed: Cash On Delivery, Check/Money Order, Credit Card, Purchase Order | DIRECT SYSTEM EVIDENCE | Given the Payment Method step, when reached, then more than one method is selectable | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |
| REQ-PAY-02 | Selecting a payment method that carries an associated fee shall cause that fee to be reflected in the order total shown at Confirm Order | Price transparency for payment surcharges | In one discovery session, selecting a fee-bearing method produced an order total equal to subtotal + shipping + that method's fee (illustrative example: a $10.00 cart with a payment method carrying a $7.00 fee produced a $17.00 total) | DIRECT SYSTEM EVIDENCE (structural rule); illustrative amounts are session-specific, not a fee schedule | Given a payment method with an associated fee is selected, when Confirm Order is reached, then the displayed total includes that fee | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |
| REQ-PAY-03 | Selecting Cash On Delivery shall require no card/payment-detail entry at the Payment Information step | Matches the nature of pay-on-delivery | COD's Payment Information step showed only descriptive text, no form fields | DIRECT SYSTEM EVIDENCE | Given COD is selected, when Payment Information is reached, then no payment-detail form is required | Guest, Authenticated | J-01, J-02 | APPROVED — BASELINED v1.0 |

**Governance decision — explicitly not generalized:** The specific fee amounts observed are **session-specific illustrative evidence only**; no fee schedule, percentage rule, or pricing model is approved. PAY-OQ-01 is **parked, non-blocking** (§13).

### 6.13 Order Confirmation

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-CONF-01 | Upon completing checkout, the system shall display a success message and generate a unique order number | Positive, referenceable proof of purchase | A completed checkout showed a success message and a generated order number (the specific number is discovery evidence only — not a fixture) | DIRECT SYSTEM EVIDENCE | Given a completed checkout, then a success message and a unique order number are shown | Authenticated | J-01 | APPROVED — BASELINED v1.0 |
| REQ-CONF-02 | The order-confirmation total shall equal the sum of item subtotal, shipping cost, any payment-method fee, and applicable tax | Ensures the customer is charged the price shown | In one discovery session the confirmed total exactly equaled the sum of its displayed components | DIRECT SYSTEM EVIDENCE | Given an order's subtotal, shipping, payment fee, and tax, then the confirmed total equals their sum | Authenticated | J-01 | APPROVED — BASELINED v1.0 |

### 6.14 Order History

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-OHIST-01 | A completed order shall appear in the authenticated customer's Order History, showing order number, status, date, and total | Lets customers track past purchases | Order History displayed the completed order with number, status, date, and matching total | DIRECT SYSTEM EVIDENCE | Given a just-completed order, when Order History is viewed, then it appears with number, status, date, and total | Authenticated | J-01 | APPROVED — BASELINED v1.0 |

**Parked, non-blocking:** OHIST-OQ-01 — whether/how a guest-checkout order can be retrieved afterward was not investigated (§13).

### 6.15 Customer Account

| ID | Statement | Rationale | Evidence Basis | Evidence Strength | Acceptance Criteria | Actor | Journey | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-ACCT-01 | An authenticated customer shall be able to access Customer Info, Addresses, and Orders sections of their account | Baseline self-service account management | All three pages loaded successfully for the authenticated discovery session, with Addresses showing the address saved during checkout | DIRECT SYSTEM EVIDENCE | Given an authenticated session, when each of the three account pages is visited, then it loads without redirect to login | Authenticated | Supporting flow to J-01 | APPROVED — BASELINED v1.0 |

**Parked, non-blocking:** ACCT-OQ-01 — "Downloadable products," "Back in stock subscriptions," "Reward points," and "Change password" were seen only as menu entries; not functionally exercised; no requirement stated for them (§13).

## 7. Negative and Exceptional Requirements

| ID | Statement | Evidence Strength | Status |
|---|---|---|---|
| NEG-01 | Registration with all fields blank is rejected with per-field required messages | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-02 | Registration with mismatched passwords is rejected | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-03 | Registration with a malformed email is rejected | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-04 | Registration with a duplicate email is rejected | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-05 | Login with a correct email but wrong password is rejected with a generic message | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-06 | Checkout cannot proceed from an empty cart | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-07 | Setting cart quantity to 0 silently removes the line item with no confirmation dialog (flagged for explicit business sign-off — some businesses treat silent destructive actions as a defect) | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-08 | Add to Cart is blocked with a specific message when a mandatory product attribute is unselected | DIRECT SYSTEM EVIDENCE | APPROVED — BASELINED v1.0 |
| NEG-09 | Gift Card wishlist-add attempt without recipient/sender fields surfaces those fields' validation instead of a wishlist confirmation | DIRECT SYSTEM EVIDENCE (behavior); resolution unknown | **PARKED — NOT IN BASELINE** (tied to WISH-OQ-02) |

## 8. Business Rules

1. A registration email must be unique across accounts (REQ-REG-04).
2. A configurable product may declare mandatory attributes that block cart addition until satisfied (REQ-CFG-01).
3. Cart line subtotal recalculates as unit price × quantity on every quantity update (REQ-CART-02).
4. Setting a cart line's quantity to 0 is treated as removal, not an error (REQ-CART-03).
5. Checkout is unavailable from an empty cart (REQ-CART-04).
6. Checkout is available both to authenticated customers and to anonymous guests via an explicit guest path (REQ-GCO-01).
7. A selected payment method may add a fee to the order total; the specific amounts observed are session-specific, not a stated general rule (REQ-PAY-02).
8. The Add to Wishlist control's availability is product-specific — not present on every product nor on any category grid page (REQ-WISH-01; WISH-OQ-01 parked for the exact rule).

## 9. Performance / NFR Requirements

### 9.1 Approved Performance Scope
MVP2 shall include performance measurement and validation covering:
- Response time
- Throughput
- Error rate
- Behavior under a defined baseline load
- Behavior under defined concurrency/load levels
- Evidence capture for all of the above
- Threshold validation as a process

This scope decision is **APPROVED — BASELINED v1.0** as a statement of *what will be measured*, formally executed in CP-MVP2-08 (JMeter). It is **not** a numeric SLA.

### 9.2 Numeric Thresholds — NOT approved, not derived from discovery
| Item | Status |
|---|---|
| Page load / response time threshold | **TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL** |
| Throughput target | **TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL** |
| Error-rate threshold | **TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL** |
| Baseline load definition (users/requests) | **TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL** |
| Concurrency/load levels | **TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL** |
| Availability/uptime expectation | **TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL** (third-party shared instance — see §11) |

No numeric threshold above is derived from the CP-MVP2-01 discovery session. Discovery interactions completed without timeout under ordinary interactive automation, but this is an anecdotal, single-session observation on a shared public instance — **explicitly not usable as an SLA basis** and not cited as such anywhere in this document.

## 10. Data Requirements / Test Data Considerations

- Registration requires a unique email per account; future test-data strategy must generate unique emails per run.
- The specific discovery test account, the specific order number produced, and the specific product IDs sampled during CP-MVP2-01 are **discovery evidence only** and must **not** be hard-coded as fixtures, golden values, or expected results in any future test case, test data set, or automation.
- Any future test data must use clearly synthetic values, not real personal information.
- **Parked (DATA-OQ-01):** no data-reset/isolation policy for this shared public demo instance is known; must be established before committing to a repeatable automated test-data strategy.

## 11. Environment and Shared Demo-Instance Assumptions

- The SUT is a third-party, publicly shared nopCommerce demo instance, not an MVP2-controlled environment.
- Other users may interact with the same instance concurrently; observed state (prices, catalog contents) may change outside MVP2's control.
- No SLA, uptime guarantee, or reset schedule is published or known.
- All CP-MVP2-01 discovery used headless Chromium via Playwright, on 2026-09-11; no cross-browser or mobile-viewport verification was performed.
- Future automated test design (CP-MVP2-05) must account for the shared/public nature of the instance rather than assuming exclusive ownership of catalog state.

## 12. Evidence and Discovery Limitations

- An initial static (non-JS, non-session) discovery pass produced some findings later **superseded** by the stateful pass — most notably, the configurable-product attribute types were mischaracterized as all-dropdowns; the stateful pass corrected this. Where superseded, this document uses only the stateful finding.
- Wishlist eligibility was sampled at one product per category (7 categories) — not exhaustive.
- Dynamic price recalculation on attribute change was tested once and was inconclusive.
- Password-recovery email delivery could not be verified (no mailbox access).
- "Downloadable products," "Back in stock subscriptions," "Reward points," and "Change password" account areas were not functionally exercised.
- Guest checkout was confirmed reachable and step-equivalent to authenticated checkout, but was **not** itself carried through to a completed order (REQ-GCO-03 evidence gap, disclosed in §6.9 and §14).
- Cart-persistence-across-login was observed as an outcome; the underlying mechanism (merge vs. session continuity) is unresolved.
- "Remember me," advanced-search filters, and category-grid sort/pagination controls were observed only historically/statically, not exercised statefully — retained here as limitations, not converted into requirements (per de-duplication governance decision).
- All findings derive from a single browser, a single session, and a limited time window — no repeated-trial confirmation was performed.

## 13. Open Questions / Parked Items (Non-Blocking to This Baseline)

| ID | Question | Parked Because | Blocks Baseline? |
|---|---|---|---|
| REG-OQ-01 | Is auto-login-after-registration intended design or demo-config artifact? | Not verifiable without target-system knowledge | No |
| PWR-OQ-01 | Does password recovery deliver a working reset email/link? | No mailbox access | No — explicitly excluded from MVP2 acceptance scope |
| CFG-OQ-01 | Does any configurable-product attribute visibly change price? | Inconclusive single test | No |
| CART-OQ-01 | Is anonymous→authenticated cart continuity a true merge or session continuity? | Not isolated by discovery | No |
| WISH-OQ-01 | What is the catalog-wide wishlist-eligibility rule? | Only 1 product/category sampled | No |
| WISH-OQ-02 | Does Gift Card wishlist-add succeed once recipient/sender fields are populated? | Not tested | No — Gift Cards excluded as canonical example |
| WISH-OQ-03 | Does "Add to cart" from the Wishlist page work? | Not exercised | No |
| ACO-OQ-01 | Exact inline validation message for a blank required checkout field? | Not cleanly isolated | No |
| SHIP-OQ-01 | Does shipping cost ever vary? | Single cart/address tested | No |
| PAY-OQ-01 | Are payment-method fees fixed or contextual? | Single session tested | No |
| OHIST-OQ-01 | Can a guest-checkout order be retrieved afterward? | Guest order not completed in discovery | No |
| ACCT-OQ-01 | What do the untested account subareas do? | Not exercised | No |
| DATA-OQ-01 | What is the shared-instance data-reset/isolation policy? | Unknown, third-party instance | No — flagged for CP-MVP2-04 |
| NFR thresholds (§9.2) | What are the approved numeric performance targets? | Not evidenced, not invented | No — flagged for CP-MVP2-08, requires separate Human/Project Target approval |

**Governance ruling:** per explicit Human Owner instruction, none of the above block this baseline's approval. They remain open work items for later checkpoints or future discovery, tracked here so they are not lost.

## 14. Requirement Traceability (Journeys ↔ Requirements)

| Journey | Traceable Requirements | Test Case ID | Automation ID | Evidence Artifacts |
|---|---|---|---|---|
| J-01 | REQ-REG-01…05, REQ-AUTH-01…03, REQ-SRCH-01…02, REQ-BRW-01, REQ-CART-01…05, REQ-ACO-01…03, REQ-SHIP-01, REQ-PAY-01…03, REQ-CONF-01…02, REQ-OHIST-01, REQ-ACCT-01, NEG-01…07 | Not yet created (CP-MVP2-03) | Not yet created (CP-MVP2-05) | `discover.js`, `probe.js`–`probe6.js` outputs, `checkout_00.html`–`checkout_final.html` |
| J-02 | REQ-BRW-01, REQ-CART-01, REQ-GCO-01…03, REQ-ACO-03 (shared field rules), REQ-SHIP-01, REQ-PAY-01…03, NEG-06 | Not yet created | Not yet created | `probe3_results.json`, `probe4.js` output, `anon_checkout.html`, `guest_checkout_step1.html` |
| J-03 | REQ-CFG-01, REQ-CART-01, NEG-08 | Not yet created | Not yet created | `probe5_results.json` |
| J-04 | REQ-CART-02…04, NEG-07 | Not yet created | Not yet created | `probe6_results.json` |
| J-05 | REQ-WISH-01…03 | Not yet created | Not yet created | `wishlist_sweep_results.json`, `wishlist_confirm.js` output |

**Traceability check result:** every one of the 5 approved journeys has at least one directly-mapped, approved requirement. No approved journey is currently un-traced. (Full validation detail in the accompanying validation report.)

## 15. Approval Decision

| Field | Value |
|---|---|
| **SRS Version** | **1.0** |
| **Status** | **APPROVED BASELINE** |
| **Baseline date** | **2026-09-11** |
| **Approver** | **Human Owner** (vaijanath.ruge@gmail.com) |
| Checkpoint | CP-MVP2-01 — Application Discovery & Approved SRS (complete) |
| Prepared by | Agentic session (Claude Code), executing explicit governance decisions issued by the Human Owner |
| Predecessor document | `requirements/MVP2_SRS_DRAFT.md` (retained, unmodified) |

**This SRS (v1.0) becomes the immutable source of truth for CP-MVP2-02 onward.** All subsequent checkpoints (Knowledge Base/RAG, LLM test-case generation, test data generation, Playwright automation, real browser execution, RCA/replanning, JMeter performance testing, final QE reporting) shall treat this document — not the draft, and not raw discovery evidence — as the authoritative requirements source.

**Change control:** Any change to this baseline after approval (adding/removing a journey, promoting a parked item to approved, altering a requirement's scope) requires a new versioned revision (e.g., v1.1) produced through the same governance process, with an explicit changelog entry. **No silent modification of this baseline is permitted.** Parked items in §13 may be resolved and promoted only through such a versioned change, never by direct edit of this file.

---

*End of Approved SRS v1.0. CP-MVP2-02 may now proceed using this document as its authoritative requirements source, subject to the Human Owner's separate go-ahead.*
