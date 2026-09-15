# POST-MVP2 ENHANCEMENT 01

## Governed Playwright Automation + Test Management + JMeter Performance Foundation

**Project:** Agentic QE MVP2 — Post-MVP2 Enhancement
**Starting Baseline:** `33b9946`
**System Under Test:** Demo Web Shop
**Primary Runtime:** **Windows 10 + VS Code**
**Status:** NEW POST-MVP2 ENHANCEMENT

---

# 1. MISSION

Starting from the frozen MVP2 preservation baseline `33b9946`, build the first post-MVP2 enhancement foundation for a **real, maintainable, human-usable and executable QE automation framework**.

The enhancement must establish:

### Functional QE flow

**Approved Requirement → Testcase Excel → Test Data Excel → Testcase/Data Mapping → Playwright Python Automation → Page Objects → Reusable Components → Multiple Evidence-Backed Locators → Real Windows Browser Execution → Logs/Evidence → Traceability**

### Performance QE flow

**Performance Requirement/NFR → Performance Scenario → Test Data → Structured JMeter Plan → Real Windows JMeter Execution → Results/Evidence → Traceability**

The objective is **not simply to generate more automation files**.

The objective is to establish a maintainable QE engineering foundation with:

* human usability;
* modularity;
* reusability;
* traceability;
* observability;
* evidence;
* governed execution.

---

# 2. ABSOLUTE GOVERNANCE BOUNDARY

MVP2 is frozen.

The frozen baseline is:

```text
33b9946
```

Do NOT modify the historical MVP2 baseline merely to make this enhancement pass.

Do NOT:

* modify the Approved SRS;
* reopen CP01–CP09;
* rewrite historical execution results;
* change historical coverage;
* change the final MVP2 governance decision;
* delete historical evidence;
* weaken existing tests;
* silently modify frozen specifications;
* implement CR-002 as though it were already authorized.

If an enhancement requires changing a frozen artifact:

**STOP → REPORT → HUMAN + DI DECIDE**

All new work must be clearly identifiable as **post-MVP2 enhancement work**.

---

# 3. CR-002 BOUNDARY

CR-002 remains:

**OPEN — NOT AUTHORIZED**

Do not modify CR-002 itself.

If runtime locator fallback/self-healing is implemented as part of this new enhancement, it must be implemented as a **new, clearly identified post-MVP2 capability**, with its own implementation and evidence.

Do not silently treat CR-002 as authorization.

Do not rewrite historical CR-002 status.

---

# 4. FIRST STEP — INSPECT BEFORE IMPLEMENTING

Before changing anything, inspect the repository and local environment.

Run:

```bash
git status
git branch --show-current
git log -1 --oneline
git remote -v
```

Confirm the starting baseline is:

```text
33b9946
```

Inspect existing:

```text
requirements/
testcases/
testdata/
automation/
performance/
reports/
docs/
tests/
```

Determine:

* existing reusable functionality;
* existing testcase artifacts;
* existing test-data artifacts;
* existing traceability;
* existing Playwright implementation;
* existing JMeter implementation;
* frozen artifacts;
* ignored artifacts;
* gaps this enhancement needs to address.

Do NOT duplicate an existing working implementation unnecessarily.

---

# 5. PRIMARY EXECUTION ENVIRONMENT — WINDOWS + VS CODE

The primary supported execution environment for this enhancement is:

**Windows 10 + VS Code**

WSL may remain available for supporting development, but WSL is NOT the acceptance environment.

Successful WSL execution does not count as successful Windows execution.

The target execution paths are:

### Playwright

```text
VS Code
 ↓
Windows Python / virtual environment
 ↓
Python Playwright
 ↓
Windows Chromium
 ↓
Demo Web Shop
```

### JMeter

```text
VS Code
 ↓
Windows Java/JRE
 ↓
Windows Apache JMeter
 ↓
JMeter .jmx
 ↓
Demo Web Shop
```

---

# 6. WINDOWS ENVIRONMENT INSPECTION

Check the actual Windows environment before installing anything.

## Playwright

Verify:

* Windows version;
* VS Code version;
* Python version;
* Python executable path;
* virtual environment;
* Playwright Python package;
* Playwright version;
* browser binaries;
* Chromium availability;
* pytest integration;
* ability to launch Chromium.

Example:

```bash
python --version
where python
python -m pip show playwright
python -m playwright --version
```

Perform an actual browser-launch verification.

## JMeter

Verify:

* Java/JRE;
* `JAVA_HOME`;
* Apache JMeter;
* JMeter version;
* JMeter executable path;
* ability to execute `.jmx` non-interactively.

Example:

```bash
java -version
where java
echo %JAVA_HOME%
jmeter --version
where jmeter
```

Use the appropriate Windows shell syntax where required.

---

# 7. INSTALLATION RULE

If Playwright is missing from the Windows environment:

* install it in the appropriate project Python environment;
* install required browser binaries;
* verify Chromium.

If JMeter is missing:

* install Apache JMeter;
* ensure compatible Windows Java/JRE;
* verify JMeter.

If compatible installations already exist:

**reuse them.**

Do not reinstall unnecessarily.

Do not install only into WSL and claim completion.

If installation requires elevated privileges or a Human decision:

**STOP → REPORT → HUMAN + DI DECIDE**

Record exact installed versions.

---

# 8. EXCEL TESTCASE REQUIREMENT

Testcases must be maintained in **Microsoft Excel `.xlsx` format**.

The Excel testcase artifact must be human-consumable by a QE professional.

It must contain actual testcase information, not merely a report generated from incomplete machine-readable artifacts.

At minimum include:

* Testcase ID;
* Requirement ID;
* Testcase title;
* Objective;
* Preconditions;
* Business steps;
* Expected result;
* Test type;
* Risk/Priority;
* Dataset reference;
* Automation reference;
* Status.

The exact workbook/sheet structure may be improved after repository inspection.

Use a clean, maintainable workbook structure.

---

# 9. EXCEL TEST DATA REQUIREMENT

Test data must also be maintained in **Microsoft Excel `.xlsx` format**.

At minimum support:

* Dataset ID;
* Testcase ID;
* Requirement ID where applicable;
* field name;
* value;
* data type/category;
* purpose;
* validity classification;
* notes.

Do not commit secrets, passwords, API keys or other sensitive credentials.

---

# 10. TESTCASE ↔ DATASET MAPPING

Explicitly maintain testcase-to-dataset mapping.

Support:

**One Testcase → Multiple Datasets**

Example:

| Testcase ID | Dataset ID | Type        | Purpose            |
| ----------- | ---------- | ----------- | ------------------ |
| TC-001      | D01        | POSITIVE    | Valid data         |
| TC-001      | D02        | NEGATIVE    | Invalid data       |
| TC-001      | D03        | EXCEPTIONAL | Boundary/exception |

The mapping must be available in Excel, preferably through a dedicated mapping sheet/workbook if that is the cleanest architecture.

Stable identifiers are mandatory:

```text
Requirement ID
   ↓
Testcase ID
   ↓
Dataset ID
   ↓
Automation ID
   ↓
Execution ID
```

### Critical rule

**Datasets change data, not business steps.**

If a different dataset requires a fundamentally different business flow, that should normally be represented as a separate testcase.

---

# 11. REQUIREMENT ↔ TESTCASE TRACEABILITY

Maintain explicit requirement-to-testcase traceability.

This should be available in human-consumable Excel and machine-readable form where appropriate.

Do not invent coverage.

Coverage must be calculated from actual persisted artifacts.

---

# 12. MACHINE-READABLE ARTIFACTS

JSON or other machine-readable artifacts may remain where useful.

However:

> **Human-consumable testcase and test-data management must be available in `.xlsx`.**

If both Excel and JSON represent the same logical artifact:

* establish a deterministic synchronization/validation mechanism;
* document which representation is authoritative for human review;
* document which representation is used by automation;
* prevent silent divergence.

Do not create two uncontrolled sources of truth.

---

# 13. PLAYWRIGHT PYTHON FRAMEWORK

Build or extend a clean **Python Playwright** automation framework.

Reuse existing MVP2 foundation where practical.

Conceptual structure:

```text
automation/
└── playwright/
    ├── config/
    ├── pages/
    ├── components/
    ├── locators/
    ├── actions/
    ├── tests/
    ├── fixtures/
    ├── data/
    ├── utils/
    ├── evidence/
    ├── logs/
    └── reports/
```

Adapt the structure based on the existing repository.

Do not create unnecessary duplicate frameworks.

---

# 14. PAGE OBJECT MODEL

Implement a proper **Page Object Model**.

Page Objects should contain:

* page-specific locators;
* page-specific actions;
* reusable navigation;
* state validation where appropriate.

Tests should express business intent rather than raw locator implementation.

Use logical page/component boundaries.

Potential examples:

```text
HomePage
RegistrationPage
LoginPage
SearchPage
ProductPage
CartPage
CheckoutPage
WishlistPage
AccountPage
```

Create only those justified by actual application journeys.

---

# 15. REUSABLE COMPONENTS / FUNCTIONS

Identify common operations and implement reusable functions/components.

Examples:

* navigation;
* login/logout;
* search;
* product selection;
* product configuration;
* add to cart;
* update quantity;
* remove item;
* checkout;
* evidence capture;
* state validation.

Avoid copy/paste implementations.

---

# 16. TEST DATA MUST BE SEPARATE FROM AUTOMATION

Automation code must not hard-code business datasets unnecessarily.

Automation should consume the Excel-derived test data through a clean data-access layer.

The data-access layer should:

* identify Dataset ID;
* load appropriate data;
* validate required fields;
* expose data to the automation;
* preserve Dataset ID in execution logs.

---

# 17. AUTOMATION TRACEABILITY

Every automation must have:

* Automation ID;
* Requirement ID;
* Testcase ID;
* Dataset ID.

Maintain:

**Requirement → Testcase → Dataset → Automation**

traceability.

A single testcase may have multiple datasets and therefore multiple executions.

Avoid ID collisions.

---

# 18. TESTCASE ↔ AUTOMATION STEP FIDELITY

The automation must represent the **same business steps as the testcase**.

Do not silently add business actions.

Separate:

### Business steps

What the testcase says the user/system should do.

### Technical setup

Fixtures, browser initialization, authentication state preparation, environment setup.

### Cleanup

Post-test cleanup.

Technical setup must not be disguised as a testcase business step.

If an existing testcase is too generic for reliable automation:

**do not silently rewrite the historical testcase.**

Create a post-MVP enhancement artifact or report the limitation.

---

# 19. MULTIPLE EVIDENCE-BACKED LOCATORS

Implement support for multiple locator candidates for important/load-bearing elements.

Preferred deterministic priority may be:

1. Test ID;
2. accessible role/name;
3. label;
4. stable attribute;
5. other evidence-backed selector.

The exact priority must be documented.

Each candidate must record:

* locator type;
* expression;
* source/evidence;
* priority;
* validation status.

Do not invent selectors merely to increase the number of candidates.

---

# 20. RUNTIME LOCATOR FALLBACK

If runtime fallback is implemented in this enhancement:

* it must be clearly identified as post-MVP2 functionality;
* it must not modify CR-002;
* it must be observable.

If primary locator fails and fallback succeeds, record:

* primary locator;
* failure;
* fallback locator;
* fallback result;
* evidence;
* execution impact.

No silent self-healing.

No requirement modification.

No testcase-step modification.

No expected-result modification.

No automatic locator-definition updates without separate governance.

If runtime fallback is NOT implemented:

**state that clearly.**

---

# 21. PLAYWRIGHT CONFIGURATION

Centralize:

* base URL;
* browser;
* headless/headed;
* workers;
* timeout;
* retries;
* screenshots;
* traces;
* video if appropriate;
* environment;
* evidence directory;
* logging.

The configuration must be suitable for execution from VS Code on Windows.

---

# 22. VS CODE WINDOWS INTEGRATION

The project must be runnable from VS Code on Windows.

Provide, where practical:

* workspace configuration;
* Python interpreter configuration;
* test discovery;
* run configuration;
* debug configuration;
* VS Code tasks;
* documented commands.

A QE engineer should be able to open the repository in Windows VS Code and execute the automation without switching to WSL.

---

# 23. PLAYWRIGHT EXECUTION LOGGING

Every execution must record at minimum:

* Execution ID;
* timestamp;
* Requirement ID;
* Testcase ID;
* Dataset ID;
* Automation ID;
* browser;
* browser version;
* environment;
* worker ID;
* start time;
* end time;
* duration;
* step results;
* final status;
* failure category;
* error details;
* locator selected;
* fallback information where applicable;
* evidence references.

Execution logs must permit reconstruction of the execution.

Do not fabricate results or evidence.

---

# 24. PLAYWRIGHT EVIDENCE

Capture appropriate:

* screenshots;
* Playwright traces;
* console logs;
* network information where useful;
* structured execution records;
* Playwright reports.

Link:

**Execution → Automation → Dataset → Testcase → Requirement**

---

# 25. RETRY GOVERNANCE

If retries are configured:

* log every attempt;
* preserve the original failure;
* record retry number;
* record final outcome.

A retry must never erase evidence of the initial failure.

Retry is not RCA.

---

# 26. PLAYWRIGHT PARALLEL EXECUTION

Implement and demonstrate local parallel execution in the Windows environment.

Support:

* multiple workers;
* isolated execution artifacts;
* worker IDs;
* unique execution IDs;
* deterministic result aggregation;
* safe test-data usage.

Run an actual parallel execution from Windows VS Code.

---

# 27. PLAYWRIGHT DISTRIBUTED EXECUTION

The framework should be architecturally ready for distributed execution.

Clearly distinguish:

### Local parallel

Multiple workers on one Windows machine.

### Distributed

Multiple execution nodes/machines or equivalent distributed browser infrastructure.

Do NOT call local workers "distributed execution."

If multiple machines are unavailable:

* implement the architecture/configuration needed for future distributed execution where practical;
* document worker/node contracts;
* document configuration;
* document prerequisites;
* ensure IDs/evidence are worker-safe.

Do not fabricate a distributed execution result.

The final report must state:

**DEMONSTRATED / CONFIGURED / NOT IMPLEMENTED**

---

# 28. JMETER PERFORMANCE FRAMEWORK

Extend/restructure the existing JMeter implementation into a clean, maintainable structure.

Conceptually:

```text
performance/
└── jmeter/
    ├── plans/
    ├── scenarios/
    ├── data/
    ├── config/
    ├── assertions/
    ├── results/
    └── reports/
```

Reuse existing CP08 artifacts where appropriate.

Do not rewrite historical CP08 results.

---

# 29. JMeter TEST PLAN DESIGN

Each performance scenario must define:

* Scenario ID;
* Requirement/NFR ID;
* workload;
* users;
* ramp-up;
* duration/loops;
* pacing;
* endpoints/actions;
* test data;
* assertions;
* metrics;
* acceptance criteria.

Do not invent performance thresholds.

If the Approved SRS does not contain a numeric threshold:

**measure → report → SLA INCONCLUSIVE**

---

# 30. JMeter MODULARITY

Avoid one giant `.jmx`.

Use appropriate reusable structures for:

* common configuration;
* HTTP defaults;
* common headers;
* authentication/session setup;
* reusable fragments/controllers;
* test data;
* individual performance scenarios.

Each scenario should remain understandable and independently executable where practical.

---

# 31. JMeter TEST DATA

Keep performance test data separate from the `.jmx` where appropriate.

Maintain:

**Scenario → Dataset → Execution → Result**

traceability.

---

# 32. JMETER VS CODE + WINDOWS EXECUTION

JMeter must execute in the Windows VS Code environment.

The target chain is:

```text
VS Code
 ↓
Windows Java/JRE
 ↓
Windows Apache JMeter
 ↓
.jmx
 ↓
Demo Web Shop
 ↓
Results/Evidence
```

Provide documented Windows commands and, where practical, VS Code tasks for execution.

Do not count WSL-only execution as satisfying this requirement.

---

# 33. REAL JMETER EXECUTION

Execute at least one real `.jmx` scenario from Windows VS Code.

Evidence must contain:

* Windows environment;
* Java version;
* JMeter version;
* plan/scenario;
* workload;
* Execution ID;
* result file;
* metrics;
* final status.

No mocked performance results.

---

# 34. JMETER DISTRIBUTED EXECUTION

Configure the architecture for future JMeter distributed execution.

Clearly distinguish:

### Local

One JMeter engine.

### Distributed

Controller/master coordinating multiple JMeter engines.

If only one Windows engine is available:

* configure/document distributed readiness;
* document prerequisites and worker configuration;
* do not claim distributed execution was demonstrated.

Report:

**DEMONSTRATED / CONFIGURED / NOT IMPLEMENTED**

---

# 35. ENVIRONMENT RECORD

Persist an environment record containing actual:

| Component           | Evidence       |
| ------------------- | -------------- |
| Windows             | Version        |
| VS Code             | Version        |
| Python              | Version + path |
| Virtual environment | Path           |
| Playwright          | Version        |
| Chromium            | Version/status |
| Java/JRE            | Version + path |
| JAVA_HOME           | Status/value   |
| JMeter              | Version + path |

Also state:

* Windows Playwright execution;
* Windows JMeter execution;
* Windows parallel execution;
* distributed execution status;
* WSL status as informational only.

---

# 36. VALIDATION STRATEGY

After implementation:

## Focused enhancement tests

Run all new tests.

## Existing regression

Run the complete existing regression suite.

Do not remove or weaken existing tests.

Report exact counts.

## Real Playwright

Run at least one genuine browser testcase against Demo Web Shop from Windows VS Code.

## Real JMeter

Run at least one genuine `.jmx` scenario against Demo Web Shop from Windows VS Code.

No mocks for claimed execution.

---

# 37. BASELINE INTEGRITY CHECK

Before committing:

```bash
git status
git diff
```

Verify changes against baseline:

```text
33b9946
```

All modifications must be attributable to this enhancement.

If any frozen MVP2 artifact has changed:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 38. REQUIRED DELIVERABLES

## Test Management

* `.xlsx` testcase workbook;
* `.xlsx` test-data workbook;
* testcase ↔ dataset mapping;
* requirement ↔ testcase traceability;
* stable IDs;
* multiple datasets per testcase.

## Playwright

* Python automation framework;
* Page Object Model;
* reusable functions/components;
* separate test data;
* multiple evidence-backed locators;
* governed fallback if implemented;
* execution logs;
* evidence;
* VS Code Windows configuration;
* local parallel execution;
* distributed-execution readiness/status.

## JMeter

* structured `.jmx` plans;
* modular scenarios;
* separate data;
* reusable configuration;
* assertions;
* real Windows execution;
* results/evidence;
* distributed-execution readiness/status.

---

# 39. REQUIRED ENHANCEMENT REPORT

Create a dedicated post-MVP2 enhancement report containing:

### Baseline

* starting SHA;
* final SHA;
* baseline integrity.

### Environment

* Windows;
* VS Code;
* Python;
* Playwright;
* Chromium;
* Java;
* JMeter.

### Test Management

* Excel testcase structure;
* Excel test-data structure;
* testcase/data mapping;
* requirement/testcase traceability.

### Playwright

* architecture;
* POM;
* reusable components;
* locator strategy;
* fallback status;
* execution logging;
* evidence;
* parallel execution;
* distributed status.

### JMeter

* architecture;
* scenario structure;
* data;
* execution;
* results;
* distributed status.

### Validation

* focused tests;
* full regression;
* real Windows Playwright result;
* real Windows JMeter result.

### Governance

* frozen-artifact integrity;
* CR-002 status;
* deferred items;
* limitations.

Clearly distinguish:

**IMPLEMENTED**

**VERIFIED**

**CONFIGURED**

**NOT IMPLEMENTED**

**DEFERRED**

Do not overclaim capability.

---

# 40. COMMIT STRATEGY

Keep this enhancement separate from unrelated future enhancements.

Preferred commit:

```text
feat: establish governed playwright and jmeter automation foundation
```

If the implementation is safer as multiple logically bounded commits, use multiple commits and report them.

Do not amend or rewrite the historical MVP2 commits.

---

# 41. COMPLETION GATE

Do not declare this enhancement complete until:

### Environment

* Windows environment inspected;
* VS Code environment verified;
* Playwright available;
* Chromium available;
* JMeter available;
* Java/JRE available.

### Test Management

* testcase Excel exists;
* test-data Excel exists;
* testcase/data mapping exists;
* requirement/testcase traceability exists.

### Playwright

* Python framework works;
* POM exists;
* reusable functions/components exist;
* test data is externalized;
* multiple locators exist where evidence supports them;
* execution logs exist;
* evidence exists;
* Windows VS Code execution works;
* Windows parallel execution is demonstrated;
* distributed status is honestly documented.

### JMeter

* structured `.jmx` plans exist;
* modular structure exists;
* data is externalized appropriately;
* Windows VS Code execution works;
* real JMeter execution is evidenced;
* distributed status is honestly documented.

### Governance

* existing regression preserved;
* frozen MVP2 artifacts unchanged;
* no unauthorized CR-002 implementation;
* all limitations documented;
* repository committed;
* final repository state verified.

---

# 42. HARD RULES

## Rule 1

**Never change the specification to make implementation pass.**

## Rule 2

**Never fabricate execution evidence.**

## Rule 3

**Never silently modify frozen MVP2 artifacts.**

## Rule 4

**Never confuse configured capability with demonstrated capability.**

## Rule 5

**Never call local parallel execution distributed execution.**

## Rule 6

**Never silently modify testcase business steps through automation.**

## Rule 7

**Datasets change data, not business steps.**

## Rule 8

**Excel must remain human-consumable.**

## Rule 9

**WSL execution does not satisfy the Windows + VS Code acceptance requirement.**

## Rule 10

When encountering a frozen-baseline conflict or authorization boundary:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 43. COMPLETION NOTIFICATION

When the enhancement run is genuinely complete:

**Windows system notification sound only.**

Do NOT display a message box.

---

# 44. FINAL INSTRUCTION TO CLAUDE

Take the lead on the implementation, but remain strictly inside the above governance boundaries.

Do not repeatedly ask whether to perform each individual step.

Inspect → implement → test → verify → document → commit → report.

Where a genuine governance decision is required:

**STOP → REPORT → HUMAN + DI DECIDE**

The goal is to produce a **real Windows/VS Code executable, modular, traceable and maintainable QE automation foundation**, while preserving `33b9946` as the untouched MVP2 historical baseline.
