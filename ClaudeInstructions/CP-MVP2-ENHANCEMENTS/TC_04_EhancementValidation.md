# CONTROLLED REQ-GCO-03 VALIDATION

## Post-Enhancement-02 Freeze — Governed Real Guest Checkout Validation

### 1. EXECUTION AUTHORITY

You are authorized to perform **one narrowly scoped validation activity** for:

**Requirement:** `REQ-GCO-03`

This authorization is provided by **Human + Di**.

This is a **controlled post-freeze validation**.

It is **NOT** authorization to reopen, modify, or reinterpret Enhancement 02.

---

# 2. IMMUTABLE BASELINE

The mandatory starting point is:

**Enhancement 02 frozen baseline:** `521b155`

Verify before doing anything else:

```text
HEAD == 521b155
origin/main == 521b155
working tree is clean
```

Also verify that the following historical baselines remain unchanged:

```text
MVP2 frozen baseline:       33b9946
Enhancement 01 baseline:    85dc6ab
Enhancement 02 baseline:    521b155
```

Do NOT rewrite history.

Do NOT reset/rebase/force-push.

Do NOT amend any frozen commit.

---

# 3. GOVERNANCE BOUNDARY

The following remain immutable:

* Approved MVP2 SRS v1.0
* CP-MVP2-01 through CP-MVP2-09
* MVP2 frozen evidence
* Enhancement 01 frozen implementation/evidence
* Enhancement 02 frozen implementation/evidence
* CR-002
* all previously frozen requirements
* all previously accepted governance decisions

In particular:

**CR-002 remains OPEN / NOT AUTHORIZED.**

Do not implement runtime locator self-healing or any other CR-002 behavior as part of this task.

Do not reopen CP06.

Do not reopen CP07.

Do not reopen CP08.

Do not reopen CP09.

Do not modify the Approved SRS.

Do not change a requirement, testcase, expected result, response code, or business rule merely to obtain PASS.

---

# 4. SOLE OBJECTIVE

The sole objective is to determine whether:

**REQ-GCO-03**

can now legitimately be moved from:

`HUMAN_REVIEW_REQUIRED`

to:

`CLOSED / AUTOMATED`

through **one real, non-mocked, Windows Playwright execution** against the real Demo Web Shop.

System under test:

`https://demowebshop.tricentis.com/`

The validation must use the actual application.

No mock server.

No simulated checkout.

No fabricated order.

No fabricated evidence.

---

# 5. WHY THIS VALIDATION IS SEPARATE

REQ-GCO-03 was intentionally left HUMAN_REVIEW_REQUIRED because validating it requires an additional real guest-path order.

The previous Enhancement 02 closure deliberately stopped at that boundary because creating another permanent order exceeded the agreed minimum-state-creation rule without explicit Human + Di authorization.

That authorization now exists.

Therefore:

**ONE additional real guest-path order is authorized solely for REQ-GCO-03 validation.**

No additional orders are authorized.

Do not create multiple guest orders.

Do not create exploratory orders.

Do not repeat the guest order merely because a non-governance test fails.

If execution fails because of an application/environment/tool issue, capture evidence and report it before deciding whether another attempt is warranted.

---

# 6. FIRST: INSPECT EXISTING ARTIFACTS

Before creating or changing anything:

Inspect the existing repository structure and identify:

* REQ-GCO-03 in the Approved SRS
* existing REQ-GCO-03 testcase
* existing testcase Excel corpus
* existing test data
* requirement/testcase traceability
* existing Playwright implementation
* existing POM/reusable components
* existing locator evidence
* existing execution/evidence conventions
* existing reporting conventions
* Enhancement 02 final freeze report
* relevant previous guest-checkout findings

Reuse existing infrastructure.

Do not reinvent the framework.

Do not create duplicate artifacts where an existing governed artifact can be reused.

---

# 7. VERIFY THE EXACT REQUIREMENT

Read the Approved SRS and determine the exact acceptance intent of:

`REQ-GCO-03`

The Approved SRS is the source of truth.

Do not infer a broader requirement.

Do not narrow the requirement to make automation easier.

Do not modify the requirement.

Record the exact requirement interpretation used for this validation in the execution report.

If repository artifacts conflict with the Approved SRS:

**STOP → REPORT → HUMAN + DI DECIDE**

Do not resolve the conflict yourself.

---

# 8. TESTCASE PREPARATION

Inspect the existing REQ-GCO-03 testcase.

The testcase must represent the actual business intent of REQ-GCO-03.

Use meaningful business steps.

Do not use generic placeholder steps.

Ensure the automation follows the testcase's intended business sequence.

If the existing testcase is insufficient to faithfully validate REQ-GCO-03:

1. identify the exact gap;
2. determine whether the gap can be corrected without changing the Approved SRS;
3. make only the minimum necessary post-freeze testcase/automation artifact correction;
4. document the correction explicitly.

Do not silently alter the testcase.

---

# 9. TEST DATA

Use the minimum necessary real test data.

The guest checkout must remain genuinely guest checkout.

Do not authenticate the guest flow.

Do not convert it into an authenticated checkout.

Do not reuse an existing authenticated order to claim guest checkout.

Do not fabricate customer/account/order information.

Use a real purchasable product and the minimum data necessary to complete the requirement.

Respect the application's actual mandatory fields.

---

# 10. DUPLICATE / STATE SAFETY

Before creating the order:

Inspect the existing repository evidence and the live application state as far as the framework permits.

The following is mandatory:

* create exactly one new guest-path order;
* do not intentionally create a duplicate order;
* do not create multiple orders for experimentation;
* do not alter existing orders;
* do not delete or manipulate unrelated application data;
* do not perform destructive cleanup.

The authorized permanent state change is:

**ONE real guest checkout order.**

Record the resulting order identifier as evidence.

---

# 11. REAL WINDOWS PLAYWRIGHT EXECUTION

Use the existing Windows Playwright Python framework.

Execute against the real Demo Web Shop.

The run must be genuinely non-mocked.

Capture, as applicable:

* browser/version
* URL
* timestamps
* testcase ID
* requirement ID
* dataset ID
* automation ID
* each major business step
* locator used
* screenshots
* browser/page logs where available
* HTTP/network evidence where useful
* final result
* order confirmation
* order identifier
* execution duration

The evidence must allow another engineer to understand what actually happened.

---

# 12. LOCATOR GOVERNANCE

Use the existing evidence-backed locator mechanism.

Multiple approved locators may be used where already supported by the existing implementation.

However:

**Do NOT introduce CR-002 runtime self-healing.**

Do not dynamically invent locators.

Do not silently alter locators after a failure merely to make the test pass.

If a locator needs correction, document:

* original locator
* evidence for the corrected locator
* reason for correction
* affected artifact
* validation result

Any correction must remain within the already authorized framework and must not modify CR-002 behavior.

---

# 13. GUEST CHECKOUT VALIDATION

Execute the actual REQ-GCO-03 guest journey.

At minimum, establish evidence for:

1. Start as an anonymous user.
2. Select an appropriate real product.
3. Add the product to cart.
4. Proceed through the guest checkout path.
5. Complete the required guest checkout information.
6. Complete the applicable shipping/payment flow required by the SRS.
7. Submit the order.
8. Verify the resulting order confirmation.
9. Capture the real order identifier.
10. Confirm the result against the exact REQ-GCO-03 acceptance intent.

Do not add business behavior not required by the SRS merely to make the journey longer.

---

# 14. FAILURE HANDLING

If the execution fails, classify the failure using the established Agentic QE categories:

* REQUIREMENT_MISMATCH / AMBIGUITY
* DATA_ISSUE
* AUTHORIZATION_ISSUE
* TOOL_ISSUE
* ENVIRONMENT_ISSUE
* THIRD_PARTY_DEPENDENCY
* CONSTRAINT
* TESTCASE_CONTENT_LIMITATION
* APPLICATION_DEFECT

Use:

**historic evidence + current evidence**

where applicable.

Do not automatically classify every failure as an application defect.

Do not automatically retry indefinitely.

Do not modify the requirement or expected result to obtain PASS.

If a failure exposes a conflict with the frozen governance boundary:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 15. PASS CRITERIA

REQ-GCO-03 may be declared:

**CLOSED / AUTOMATED**

only if all of the following are true:

* exact Approved SRS intent is satisfied;
* testcase correctly represents that intent;
* test data is valid;
* automation faithfully implements the testcase;
* execution is real and non-mocked;
* guest checkout is genuinely anonymous;
* required guest checkout succeeds;
* real order confirmation is obtained;
* real order identifier is captured;
* evidence is persisted;
* requirement → testcase → dataset → automation → execution traceability is intact;
* no prohibited governance change occurred;
* no frozen artifact drift occurred;
* regression remains healthy;
* repository state is verified.

A generated script or a green unit test alone is NOT sufficient.

---

# 16. IF REQ-GCO-03 FAILS

If the real execution does not satisfy REQ-GCO-03:

Do NOT force closure.

Do NOT change the SRS.

Do NOT weaken the testcase.

Do NOT alter expected behavior.

Do NOT fabricate a successful order.

Instead:

1. preserve evidence;
2. classify the failure;
3. identify root cause;
4. determine whether it is a testcase-content, automation, environment, application, or requirement issue;
5. report the exact finding;
6. leave REQ-GCO-03 as HUMAN_REVIEW_REQUIRED unless the evidence legitimately supports another governed disposition.

---

# 17. POST-RUN VERIFICATION

After the execution:

Run the relevant focused tests.

Then run the complete regression suite.

Verify:

* no existing test was weakened;
* no frozen artifact changed;
* no SRS change occurred;
* CP01–CP09 remain closed;
* CR-002 remains OPEN / NOT AUTHORIZED;
* Enhancement 02 frozen baseline remains historically intact;
* no unrelated permanent state was created.

Perform a frozen-integrity comparison against:

`521b155`

and report any differences explicitly.

---

# 18. REPOSITORY CHANGES

Because this is a post-freeze controlled validation, distinguish clearly between:

### Frozen baseline

`521b155`

and

### New validation artifacts

Only create/update artifacts genuinely required to document this controlled validation.

Do not silently fold changes into the historical Enhancement 02 freeze.

Do not modify historical reports to make them appear as though this validation happened before the freeze.

Create a clearly dated validation report.

---

# 19. COMMIT GOVERNANCE

Do not modify `521b155`.

If new validation artifacts are required and all verification succeeds, create a **new commit after 521b155**.

The new commit must clearly represent:

**Controlled REQ-GCO-03 Post-Freeze Validation**

Do not amend the old freeze commit.

Do not force-push.

Push normally to `origin/main` only after verification.

---

# 20. FINAL REPORT

Create a comprehensive report containing:

## Executive Summary

* validation objective
* authorization
* starting baseline
* final commit, if any
* final disposition

## Requirement

* exact REQ-GCO-03 identifier
* Approved SRS interpretation
* acceptance intent

## Testcase

* testcase ID
* testcase steps
* dataset
* automation ID

## Execution

* Windows environment
* browser/version
* real SUT
* execution timestamp
* execution result
* duration

## Evidence

* screenshots
* logs
* order confirmation
* real order identifier
* relevant browser/network evidence

## Traceability

```text
Requirement
    ↓
Testcase
    ↓
Dataset
    ↓
Automation
    ↓
Execution
    ↓
Evidence
    ↓
Result
```

## Root Cause

If failure occurred, provide governed RCA.

## Governance

Explicitly state:

* Approved SRS unchanged
* CP01–CP09 unchanged
* CR-002 remains OPEN / NOT AUTHORIZED
* frozen baseline unchanged
* no unauthorized requirement change
* no fabricated evidence
* one authorized guest order only

## Regression

Report focused and full regression results.

## Final Disposition

Use exactly one of:

`CLOSED / AUTOMATED`

or

`HUMAN_REVIEW_REQUIRED`

or another explicitly justified governed disposition.

Do not claim closure merely because the automation script executes.

---

# 21. FINAL RESPONSE TO HUMAN + DI

At completion, provide a concise execution summary containing:

1. Starting commit
2. Final commit
3. REQ-GCO-03 result
4. Real guest order created: YES/NO
5. Order identifier
6. Focused test result
7. Full regression result
8. Frozen-integrity result
9. Any new findings
10. Exact report path
11. Whether REQ-GCO-03 can legitimately be considered closed

---

# 22. ABSOLUTE GOVERNANCE RULE

The governing principle remains:

**NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.**

If reality conflicts with the specification:

**STOP → REPORT → HUMAN + DI DECIDE**

The purpose of this exercise is to discover and prove the truth of REQ-GCO-03 against the real system — not to manufacture a GREEN result.

---

# 23. START CONDITION

Before beginning execution, print:

```text
CONTROLLED REQ-GCO-03 VALIDATION
Starting baseline: 521b155
MVP2 frozen baseline: 33b9946
Enhancement 01 baseline: 85dc6ab
CR-002: OPEN / NOT AUTHORIZED
Authorization: HUMAN + DI
Authorized permanent state creation: ONE real guest checkout order
Objective: Validate REQ-GCO-03 only
```

Then proceed with inspection and execution.

Do not ask for additional confirmation unless a genuine governance conflict, safety issue, or requirement ambiguity is encountered.
