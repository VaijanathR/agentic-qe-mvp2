# Agentic QE MVP2 — Overall Summary, Claude Execution Instructions & Engineering Rationale

**Project:** Agentic QE — MVP2
**System Under Test:** Demo Web Shop
**Baseline Status:** **FROZEN — ACCEPTED WITH EXPLICIT LIMITATIONS**
**Final Commit:** `6766541`
**Final Decision:** **MVP2 — ACCEPTED WITH EXPLICIT LIMITATIONS — MECHANISM MVP COMPLETE**

---

# 1. Purpose of This Document

This document preserves the **overall history, engineering intent, governance decisions, and Claude execution instructions** used to build Agentic QE MVP2.

It is intentionally complementary to the **MVP2 Frozen Baseline Preservation Charter**.

The Preservation Charter defines how the completed baseline must be protected.

This document records:

* why MVP2 was created;
* what we intended to prove;
* how the implementation was divided into checkpoints;
* the major instructions given to Claude;
* why those instructions were given;
* what each checkpoint actually demonstrated;
* important governance decisions made during implementation;
* what MVP2 proved;
* what MVP2 deliberately did not prove;
* why the final MVP was accepted despite limited business coverage.

This is a **historical and governance record**, not a new specification.

---

# 2. Why MVP2 Was Created

MVP1 was established as the frozen Customer API / reusable Agentic QE engine reference implementation.

MVP2 was intentionally created as the next step:

> **Take the Agentic QE mechanism beyond a controlled API example and demonstrate it end-to-end against a real application.**

The selected first System Under Test was:

**Demo Web Shop**

MVP2 therefore became the practical demonstration of whether an Agentic QE system could operate across a realistic QE lifecycle rather than merely generate isolated testcases or code.

The intended progression was:

**Requirements → Knowledge → Testcases → Test Data → Automation → Real Execution → Evidence → RCA → Replanning → Governance → Performance → Unified Reporting**

---

# 3. Core Engineering Philosophy

From the beginning, MVP2 was governed by several principles.

## 3.1 Approved requirements are the source of truth

The Agentic QE system must reason from an **Approved SRS**, not from assumptions, implementation behavior, or an LLM's interpretation of what the application "probably" does.

Therefore:

> **Approved specification takes precedence over generated content, historical artifacts, and agent inference.**

---

## 3.2 Evidence must be distinguishable from inference

The system was required to distinguish between:

1. Approved baseline
2. Direct system evidence
3. Current testing evidence
4. Historical evidence
5. Agent inference

This prevents an LLM from presenting an assumption as an observed fact.

---

## 3.3 LLM reasoning must remain governed

The LLM is useful for reasoning and generation, but deterministic mechanisms must govern critical decisions.

The overall philosophy became:

> **LLM reasons and generates. Deterministic code validates and governs. Agents coordinate. Tools act. Evidence supports conclusions.**

This distinction was fundamental to the MVP.

---

## 3.4 Failures must remain failures

One of the strongest governance principles was:

> **NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.**

The equivalent rule applied to test data, expected response codes, execution evidence, and historical results.

A failing test must be investigated and classified—not manipulated until it passes.

---

## 3.5 Human authority must remain explicit

Claude was deliberately not given authority to:

* change frozen specifications;
* self-authorize change requests;
* reinterpret conflicts as requirements;
* silently change expected behavior;
* convert failures into passes;
* introduce future functionality without authorization.

Where a conflict existed:

> **STOP → REPORT → HUMAN + DI DECIDE**

This preserved human governance over the agent.

---

# 4. Why MVP2 Was Divided into CP01–CP09

Rather than asking Claude to build a large Agentic QE system in one uncontrolled run, we divided MVP2 into independently governed checkpoints.

This provided:

* smaller implementation boundaries;
* frozen intermediate contracts;
* easier verification;
* traceable evidence;
* regression protection;
* clear rollback points;
* prevention of scope creep;
* explicit Human + Di approval before advancing.

The sequence was:

| Checkpoint | Purpose                       |
| ---------- | ----------------------------- |
| CP-MVP2-01 | Discovery & Approved SRS      |
| CP-MVP2-02 | Knowledge Base + RAG          |
| CP-MVP2-03 | LLM Testcase Generation       |
| CP-MVP2-04 | LLM Test Data Generation      |
| CP-MVP2-05 | Playwright E2E Generation     |
| CP-MVP2-06 | Real Browser Execution        |
| CP-MVP2-07 | RCA + Replanning + Governance |
| CP-MVP2-08 | JMeter Performance Testing    |
| CP-MVP2-09 | Unified Final QE Reporting    |

Each checkpoint had a specific purpose and was not intended to solve every problem in the overall system.

---

# 5. Standard Instruction Pattern Given to Claude

Across checkpoints, Claude was repeatedly instructed to follow this operating model:

### Before implementation

1. Inspect the repository.
2. Inspect the applicable frozen specification.
3. Inspect existing preparation/governance artifacts.
4. Understand the current baseline.
5. Identify conflicts before making changes.

### During implementation

1. Implement only the authorized scope.
2. Preserve frozen artifacts.
3. Do not invent requirements.
4. Do not weaken tests.
5. Do not silently change expected behavior.
6. Add deterministic validation wherever governance required it.
7. Preserve evidence.

### After implementation

1. Run focused tests.
2. Run the complete regression suite.
3. Verify frozen-artifact integrity.
4. Verify repository state.
5. Verify the implementation in a fresh process/clone where applicable.
6. Persist the execution evidence and report.
7. Commit the work.
8. Confirm the final HEAD.
9. Signal completion using the **Windows system notification sound only**.

The repeated structure was intentional: it reduced the risk of a long-running agent drifting away from the governing contract.

---

# 6. CP01 — Discovery & Approved SRS

## Instruction to Claude

Claude was instructed to discover the Demo Web Shop application and produce the Approved SRS without inventing functionality.

The SRS had to identify:

* business journeys;
* capabilities;
* functional requirements;
* acceptance criteria;
* business rules;
* relevant NFR/security considerations;
* open questions.

## Why we gave these instructions

We needed a formal application-specific source of truth before asking an LLM to generate testcases.

Without this step, later generations could be based on:

* website assumptions;
* observed UI behavior;
* generic ecommerce knowledge;
* LLM hallucination.

Therefore CP01 established the contract against which all later artifacts would be judged.

**Result:** CP01 frozen and closed.

---

# 7. CP02 — Knowledge Base + RAG

## Instruction to Claude

Claude was instructed to build a governed knowledge/retrieval mechanism in which:

* the Approved SRS was authoritative;
* Draft material could not override Approved material;
* historical material was appropriately separated;
* retrieval remained deterministic where authority mattered;
* inference was explicitly lower in authority;
* queries could be validated against known requirements and capabilities.

## Why we gave these instructions

An Agentic QE system cannot safely use RAG merely because a document was retrieved.

It must know **which retrieved document is authoritative**.

This checkpoint therefore tested the governance layer behind retrieval rather than simply testing whether an LLM could find text.

**Result:** CP02 frozen and closed.

---

# 8. CP03 — LLM Testcase Generation

## Instruction to Claude

Claude was instructed to use the approved requirements and governed context to generate testcases.

The generation mechanism had to:

* remain grounded in the Approved SRS;
* provide requirement traceability;
* distinguish generated reasoning from evidence;
* avoid inventing unsupported behavior;
* support deterministic validation;
* use the live Claude provider rather than a fake/mock LLM response for the real pipeline demonstration.

## Why we gave these instructions

This was the first major test of whether the Agentic QE mechanism could move from:

**requirement → executable QE intent**

The objective was not to generate a huge number of testcases.

The objective was to prove that the **LLM generation stage itself was real, governed and traceable**.

CP03 was therefore frozen once the mechanism and regression evidence were established.

---

# 9. CP04 — LLM Test Data Generation

## Instruction to Claude

Claude was instructed to generate test data from approved requirements and testcase context while respecting constraints such as:

* no duplicate customers where uniqueness was required;
* no invented requirement changes;
* no changing data merely to make a testcase pass;
* explicit candidate/acceptance handling;
* traceability between testcase and data.

## Why we gave these instructions

Test data is not an incidental input.

For Agentic QE, generated data must itself be governed.

A generated dataset that violates a business rule can create a false failure or false success.

Therefore CP04 treated test data as a first-class QE artifact.

**Result:** CP04 frozen and closed.

---

# 10. CP05 — Playwright E2E Generation

## Instruction to Claude

Claude was instructed to generate Playwright automation from the testcase/data context.

The automation generation had to remain traceable to the testcase and requirement.

At this stage we deliberately did **not** authorize unrestricted self-healing or runtime locator fallback.

## Why we gave these instructions

Automation is where an LLM can easily become dangerous if it is allowed to invent selectors, alter steps, or change expected behavior.

The checkpoint therefore emphasized:

* traceability;
* evidence-backed automation;
* deterministic validation;
* honest unsupported states.

When locator evidence was insufficient, the correct answer was **unsupported**, not a fabricated selector.

**Result:** CP05 frozen and closed.

---

# 11. CP06 — Real Browser Execution

## Instruction to Claude

Claude was instructed to execute generated automation against the real Demo Web Shop using a real browser.

The execution layer had to:

* launch a real Chromium browser;
* use the generated automation;
* preserve execution evidence;
* distinguish executable from unsupported automation;
* avoid fabricated execution results;
* preserve honest NOT_EXECUTED states;
* avoid unauthorized retry/self-healing behavior.

## Why we gave these instructions

This was the transition from **generation** to **real-world execution**.

We needed to prove that the Agentic QE system could actually operate against a live SUT rather than producing simulated results.

The deliberate blocking of unsupported automation was important.

A system that reports success despite unsupported locators is worse than a system that honestly reports:

**NOT_EXECUTED**

**Result:** CP06 closed with advisories.

---

# 12. CP07 — RCA + Replanning + Governance

## Instruction to Claude

Claude was instructed to analyze real execution failures and classify them deterministically.

The RCA mechanism had to distinguish categories such as:

* requirement mismatch/ambiguity;
* data issue;
* authorization issue;
* tool issue;
* environment issue;
* third-party dependency;
* constraint violation.

Claude was also instructed that replanning could not automatically authorize prohibited changes.

Human review remained mandatory where governance boundaries were crossed.

## Why we gave these instructions

A true Agentic QE system must do more than report:

> "Test failed."

It must reason about **why** it failed and determine what action is permitted.

However, reasoning about a failure must not become permission to rewrite the system.

Therefore the architecture deliberately separated:

**RCA → Recommendation → Governance Decision**

rather than:

**RCA → Agent automatically changes everything**

CP07 exposed the important testcase-content limitation and correctly classified it rather than hiding it.

**Result:** CP07 closed GREEN WITH ADVISORIES.

---

# 13. CP08 — JMeter Performance Testing

## Instruction to Claude

Claude was instructed to implement genuine Apache JMeter performance testing.

Requirements included:

* real executable `.jmx`;
* defined performance scenario;
* defined workload;
* real execution;
* real metrics;
* persisted evidence;
* deterministic reporting;
* no invented numeric SLA threshold.

Claude was explicitly prohibited from inventing an acceptable response-time threshold when the Approved SRS did not contain one.

## Why we gave these instructions

Performance testing is especially vulnerable to meaningless "green" results.

A measured response time is evidence.

It is **not automatically a PASS** unless there is an approved acceptance criterion against which it can be evaluated.

Therefore the correct result was:

**Capability PASS + Numeric SLA INCONCLUSIVE**

The missing threshold remained a Human/Project decision rather than becoming an invented requirement.

The Windows JMeter environment issue was subsequently root-caused and corrected without weakening the test.

**Result:** CP08 closed with **zero actionable debt**.

---

# 14. CP09 — Unified Final QE Reporting

## Instruction to Claude

Claude was instructed to produce a deterministic, read-only aggregation of the complete MVP evidence.

The report had to include:

* requirements;
* testcases;
* test data;
* automation;
* execution;
* RCA;
* replanning;
* governance;
* performance;
* evidence;
* coverage;
* limitations.

Claude was specifically instructed **not to declare the final MVP governance decision inside CP09**.

## Why we gave these instructions

We wanted to separate:

**Evidence aggregation**

from

**Human governance acceptance**

This prevented the reporting mechanism from effectively grading itself.

CP09 therefore produced the final factual picture, after which Human + Di made the separate final governance decision.

**Result:** CP09 complete and closed.

---

# 15. Important Governance Interventions During MVP2

Several situations demonstrated why the governance model was necessary.

## 15.1 Testcase persistence

We discovered that generated testcase artifacts were not initially persisted as first-class repository artifacts.

Rather than pretending the lifecycle was complete, we performed a forensic investigation.

The conclusion was:

* the frozen CP03 specification had not explicitly required file persistence;
* therefore this was not silently labelled a CP03 specification violation;
* a lifecycle persistence change was subsequently defined through CR-001.

This reinforced the principle:

> **Do not retrospectively change history to make an earlier checkpoint appear stronger.**

---

## 15.2 CR-001 — Persistent Artifact Lifecycle

CR-001 was introduced to establish first-class persistence and linkage across:

* requirements;
* testcases;
* RBTP;
* requirement ↔ testcase traceability;
* dependency matrix;
* test data;
* testcase ↔ data;
* automation;
* automation ↔ testcase;
* execution;
* execution summary;
* evidence.

A terminology correction was also made:

**RBTP = Risk Based Test Prioritization**

rather than the initially incorrect interpretation of Requirement-Based Test Plan.

The correction was governed rather than silently propagated.

CR-001 was subsequently approved with advisories.

---

# 16. Multi-Locator / CR-002 Work

During the implementation, an important engineering concern emerged:

> A testcase should not fail merely because one developer naming/locator choice is wrong when multiple evidence-backed locators exist.

A proposal was therefore created for:

**Multiple evidence-backed locators + runtime locator fallback/self-healing**

However, CP06's frozen execution rules did not authorize runtime fallback.

Therefore:

**CR-002 was created.**

It remains:

**OPEN — NOT AUTHORIZED**

No self-healing or runtime locator fallback was silently introduced.

This was a deliberate governance success.

The capability may be valuable in the future, but MVP2 was not allowed to evolve its own contract without authorization.

---

# 17. The Testcase-Content Limitation

During real execution and RCA, we discovered a substantive limitation in generated testcase content.

Some generated testcases contained structurally valid but overly generic business steps rather than sufficiently explicit prerequisite/setup/business-action steps.

This became particularly important because automation generated from such a testcase can technically follow the testcase while still failing to establish the state required for meaningful execution.

The important governance decision was:

> **Do not repair the limitation by silently changing the frozen MVP.**

It was:

* identified;
* evidenced;
* root-caused;
* reported;
* carried into the final limitations;
* parked for future enhancement.

This is now one of the most important lessons from MVP2.

---

# 18. Final Evidence Picture

The final unified report established:

**35 Approved SRS requirements**

→ **4 requirements with generated testcases**

→ **1 requirement reaching real browser execution**

→ **0 requirements with verified business-level PASS**

The real execution chain for REQ-ACO-03 was genuine and complete:

**Requirement → Testcase → Test Data → Automation → Real Browser → Evidence → RCA → Replanning → Governance**

The execution result was a genuine FAIL.

The RCA identified the testcase-content limitation.

The governance layer correctly prevented unauthorized replanning/self-healing.

Therefore the mechanism demonstrated the intended governed behavior even though business coverage remained narrow.

---

# 19. What MVP2 Successfully Proved

MVP2 successfully demonstrated the mechanism for:

* Approved-SRS-driven QE reasoning;
* governed RAG;
* LLM testcase generation;
* LLM test-data generation;
* requirement/testcase traceability;
* automation generation;
* real browser execution;
* evidence capture;
* failure analysis;
* RCA;
* governed replanning;
* governance controls;
* performance-test generation/execution;
* unified QE reporting;
* preservation of honest failures and inconclusive outcomes.

Most importantly, the chain was demonstrated with **real, non-mocked evidence**.

---

# 20. What MVP2 Did Not Prove

MVP2 does **not** establish:

* broad Demo Web Shop business coverage;
* complete testcase quality across the SRS;
* verified business PASS across the application;
* production-ready self-healing;
* complete runtime locator fallback;
* distributed execution;
* CI/CD integration;
* production-grade security/penetration testing;
* cross-platform portability;
* production-scale performance engineering.

These are limitations of the completed Mechanism MVP, not reasons to rewrite its historical results.

---

# 21. Final Human + Di Governance Decision

After CP01–CP09 were completed and the evidence was independently reviewed, the final decision was:

# **MVP2 — ACCEPTED WITH EXPLICIT LIMITATIONS**

## **MECHANISM MVP COMPLETE**

This means:

> The Agentic QE mechanism has been successfully demonstrated end-to-end under governance against a real SUT.

It does **not** mean:

> The Demo Web Shop has been comprehensively tested or that the application has been proven business-correct.

That distinction is fundamental.

---

# 22. Final Repository State

**Final commit:**

`6766541`

**Final HEAD:**

`6766541 == origin/main`

Final governance closure was persisted in:

`docs/claude-execution-reports/MVP2-FINAL/MVP2-FINAL-GOVERNANCE-CLOSURE-20260915-103819.md`

Frozen-artifact integrity was re-verified.

The final regression state was:

**360 passed + 1 honest skip**

CR-002 remains:

**OPEN — NOT AUTHORIZED**

---

# 23. Lessons We Should Carry Into Future Agentic QE Work

## Lesson 1 — Mechanism proof and business coverage are different objectives

A mechanism can be successfully demonstrated without having broad business coverage.

Both metrics must be reported separately.

---

## Lesson 2 — Structural testcase validity is not enough

A testcase can have the correct schema, IDs and traceability while still being substantively inadequate for reliable automation.

Future systems need stronger business-step quality validation.

---

## Lesson 3 — Evidence hierarchy is essential

An LLM must never be allowed to treat inference as equivalent to direct system evidence.

---

## Lesson 4 — Honest failure is a success of governance

A FAIL that is correctly classified and root-caused is more valuable than a fabricated PASS.

---

## Lesson 5 — Agents need explicit authority boundaries

An agent may identify an improvement without being authorized to implement it.

CR-002 is a concrete example.

---

## Lesson 6 — Generated artifacts must become first-class lifecycle objects

Requirements, testcases, data, automation and execution evidence need stable identity and traceability.

This became a major lesson from CR-001.

---

## Lesson 7 — Performance results require approved acceptance criteria

A measured number is not automatically a PASS.

If the approved specification has no numeric threshold:

**Report the measurement + classify the SLA result as INCONCLUSIVE + escalate the decision.**

---

## Lesson 8 — Freeze early, evolve separately

Once a checkpoint or MVP is frozen, future improvements should be implemented as governed evolution rather than silent mutation.

---

# 24. Relationship to the Frozen Baseline

This document is historical.

It must not be interpreted as authorization to modify MVP2.

The authoritative current baseline remains:

**MVP2 — FROZEN**

Future implementation must follow:

**Specify → Review → Freeze → Implement → Verify → Gate**

If a future implementation conflicts with the frozen baseline:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 25. Final Statement

MVP2 should be remembered not as an application-wide automated testing solution, but as what it deliberately set out to become:

> **A governed Mechanism MVP demonstrating that an Agentic QE system can move from approved requirements through AI-assisted QE generation, real automation and execution, evidence-based failure analysis, governed replanning, performance testing and unified reporting—without allowing the agent to rewrite the rules when reality does not match expectations.**

That is the capability MVP2 successfully demonstrated.

**MVP2 is now frozen.**

**Future work evolves from this baseline; it does not rewrite it.**
