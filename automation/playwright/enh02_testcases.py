"""
Post-MVP2 Enhancement 02 — the new, explicit, business-level testcase
corpus (25 testcases across 25 requirements). Each testcase's business
steps and expected result are grounded directly in that requirement's own
Statement/Acceptance Criteria text in `requirements/MVP2_SRS_v1.0_APPROVED.md`
-- nothing invented beyond what the Approved SRS already states. None of
the historical MVP2 testcases (`testcases/generated/`, frozen at baseline
`33b9946`) are modified; this is an entirely new, additive corpus,
following the same pattern established by
`automation/playwright/enh01_testcase.py`.

`test_type` uses the same POSITIVE/NEGATIVE/ALTERNATE/EXCEPTIONAL
vocabulary already established by CP-03 (`testcases/schema.py`), reused
verbatim, no new vocabulary invented.
"""
from __future__ import annotations

ENH02_TESTCASES = [
    {
        "testcase_id": "ENH02-TC-REQ-REG-02-MISMATCH",
        "requirement_ids": ["REQ-REG-02"],
        "title": "Registration rejects mismatched Password/Confirm password",
        "objective": "Verify REQ-REG-02: registration is rejected when the two password fields do not match.",
        "test_type": "NEGATIVE",
        "preconditions": ["The real registration page is reachable."],
        "business_steps": [
            "Navigate to the home page.",
            "Select the 'Register' link.",
            "Enter valid, unique First name, Last name, and Email.",
            "Enter a valid Password.",
            "Enter a different value in Confirm password.",
            "Submit the registration form.",
            "Observe the resulting page for the password-mismatch message.",
        ],
        "expected_result": "REQ-REG-02 (Approved SRS): \"The password and confirmation password do not match.\" is shown and no account is created.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-REG-02-01"],
        "automation_id": "ENH02-PW-TC-REQ-REG-02-MISMATCH", "status": "AUTOMATED", "notes": "Non-mutating: rejected submission, no account created.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-REG-03-MALFORMED-EMAIL",
        "requirement_ids": ["REQ-REG-03"],
        "title": "Registration rejects a malformed email",
        "objective": "Verify REQ-REG-03: registration is rejected when the email is not a valid email format.",
        "test_type": "NEGATIVE",
        "preconditions": ["The real registration page is reachable."],
        "business_steps": [
            "Navigate to the home page.",
            "Select the 'Register' link.",
            "Enter valid First name, Last name.",
            "Enter a malformed email value (not-an-email).",
            "Enter matching, valid Password and Confirm password.",
            "Submit the registration form.",
            "Observe the resulting page for the email-format message.",
        ],
        "expected_result": "REQ-REG-03 (Approved SRS): \"Wrong email\" is shown and no account is created.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-REG-03-01"],
        "automation_id": "ENH02-PW-TC-REQ-REG-03-MALFORMED-EMAIL", "status": "AUTOMATED", "notes": "Non-mutating: rejected submission.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-REG-05-AUTO-LOGIN",
        "requirement_ids": ["REQ-REG-05"],
        "title": "Successful registration authenticates the user automatically",
        "objective": "Verify REQ-REG-05: a valid, unique registration results in an immediately authenticated state, with no separate login step.",
        "test_type": "POSITIVE",
        "preconditions": ["The real registration page is reachable."],
        "business_steps": [
            "Navigate to the home page.",
            "Select the 'Register' link.",
            "Enter a genuinely unique, synthetic First name, Last name, Email (timestamp-suffixed to guarantee uniqueness), Password, and Confirm password.",
            "Submit the registration form.",
            "Observe the resulting page for an authenticated-state indicator (e.g. the account/logout link replacing 'Register'/'Log in').",
        ],
        "expected_result": "REQ-REG-05 (Approved SRS): the resulting page shows an authenticated state without a separate login step.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-REG-05-01"],
        "automation_id": "ENH02-PW-TC-REQ-REG-05-AUTO-LOGIN", "status": "AUTOMATED",
        "notes": "The ONE real, one-time account creation this enhancement performs. Never repeated/parallelized. Reused (read-only afterward) by REQ-REG-04/AUTH-01/AUTH-03/ACCT-01/CART-05/PWR-01.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-REG-04-DUPLICATE-EMAIL",
        "requirement_ids": ["REQ-REG-04"],
        "title": "Registration rejects a duplicate email",
        "objective": "Verify REQ-REG-04: attempting to register again with an email already on file is rejected.",
        "test_type": "NEGATIVE",
        "preconditions": ["The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN already exists."],
        "business_steps": [
            "Navigate to the home page.",
            "Select the 'Register' link.",
            "Enter valid First name, Last name, matching Password/Confirm password.",
            "Enter the Email already used by the real account from ENH02-TC-REQ-REG-05-AUTO-LOGIN.",
            "Submit the registration form.",
            "Observe the resulting page for the duplicate-email message.",
        ],
        "expected_result": "REQ-REG-04 (Approved SRS): \"The specified email already exists\" is shown and no second account is created.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-REG-04-01"],
        "automation_id": "ENH02-PW-TC-REQ-REG-04-DUPLICATE-EMAIL", "status": "AUTOMATED",
        "notes": "Reuses the one real account's email; never registers a second real account.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-AUTH-01-VALID-LOGIN",
        "requirement_ids": ["REQ-AUTH-01"],
        "title": "Login succeeds with correct, registered credentials",
        "objective": "Verify REQ-AUTH-01: correct email/password reaches an authenticated state.",
        "test_type": "POSITIVE",
        "preconditions": ["The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN already exists and is logged out."],
        "business_steps": [
            "Navigate to the home page.",
            "Select the 'Log in' link.",
            "Enter the real account's Email and Password.",
            "Submit the login form.",
            "Observe the resulting page for an authenticated-state indicator.",
        ],
        "expected_result": "REQ-AUTH-01 (Approved SRS): an authenticated state is reached.",
        "risk": "HIGH", "priority": "HIGH",
        "dataset_ids": ["ENH02-TD-REG-05-01"],
        "automation_id": "ENH02-PW-TC-REQ-AUTH-01-VALID-LOGIN", "status": "AUTOMATED", "notes": "Uses the one real account; read-only.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-AUTH-02-WRONG-PASSWORD",
        "requirement_ids": ["REQ-AUTH-02"],
        "title": "Login rejects an incorrect password with a generic message",
        "objective": "Verify REQ-AUTH-02: an incorrect password is rejected with a generic, non-field-specific message.",
        "test_type": "NEGATIVE",
        "preconditions": ["The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN already exists."],
        "business_steps": [
            "Navigate to the home page.",
            "Select the 'Log in' link.",
            "Enter the real account's registered Email with an incorrect password.",
            "Submit the login form.",
            "Observe the resulting page for the generic rejection message.",
        ],
        "expected_result": "REQ-AUTH-02 (Approved SRS): \"The credentials provided are incorrect\" is shown and no session is created.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-REG-05-01"],
        "automation_id": "ENH02-PW-TC-REQ-AUTH-02-WRONG-PASSWORD", "status": "AUTOMATED",
        "notes": "Real finding (this task): the exact SRS-quoted message only appears for a *registered* email with a wrong password; a non-existent email instead produces a real, different message ('No customer account found.'). Reuses the one real account; never authenticates.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-AUTH-03-RELOGIN",
        "requirement_ids": ["REQ-AUTH-03"],
        "title": "A just-registered account can log in again after logout",
        "objective": "Verify REQ-AUTH-03: no hidden onboarding blocker prevents an immediate, explicit re-login.",
        "test_type": "POSITIVE",
        "preconditions": ["The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN exists (already authenticated from registration)."],
        "business_steps": [
            "From the authenticated state left by registration, select 'Log out'.",
            "Select the 'Log in' link.",
            "Enter the real account's Email and Password.",
            "Submit the login form.",
            "Observe the resulting page for an authenticated-state indicator.",
        ],
        "expected_result": "REQ-AUTH-03 (Approved SRS): login succeeds.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-REG-05-01"],
        "automation_id": "ENH02-PW-TC-REQ-AUTH-03-RELOGIN", "status": "AUTOMATED", "notes": "Uses the one real account.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-PWR-01-RECOVERY-UI",
        "requirement_ids": ["REQ-PWR-01"],
        "title": "Password recovery request accepted at the UI level",
        "objective": "Verify REQ-PWR-01: submitting a password-recovery request for a registered email shows UI acceptance, no error.",
        "test_type": "POSITIVE",
        "preconditions": ["The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN exists."],
        "business_steps": [
            "Navigate to the password-recovery page.",
            "Enter the real account's registered Email.",
            "Submit the recovery request.",
            "Observe the resulting page for the acceptance message and absence of an error.",
        ],
        "expected_result": "REQ-PWR-01 (Approved SRS): the UI shows acceptance and no error. (UI-acceptance scope only -- email delivery/reset-token validity are explicitly out of MVP2 acceptance scope, per SRS sec. 6.3.)",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": ["ENH02-TD-REG-05-01"],
        "automation_id": "ENH02-PW-TC-REQ-PWR-01-RECOVERY-UI", "status": "AUTOMATED", "notes": "Read-only UI check; no email delivery verified or claimed.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-SRCH-01-VALID-KEYWORD",
        "requirement_ids": ["REQ-SRCH-01"],
        "title": "Search returns matching product results for a valid keyword",
        "objective": "Verify REQ-SRCH-01: a keyword matching existing products renders at least one result.",
        "test_type": "POSITIVE",
        "preconditions": ["The real search page is reachable."],
        "business_steps": [
            "Navigate to the home page.",
            "Enter a real, known keyword (e.g. 'book') in the search box.",
            "Submit the search.",
            "Observe the results page for at least one rendered result.",
        ],
        "expected_result": "REQ-SRCH-01 (Approved SRS): at least one result renders.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-SRCH-01-01"],
        "automation_id": "ENH02-PW-TC-REQ-SRCH-01-VALID-KEYWORD", "status": "AUTOMATED", "notes": "Safe, read-only GET.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-SRCH-02-NO-RESULTS",
        "requirement_ids": ["REQ-SRCH-02"],
        "title": "Search shows an explicit no-results message for a nonsense keyword",
        "objective": "Verify REQ-SRCH-02: a keyword matching nothing shows the explicit no-results message.",
        "test_type": "NEGATIVE",
        "preconditions": ["The real search page is reachable."],
        "business_steps": [
            "Navigate to the home page.",
            "Enter a nonsense keyword guaranteed to match nothing.",
            "Submit the search.",
            "Observe the results page for the explicit no-results message.",
        ],
        "expected_result": "REQ-SRCH-02 (Approved SRS): \"No products were found that matched your criteria.\" is shown, zero results render.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": ["ENH02-TD-SRCH-02-01"],
        "automation_id": "ENH02-PW-TC-REQ-SRCH-02-NO-RESULTS", "status": "AUTOMATED", "notes": "Safe, read-only GET.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-BRW-01-CATEGORY-GRID",
        "requirement_ids": ["REQ-BRW-01"],
        "title": "Selecting a top-level category renders a product grid",
        "objective": "Verify REQ-BRW-01: navigating to a top-level category renders a product grid.",
        "test_type": "POSITIVE",
        "preconditions": ["The real main navigation is reachable."],
        "business_steps": [
            "Navigate to the home page.",
            "Select the 'Books' top-level category link from the main navigation.",
            "Observe the resulting page for a rendered product grid.",
        ],
        "expected_result": "REQ-BRW-01 (Approved SRS): a product grid renders.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-BRW-01-CATEGORY-GRID", "status": "AUTOMATED", "notes": "Safe, read-only GET.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-CFG-01-MANDATORY-ATTRIBUTE",
        "requirement_ids": ["REQ-CFG-01"],
        "title": "Add to Cart blocked when a mandatory configurable attribute is unselected",
        "objective": "Verify REQ-CFG-01: a configurable product with an unselected mandatory attribute blocks Add to Cart with a message naming that attribute.",
        "test_type": "NEGATIVE",
        "preconditions": ["A real configurable product page ('Build your own computer') with a mandatory, no-default attribute (HDD) is reachable."],
        "business_steps": [
            "Navigate to the 'Build your own computer' product page.",
            "Leave the mandatory HDD attribute unselected.",
            "Select Add to Cart.",
            "Observe the resulting message for a specific reference to the missing attribute.",
            "Confirm the cart remains unchanged.",
        ],
        "expected_result": "REQ-CFG-01 (Approved SRS): a message names the missing attribute (\"Please select HDD\") and the cart is unchanged.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-CFG-01-MANDATORY-ATTRIBUTE", "status": "AUTOMATED",
        "notes": "Real, live-discovered evidence (this task): the mandatory attribute is 'HDD' (radio group product_attribute_16_3_6, no default selection); real observed message 'Please select HDD'.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-CART-01-ADD-CONFIRMATION",
        "requirement_ids": ["REQ-CART-01"],
        "title": "Add to Cart confirms the addition",
        "objective": "Verify REQ-CART-01: adding a product to the cart shows a success notice and increments the cart count.",
        "test_type": "POSITIVE",
        "preconditions": ["A real product detail page is reachable."],
        "business_steps": [
            "Navigate to a real product detail page ('3rd Album').",
            "Select Add to Cart.",
            "Observe the success notice.",
            "Observe the cart-count indicator incrementing.",
        ],
        "expected_result": "REQ-CART-01 (Approved SRS): a success notice appears and cart count increments.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-CART-01-ADD-CONFIRMATION", "status": "AUTOMATED", "notes": "Session-scoped cart; safe, ephemeral.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-CART-02-QUANTITY-UPDATE",
        "requirement_ids": ["REQ-CART-02"],
        "title": "Updating quantity recalculates subtotal and total",
        "objective": "Verify REQ-CART-02: changing a cart line's quantity recalculates that line's subtotal proportionally.",
        "test_type": "POSITIVE",
        "preconditions": ["A cart with one real item exists (chained from REQ-CART-01's own add step)."],
        "business_steps": [
            "With one item in the cart, navigate to the cart page.",
            "Change the line item's quantity from 1 to 3.",
            "Select 'Update shopping cart'.",
            "Observe the line subtotal and cart total for proportional recalculation.",
        ],
        "expected_result": "REQ-CART-02 (Approved SRS): subtotal = unit price x 3 and the cart total reflects it.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-CART-02-QUANTITY-UPDATE", "status": "AUTOMATED", "notes": "Session-scoped, chained after adding one real item.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-CART-03-ZERO-QUANTITY-REMOVES",
        "requirement_ids": ["REQ-CART-03"],
        "title": "Setting quantity to 0 removes the line item without a prompt",
        "objective": "Verify REQ-CART-03: a cart line whose quantity is set to 0 and updated is removed silently.",
        "test_type": "NEGATIVE",
        "preconditions": ["A cart with one real item exists."],
        "business_steps": [
            "With one item in the cart, navigate to the cart page.",
            "Set the line item's quantity to 0.",
            "Select 'Update shopping cart'.",
            "Observe that the line item no longer appears and no confirmation dialog was shown.",
        ],
        "expected_result": "REQ-CART-03 (Approved SRS): the line item no longer appears; no prompt is shown.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-CART-03-ZERO-QUANTITY-REMOVES", "status": "AUTOMATED", "notes": "Session-scoped.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-CART-04-EMPTY-CART-STATE",
        "requirement_ids": ["REQ-CART-04"],
        "title": "Empty cart shows an empty-state message and blocks checkout",
        "objective": "Verify REQ-CART-04: an empty cart shows the empty-state message with no active checkout.",
        "test_type": "NEGATIVE",
        "preconditions": ["The cart is empty (chained after REQ-CART-03's own removal step, or a fresh session)."],
        "business_steps": [
            "With an empty cart, navigate to the cart page.",
            "Observe the empty-state message.",
            "Confirm no active checkout action is available.",
        ],
        "expected_result": "REQ-CART-04 (Approved SRS): \"Your Shopping Cart is empty!\" shows and checkout cannot proceed.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-CART-04-EMPTY-CART-STATE", "status": "AUTOMATED", "notes": "Session-scoped.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-CART-05-PERSISTENCE-ACROSS-LOGIN",
        "requirement_ids": ["REQ-CART-05"],
        "title": "Anonymous cart item persists after logging in",
        "objective": "Verify REQ-CART-05: an item added anonymously remains present in the cart immediately after the same session authenticates.",
        "test_type": "POSITIVE",
        "preconditions": ["The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN exists."],
        "business_steps": [
            "As an anonymous session, add a real product to the cart.",
            "Log in with the real account's Email/Password, same browser session.",
            "Navigate to the cart page.",
            "Observe that the previously added item is still present.",
        ],
        "expected_result": "REQ-CART-05 (Approved SRS): the anonymously added item remains visible after login.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": ["ENH02-TD-REG-05-01"],
        "automation_id": "ENH02-PW-TC-REQ-CART-05-PERSISTENCE-ACROSS-LOGIN", "status": "AUTOMATED",
        "notes": "Uses the one real account. Per SRS sec. 6.7's own governance note, this is narrow outcome evidence only -- CART-OQ-01 (merge vs. session-continuity mechanism) remains parked, not asserted here.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-WISH-01-ADD-TO-WISHLIST",
        "requirement_ids": ["REQ-WISH-01"],
        "title": "Add to Wishlist on an eligible product detail page",
        "objective": "Verify REQ-WISH-01: a product detail page exposing Add to Wishlist allows adding the product to the wishlist.",
        "test_type": "POSITIVE",
        "preconditions": ["A real, eligible product detail page (Digital Downloads: '3rd Album') exposing Add to Wishlist is reachable."],
        "business_steps": [
            "Navigate to the '3rd Album' product detail page.",
            "Select 'Add to wishlist'.",
            "Observe the wishlist-add confirmation.",
        ],
        "expected_result": "REQ-WISH-01 (Approved SRS): a wishlist-add confirmation shows.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-WISH-01-ADD-TO-WISHLIST", "status": "AUTOMATED",
        "notes": "Anonymous, session-scoped; per SRS sec. 6.8, eligibility is product-specific, never generalized to every product.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM",
        "requirement_ids": ["REQ-WISH-02"],
        "title": "Wishlist page reflects a just-added item with price and actions",
        "objective": "Verify REQ-WISH-02: the /wishlist page shows a just-added item with its price and available actions.",
        "test_type": "POSITIVE",
        "preconditions": ["An item was just added to the wishlist (chained from REQ-WISH-01)."],
        "business_steps": [
            "After adding an item to the wishlist, navigate to the wishlist page.",
            "Observe the item's presence, price, and available actions (Remove, Add to cart).",
        ],
        "expected_result": "REQ-WISH-02 (Approved SRS): the item appears with price and available actions.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM", "status": "AUTOMATED", "notes": "Chained after REQ-WISH-01.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-WISH-03-SHAREABLE-URL",
        "requirement_ids": ["REQ-WISH-03"],
        "title": "Anonymous wishlist displays a shareable URL",
        "objective": "Verify REQ-WISH-03: an anonymous user's wishlist page displays a shareable URL, without requiring an account.",
        "test_type": "POSITIVE",
        "preconditions": ["An anonymous session has items in its wishlist (chained from REQ-WISH-01)."],
        "business_steps": [
            "As an anonymous session with items in the wishlist, navigate to the wishlist page.",
            "Observe the page for a displayed shareable URL.",
        ],
        "expected_result": "REQ-WISH-03 (Approved SRS): a shareable URL is displayed.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-WISH-03-SHAREABLE-URL", "status": "AUTOMATED", "notes": "Anonymous, chained after REQ-WISH-01.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-GCO-01-GUEST-CHECKOUT-INIT",
        "requirement_ids": ["REQ-GCO-01"],
        "title": "Anonymous user initiates checkout via 'Checkout as Guest'",
        "objective": "Verify REQ-GCO-01: an anonymous user with cart items can initiate checkout via an explicit guest option, without creating an account.",
        "test_type": "POSITIVE",
        "preconditions": ["An anonymous session has a real item in the cart."],
        "business_steps": [
            "With a real item in the cart, accept the Terms of Service checkbox.",
            "Select 'Checkout'.",
            "On the guest-or-register interstitial, select 'Checkout as Guest'.",
            "Observe that the checkout page loads, still anonymous (no account created).",
        ],
        "expected_result": "REQ-GCO-01 (Approved SRS): a working 'Checkout as Guest' path proceeds without login/registration.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-GCO-01-GUEST-CHECKOUT-INIT", "status": "AUTOMATED", "notes": "Stops at checkout entry; does not submit billing/shipping/payment data or complete an order (see REQ-GCO-03).",
    },
    {
        "testcase_id": "ENH02-TC-REQ-GCO-02-GUEST-STEP-SEQUENCE",
        "requirement_ids": ["REQ-GCO-02"],
        "title": "Guest checkout presents the same Billing Address step as authenticated checkout",
        "objective": "Verify REQ-GCO-02: the guest checkout session renders the same named step structure as the authenticated flow.",
        "test_type": "POSITIVE",
        "preconditions": ["A guest checkout session has just been initiated (chained from REQ-GCO-01)."],
        "business_steps": [
            "Having reached the guest checkout page, observe the first step's heading/content.",
        ],
        "expected_result": "REQ-GCO-02 (Approved SRS): the same named 'Billing address' step structure appears as for an authenticated user.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-GCO-02-GUEST-STEP-SEQUENCE", "status": "AUTOMATED", "notes": "Chained after REQ-GCO-01; does not proceed past Billing Address.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-ACO-03-ADDRESS-FORM-VALIDATION",
        "requirement_ids": ["REQ-ACO-03"],
        "title": "Billing address form blocks progression when required fields are blank",
        "objective": "Verify REQ-ACO-03: submitting the Billing Address step with required fields blank blocks progression.",
        "test_type": "NEGATIVE",
        "preconditions": ["A guest checkout session has reached the Billing Address step (chained from REQ-GCO-01/02)."],
        "business_steps": [
            "At the Billing Address step, leave the required fields (First name, Last name, Email, Country, City, Address 1, Zip/postal code, Phone number) blank.",
            "Attempt to continue to the next step.",
            "Observe that progression is blocked.",
        ],
        "expected_result": "REQ-ACO-03 (Approved SRS): progression to the next step is blocked when required fields are blank.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-ACO-03-ADDRESS-FORM-VALIDATION", "status": "AUTOMATED",
        "notes": "New, non-mutating validation-only automation. Real FAIL evidence from the original MVP2 real-execution vertical slice (REALISM-SLICE-EXEC-D01, etc.) already exists separately and is not re-created or overwritten here.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-ACCT-01-ACCOUNT-PAGES",
        "requirement_ids": ["REQ-ACCT-01"],
        "title": "Authenticated customer can access Customer Info, Addresses, and Orders",
        "objective": "Verify REQ-ACCT-01: all three account pages load without redirect to login for an authenticated session.",
        "test_type": "POSITIVE",
        "preconditions": ["The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN exists and is authenticated."],
        "business_steps": [
            "While authenticated, navigate to the Customer Info page.",
            "Navigate to the Addresses page.",
            "Navigate to the Orders page.",
            "Observe that each page loads without redirecting to the login page.",
        ],
        "expected_result": "REQ-ACCT-01 (Approved SRS): each of the three account pages loads without redirect to login.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": ["ENH02-TD-REG-05-01"],
        "automation_id": "ENH02-PW-TC-REQ-ACCT-01-ACCOUNT-PAGES", "status": "AUTOMATED", "notes": "Uses the one real account; read-only.",
    },

    # --- Post-MVP2 Enhancement 02 Deferred-10 Closure: the ONE real,
    # order-completing checkout, and its two directly-dependent follow-on
    # checks. Real evidence for the exact business steps below (field
    # ids, step-transition buttons, real Payments.CashOnDelivery/
    # CheckMoneyOrder Payment Info content, the real $7.00
    # "Payment method additional fee" this SUT applies to
    # Payments.CashOnDelivery) comes from a real, live Playwright
    # investigation this task performed against the real SUT (never
    # confirming an order during that investigation), cross-checked
    # against the original CP01 discovery captures in
    # `knowledge/historical/discovery_evidence/captures/checkout_00.html`
    # through `checkout_final.html`.
    {
        "testcase_id": "ENH02-TC-REQ-ACO-01-AUTHENTICATED-CHECKOUT-COMPLETION",
        "requirement_ids": ["REQ-ACO-01", "REQ-SHIP-01", "REQ-PAY-01", "REQ-PAY-02", "REQ-PAY-03", "REQ-CONF-01", "REQ-CONF-02"],
        "title": "Authenticated checkout proceeds through all named steps to a completed order",
        "objective": (
            "Verify REQ-ACO-01 (authenticated checkout reaches a completed order through Billing Address, "
            "Shipping Address, Shipping Method, Payment Method, Payment Info, Confirm Order), and, as real, "
            "directly-observed checkpoints within that same, single, non-repeatable state transition: "
            "REQ-SHIP-01 (Shipping Method presents multiple real options), REQ-PAY-01 (Payment Method presents "
            "multiple real options), REQ-PAY-03 (Cash On Delivery requires no payment-detail form), REQ-PAY-02 "
            "(the fee-bearing payment method's fee is reflected in the order total), and REQ-CONF-01/REQ-CONF-02 "
            "(the completed order shows a success message with a unique order number, and the confirmed total "
            "equals the sum of its components)."
        ),
        "test_type": "POSITIVE",
        "preconditions": [
            "The real account created by ENH02-TC-REQ-REG-05-AUTO-LOGIN exists and is authenticated.",
            "A real, physical (non-digital-download) product is reachable ('Computing and Internet' book) -- "
            "real evidence, this task: a cart containing only digital-download items skips the Shipping Address/"
            "Shipping Method steps entirely, so a physical item is a genuine precondition, not an implementation "
            "detail.",
        ],
        "business_steps": [
            "Add the real 'Computing and Internet' product to the cart.",
            "Accept the Terms of Service checkbox and select 'Checkout' (already authenticated: no guest interstitial appears).",
            "At the Billing Address step, enter First name, Last name, Email, Country (United States), State, City, Address 1, Zip/postal code, Phone number, then Continue.",
            "At the Shipping Address step, accept the pre-selected address (the just-entered Billing Address, auto-saved and offered as the default shipping address), then Continue.",
            "At the Shipping Method step, observe that multiple real shipping options are presented; select the default option and Continue.",
            "At the Payment Method step, observe that multiple real payment options are presented; select Cash On Delivery and Continue.",
            "At the Payment Info step, observe that Cash On Delivery presents no payment-detail form, then Continue.",
            "At the Confirm Order step, observe the real Sub-Total/Shipping/Payment method additional fee/Tax/Total breakdown.",
            "Select 'Confirm' to submit the order.",
            "Observe the Order Completed page for the success message and a real, unique order number.",
        ],
        "expected_result": (
            "REQ-ACO-01: the order completes and the Order Completed page renders. REQ-SHIP-01/REQ-PAY-01: each "
            "respective step presents more than one real, selectable option. REQ-PAY-03: the Payment Info step "
            "renders zero real input/select/textarea fields for Cash On Delivery. REQ-PAY-02: the confirmed total "
            "reflects the payment method's additional fee. REQ-CONF-01: a real order number is shown. REQ-CONF-02: "
            "Total == Sub-Total + Shipping + Payment method additional fee + Tax (computed check, never a "
            "hard-coded literal per SRS sec. 10)."
        ),
        "risk": "HIGH", "priority": "HIGH",
        "dataset_ids": ["ENH02-TD-ACO-01-01"],
        "automation_id": "ENH02-PW-TC-REQ-ACO-01-AUTHENTICATED-CHECKOUT-COMPLETION", "status": "AUTOMATED",
        "notes": (
            "The ONE real, permanent order this closure work creates -- never repeated, never parallelized. "
            "Chained immediately after ENH02-TC-REQ-PWR-01-RECOVERY-UI in the same real browser session/test "
            "function, reusing the already-authenticated shared account rather than logging in again. Reused "
            "(read-only afterward) by ENH02-TC-REQ-OHIST-01-ORDER-APPEARS-IN-HISTORY and "
            "ENH02-TC-REQ-ACO-02-SAVED-ADDRESS-REUSE."
        ),
    },
    {
        "testcase_id": "ENH02-TC-REQ-OHIST-01-ORDER-APPEARS-IN-HISTORY",
        "requirement_ids": ["REQ-OHIST-01"],
        "title": "A just-completed order appears in the customer's Order History",
        "objective": "Verify REQ-OHIST-01: the real order number just obtained from Order Completed appears in /customer/orders.",
        "test_type": "POSITIVE",
        "preconditions": ["The real order from ENH02-TC-REQ-ACO-01-AUTHENTICATED-CHECKOUT-COMPLETION has just completed, and its real order number is known."],
        "business_steps": [
            "Navigate to the Order History page (Orders, under My account).",
            "Observe that the real order number just obtained is listed.",
        ],
        "expected_result": "REQ-OHIST-01 (Approved SRS): the completed order appears in Order History.",
        "risk": "MEDIUM", "priority": "MEDIUM",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-OHIST-01-ORDER-APPEARS-IN-HISTORY", "status": "AUTOMATED",
        "notes": "Read-only; reuses the one real order, no new mutation.",
    },
    {
        "testcase_id": "ENH02-TC-REQ-ACO-02-SAVED-ADDRESS-REUSE",
        "requirement_ids": ["REQ-ACO-02"],
        "title": "A repeat checkout offers the previously-saved address via selection",
        "objective": "Verify REQ-ACO-02: on a second checkout entry by the same account, a previously-saved address is offered via a selection control, rather than requiring re-entry.",
        "test_type": "POSITIVE",
        "preconditions": ["The real account has at least one previously-saved address (from ENH02-TC-REQ-ACO-01-AUTHENTICATED-CHECKOUT-COMPLETION's real Billing Address submission)."],
        "business_steps": [
            "Add a real product to the cart.",
            "Accept the Terms of Service checkbox and select 'Checkout'.",
            "At the Billing Address step, observe the address-selection control.",
            "Do not proceed further (this testcase does not create a second order).",
        ],
        "expected_result": "REQ-ACO-02 (Approved SRS): the address-selection control offers the previously-saved address as an option, in addition to 'New Address'.",
        "risk": "LOW", "priority": "LOW",
        "dataset_ids": [],
        "automation_id": "ENH02-PW-TC-REQ-ACO-02-SAVED-ADDRESS-REUSE", "status": "AUTOMATED",
        "notes": (
            "Deliberately stops at Billing Address -- per governing instruction sec. 7/8 ('minimum necessary "
            "permanent state creation', 'no duplicate-order pollution'), this enhancement creates exactly ONE "
            "real order; this testcase reuses that order's real saved-address side effect rather than "
            "completing a second one."
        ),
    },
]
