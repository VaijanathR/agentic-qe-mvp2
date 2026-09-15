"""
Post-MVP2 Enhancement 02 -- the ONE real, one-time account this
enhancement creates, and every real testcase that reuses it, chained
sequentially in a single real browser session/test function:

REQ-REG-05 (register) -> REQ-REG-04 (duplicate-email rejection) ->
REQ-AUTH-01 (login) -> REQ-AUTH-03 (logout + re-login) ->
REQ-ACCT-01 (account pages) -> REQ-CART-05 (cart persists across login) ->
REQ-PWR-01 (password-recovery UI acceptance)

Deliberately NOT run under pytest-xdist parallel workers (each worker
would otherwise attempt its own real registration) -- see the
Enhancement-02 report's "Real functional execution" section for how this
was invoked.
"""
from __future__ import annotations

from automation.playwright.components.navigation import start_at_home
from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.data_access import load_dataset
from automation.playwright.enh02_testdata import shared_account_credentials
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.account_pages import AccountPage, PasswordRecoveryPage
from automation.playwright.pages.cart_page import CartPage
from automation.playwright.pages.catalog_pages import ProductPage
from automation.playwright.pages.login_page import LoginPage
from automation.playwright.tests.enh02_helpers import real_execution

REQUIRED_FIELDS = ["first_name", "last_name", "email", "password", "confirm_password"]


def test_shared_account_chain(browser_page, worker_id):
    page, browser_version = browser_page
    dataset = load_dataset("ENH02-TD-REG-05-01", required_fields=REQUIRED_FIELDS)

    # --- REQ-REG-05: the one real registration ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-REG-05-AUTO-LOGIN", requirement_ids=["REQ-REG-05"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-REG-05-AUTO-LOGIN",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        home = start_at_home(page, DEFAULT_CONFIG)
        steps.append({"step_order": 1, "description": "Navigate to home page", "status": "PASS"})
        registration, nav_resolution = home.go_to_registration()
        steps.append({"step_order": 2, "description": "Select 'Register' link", "status": "PASS", "locator_resolution": nav_resolution.to_dict()})
        for field, method in [
            ("first_name", registration.fill_first_name), ("last_name", registration.fill_last_name),
            ("email", registration.fill_email), ("password", registration.fill_password),
            ("confirm_password", registration.fill_confirm_password),
        ]:
            resolution = method(dataset.fields[field])
            steps.append({"step_order": len(steps) + 1, "description": f"Fill {field}", "status": "PASS" if resolution["resolved_candidate"] else "FAIL", "locator_resolution": resolution})
        submit_resolution = registration.submit()
        steps.append({"step_order": len(steps) + 1, "description": "Submit registration form", "status": "PASS" if submit_resolution["resolved_candidate"] else "FAIL", "locator_resolution": submit_resolution})
        page.wait_for_timeout(1000)
        authenticated = page.locator("a.ico-logout").count() > 0
        steps.append({"step_order": len(steps) + 1, "description": "Observe authenticated-state indicator (no separate login step)", "status": "PASS" if authenticated else "FAIL"})
        mark(ExecutionStatus.PASS if authenticated else ExecutionStatus.FAIL, None if authenticated else "ASSERTION_FAILURE", None if authenticated else "No authenticated-state indicator observed")
        assert authenticated, "Real registration did not result in an authenticated state"

    # --- REQ-REG-04: duplicate email is rejected (reuses the same real email) ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-REG-04-DUPLICATE-EMAIL", requirement_ids=["REQ-REG-04"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-REG-04-DUPLICATE-EMAIL",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        page.locator("a.ico-logout").first.click()
        page.wait_for_timeout(1000)
        steps.append({"step_order": 1, "description": "Log out", "status": "PASS"})
        home = start_at_home(page, DEFAULT_CONFIG)
        steps.append({"step_order": 2, "description": "Navigate to home page", "status": "PASS"})
        registration, nav_resolution = home.go_to_registration()
        steps.append({"step_order": 3, "description": "Select 'Register' link", "status": "PASS", "locator_resolution": nav_resolution.to_dict()})
        registration.fill_first_name("Duplicate-Attempt")
        registration.fill_last_name("Duplicate-Attempt")
        registration.fill_email(dataset.fields["email"])
        registration.fill_password("Some-Other-Pw-1")
        registration.fill_confirm_password("Some-Other-Pw-1")
        steps.append({"step_order": 4, "description": "Fill the already-registered email with otherwise-valid data", "status": "PASS"})
        registration.submit()
        steps.append({"step_order": 5, "description": "Submit registration form", "status": "PASS"})
        page.wait_for_timeout(500)
        expected = "The specified email already exists"
        observed = expected in registration.result_text()
        steps.append({"step_order": 6, "description": "Observe duplicate-email message", "status": "PASS" if observed else "FAIL"})
        mark(ExecutionStatus.PASS if observed else ExecutionStatus.FAIL, None if observed else "ASSERTION_FAILURE", None if observed else "Duplicate-email message not observed")
        assert observed, "Real duplicate-email registration attempt did not show the expected message"

    # --- REQ-AUTH-01: login succeeds with correct credentials ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-AUTH-01-VALID-LOGIN", requirement_ids=["REQ-AUTH-01"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-AUTH-01-VALID-LOGIN",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        creds = shared_account_credentials()
        login = LoginPage(page, DEFAULT_CONFIG)
        login.open()
        steps.append({"step_order": 1, "description": "Navigate to login page", "status": "PASS"})
        email_res = login.fill_email(creds["email"])
        steps.append({"step_order": 2, "description": "Fill real account email", "status": "PASS" if email_res["resolved_candidate"] else "FAIL", "locator_resolution": email_res})
        password_res = login.fill_password(creds["password"])
        steps.append({"step_order": 3, "description": "Fill real account password", "status": "PASS" if password_res["resolved_candidate"] else "FAIL", "locator_resolution": password_res})
        submit_res = login.submit()
        steps.append({"step_order": 4, "description": "Submit login form", "status": "PASS" if submit_res["resolved_candidate"] else "FAIL", "locator_resolution": submit_res})
        page.wait_for_timeout(1000)
        authenticated = login.is_authenticated()
        steps.append({"step_order": 5, "description": "Observe authenticated state", "status": "PASS" if authenticated else "FAIL"})
        mark(ExecutionStatus.PASS if authenticated else ExecutionStatus.FAIL, None if authenticated else "ASSERTION_FAILURE", None if authenticated else "Authenticated state not reached")
        assert authenticated, "Real login with correct credentials did not reach an authenticated state"

    # --- REQ-AUTH-02: wrong password rejected with the generic message
    # (real finding, this task: only appears for a REGISTERED email) ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-AUTH-02-WRONG-PASSWORD", requirement_ids=["REQ-AUTH-02"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-AUTH-02-WRONG-PASSWORD",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        creds = shared_account_credentials()
        page.locator("a.ico-logout").first.click()
        page.wait_for_timeout(1000)
        steps.append({"step_order": 1, "description": "Log out first, so this check starts from a genuinely anonymous session", "status": "PASS"})
        login = LoginPage(page, DEFAULT_CONFIG)
        login.open()
        steps.append({"step_order": 2, "description": "Navigate to login page", "status": "PASS"})
        login.fill_email(creds["email"])
        login.fill_password("Deliberately-Wrong-Pw-1")
        steps.append({"step_order": 3, "description": "Fill the real account's email with an incorrect password", "status": "PASS"})
        login.submit()
        steps.append({"step_order": 4, "description": "Submit login form", "status": "PASS"})
        page.wait_for_timeout(500)
        expected = "The credentials provided are incorrect"
        result_text = login.result_text()
        observed = expected in result_text
        not_authenticated = not login.is_authenticated()
        steps.append({"step_order": 5, "description": "Observe generic rejection message and no session", "status": "PASS" if (observed and not_authenticated) else "FAIL"})
        success = observed and not_authenticated
        mark(ExecutionStatus.PASS if success else ExecutionStatus.FAIL, None if success else "ASSERTION_FAILURE", None if success else f"observed={observed} not_authenticated={not_authenticated}")
        assert success, f"Real execution did not observe the expected generic rejection (observed={observed}, not_authenticated={not_authenticated})"

    # --- REQ-AUTH-03: logout then re-login succeeds ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-AUTH-03-RELOGIN", requirement_ids=["REQ-AUTH-03"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-AUTH-03-RELOGIN",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        creds = shared_account_credentials()
        # The session is already logged out at this point (carried over
        # from ENH02-TC-REQ-AUTH-02-WRONG-PASSWORD's own real, deliberate
        # logout step, run immediately before this one) -- the real
        # logout -> login sequence REQ-AUTH-03 requires has already
        # genuinely occurred; this testcase's own contribution is the
        # real re-login itself.
        login = LoginPage(page, DEFAULT_CONFIG)
        login.open()
        steps.append({"step_order": 1, "description": "Navigate to login page (session already logged out)", "status": "PASS"})
        login.fill_email(creds["email"])
        login.fill_password(creds["password"])
        login.submit()
        steps.append({"step_order": 2, "description": "Log in again with the same real account", "status": "PASS"})
        page.wait_for_timeout(1000)
        authenticated = login.is_authenticated()
        steps.append({"step_order": 3, "description": "Observe authenticated state", "status": "PASS" if authenticated else "FAIL"})
        mark(ExecutionStatus.PASS if authenticated else ExecutionStatus.FAIL, None if authenticated else "ASSERTION_FAILURE", None if authenticated else "Re-login did not reach an authenticated state")
        assert authenticated, "Real re-login did not succeed"

    # --- REQ-ACCT-01: account pages load without redirect to login ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-ACCT-01-ACCOUNT-PAGES", requirement_ids=["REQ-ACCT-01"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-ACCT-01-ACCOUNT-PAGES",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        account = AccountPage(page, DEFAULT_CONFIG)
        results = {}
        for name, opener in [("Customer Info", account.open_customer_info), ("Addresses", account.open_addresses), ("Orders", account.open_orders)]:
            opener()
            page.wait_for_timeout(500)
            redirected = account.redirected_to_login()
            results[name] = redirected
            steps.append({"step_order": len(steps) + 1, "description": f"Navigate to {name} page", "status": "FAIL" if redirected else "PASS"})
        all_loaded = not any(results.values())
        mark(ExecutionStatus.PASS if all_loaded else ExecutionStatus.FAIL, None if all_loaded else "ASSERTION_FAILURE", None if all_loaded else f"redirects={results}")
        assert all_loaded, f"Real account pages redirected to login unexpectedly: {results}"

    # --- REQ-CART-05: anonymous cart item persists after login ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-CART-05-PERSISTENCE-ACROSS-LOGIN", requirement_ids=["REQ-CART-05"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-CART-05-PERSISTENCE-ACROSS-LOGIN",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        creds = shared_account_credentials()
        page.locator("a.ico-logout").first.click()
        page.wait_for_timeout(1000)
        steps.append({"step_order": 1, "description": "Log out (become anonymous)", "status": "PASS"})
        product = ProductPage(page, DEFAULT_CONFIG)
        product.open("/album-3")
        add_resolution = product.add_to_cart("#add-to-cart-button-53")
        page.wait_for_timeout(1500)  # real, AJAX add-to-cart; see the same real timing bug found/fixed in test_enh02_guest_checkout.py
        steps.append({"step_order": 2, "description": "As anonymous session, add a real product to the cart", "status": "PASS" if add_resolution["resolved_candidate"] else "FAIL", "locator_resolution": add_resolution})
        login = LoginPage(page, DEFAULT_CONFIG)
        login.open()
        login.fill_email(creds["email"])
        login.fill_password(creds["password"])
        login.submit()
        steps.append({"step_order": 3, "description": "Log in with the real account, same session", "status": "PASS"})
        page.wait_for_timeout(1000)
        cart = CartPage(page, DEFAULT_CONFIG)
        cart.open()
        steps.append({"step_order": 4, "description": "Navigate to cart page", "status": "PASS"})
        still_present = not cart.is_empty()
        steps.append({"step_order": 5, "description": "Observe the anonymously added item is still present", "status": "PASS" if still_present else "FAIL"})
        mark(ExecutionStatus.PASS if still_present else ExecutionStatus.FAIL, None if still_present else "ASSERTION_FAILURE", None if still_present else "Cart was empty after login")
        assert still_present, "Real anonymous cart item did not persist after login"

    # --- REQ-PWR-01: password-recovery request accepted at the UI level ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-PWR-01-RECOVERY-UI", requirement_ids=["REQ-PWR-01"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-PWR-01-RECOVERY-UI",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        creds = shared_account_credentials()
        recovery = PasswordRecoveryPage(page, DEFAULT_CONFIG)
        recovery.open()
        steps.append({"step_order": 1, "description": "Navigate to password-recovery page", "status": "PASS"})
        resolution = recovery.submit_email(creds["email"])
        steps.append({"step_order": 2, "description": "Submit the real registered account's email", "status": "PASS", "locator_resolution": resolution})
        accepted = recovery.shows_acceptance()
        steps.append({"step_order": 3, "description": "Observe UI acceptance, no error", "status": "PASS" if accepted else "FAIL"})
        mark(ExecutionStatus.PASS if accepted else ExecutionStatus.FAIL, None if accepted else "ASSERTION_FAILURE", None if accepted else f"result_text={recovery.result_text()!r}")
        assert accepted, f"Real password-recovery request for a registered email was not accepted (result_text={recovery.result_text()!r})"
