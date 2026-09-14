# CR-001 / MVP2 — CONTINUE: PLAYWRIGHT AUTOMATION GENERATION + EXECUTION

## Objective

Continue the MVP2 Agentic QE implementation continuously from the current repository state.

The immediate priority is:

**Persisted Testcase + Persisted Test Data → Playwright Automation Generation → Multiple Evidence-Backed Locators → Real Chromium Execution → Persisted Execution Evidence**

The MVP execution environment is **Windows-first**.

Do NOT spend effort on Linux/macOS portability at this stage. The persistence pointer portability issue is a known advisory and is explicitly parked for later.

---

# 1. GOVERNANCE — MANDATORY

Before modifying implementation:

1. Inspect the current repository state.
2. Inspect:

   * frozen CP-MVP2-03 specification
   * frozen CP-MVP2-04 specification
   * frozen CP-MVP2-05 specification
   * frozen CP-MVP2-06 specification
   * current CP-05 implementation
   * current CP-06 implementation
   * current persistence implementation
   * current generated automation artifacts
   * current persisted testcase artifacts
   * current persisted test-data artifacts
   * current automation ID collision advisory
   * current Demo Web Shop discovery/DOM evidence
3. Determine whether the new multi-locator requirement can be implemented within the existing frozen contracts.
4. If a frozen specification or contract must change:

   * STOP implementation.
   * Produce a formal CR/change proposal.
   * Do not silently modify the frozen specification.
5. If implementation can proceed without changing the frozen contract:

   * proceed with implementation.
6. Never change requirements, expected results, test data, response codes, or business behavior merely to make automation pass.

Golden rule:

**NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.**

---

# 2. NEW HUMAN REQUIREMENT — MULTIPLE LOCATORS

For important/load-bearing UI elements, Playwright automation must support **multiple evidence-backed locator candidates**.

The purpose is to prevent an otherwise valid testcase from failing unnecessarily because of a developer naming/locator change.

This is NOT permission for arbitrary locator guessing.

Every locator candidate must be supported by actual application evidence.

Preferred evidence-backed strategies should be considered in deterministic priority order, for example:

1. TEST_ID
2. ROLE + accessible name
3. LABEL
4. STABLE_ATTRIBUTE
5. other explicitly supported stable evidence-backed locator

Do not invent unsupported locator strategies.

---

# 3. LOCATOR CANDIDATE MODEL

Inspect the existing automation schema first.

If the current schema can accommodate this without violating the frozen CP-05 contract, extend the implementation appropriately.

Conceptually, a load-bearing element should be capable of representing:

```text
locator_candidates:
  - priority
  - strategy
  - locator
  - evidence_source
  - evidence_reference
  - confidence
```

The exact implementation/schema must be derived from the existing project architecture rather than invented independently.

Each candidate must have:

* deterministic priority
* locator strategy
* actual locator
* evidence source/reference
* confidence classification

Possible confidence values may be:

* HIGH
* MEDIUM
* LOW

Use the project's existing conventions if already defined.

Do not introduce unnecessary schema duplication.

---

# 4. EXECUTION BEHAVIOR

At runtime:

1. Attempt the highest-priority valid locator.
2. If it succeeds, continue normally.
3. If it fails, attempt the next evidence-backed candidate.
4. Continue deterministically through the candidate set.
5. If a fallback succeeds:

   * the business testcase may still PASS;
   * execution MUST record that fallback was required.
6. If all candidates fail:

   * record the appropriate execution failure/block condition;
   * do not invent another locator;
   * do not modify the requirement;
   * do not silently change the automation.

Example execution evidence:

```text
Primary locator: FAILED
Fallback locator #2: PASSED
Fallback used: TRUE
Locator health: YELLOW
Business assertion: PASSED
```

The fallback must never disappear from the execution evidence.

---

# 5. IMPORTANT DISTINCTION

A successful fallback does NOT mean the automation is completely healthy.

For example:

```text
Business result: PASS
Automation health: YELLOW
Reason: primary locator failed; fallback locator succeeded
```

This distinction is important for future CP-07 RCA/replanning/self-healing.

Do NOT implement autonomous self-healing in CP-06 unless explicitly authorized by the applicable frozen specification/change control.

---

# 6. AUTOMATION ID COLLISION

Investigate the existing:

`AUTOMATION_ID_COLLISION_ADVISORY`

before creating or persisting additional automation artifacts.

Determine whether the current automation identity model is sufficient for:

* testcase
* test-data-set
* automation version
* locator candidate set

Do not silently overwrite distinct automation artifacts.

If the current frozen contract prevents correct unique identity:

**STOP → REPORT → PROPOSE CR**

Do not create a workaround that corrupts traceability.

---

# 7. FIRST VERTICAL SLICE

Do NOT generate a huge automation corpus yet.

Select **one real persisted testcase + its real persisted test data** from the current committed repository corpus.

Prefer a testcase where:

* requirement is approved
* testcase is ACCEPTED
* test data is ACCEPTED
* actual Demo Web Shop DOM evidence exists
* a meaningful browser flow can be executed

Document why that testcase was selected.

Then prove the complete chain:

```text
Approved Requirement
        ↓
Persisted Testcase
        ↓
Persisted Test Data
        ↓
Playwright Automation
        ↓
Multiple Evidence-Backed Locators
        ↓
Persisted Automation Artifact
        ↓
Real Chromium Browser
        ↓
Execution Evidence
        ↓
Execution Result
        ↓
Requirement/Testcase Traceability
```

---

# 8. PLAYWRIGHT QUALITY REQUIREMENTS

Generated automation must:

* use Playwright
* run against the real Demo Web Shop
* use real evidence-backed locators
* avoid arbitrary sleeps where deterministic synchronization is available
* use reusable functions/components where appropriate
* keep business intent visible
* maintain testcase traceability
* maintain test-data traceability
* capture meaningful assertions
* capture failure evidence
* preserve locator fallback evidence
* avoid hard-coded secrets/PII
* avoid modifying requirements or expected behavior
* avoid silently accepting a different business outcome

Do not create elaborate framework abstractions unless they provide real reuse.

---

# 9. PERSISTENCE REQUIREMENTS

Automation must be persisted as a first-class repository artifact.

At minimum establish reliable relationships:

```text
Automation
   ↓
Testcase ID
   ↓
Requirement ID(s)

Automation
   ↓
Test Data Set ID
```

The artifact must be recoverable from a fresh process.

Do not treat:

* console output
* Markdown report examples
* Python in-memory objects

as persistence.

Repository-grade persistence means the actual artifact files exist under version control.

---

# 10. EXECUTION EVIDENCE

The real browser execution must persist:

* execution ID
* actual timestamp
* automation ID
* testcase ID
* test-data-set ID
* requirement ID(s)
* browser
* browser version
* environment/runtime information
* locator attempted
* locator selected
* fallback usage
* step result
* assertion result
* final status
* screenshots where required
* logs/evidence paths
* failure classification where applicable

Do not fabricate any execution result.

---

# 11. VALIDATION

Before declaring the vertical slice complete, prove:

### Artifact validation

* testcase exists in repository
* test data exists in repository
* automation exists in repository
* traceability resolves correctly
* no duplicate/ambiguous automation identity

### Locator validation

* primary locator is evidence-backed
* fallback locator(s) are evidence-backed
* locator priority is deterministic
* no unsupported locator is silently introduced

### Browser validation

* real Chromium launches
* real Demo Web Shop is accessed
* real automation executes
* business assertion is evaluated
* execution evidence is persisted

### Fresh-process validation

From a new Python process:

* load persisted testcase
* load persisted test data
* load persisted automation
* resolve traceability
* execute/load the automation using the supported Windows environment

Do not regenerate artifacts during this verification.

---

# 12. TESTING

Add deterministic tests for:

* multiple locator schema
* locator priority
* fallback selection
* fallback evidence
* all-locators-fail behavior
* traceability
* persistence
* automation identity
* execution evidence
* regression compatibility

Then run:

1. focused new tests
2. full regression suite

Do not modify frozen upstream tests merely to obtain GREEN.

---

# 13. SECURITY

Security/penetration testing remains **POST-MVP / PARKED** unless an existing approved specification explicitly authorizes it.

Do not expand scope into security implementation during this task.

The previously established principle remains:

**The same evidence, traceability, governance and persistence discipline will eventually apply to security/penetration testing.**

---

# 14. REQUIRED DELIVERABLES

At completion provide:

1. starting HEAD
2. implementation commit(s)
3. evidence commit(s)
4. exact files added/modified
5. frozen files confirmed untouched
6. selected testcase
7. selected test data
8. generated automation artifact
9. locator candidates and their evidence
10. automation ID/identity result
11. browser execution result
12. execution evidence locations
13. testcase → requirement traceability
14. automation → testcase traceability
15. automation → test-data traceability
16. focused test results
17. full regression result
18. fresh-process verification
19. known advisories
20. blockers, if any

Do NOT declare the Di/Human gate yourself.

---

# 15. COMPLETION SIGNAL

After ALL work is genuinely complete, including:

* implementation
* tests
* evidence
* commits
* push
* remote verification
* completion report

invoke the existing Windows-native completion notification:

**MessageBox: "Task complete"**

and play the Windows system notification sound if the existing mechanism is available.

The notification must occur only after the complete task is finished.

---

# FINAL PRINCIPLE

We are no longer interested merely in proving that Python modules can generate JSON.

We are proving a real Agentic QE lifecycle:

**Understand → Generate → Persist → Trace → Automate → Execute → Capture Evidence → Assess → Report**

The first successful vertical slice is more valuable than a large unverified automation corpus.

Proceed continuously unless a genuine frozen-specification conflict, ambiguity, security issue, or implementation blocker requires Human + Di intervention.
