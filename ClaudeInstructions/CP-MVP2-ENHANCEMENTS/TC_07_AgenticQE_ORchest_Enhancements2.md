# Agentic QE Enhancement Wave 2

## Agentic Intelligence, Regression Selection & Execution Orchestration

### Master Claude Execution Instruction v1.0

---

## 1. Mission

Continue the Agentic QE implementation from the **verified and gated repository baseline `2778936`**.

This is a governed enhancement of the existing Agentic QE Orchestration implementation.

The objective is to evolve the current orchestration capability from a demonstrated multi-requirement execution mechanism into a stronger **Agentic QE intelligence and execution layer** that can:

**understand → assess → select → prioritize → plan → execute → observe → diagnose → replan → govern → report**

across functional and performance testing.

The implementation must remain evidence-driven, deterministic where governance requires determinism, and genuinely agentic where reasoning adds value.

Do NOT create fake agentic behavior by merely renaming deterministic functions as "agents."

---

# 2. Authoritative Starting Baseline

Starting baseline:

**`2778936`**

Verify that the working repository starts from this commit and that the working tree is clean before implementation.

Do not modify historical frozen baselines.

---

# 3. Frozen / Protected Baselines

The following remain protected:

* MVP2 frozen baseline: `33b9946`
* Enhancement 01 baseline: `85dc6ab`
* Enhancement 02 final baseline: `521b155`
* REQ-GCO-03 controlled closure: `905c1cb`
* Initial orchestration implementation/final substantive commit: `ea0c8fa`
* orchestration reconciliation commit: `984d18b`
* current verified orchestration expansion baseline: `2778936`

Do not rewrite history.

Do not amend historical commits.

Do not silently alter frozen specifications.

---

# 4. Governance

The governing lifecycle remains:

**Specify → Review → Freeze → Implement → Verify → Gate**

For this enhancement:

1. inspect the existing architecture/specification;
2. identify whether a specification change is required;
3. if required, create/update the enhancement specification;
4. clearly identify the proposed specification delta;
5. implementation may proceed only against the authorized enhancement scope;
6. verify with real evidence;
7. freeze only after verification.

If implementation encounters a conflict with a frozen specification:

**STOP → REPORT → HUMAN + DI DECIDE**

Never change the specification merely to make implementation pass.

---

# 5. Core Principle

The target architecture is:

**LLM reasons**
→ **agents coordinate**
→ **deterministic services validate**
→ **tools execute**
→ **evidence records reality**
→ **governance controls decisions**

Do not reverse this model.

The LLM must never become the authority for:

* frozen requirement interpretation;
* authorization;
* evidence validity;
* test result truth;
* baseline modification;
* governance approval;
* protected-state mutation.

---

# 6. Enhancement Scope

Implement the following as one coherent enhancement.

---

## A. Requirement Intelligence

Build or strengthen requirement intelligence capable of:

* selecting requirements by capability;
* understanding requirement relationships;
* identifying affected journeys;
* identifying dependencies;
* identifying prerequisite requirements;
* identifying requirements requiring exclusive state;
* identifying requirements that should not be executed because evidence/state is insufficient.

For every selected requirement persist:

* requirement ID;
* requirement text/reference;
* capability;
* risk;
* dependencies;
* prerequisites;
* execution eligibility;
* reason for selection;
* reason for exclusion/deferment;
* evidence supporting the decision.

Do not fabricate requirement relationships.

---

# 7. Intelligent Regression Selection

Implement evidence-backed regression selection.

Given a changed or selected requirement:

1. identify directly impacted testcases;
2. identify indirectly impacted testcases;
3. identify dependent requirements;
4. identify affected automation;
5. identify relevant datasets;
6. identify required regression scope;
7. explain selected and excluded tests.

The output must distinguish:

* SELECTED;
* NOT_SELECTED;
* BLOCKED;
* DEFERRED;
* EXCLUSIVE;
* PREREQUISITE_REQUIRED.

Every exclusion/deferment must have a reason.

---

# 8. RBTP Integration

Integrate Risk Based Test Prioritization into orchestration.

Risk selection must consider, where available:

* business criticality;
* requirement risk;
* historical failure evidence;
* defect history;
* dependency impact;
* change impact;
* execution cost;
* environment availability.

Do not invent historical probabilities.

If historical evidence does not exist, explicitly state that.

---

# 9. Dependency-Aware Planning

Strengthen the execution planner.

Support at minimum:

* SAFE_PARALLEL
* SEQUENTIAL
* PREREQUISITE_DEPENDENT
* EXCLUSIVE
* BLOCKED

The planner must produce a deterministic explanation of why a requirement belongs to each category.

The planner must consider real stateful consequences.

Example:

A testcase that creates a permanent customer account must not automatically be executed multiple times merely because regression selection includes it.

---

# 10. Meaningful Agent Specialization

Introduce structured agent roles where they provide real separation of responsibility.

Candidate roles:

### Requirement Analysis Agent

Interprets requirements and identifies dependencies/risk.

### Test Planning Agent

Selects and prioritizes testcases.

### Test Data Agent

Identifies or generates permitted datasets.

### Automation Agent

Maps testcases to executable automation.

### Execution Agent

Controls actual execution.

### RCA Agent

Analyzes evidence and classifies failures.

### Replanning Agent

Produces candidate next actions within governance constraints.

### QE Reporting Agent

Builds consolidated evidence-backed reporting.

Do not require every role to invoke an LLM.

Use deterministic implementation when deterministic behavior is sufficient.

The architecture must document why an LLM is or is not used at each boundary.

---

# 11. LLM Boundary

Demonstrate at least one meaningful reasoning boundary where an LLM adds value.

Candidate use cases:

* ambiguous requirement interpretation;
* testcase quality assessment;
* RCA hypothesis generation;
* candidate replanning;
* risk reasoning.

The LLM output must never directly authorize execution.

Persist:

* prompt/context identity;
* model/provider;
* output;
* confidence;
* deterministic validation result;
* final governed decision.

If no live LLM is required for a particular workflow, do not fake one.

---

# 12. Decision Contract

Every significant agent decision should use a structured contract containing at minimum:

* decision ID;
* actor/agent;
* input references;
* decision;
* rationale;
* evidence references;
* confidence;
* alternatives;
* governance status;
* next action;
* timestamp.

The contract must be persisted.

---

# 13. Failure → RCA → Replanning Loop

Generalize the current controlled failure flow.

Required lifecycle:

**EXECUTION FAILURE**
→ **CLASSIFICATION**
→ **RCA**
→ **CONFIDENCE**
→ **REPLAN CANDIDATES**
→ **GOVERNANCE**
→ **AUTHORIZED ACTION**
→ **EXECUTION**

Support at minimum:

* RETRY;
* REPLAN;
* HUMAN_REVIEW_REQUIRED;
* ACTION_DEFERRED_TO_HUMAN;
* BLOCKED.

Do not allow a replan to override an existing Human Review boundary.

---

# 14. Replanning Guardrails

A replan must NOT:

* change requirements;
* change expected response codes;
* modify frozen SRS;
* alter approved acceptance criteria;
* fabricate test data;
* fabricate evidence;
* silently change performance thresholds;
* bypass authorization;
* bypass Human Review;
* execute prohibited state-changing actions.

Any prohibited proposal must be rejected and persisted as a governance event.

---

# 15. Persistent State and Recovery

Strengthen orchestration persistence.

Persist enough state to resume after interruption:

* selected requirements;
* execution plan;
* current state;
* completed steps;
* failed steps;
* evidence references;
* decisions;
* RCA;
* replanning state;
* governance state.

Demonstrate:

1. start orchestration;
2. interrupt it;
3. restore persisted state;
4. resume from the correct state;
5. do not repeat completed destructive/state-changing actions.

---

# 16. Parallel Execution Intelligence

Extend parallel execution beyond the existing demonstration.

The orchestrator must determine which tests can safely run concurrently.

Demonstrate:

* genuinely parallel execution;
* shared-resource awareness;
* exclusive-resource serialization;
* dependency serialization.

Do not claim distributed execution.

Local multi-process execution is sufficient for this enhancement.

Distributed execution remains future work unless a real second execution environment is available.

---

# 17. Dry-Run Mode

Implement a true dry-run planning mode.

Example:

`orchestrator --dry-run`

It must produce:

* selected requirements;
* selected testcases;
* datasets;
* dependencies;
* planned execution order;
* parallel groups;
* expected resources;
* excluded/deferred items;
* reasons;
* governance constraints.

Dry-run must not execute tests or mutate SUT state.

---

# 18. Performance Orchestration

Integrate existing JMeter capability into the same orchestration model.

Support:

Requirement
→ Performance testcase
→ workload/data
→ JMeter plan
→ execution
→ metrics
→ threshold validation
→ evidence
→ RCA/replanning
→ governance.

Respect the existing rule:

**No approved numeric threshold = SLA INCONCLUSIVE.**

Never invent a performance threshold.

Use real Windows JMeter execution.

Do not claim distributed performance execution.

---

# 19. Unified QE Intelligence

Create a consolidated traceability model:

**Requirement**
→ **Risk**
→ **Testcase**
→ **Dataset**
→ **Automation**
→ **Execution**
→ **Evidence**
→ **Result**
→ **RCA**
→ **Replan**
→ **Governance**

Every link must use stable identifiers.

No orphaned generated artifacts.

---

# 20. Dynamic Multi-Requirement Demonstration

Do not simply reuse the previous six hard-coded requirements.

Create a demonstration where the orchestrator:

1. receives a meaningful requirement/capability scope;
2. discovers applicable requirements;
3. performs risk/impact analysis;
4. selects testcases;
5. selects datasets;
6. builds dependency-aware execution plan;
7. determines parallel/sequential/exclusive groups;
8. executes appropriate tests;
9. captures evidence;
10. produces consolidated results.

At least one requirement should be deliberately excluded or deferred for a governance/state reason.

The exclusion must be generated by orchestration logic.

---

# 21. Governance Stress Testing

Add tests attempting to violate governance.

At minimum attempt:

1. frozen requirement modification;
2. response-code modification;
3. acceptance-criteria modification;
4. evidence fabrication;
5. unauthorized state mutation;
6. bypassing Human Review;
7. silent baseline change;
8. invalid replan.

Every attempt must be blocked.

Persist evidence of the block.

---

# 22. Real Execution

All meaningful execution demonstrations must be real and non-mocked.

Use:

* Windows;
* VS Code environment;
* real Chromium/Playwright;
* real Demo Web Shop;
* real JMeter where performance is exercised.

Clearly distinguish:

* REAL_EXECUTED;
* PLANNED;
* SIMULATED;
* BLOCKED;
* DEFERRED.

Do not report planned execution as executed.

---

# 23. Defect Handling

If defects are discovered:

1. reproduce;
2. classify;
3. identify root cause;
4. fix only within enhancement scope;
5. add regression coverage;
6. rerun focused tests;
7. rerun broader regression.

Do not weaken existing tests.

Do not modify frozen artifacts to hide failures.

---

# 24. Testing

Create focused tests for every new capability.

Minimum coverage should include:

* requirement intelligence;
* regression selection;
* RBTP;
* dependency planning;
* parallel planning;
* exclusive-resource handling;
* agent contracts;
* decision contracts;
* LLM boundary;
* RCA;
* replanning;
* prohibited-action guards;
* persistence;
* recovery;
* dry-run;
* performance orchestration;
* unified reporting.

---

# 25. Regression

Run:

1. focused enhancement tests;
2. complete existing regression;
3. governance tests;
4. fresh-clone verification.

Report exact:

* passed;
* failed;
* skipped;
* blocked;
* pre-existing failures.

Never hide failures.

---

# 26. Frozen Integrity

Verify zero unintended drift against:

* `33b9946`
* `85dc6ab`
* `521b155`
* `905c1cb`
* `2778936`

Do not merely compare filenames.

Use cryptographic/hash or equivalent deterministic integrity checks where practical.

Report any drift explicitly.

---

# 27. Fresh Clone

Clone the final repository into a clean location.

From the fresh clone:

* install required dependencies;
* run focused tests;
* run regression;
* execute at least one real orchestration demonstration;
* verify reports/evidence are accessible.

Document any genuine environment limitation.

---

# 28. Final Coverage Matrix

Produce a final matrix covering:

| Area                      | Implemented | Tested | Real Execution | Evidence | Limitation |
| ------------------------- | ----------- | ------ | -------------- | -------- | ---------- |
| Requirement intelligence  |             |        |                |          |            |
| Regression selection      |             |        |                |          |            |
| RBTP                      |             |        |                |          |            |
| Dependency planning       |             |        |                |          |            |
| Parallel execution        |             |        |                |          |            |
| Agent specialization      |             |        |                |          |            |
| LLM boundary              |             |        |                |          |            |
| RCA                       |             |        |                |          |            |
| Replanning                |             |        |                |          |            |
| Persistence/recovery      |             |        |                |          |            |
| Dry run                   |             |        |                |          |            |
| Performance orchestration |             |        |                |          |            |
| Unified QE intelligence   |             |        |                |          |            |
| Governance                |             |        |                |          |            |

Do not mark an area complete merely because source code exists.

---

# 29. Final Execution Report

Create:

`docs/claude-execution-reports/AGENTIC-QE-ORCHESTRATION/`

with a uniquely timestamped final report.

The report must contain:

* starting commit;
* final commit;
* specification status;
* implementation summary;
* architecture changes;
* agent boundaries;
* LLM boundary;
* real executions;
* execution results;
* RCA;
* replanning;
* governance;
* performance results;
* regression results;
* fresh-clone results;
* frozen-integrity results;
* defects found/fixed;
* limitations;
* deferred work;
* exact repository HEAD.

The report must never claim greater coverage than the evidence supports.

---

# 30. CR-002 Boundary

CR-002 remains:

**OPEN — NOT AUTHORIZED**

Do not implement unauthorized runtime locator self-healing.

Do not reinterpret this enhancement as authorization for CR-002.

---

# 31. Docker Boundary

Docker remains deferred.

Do not introduce Docker merely to demonstrate agentic orchestration.

The current priority remains:

**Agentic QE Orchestration first. Docker later.**

---

# 32. No Fake Agenticity

The following are prohibited:

* hard-coded "agent" names around deterministic code;
* precomputed decisions presented as dynamic reasoning;
* fabricated LLM calls;
* simulated execution reported as real;
* static execution plans presented as dynamically generated;
* fake parallel execution;
* fake RCA;
* fake evidence.

Where deterministic behavior is sufficient, use deterministic behavior and explain why.

Where reasoning materially adds value, demonstrate genuine reasoning.

---

# 33. Continuous Execution Rule

After starting this enhancement:

**continue automatically through all technically independent tasks.**

Do not stop for routine implementation decisions.

Stop only when:

* a frozen specification conflict occurs;
* unauthorized scope is required;
* destructive state requires explicit Human + Di authorization;
* a genuine blocker prevents safe continuation.

Otherwise continue through implementation, testing, evidence, regression, fresh clone and final reporting.

---

# 34. Final Commit

Only after all verification is complete:

1. create the final enhancement commit;
2. push to `origin/main`;
3. verify HEAD equals `origin/main`;
4. record the exact commit SHA;
5. ensure working tree is clean.

Do not call an intermediate commit the final baseline.

---

# 35. Final Governance Status

The final report must explicitly state one of:

* PASS
* PASS WITH EXPLICIT LIMITATIONS
* GOVERNANCE HOLD
* FAILED

Do not use ambiguous wording.

---

# 36. Mandatory Completion Notification

As the final operational action, after all work is complete and after the final commit/push/report verification:

From WSL verify:

`command -v powershell.exe`

Then execute exactly three sequential Windows system notification sounds:

`powershell.exe -NoProfile -Command "[System.Media.SystemSounds]::Exclamation.Play()"`

followed by:

`sleep 1`

Then repeat the sound command and `sleep 1`, then repeat the sound command.

Requirements:

* exactly 3 sounds;
* sequential;
* Windows system notification sound;
* no message box;
* no popup;
* no additional notification;
* this must be the final operational action.

Report:

`COMPLETION_NOTIFICATION: SUCCESS — 3 Windows system notification sounds played sequentially.`

---

# 37. Final Instruction

Do not stop merely because one capability is difficult.

Investigate, implement, test, document and continue wherever the work remains within authorized scope.

Do not manufacture completeness.

Do not change frozen specifications.

Do not silently authorize CR-002.

Do not introduce Docker.

Use real evidence.

Preserve the governed Agentic QE architecture.

**Start from `2778936` and execute this enhancement continuously through final verification and gate.**
