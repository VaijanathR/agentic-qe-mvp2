# AGENTIC QE ORCHESTRATION

## Master Claude Implementation Instruction v1.0

---

# 1. MISSION

You are implementing the next major phase of the Agentic QE project:

**Agentic QE Orchestration**

The objective is to evolve the existing MVP2 implementation from a collection of demonstrated QE capabilities into a **governed, evidence-driven, end-to-end Agentic QE orchestration system**.

The system should be capable of coordinating:

```text
Approved Requirements
        ↓
Requirement Understanding
        ↓
Impact / Risk Analysis
        ↓
Test Strategy
        ↓
Testcase Selection / Generation
        ↓
Test Data Selection / Generation
        ↓
Requirement ↔ TC ↔ Data Traceability
        ↓
Automation Selection / Generation
        ↓
Execution Planning
        ↓
Functional / Performance Execution
        ↓
Evidence Collection
        ↓
Failure Classification
        ↓
RCA
        ↓
Replanning Decision
        ↓
Governed Action / Human Review
        ↓
Re-execution / Regression
        ↓
Coverage / QE Intelligence
        ↓
Final Evidence-backed QE Report
```

This phase is about **orchestration and decision-making**, not merely adding more scripts.

---

# 2. STARTING BASELINE

The mandatory starting baseline is:

**`905c1cb`**

This is the current post-freeze MVP2 state after:

* MVP2 mechanism implementation
* Enhancement 01
* Enhancement 02
* controlled REQ-GCO-03 validation
* 35/35 requirement coverage
* functional automation
* performance automation
* testcase corpus
* test data corpus
* traceability
* Playwright automation
* JMeter automation
* evidence
* RCA
* replanning
* governance
* reporting

Historical baselines:

```text
MVP2 mechanism             33b9946
Enhancement 01             85dc6ab
Enhancement 02             521b155
REQ-GCO-03 closure         905c1cb
```

Verify the repository state before beginning.

Do not rewrite history.

Do not amend historical commits.

Do not force-push.

---

# 3. GOVERNANCE MODEL

The governing lifecycle remains:

**Specify → Review → Freeze → Implement → Verify → Gate**

This is mandatory.

Do not bypass specification.

Do not silently alter a frozen specification.

Do not change a requirement to make implementation pass.

If implementation conflicts with a frozen specification:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 4. EXISTING FROZEN ASSETS

Treat the following as protected historical assets:

* Approved MVP2 SRS v1.0
* CP-MVP2-01 through CP-MVP2-09
* MVP2 evidence
* MVP2 reports
* Enhancement 01 artifacts
* Enhancement 02 artifacts
* REQ-GCO-03 validation artifacts
* existing testcase corpus
* existing test data
* existing traceability
* existing automation
* existing evidence
* existing performance implementation
* existing governance implementation

Do not modify historical artifacts merely for convenience.

New phase artifacts should be additive wherever possible.

---

# 5. CR-002 BOUNDARY

**CR-002 remains OPEN / NOT AUTHORIZED.**

Do not implement CR-002.

Do not implement autonomous runtime locator self-healing.

The orchestration system may:

* detect locator failure;
* classify it;
* collect evidence;
* propose a correction;
* request human approval.

It must not silently apply CR-002 behavior.

---

# 6. DOCKER BOUNDARY

Docker is intentionally **deferred**.

Do not create Dockerfiles.

Do not create Docker Compose configurations.

Do not redesign the architecture around Docker.

However, the architecture must provide clean extension points so Docker can later package the same execution components.

Future sequence:

```text
Agentic QE Orchestration
        ↓
Execution Architecture
        ↓
CI/CD
        ↓
Docker
        ↓
Distributed / Cloud Execution
```

---

# 7. FIRST TASK — REPOSITORY DISCOVERY

Before implementation, inspect the repository thoroughly.

Identify:

* current architecture
* orchestration components
* RAG
* LLM integration
* testcase generation
* testcase persistence
* test data
* traceability
* Playwright
* POMs
* reusable components
* locator handling
* execution
* JMeter
* evidence
* RCA
* replanning
* governance
* reporting
* configuration
* provider abstraction
* tests
* CLI/entry points
* existing schemas
* existing IDs

Reuse existing components.

**Do not reinvent working infrastructure.**

---

# 8. CREATE THE SPECIFICATION

Before substantial implementation, create:

`docs/AGENTIC-QE-ORCHESTRATION-SPECIFICATION-v1.0.md`

The specification must cover the complete architecture and behavior described in this instruction.

It must define:

* objectives
* scope
* architecture
* components
* agents/modules
* state machine
* orchestration
* decisions
* traceability
* evidence
* governance
* execution
* RCA
* replanning
* reporting
* extension points
* acceptance criteria
* limitations

Once implementation begins:

**the specification is frozen.**

---

# 9. CORE ARCHITECTURAL PRINCIPLE

Maintain this responsibility separation:

```text
RAG
= authoritative knowledge

LLM
= reasoning / interpretation / planning / generation

Deterministic Code
= validation / policy / state / traceability / enforcement

Agents
= specialized reasoning/action responsibilities

Orchestrator
= workflow coordination

Tools
= actual system interaction

Evidence
= proof

Human
= governance authority
```

The LLM must never become the final authority for governance.

---

# 10. CENTRAL ORCHESTRATOR

Implement a central Agentic QE Orchestrator.

It must coordinate:

1. Requirement Discovery
2. Requirement Validation
3. Requirement Classification
4. Impact Analysis
5. Risk Assessment
6. Test Strategy
7. Testcase Selection
8. Testcase Generation
9. Test Data Selection
10. Test Data Generation
11. Traceability Validation
12. Automation Assessment
13. Automation Selection
14. Automation Generation
15. Execution Planning
16. Functional Execution
17. Performance Execution
18. Evidence Collection
19. Result Validation
20. Failure Classification
21. RCA
22. Replanning Assessment
23. Human Approval
24. Re-execution
25. Regression Selection
26. Regression Execution
27. Coverage Analysis
28. Final QE Reporting

Not every requirement needs every stage.

The orchestrator must support controlled branching.

---

# 11. ORCHESTRATION STATE MACHINE

Implement explicit lifecycle states.

Baseline model:

```text
RECEIVED
    ↓
UNDERSTANDING
    ↓
VALIDATED
    ↓
IMPACT_ANALYZED
    ↓
RISK_ASSESSED
    ↓
TEST_STRATEGY_READY
    ↓
TESTCASES_READY
    ↓
DATA_READY
    ↓
TRACEABILITY_VALID
    ↓
AUTOMATION_READY
    ↓
EXECUTION_PLANNED
    ↓
EXECUTING
    ↓
EVIDENCE_COLLECTED
    ↓
RESULT_ANALYZED
    ↓
RCA_REQUIRED
    ↓
RCA_COMPLETE
    ↓
REPLAN_ASSESSED
    ↓
HUMAN_REVIEW / ACTION_ALLOWED
    ↓
REEXECUTION
    ↓
REGRESSION
    ↓
FINAL_REPORT
```

The implementation may use additional states where justified.

Invalid transitions must be rejected deterministically.

---

# 12. REQUIREMENT INTELLIGENCE

For every requirement, capture:

* requirement ID
* requirement text
* source
* version
* approval status
* evidence strength
* business capability
* dependencies
* related requirements
* risk
* testcase coverage
* automation coverage
* execution coverage
* performance relevance
* status

Approved SRS remains the source of truth.

---

# 13. SOURCE AUTHORITY

Use the established evidence hierarchy:

```text
1. Approved baseline
2. Direct system evidence
3. Current testing artifact
4. Historical evidence
5. Agent inference
```

Approval status and evidence strength remain separate dimensions.

Historical evidence must not silently override an Approved requirement.

Conflicts become governance findings.

---

# 14. REQUIREMENT IMPACT ANALYSIS

Given a requirement/change, determine:

* directly impacted testcases
* indirectly impacted testcases
* datasets
* automation
* reusable components
* performance scenarios
* dependencies
* regression scope
* historical failure information
* risk

Use deterministic traceability where possible.

---

# 15. RISK-BASED TEST PRIORITIZATION

Implement a transparent risk model.

Where available consider:

* business criticality
* complexity
* dependency count
* historical failure rate
* recent failures
* change impact
* execution cost
* customer impact
* performance relevance
* security relevance

Never fabricate statistics.

Explicitly distinguish:

```text
OBSERVED
CALCULATED
HISTORICAL
INFERRED
UNKNOWN
```

The orchestrator must explain why a testcase was prioritized.

---

# 16. TEST STRATEGY

Generate/select:

* positive tests
* alternate tests
* exceptional tests
* negative tests
* boundary tests where applicable
* dependency tests
* performance tests
* regression tests

Prefer compact variants with strong coverage.

Avoid unnecessary combinatorial explosion.

---

# 17. TESTCASE MANAGEMENT

Reuse existing testcases whenever valid.

Generate new testcases only where required.

Each testcase should contain:

* testcase ID
* requirement ID(s)
* title
* objective
* preconditions
* business steps
* expected results
* type
* priority
* risk
* dependencies
* dataset references
* automation status
* performance relevance

Generic placeholders are not acceptable.

---

# 18. TESTCASE QUALITY GATE

Before executable status, validate:

* requirement alignment
* complete business steps
* expected results
* prerequisites
* data requirements
* automation feasibility
* dependencies
* traceability
* duplication

Support states such as:

```text
DRAFT
REVIEW_REQUIRED
READY
AUTOMATABLE
BLOCKED
EXECUTED
```

---

# 19. TEST DATA ORCHESTRATION

The orchestrator must determine whether data already exists.

Preferred order:

```text
Reuse valid existing data
        ↓
Generate new data only when necessary
```

Support:

* multiple datasets/testcase
* uniqueness
* dependency-aware data
* stateful data
* safe cleanup
* permanent-state awareness

Never create unnecessary real SUT state.

---

# 20. DATA GOVERNANCE

Before state-changing execution determine:

* whether data creation is necessary
* whether valid data exists
* duplicate risk
* cleanup capability
* permanent state implications
* authorization

Unauthorized permanent state:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 21. TRACEABILITY

Maintain:

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
RCA
    ↓
Replan
    ↓
Final Result
```

Stable IDs are mandatory.

No orphaned automation.

No execution without traceability.

---

# 22. AUTOMATION ASSESSMENT

Before generating automation determine:

* whether automation already exists
* whether it is reusable
* testcase compatibility
* prerequisites
* locator evidence
* data hooks
* reusable components

Reuse valid automation.

Avoid unnecessary duplicate automation.

---

# 23. PLAYWRIGHT ORCHESTRATION

Use the existing Playwright Python framework.

The orchestrator must:

1. select automation
2. validate readiness
3. select environment/browser
4. prepare data
5. execute
6. capture evidence
7. determine result
8. classify failures
9. trigger RCA
10. determine next action

Do not bypass governance.

---

# 24. LOCATOR GOVERNANCE

Use existing evidence-backed locator infrastructure.

Multiple locators may be used where already supported.

Do not implement CR-002 runtime self-healing.

Locator failure may result in:

```text
DETECTED
CLASSIFIED
EVIDENCE_CAPTURED
RECOMMENDATION_CREATED
HUMAN_REVIEW_REQUIRED
```

where appropriate.

---

# 25. PERFORMANCE ORCHESTRATION

Use the existing JMeter infrastructure.

Determine whether a requirement is performance relevant.

For performance scenarios capture:

* scenario
* workflow/endpoint
* workload
* concurrency
* ramp-up
* pacing
* loops/duration
* data
* environment
* metrics
* approved thresholds

Never invent numeric thresholds.

Missing threshold:

`SLA_STATUS = INCONCLUSIVE`

---

# 26. EXECUTION PLANNING

Execution plans must consider:

* risk
* dependencies
* data
* automation readiness
* environment
* cost
* functional/performance scope
* parallelization safety

Stateful tests must be recognized.

---

# 27. PARALLELIZATION

Classify tests:

```text
SAFE_TO_PARALLELIZE
STATE_DEPENDENT
RESOURCE_CONFLICT
UNKNOWN
```

Do not parallelize shared-state tests merely for speed.

Distinguish capability from demonstrated safety.

---

# 28. DISTRIBUTED READINESS

Design for future distributed execution.

Do not claim distributed execution unless genuinely demonstrated.

Future capability may be:

`CONFIGURED / NOT_IMPLEMENTED`

---

# 29. FAILURE CLASSIFICATION

Support at least:

```text
REQUIREMENT_MISMATCH
REQUIREMENT_AMBIGUITY
TESTCASE_CONTENT_LIMITATION
DATA_ISSUE
AUTHORIZATION_ISSUE
TOOL_ISSUE
ENVIRONMENT_ISSUE
APPLICATION_DEFECT
THIRD_PARTY_DEPENDENCY
CONSTRAINT
AUTOMATION_DEFECT
LOCATOR_ISSUE
PERFORMANCE_THRESHOLD_MISSING
```

Classification must use current evidence and historical evidence where available.

Expose confidence.

---

# 30. RCA

RCA must be evidence-driven:

```text
Observed Evidence
        ↓
Candidate Causes
        ↓
Evidence Comparison
        ↓
Most Supported Cause
        ↓
Confidence
        ↓
Recommended Action
```

Do not represent LLM guesses as facts.

Retain alternative causes when confidence is insufficient.

---

# 31. REPLANNING

After failure determine:

```text
REPLAN_ALLOWED
REPLAN_NOT_ALLOWED
HUMAN_REVIEW_REQUIRED
NO_REPLAN_REQUIRED
```

Consider:

* failure type
* confidence
* governance
* requirement integrity
* testcase quality
* data
* environment
* retry history
* previous outcomes

---

# 32. REPLANNING PROHIBITIONS

Never replan by changing:

* Approved requirements
* expected results
* acceptance criteria
* business rules
* response codes
* valid test data merely to pass
* required business steps

Never turn failure into PASS by changing the contract.

---

# 33. RETRY POLICY

Implement bounded retries.

Examples:

```text
Transient infrastructure issue
→ retry may be allowed

Application defect
→ retry is not resolution

Requirement mismatch
→ retry inappropriate

Testcase-content limitation
→ retry inappropriate

Unauthorized state change
→ STOP
```

Record every retry.

---

# 34. HUMAN APPROVAL

Implement structured approval.

Human approval required for:

* requirement changes
* expected-result changes
* unauthorized permanent state
* destructive cleanup
* CR-002 behavior
* major testcase reinterpretation
* policy exceptions
* governance conflicts

Approval record should include:

* approval ID
* reason
* evidence
* proposed action
* risk
* affected requirements
* affected artifacts
* impact
* requested decision

---

# 35. GOVERNANCE STATES

Implement:

```text
GREEN
YELLOW
RED
```

GREEN = authorized deterministic action.

YELLOW = review/approval required.

RED = governance conflict, unsafe action, unsupported behavior, or requirement conflict.

RED actions must not execute automatically.

---

# 36. EVIDENCE

Evidence must prove:

* what was decided
* why
* what was executed
* what happened
* what supports the conclusion

Never fabricate:

* IDs
* metrics
* screenshots
* order numbers
* timings
* results
* RCA
* coverage

---

# 37. ORCHESTRATION JOURNAL

Persist a machine-readable orchestration journal containing:

* orchestration ID
* timestamp
* initiating requirement/change
* current state
* decision
* concise decision rationale
* tool invocation
* result
* evidence references
* next state
* approval state

Do not store hidden chain-of-thought.

Store concise rationale and evidence references.

---

# 38. ORCHESTRATION ID

Use a stable ID such as:

`ORCH-YYYYMMDD-HHMMSS-XXXX`

Every child artifact references the orchestration ID.

---

# 39. OBSERVABILITY

Provide structured logs for:

* state transitions
* decisions
* tool calls
* execution
* errors
* approvals
* retries
* replanning

Support human-readable and machine-readable logs.

---

# 40. LLM PROVIDER ABSTRACTION

Preserve provider abstraction.

Capture:

* provider
* model
* task
* input reference
* output
* validation result
* fallback status

Do not couple the orchestrator permanently to one provider.

Do not use fake LLM responses in real production-path demonstrations.

Fixtures are permitted for deterministic tests when explicitly identified.

---

# 41. DETERMINISTIC LLM OUTPUT VALIDATION

Every LLM-generated executable artifact must pass deterministic validation for:

* schema
* IDs
* requirement references
* testcase structure
* data references
* allowed actions
* governance state
* traceability
* expected results
* execution eligibility

Invalid outputs must be rejected.

---

# 42. AGENT SPECIALIZATION

Use specialized agents/modules only where useful.

Potential roles:

```text
Requirement Agent
Risk Agent
Test Strategy Agent
Testcase Agent
Test Data Agent
Traceability Agent
Automation Agent
Execution Agent
Performance Agent
Evidence Agent
RCA Agent
Replanning Agent
Governance Agent
Reporting Agent
```

Do not create artificial agents merely for terminology.

A normal Python module is preferable when an independent agent provides no value.

---

# 43. DECISION CONTRACT

Major decisions should use a structured contract containing:

```text
decision_id
orchestration_id
stage
input_references
decision
reason
evidence_references
confidence
risk
governance_state
proposed_action
approval_required
next_state
```

---

# 44. RAG

Reuse the existing RAG.

It must support authoritative retrieval for:

* requirements
* business rules
* capabilities
* testcase information
* historical evidence
* known constraints

Retain source references.

---

# 45. HISTORICAL INTELLIGENCE

Where historical execution data exists, use it for:

* failure frequency
* flaky behavior
* duration
* prior RCA
* locator failures
* environment failures
* performance trends

Clearly separate historical from current evidence.

---

# 46. REGRESSION SELECTION

Select regression based on:

* impacted requirements
* dependencies
* reusable components
* historical relationships
* risk

Support:

```text
TARGETED_REGRESSION
DEPENDENCY_REGRESSION
RISK_REGRESSION
FULL_REGRESSION
```

Explain the selection.

---

# 47. COVERAGE

Report separately:

```text
Requirement Coverage
Testcase Coverage
Dataset Coverage
Automation Coverage
Execution Coverage
Evidence Coverage
Performance Coverage
```

Maintain the distinctions:

```text
Generated ≠ Executable
Executable ≠ Executed
Executed ≠ Passed
Passed ≠ Fully Covered
```

---

# 48. FINAL QE INTELLIGENCE

Final reporting must distinguish:

* requirement covered
* testcase generated
* automation generated
* execution performed
* execution passed
* execution failed
* RCA available
* evidence available
* human review required

No misleading overall GREEN.

---

# 49. CLI / ENTRY POINT

Provide a clear orchestrator entry point.

Support concepts such as:

```text
orchestrate requirement
orchestrate change
orchestrate regression
orchestrate testcase
orchestrate performance
show status
show traceability
show approvals
show evidence
```

Use simple syntax.

---

# 50. DRY RUN

Provide dry-run mode.

Dry-run should display:

* selected requirements
* risk
* testcase selection
* datasets
* automation
* execution plan
* governance gates

without modifying the SUT.

Explicitly label:

`DRY_RUN`

---

# 51. REAL EXECUTION

Provide real execution mode explicitly labelled:

`REAL_EXECUTION`

Real execution must operate against the actual SUT.

---

# 52. STATE PERSISTENCE

Persist enough state to survive process termination.

At minimum:

* orchestration state
* decisions
* approvals
* artifact references
* execution results
* evidence references

Do not rely solely on in-memory state.

---

# 53. RECOVERY

After interruption, the system should identify:

* completed stages
* failed stage
* pending stages
* retry safety
* pending approval

Do not blindly restart everything.

---

# 54. SECURITY / SECRETS

Do not hard-code credentials.

Do not expose credentials/tokens in logs.

Do not store secrets in evidence.

Security/penetration testing remains a separate future capability unless already implemented.

---

# 55. ORCHESTRATOR PERFORMANCE

Avoid unnecessary LLM calls.

Prefer deterministic processing when sufficient.

Track where practical:

* LLM calls
* execution duration
* retries
* testcase count
* automation count
* performance runs

Do not sacrifice governance for speed.

---

# 56. REQUIRED END-TO-END DEMONSTRATION

Demonstrate at least one real, non-mocked orchestration against:

`https://demowebshop.tricentis.com/`

Prefer a representative existing requirement such as:

`REQ-GCO-03`

or another safe requirement.

Demonstrate:

```text
Requirement
→ RAG
→ Risk / Impact
→ Testcase
→ Data
→ Traceability
→ Automation
→ Execution Plan
→ Real Execution
→ Evidence
→ Result
→ RCA where applicable
→ Replanning
→ Governance
→ Regression
→ Final Report
```

If the successful scenario naturally does not produce an RCA/replan event, demonstrate RCA/replanning independently through a clearly marked controlled test fixture.

Do not fabricate a production failure.

---

# 57. CONTROLLED FAILURE DEMONSTRATION

Demonstrate at least one controlled failure.

It may use:

* deterministic fixture
* safe invalid input
* controlled environment simulation

Clearly mark it:

`CONTROLLED TEST FAILURE`

Demonstrate:

```text
Failure
→ Classification
→ RCA
→ Replan Assessment
→ Governance Decision
```

---

# 58. GOVERNANCE NEGATIVE TESTS

Explicitly verify that the orchestrator blocks:

1. changing Approved SRS to make a test pass;
2. changing expected result to make a test pass;
3. creating unauthorized permanent SUT state;
4. silently implementing CR-002;
5. fabricating evidence;
6. bypassing human approval;
7. invalid state transition;
8. using an unapproved performance threshold.

Each must be rejected or escalated deterministically.

---

# 59. REGRESSION

Run existing regression.

No existing functionality may be weakened.

Known pre-existing failures must remain identified as pre-existing.

Do not rewrite tests merely to achieve GREEN.

---

# 60. FROZEN-INTEGRITY VERIFICATION

Verify integrity against:

```text
33b9946
85dc6ab
521b155
905c1cb
```

The historical baselines must remain intact.

Any unexpected drift must be reported.

---

# 61. DOCUMENTATION

Provide appropriate documentation for:

* architecture
* orchestration
* state machine
* agents/modules
* decision contracts
* governance
* CLI
* configuration
* execution
* evidence
* troubleshooting
* extension points
* limitations

Avoid duplicate documents.

---

# 62. ARCHITECTURE DIAGRAM

Provide an architecture diagram covering:

```text
User
 ↓
Agentic QE Orchestrator
 ↓
Planning / Decision Layer
 ↓
Specialized Agents / Modules
 ↓
RAG + LLM + Tools
 ↓
Functional / Performance Execution
 ↓
Evidence
 ↓
RCA / Replanning
 ↓
Governance
 ↓
Reporting
```

Also show traceability and state flow.

---

# 63. NO FAKE AGENTICITY

The system must not be called agentic simply because an LLM was called.

The final report must explicitly identify:

* where LLM reasoning occurred;
* where deterministic code validated/enforced;
* where governance made the final decision.

---

# 64. NO OVER-ENGINEERING

Do not introduce unnecessary:

* microservices
* message queues
* databases
* cloud dependencies
* agent frameworks

unless justified.

A robust modular Python implementation is acceptable.

---

# 65. EXTENSION POINTS

Design clean extension points for:

* Docker
* CI/CD
* distributed execution
* cloud execution
* additional browsers
* additional SUTs
* additional LLM providers
* additional performance tools
* security testing
* advanced self-healing
* CR-002

Do not implement these unless explicitly in scope.

---

# 66. ACCEPTANCE CRITERIA

The phase is complete only when:

### Architecture

* central orchestrator exists;
* state machine exists;
* responsibilities are clear.

### Requirement Intelligence

* Approved SRS retrieval works;
* impact analysis works;
* risk assessment works.

### Test Management

* testcase selection works;
* testcase generation works;
* data selection works;
* traceability works.

### Automation

* existing automation can be selected;
* readiness is validated;
* Playwright can be orchestrated.

### Performance

* performance relevance is identified;
* JMeter can be orchestrated.

### Failure Intelligence

* classification works;
* RCA works;
* confidence is represented;
* replanning works.

### Governance

* GREEN/YELLOW/RED works;
* approval works;
* prohibited actions are blocked;
* CR-002 remains unauthorized.

### Evidence

* orchestration journal exists;
* execution evidence persists;
* traceability persists.

### Reporting

Separate reporting exists for:

* requirement coverage
* testcase coverage
* automation coverage
* execution coverage
* evidence coverage
* performance coverage
* governance

### Real Proof

At least one real end-to-end orchestration is demonstrated against Demo Web Shop.

### Negative Proof

At least one controlled failure demonstrates:

```text
Failure → RCA → Replanning → Governance
```

### Regression

Existing regression remains healthy.

### Integrity

No unauthorized frozen-baseline drift.

---

# 67. REQUIRED DELIVERABLES

Create/update, as appropriate:

```text
docs/AGENTIC-QE-ORCHESTRATION-SPECIFICATION-v1.0.md

docs/AGENTIC-QE-ORCHESTRATION-ARCHITECTURE.md

docs/claude-execution-reports/AGENTIC-QE-ORCHESTRATION/
    └── comprehensive execution report

orchestration/
    ├── orchestrator
    ├── state
    ├── decisions
    ├── governance
    ├── agents/modules
    ├── traceability
    ├── execution planning
    ├── evidence
    ├── RCA
    └── replanning
```

Adapt paths to existing architecture when doing so avoids duplication.

---

# 68. FINAL REPORT

The final report must include:

## Baseline

Starting commit and final commit.

## Specification

Specification version and SHA.

## Architecture

Implemented components.

## Orchestration

End-to-end state flow.

## Agentic Decisions

Major reasoning/decision points.

## Functional

Playwright orchestration evidence.

## Performance

JMeter orchestration evidence.

## Failure

Controlled failure path.

## RCA

Root cause and confidence.

## Replanning

Decision and governance outcome.

## Human Approval

Approval mechanisms demonstrated.

## Negative Governance

Blocked prohibited actions.

## Traceability

Requirement → TC → Data → Automation → Execution → Evidence.

## Coverage

Requirement/testcase/data/automation/execution/evidence/performance.

## Regression

Focused and full results.

## Integrity

Frozen baseline verification.

## Limitations

Explicit limitations.

## Future

Docker, CI/CD, distributed execution, CR-002, security, etc.

---

# 69. COMMIT GOVERNANCE

Do not commit until:

1. specification is complete;
2. implementation is complete;
3. focused tests pass;
4. existing regression is verified;
5. real E2E orchestration is demonstrated;
6. governance negative tests pass;
7. frozen integrity is verified;
8. final report is complete.

Then create a new commit based on:

**`905c1cb`**

Do not amend `905c1cb`.

Do not force-push.

Push normally after verification.

Confirm:

```text
HEAD == origin/main
working tree clean
```

---

# 70. FINAL STATUS

The final report must declare exactly one:

```text
PASS
PASS WITH EXPLICIT LIMITATIONS
BLOCKED — GOVERNANCE
BLOCKED — TECHNICAL
```

Do not claim PASS if mandatory acceptance criteria are incomplete.

Do not hide limitations.

---

# 71. ABSOLUTE GOVERNANCE RULES

These rules override convenience:

### Rule 1

**Approved SRS is the source of truth.**

### Rule 2

**NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.**

### Rule 3

Frozen-specification conflict:

**STOP → REPORT → HUMAN + DI DECIDE**

### Rule 4

Never fabricate evidence.

### Rule 5

Never fabricate execution results.

### Rule 6

Never fabricate historical probability.

### Rule 7

Never create unauthorized permanent SUT state.

### Rule 8

Never bypass human approval.

### Rule 9

CR-002 remains:

**OPEN / NOT AUTHORIZED**

### Rule 10

Docker remains:

**DEFERRED**

### Rule 11

Generated ≠ Executable.

### Rule 12

Executable ≠ Executed.

### Rule 13

Executed ≠ Passed.

### Rule 14

Passed ≠ Fully Covered.

### Rule 15

Do not repeatedly ask Human + Di for confirmation for ordinary implementation decisions.

Proceed autonomously within this approved scope.

Pause only for:

* governance conflict;
* frozen-spec conflict;
* unresolved requirement ambiguity;
* unauthorized permanent state;
* destructive action;
* CR-002 boundary;
* security-sensitive action outside scope.

Otherwise:

**inspect → reason → implement → test → verify → report.**

---

# 72. FINAL COMPLETION NOTIFICATION — LAST INSTRUCTION

**THIS IS THE FINAL INSTRUCTION IN THIS DOCUMENT. NOTHING FOLLOWS THIS SECTION.**

After ALL work requested by this instruction has been completed, including:

* repository inspection
* specification creation
* specification freeze
* implementation
* unit/integration testing
* real functional execution
* real performance execution where applicable
* controlled failure demonstration
* RCA demonstration
* replanning demonstration
* governance negative testing
* regression
* frozen-integrity verification
* documentation
* final report
* Git commit
* Git push
* confirmation that `HEAD == origin/main`
* confirmation that the working tree is clean

play the **Windows system notification sound THREE TIMES** to indicate that the complete Claude execution session has finished.

Requirements:

1. Play exactly **3 notification sounds**.
2. Play them sequentially.
3. Use a Windows system notification sound.
4. Do not display a message box.
5. Do not require user interaction.
6. Do not play notification sounds for intermediate milestones.
7. Do not play the sounds before final Git push and verification.
8. Play the sounds whether the final status is:

   * `PASS`
   * `PASS WITH EXPLICIT LIMITATIONS`
   * `BLOCKED — GOVERNANCE`
   * `BLOCKED — TECHNICAL`
9. The purpose of the sounds is to signal **completion of the Claude session**, not success.
10. The three notification sounds must be the **last operational action performed by Claude** for this instruction set.

**FINAL ACTION: PLAY THE WINDOWS SYSTEM NOTIFICATION SOUND THREE TIMES NOW.**
