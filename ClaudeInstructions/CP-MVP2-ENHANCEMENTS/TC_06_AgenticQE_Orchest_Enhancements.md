# AGENTIC QE ENHANCEMENT CONTINUATION

## ORCHESTRATION EXPANSION — MASTER CLAUDE IMPLEMENTATION INSTRUCTION v1.0

---

# 1. Mission

Continue the Agentic QE enhancement program from the frozen Agentic QE Orchestration baseline.

Starting repository baseline:

**`ae1056b`**

The objective is to evolve the existing Agentic QE Orchestration layer from a demonstrated orchestration mechanism into a broader, practical, evidence-driven QE orchestration capability.

The central focus of this enhancement is:

> **Multi-requirement orchestration + intelligent regression selection + dependency-aware execution + failure/RCA/replanning integration + consolidated QE intelligence.**

Where technically appropriate, incorporate additional orchestration improvements into the same continuous implementation cycle.

This is a **continuous implementation instruction**.

Do NOT artificially divide the work into many small approval checkpoints.

Execute all authorized work continuously.

Stop only for a genuine governance decision or an explicitly prohibited action.

---

# 2. Existing Frozen Baselines

The following historical baselines are protected:

* MVP2 frozen baseline: `33b9946`
* Enhancement 01: `85dc6ab`
* Enhancement 02: `521b155`
* Controlled REQ-GCO-03 validation: `905c1cb`
* Agentic QE Orchestration: `ae1056b`

Do NOT rewrite history.

Do NOT amend historical commits.

Do NOT modify frozen artifacts merely to make new implementation pass.

The current working baseline is:

**`ae1056b`**

---

# 3. Existing Governance

The governing engineering lifecycle remains:

**Specify → Review → Freeze → Implement → Verify → Gate**

The current enhancement scope is authorized as the next continuation of the existing Agentic QE enhancement program.

Within this authorized scope, Claude may make normal technical implementation decisions without asking for intermittent approval.

Claude MUST NOT stop merely because:

* a normal implementation choice exists;
* multiple technically equivalent approaches are possible;
* a test exposes a defect introduced by the new implementation;
* documentation needs correction;
* a normal refactoring is required;
* a normal Windows/WSL compatibility issue is discovered;
* additional tests are needed;
* a reusable component is needed;
* a reasonable implementation improvement is discovered within this scope.

Claude SHOULD resolve such issues itself, verify the resolution, document the evidence, and continue.

---

# 4. Mandatory Governance Stop Conditions

STOP → REPORT → HUMAN + DI DECIDE if any action would require:

1. changing the Approved MVP2 SRS;
2. changing a frozen CP01–CP09 specification;
3. changing a frozen Enhancement 01/02 requirement or acceptance boundary;
4. implementing CR-002 or runtime locator self-healing;
5. changing expected results merely to make a test pass;
6. inventing or silently changing performance thresholds;
7. fabricating test data, IDs, execution results, screenshots, logs, metrics, or evidence;
8. bypassing required human approval;
9. creating unauthorized permanent SUT state;
10. weakening/removing existing regression tests;
11. changing frozen historical artifacts;
12. materially expanding beyond this enhancement's architectural scope;
13. introducing a business requirement that is not already authorized.

Never solve a governance problem by changing the specification.

---

# 5. Core Principle

The target architecture is:

**Requirements → Authority → Impact → Risk → Strategy → Testcases → Data → Traceability → Automation → Execution Plan → Execution → Evidence → Result → RCA → Replanning → Governance → Regression → QE Intelligence**

The orchestrator coordinates existing capabilities.

Do NOT rebuild existing capabilities unnecessarily.

Do NOT create a second implementation of an existing capability merely to make the architecture appear more agentic.

Reuse the project's existing:

* RAG;
* LLM boundary;
* RBTP;
* dependency matrix;
* testcase pipelines;
* test data pipelines;
* traceability;
* Playwright/POM;
* JMeter;
* RCA;
* replanning;
* governance;
* evidence;
* reporting.

---

# 6. First Action — Repository Discovery

Before implementation:

1. Checkout the current repository.
2. Verify current HEAD.
3. Verify `HEAD == origin/main`.
4. Verify working tree status.
5. Inspect the existing orchestration implementation.
6. Read:

   * orchestration specification;
   * architecture;
   * execution report;
   * existing tests;
   * existing reports;
   * existing requirement/testcase/data/traceability artifacts.
7. Identify all reusable existing capabilities.
8. Identify the current limitations.
9. Establish a baseline regression count.

Do not assume the previous execution summary is sufficient.

Inspect the actual repository.

---

# 7. Enhancement Scope

Implement the following as one coherent enhancement wave.

Tasks are ordered logically, but Claude should continue automatically from one task to the next where no governance decision is required.

---

# PHASE A — Orchestration Coverage Expansion

Expand the orchestrator beyond the currently demonstrated single requirement.

The orchestrator must be capable of accepting multiple requirements in one governed run.

Demonstrate, where existing artifacts support it:

* multiple functional requirements;
* multiple testcases;
* multiple datasets;
* dependency relationships;
* safe parallel execution;
* stateful sequential execution;
* shared-account constraints;
* prerequisite chains.

Do not claim all 35 requirements are orchestrated unless they are actually processed through the orchestrator.

Distinguish clearly between:

* orchestratable;
* planned;
* generated;
* automation-ready;
* executable;
* executed;
* passed;
* failed;
* blocked;
* deferred.

---

# PHASE B — Requirement Intelligence

Connect the orchestrator to the existing authoritative requirement/RAG mechanisms.

For every selected requirement determine:

* requirement ID;
* requirement text;
* authority;
* approval state;
* evidence strength;
* related requirements;
* dependencies;
* impacted testcase(s);
* risk;
* execution eligibility.

Approved SRS remains authoritative.

Historical information may inform reasoning but MUST NOT override an Approved requirement.

---

# PHASE C — Impact Analysis

Implement deterministic requirement impact analysis.

Given a changed or selected requirement, determine:

**Requirement → affected testcase(s) → dataset(s) → automation → dependencies → regression scope**

Where sufficient evidence exists, identify:

* direct impact;
* dependency impact;
* downstream impact;
* regression candidates.

Do not invent relationships.

Every inferred relationship must be labelled as inference unless supported by authoritative evidence.

---

# PHASE D — Intelligent RBTP / Risk Selection

Reuse the existing RBTP capability.

For a multi-requirement run, produce a deterministic execution priority based on available evidence such as:

* requirement criticality;
* risk;
* dependency;
* business impact;
* testcase availability;
* automation readiness;
* historical evidence;
* failure history.

The orchestrator must preserve the distinction between:

**risk-based prioritization**

and

**test execution eligibility**.

A high-risk requirement does not automatically become executable if its prerequisite or automation state is invalid.

---

# PHASE E — Dependency-Aware Execution Planning

Build an explicit execution plan.

The planner must distinguish:

### SAFE PARALLEL

Tests that do not share unsafe mutable state.

### SEQUENTIAL

Tests requiring ordering.

### PREREQUISITE-DEPENDENT

Tests requiring a previous state or artifact.

### EXCLUSIVE

Tests requiring exclusive access to an account, dataset, environment or resource.

### BLOCKED

Tests that cannot legitimately execute.

The execution plan must contain the reason for the selected mode.

Do not simply execute everything in parallel.

---

# PHASE F — Multi-Requirement Orchestration Demonstration

Create at least one real end-to-end demonstration containing multiple requirements.

Prefer a compact but meaningful dependency chain.

Demonstrate:

Requirement selection
→ impact analysis
→ RBTP
→ testcase selection
→ dataset selection
→ dependency planning
→ automation selection
→ execution
→ evidence
→ result
→ consolidated reporting.

Use real Windows execution where existing automation supports it.

No mocks for the primary demonstration.

---

# PHASE G — Parallel Execution Intelligence

Integrate the existing safe parallel execution capability.

Demonstrate that the orchestrator can identify tests that are:

* parallel-safe;
* sequential;
* stateful;
* dependency-bound.

Use parallel execution only where safe.

Where tests cannot safely run in parallel, record why.

Do not create false distributed execution claims.

Local multi-worker execution may be demonstrated.

Distributed execution may remain:

**CONFIGURED / NOT IMPLEMENTED**

unless a genuine second execution environment exists.

---

# PHASE H — Regression Intelligence

Implement intelligent regression selection.

The orchestrator should be able to determine:

> "What needs to run because of this requirement/change/failure?"

Use:

**Requirement impact + dependency graph + risk + automation availability + historical failure evidence**

to select the regression set.

The system should explicitly explain why each regression candidate was selected.

Where full regression is still appropriate, preserve the ability to execute it.

Do not remove the existing full-regression capability.

---

# PHASE I — Failure Classification Expansion

Strengthen failure classification.

Support, where evidence allows:

* REQUIREMENT_MISMATCH;
* REQUIREMENT_AMBIGUITY;
* TESTCASE_CONTENT;
* TEST_DATA;
* AUTOMATION;
* LOCATOR;
* BROWSER;
* TOOL;
* ENVIRONMENT;
* AUTHENTICATION;
* AUTHORIZATION;
* DEPENDENCY;
* THIRD_PARTY;
* PERFORMANCE;
* SUT_DEFECT;
* GOVERNANCE;
* UNKNOWN.

Classification must be evidence-driven.

Include confidence.

Do not manufacture certainty.

---

# PHASE J — RCA Integration

For every genuine failure that enters RCA:

Record:

* failure;
* evidence;
* classification;
* probable root cause;
* confidence;
* supporting evidence;
* contradictory evidence;
* affected requirement;
* affected testcase;
* recommended action.

Preserve the distinction between:

**observed fact**

and

**agent inference**.

Do not label an SUT defect merely because an automation test failed.

---

# PHASE K — Replanning

Integrate the existing replanning mechanism into multi-requirement orchestration.

A failure may result in:

* retry;
* alternate eligible testcase;
* alternate dataset;
* prerequisite establishment;
* environment retry;
* human review;
* action deferred;
* terminal failure.

Every replan must explain:

* why;
* what changes;
* what remains unchanged;
* whether approval is required.

---

# PHASE L — Replanning Guardrails

The orchestrator MUST NOT autonomously:

* modify the Approved SRS;
* change expected results;
* alter response codes;
* silently change test data to avoid failure;
* implement CR-002;
* bypass human approval;
* fabricate evidence;
* invent a performance threshold;
* create unauthorized permanent SUT state.

A prohibited recovery action becomes:

**HUMAN_REVIEW_REQUIRED**

not an autonomous action.

---

# PHASE M — Persistent Orchestration State

Strengthen the persisted orchestration journal.

Persist at minimum:

* orchestration ID;
* timestamp;
* selected requirements;
* current state;
* decisions;
* risk;
* execution plan;
* testcase IDs;
* dataset IDs;
* automation IDs;
* execution IDs;
* evidence references;
* failures;
* RCA;
* replan;
* governance decision;
* final status.

The journal must support recovery/resume where technically practical.

A partially completed orchestration must not silently restart from an incorrect state.

---

# PHASE N — Orchestration Resume / Recovery

Implement a governed resume mechanism where practical.

Demonstrate:

1. start orchestration;
2. persist state;
3. simulate/intercept interruption;
4. reload persisted state;
5. resume from the correct state;
6. avoid duplicate unsafe execution.

Do not duplicate permanent SUT state merely to demonstrate resume.

If a safe demonstration cannot be performed against the live SUT, use a deterministic orchestration-state test rather than fabricate live evidence.

Clearly label the level of demonstration.

---

# PHASE O — LLM Boundary

Use the existing LLM integration where reasoning genuinely adds value.

Potential uses:

* requirement interpretation;
* testcase generation;
* ambiguity analysis;
* risk reasoning;
* failure interpretation;
* RCA reasoning;
* replan proposal;
* final QE intelligence.

Do NOT invoke an LLM merely to claim agenticity.

Where deterministic evidence is sufficient, use deterministic processing.

LLM output MUST pass deterministic validation before affecting governed execution.

---

# PHASE P — Agent Specialization

Where justified, formalize meaningful capability boundaries such as:

* Requirement Intelligence;
* Risk/RBTP;
* Test Strategy;
* Testcase;
* Test Data;
* Traceability;
* Automation;
* Execution;
* RCA;
* Replanning;
* Governance;
* Reporting.

Do NOT create artificial "agents" that merely rename Python functions.

A component should be called an agent/service only when it has a meaningful decision or coordination responsibility.

---

# PHASE Q — Decision Contract

Strengthen the orchestration decision contract.

Every important decision should expose, where applicable:

* decision ID;
* input evidence;
* selected action;
* alternatives;
* reason;
* confidence;
* governing rule;
* approval requirement;
* outcome.

This should make orchestration decisions auditable.

---

# PHASE R — Unified QE Intelligence

Improve the final report so that a stakeholder can understand:

### What was tested?

### Why was it tested?

### What evidence supports the decision?

### What passed?

### What failed?

### Why did it fail?

### What was not executed?

### What was blocked?

### What requires human decision?

### What should happen next?

The report must distinguish:

**coverage**

from

**execution**

from

**verified PASS**.

Never report generated coverage as execution coverage.

---

# PHASE S — Observability

Strengthen orchestration observability.

Provide useful logs for:

* orchestration start/end;
* state transition;
* decision;
* agent/service invocation;
* tool invocation;
* execution;
* evidence;
* failure;
* RCA;
* replan;
* governance decision.

Every important event should be associated with the orchestration ID.

---

# PHASE T — CLI / User Experience

Improve the existing orchestration CLI where useful.

Support, as appropriate:

* selecting one requirement;
* selecting multiple requirements;
* selecting a requirement set;
* dry-run planning;
* execute;
* resume;
* status;
* report.

Do not create unnecessary CLI complexity.

---

# PHASE U — Dry Run

Implement or strengthen a genuine dry-run mode.

Dry run must:

* perform requirement analysis;
* calculate impact;
* calculate risk;
* identify testcases;
* identify datasets;
* identify automation;
* create execution plan;
* identify dependencies;
* identify expected governance decisions;

but MUST NOT perform destructive or live execution.

The dry-run result must clearly distinguish:

**PLANNED**

from

**EXECUTED**.

---

# PHASE V — Real Execution

Execute at least one meaningful multi-requirement orchestration against the real Demo Web Shop.

Use real Windows Playwright execution where applicable.

Use real JMeter where applicable.

Persist actual evidence.

Do not use mocks for the primary end-to-end proof.

---

# PHASE W — Controlled Failure

Include at least one controlled failure demonstration.

It MUST be clearly labelled:

**CONTROLLED TEST FAILURE**

It must demonstrate:

Failure
→ Classification
→ RCA
→ Replanning assessment
→ Governance
→ final decision.

Do not represent the controlled failure as a production SUT defect.

If classification is imperfect, report the limitation honestly.

---

# PHASE X — Performance Integration

Expand performance orchestration only where existing approved requirements/scenarios support it.

Use real JMeter execution where applicable.

Never invent:

* SLA;
* latency threshold;
* throughput threshold;
* concurrency requirement.

If a numeric threshold is absent:

**SLA = INCONCLUSIVE**

Do not convert it into PASS.

---

# PHASE Y — Security Boundary

Do not introduce penetration/security testing requiring a new approved scope.

Existing security/penetration work that is explicitly parked remains parked.

The orchestrator may preserve extension points for future security orchestration.

Do not silently activate parked requirements.

---

# PHASE Z — Docker Boundary

Docker remains deferred.

Do NOT implement Docker as part of this enhancement unless it becomes technically necessary for an already-authorized capability.

Architecture may preserve clean extension points for future Docker execution.

Do not spend the main implementation cycle on Docker.

Docker remains the last major infrastructure concern.

---

# 8. No Fake Agenticity

The following are prohibited:

* renaming functions as "agents" without new capability;
* calling deterministic code an LLM agent;
* claiming autonomous reasoning where none occurred;
* claiming distributed execution without multiple execution environments;
* claiming self-healing when CR-002 remains unauthorized;
* claiming full requirement execution merely because testcases exist;
* claiming PASS without execution evidence.

Evidence must support every claim.

---

# 9. Test Strategy

For every implementation component:

1. Add focused tests.
2. Run focused tests.
3. Fix implementation defects.
4. Re-run focused tests.
5. Run relevant existing regression.
6. Continue to the next authorized component.

Do not stop for Human approval after ordinary test failures.

---

# 10. Regression Requirement

At completion:

Run:

* all new orchestration tests;
* all relevant existing tests;
* full existing regression.

Record:

* passed;
* failed;
* skipped;
* newly discovered failures;
* pre-existing failures;
* unrelated failures.

Do not hide failures.

Do not weaken tests.

Do not change assertions merely to achieve GREEN.

---

# 11. Fresh Clone Verification

Perform a fresh-clone verification from the final commit.

Verify:

* repository checkout;
* dependency setup;
* orchestration tests;
* required regression;
* required real execution;
* required evidence availability;
* final report availability.

Clearly identify any failures caused by known repository/environment limitations.

---

# 12. Frozen Integrity Verification

Verify zero unauthorized drift against:

* `33b9946`
* `85dc6ab`
* `521b155`
* `905c1cb`
* `ae1056b`

The current enhancement must be additive unless an existing mutable artifact is legitimately extended.

Do not modify historical frozen baselines.

---

# 13. Bug Fix Policy

Claude MAY fix defects discovered during this enhancement when:

* the defect is within the current implementation scope;
* the fix does not alter an Approved requirement;
* the fix does not alter a frozen specification;
* the fix does not implement CR-002;
* the fix does not weaken governance;
* regression verifies the correction.

Document every significant defect and correction.

---

# 14. Evidence Requirements

For each real execution capture, where applicable:

* orchestration ID;
* requirement ID;
* testcase ID;
* dataset ID;
* automation ID;
* execution ID;
* timestamps;
* browser/tool version;
* environment;
* logs;
* screenshots;
* performance results;
* RCA;
* governance outcome.

Never fabricate missing evidence.

---

# 15. Final Coverage Matrix

Create/update a consolidated matrix showing, for every relevant requirement:

| Requirement | Risk | Dependency | Testcase | Dataset | Automation | Orchestrated | Executed | Result | Evidence | RCA | Replan | Governance |
| ----------- | ---- | ---------- | -------- | ------- | ---------- | ------------ | -------- | ------ | -------- | --- | ------ | ---------- |

The matrix MUST distinguish:

* not selected;
* selected;
* generated;
* automation-ready;
* blocked;
* executed;
* PASS;
* FAIL;
* INCONCLUSIVE;
* HUMAN_REVIEW_REQUIRED.

---

# 16. Final Execution Report

Create one consolidated report under:

`docs/claude-execution-reports/AGENTIC-QE-ORCHESTRATION/`

The report must contain:

1. starting commit;
2. final commit;
3. objective;
4. implemented capabilities;
5. architecture changes;
6. requirement coverage;
7. multi-requirement demonstration;
8. regression intelligence;
9. real functional execution;
10. real performance execution;
11. controlled failure;
12. RCA;
13. replanning;
14. governance;
15. prohibited-action tests;
16. defects discovered/fixed;
17. regression results;
18. fresh-clone results;
19. frozen-integrity results;
20. known limitations;
21. deferred work;
22. CR-002 status;
23. Docker status;
24. final recommendation;
25. exact completion status.

Do not claim more than the evidence demonstrates.

---

# 17. Final Acceptance Criteria

The enhancement is eligible for closure only if:

* orchestration remains governed;
* multiple requirements can be processed;
* dependency-aware execution planning exists;
* risk-based selection is integrated;
* regression selection is evidence-driven;
* failure classification is integrated;
* RCA is integrated;
* replanning is integrated;
* prohibited actions remain blocked;
* persisted orchestration state works;
* dry-run works;
* real execution works;
* controlled failure works;
* LLM boundary remains governed;
* no fake agenticity exists;
* existing regression remains intact;
* fresh clone is verified;
* frozen baselines remain unchanged;
* evidence is persisted;
* final report exists;
* final commit is pushed.

If any criterion is legitimately impossible within the current environment, record it explicitly as a limitation rather than fabricating closure.

---

# 18. Final Governance Status

Use one of:

### PASS

All acceptance criteria demonstrated.

### PASS WITH EXPLICIT LIMITATIONS

Core mechanism works but one or more bounded capabilities remain incomplete.

### BLOCKED — GOVERNANCE

Human + Di decision required.

### BLOCKED — TECHNICAL

A genuine technical blocker prevents completion.

Do not manufacture PASS.

---

# 19. Continuous Execution Rule

This is a **single continuous implementation cycle**.

After completing one authorized task:

**continue automatically to the next authorized task.**

Do not return control to Human + Di merely because a task boundary has been reached.

Do not ask:

> "Should I continue?"

Continue.

Only stop when:

1. the entire authorized scope is complete; OR
2. a genuine governance decision is required; OR
3. a genuine technical blocker prevents further progress.

---

# 20. Completion Commit

Before declaring completion:

1. Run final focused tests.
2. Run full regression.
3. Verify evidence.
4. Verify frozen integrity.
5. Verify fresh clone.
6. Generate final report.
7. Commit all authorized changes.
8. Push to `origin/main`.
9. Verify:

```text
HEAD == origin/main
working tree clean
```

Record the final commit SHA in the report.

---

# 21. DO NOT REOPEN PREVIOUSLY FROZEN WORK

Do not reopen:

* MVP2 CP01–CP09;
* Enhancement 01;
* Enhancement 02;
* REQ-GCO-03 validation;
* Agentic QE Orchestration baseline `ae1056b`.

If a current enhancement discovers an apparent conflict with any frozen artifact:

**STOP → REPORT → HUMAN + DI DECIDE**

Never resolve the conflict by modifying the frozen artifact.

---

# 22. MANDATORY THREE-BELL COMPLETION SIGNAL

This section is intentionally the **FINAL OPERATIONAL INSTRUCTION**.

After ALL work is complete, including:

* implementation;
* testing;
* bug fixes;
* regression;
* fresh-clone verification;
* frozen-integrity verification;
* final report;
* final commit;
* Git push;
* `HEAD == origin/main`;
* clean working tree;

Claude MUST play the Windows system notification sound **EXACTLY THREE TIMES**.

This is a completion signal only.

It does NOT indicate PASS.

It MUST occur for:

* PASS;
* PASS WITH EXPLICIT LIMITATIONS;
* BLOCKED — GOVERNANCE;
* BLOCKED — TECHNICAL.

## WSL / Windows Execution

Claude is running from WSL Ubuntu on Windows.

Do NOT rely only on Linux terminal bell output.

First verify that Windows PowerShell is callable:

```bash
command -v powershell.exe
```

Then invoke the Windows system notification sound using:

```bash
powershell.exe -NoProfile -Command "[System.Media.SystemSounds]::Exclamation.Play()"
```

Execute it three times sequentially:

```bash
powershell.exe -NoProfile -Command "[System.Media.SystemSounds]::Exclamation.Play()"
sleep 1
powershell.exe -NoProfile -Command "[System.Media.SystemSounds]::Exclamation.Play()"
sleep 1
powershell.exe -NoProfile -Command "[System.Media.SystemSounds]::Exclamation.Play()"
```

The three sounds MUST be:

**BELL 1 → BELL 2 → BELL 3**

Exactly three.

Do NOT:

* play once;
* play twice;
* play four or more times;
* play sounds during intermediate work;
* play sounds before the final push;
* play sounds before final verification;
* use a message box;
* require user interaction.

If the preferred mechanism fails, make a reasonable Windows/WSL-compatible attempt to invoke the Windows system notification sound.

If the sound cannot be invoked, explicitly record:

`COMPLETION_NOTIFICATION: FAILED — Windows notification sound could not be invoked from the execution environment.`

If successful, record:

`COMPLETION_NOTIFICATION: SUCCESS — 3 Windows system notification sounds played sequentially.`

## ABSOLUTE FINAL-ACTION RULE

After the **third sound**, STOP.

Do not execute another command.

Do not inspect Git again.

Do not modify a file.

Do not commit.

Do not push.

Do not run tests.

Do not clean up.

Do not generate another report.

Do not perform any additional verification.

**The third Windows notification sound MUST be the final operational action of the entire Claude session.**

# END OF INSTRUCTION
