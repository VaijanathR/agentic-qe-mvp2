# CP-MVP2 — GOVERNANCE-ONLY RECONCILIATION

## CR-001 Canonical State Correction Before Batch-2 Final Gate

**Repository:** `agentic-qe-mvp2`
**Branch:** `main`

---

# 1. PURPOSE

This is a **GOVERNANCE-ONLY reconciliation task**.

Do NOT modify:

* Batch-2 implementation
* Batch-2 tests
* Batch-2 evidence
* CP-MVP2-01
* CP-MVP2-02
* CP-MVP2-03
* CP-MVP2-04
* CP-MVP2-05
* CP-MVP2-06
* Approved SRS
* any frozen implementation
* any generated testcase
* any test data
* any Playwright automation
* execution code
* execution evidence

The purpose is solely to reconcile the canonical CR-001 documents with the governance state already established by the prior CR-001 reconciliation work.

---

# 2. STARTING STATE

Verify current HEAD and origin/main.

Starting Batch-2 implementation:

`53a4f385ef5c530e063370a0c63a21b367abcec7`

Batch-2 evidence:

`b33f5c92709cb60ada2815025d7755ead3855ead3851e9`

Prior governance reconciliation:

`1bc2a9eccf3a03e146cc0ba5620e2821f7e97b7d`

Do not assume these commits are current. Inspect the actual repository.

---

# 3. INSPECT THESE TWO CANONICAL DOCUMENTS

Inspect:

`docs/CP-MVP2-CR-001-PERSISTENT-LIFECYCLE-v1.0.md`

`docs/CP-MVP2-CR-001-ARCHITECTURE-IMPACT-ASSESSMENT-v1.0.md`

Also inspect:

`docs/claude-execution-reports/CP-MVP2-CR-001/CP-MVP2-CR-001-GOVERNANCE-RECONCILIATION-20260914-184306-D7F734.md`

and the Batch-2 report:

`docs/claude-execution-reports/CP-MVP2-CR-001/CP-MVP2-BATCH2-EXEC-20260914-190701-CA5312.md`

---

# 4. REQUIRED GOVERNANCE STATE

The canonical CR documents must accurately reflect the state established by Batch 1.

The CR status must NOT falsely say:

`PROPOSED — PENDING HUMAN + DI REVIEW. NOT APPROVED. NOT IMPLEMENTED.`

The canonical documents should instead clearly state:

**BATCH 1 IMPLEMENTATION AUTHORIZED AND COMPLETE — AWAITING DI FINAL GATE**

This wording is intentional.

Do NOT change it to:

* APPROVED
* FINAL APPROVED
* DI APPROVED
* CR CLOSED
* Batch 2 APPROVED

because the independent Di gate has not yet been issued.

---

# 5. RBTP DEFINITION

Verify that every relevant occurrence defines RBTP as:

**Risk-Based Test Prioritization**

NOT:

**Requirement-Based Test Plan**

Remove/reconcile only stale governance wording that contradicts the already-established CR-001 decision.

RBTP must retain its intended purpose:

> Determine which testcases should be executed first and why, using evidence-backed risk factors.

Do not redesign the RBTP implementation.

Do not change the RBTP schema or code.

---

# 6. CANONICAL CR CONTENT

The CR must accurately reflect the already-authorized Batch-1 architecture:

**APPROVED SRS**
→ **PERSISTED TESTCASES**
→ **REQ↔TC TRACEABILITY**
→ **RBTP**
→ **DEPENDENCY / REUSABILITY MATRIX**
→ **PERSISTED TEST DATA**
→ **TC↔DATA TRACEABILITY**
→ **PERSISTED PLAYWRIGHT AUTOMATION**
→ **AUTOMATION↔TC TRACEABILITY**
→ **REUSABLE COMPONENT CANDIDATES**
→ **EXECUTION**
→ **TIMESTAMPED EXECUTION LOG**
→ **EXECUTION SUMMARY**
→ **CP-07**

Do not add new architecture beyond what is already implemented/authorized.

---

# 7. BATCH-2 STATE

The documents may acknowledge that Batch 2 has been implemented, but must NOT declare the independent Di final gate.

The appropriate wording is equivalent to:

**Batch 2 implementation completed and evidenced; awaiting independent Human + Di final gate.**

Do not claim:

* Batch-2 final PASS
* Batch-2 approved
* Di approved Batch 2

---

# 8. PRESERVE GOVERNANCE BOUNDARIES

Confirm and preserve:

* CP-01–06 specifications remain frozen.
* Approved SRS remains unchanged.
* Security/penetration testing remains POST-MVP/PARKED.
* Automation ID collision remains an advisory.
* DATA-OQ-01 remains unresolved/unweakened.
* No retroactive rewriting of historical artifacts.
* No silent specification changes.
* No implementation changes.

---

# 9. CHANGE LIMIT

This task may modify ONLY:

`docs/CP-MVP2-CR-001-PERSISTENT-LIFECYCLE-v1.0.md`

`docs/CP-MVP2-CR-001-ARCHITECTURE-IMPACT-ASSESSMENT-v1.0.md`

If any other file appears to require modification:

**STOP → REPORT → DO NOT MODIFY IT.**

---

# 10. VERIFY THE DI-GATE BOUNDARY

The repository must not claim that Di has approved:

* CR-001
* Batch 1
* Batch 2

The canonical state must make clear that independent Human + Di verification remains the final governance gate.

---

# 11. VALIDATION

After editing, verify:

### CR document

* correct status
* correct RBTP definition
* correct Batch-1 state
* correct Batch-2 state
* no false approval claim
* no stale "not implemented" claim
* no architecture contradiction

### Architecture Impact Assessment

* consistent with CR
* correct RBTP meaning
* consistent lifecycle
* Batch-1 implementation state correct
* Batch-2 state correct
* no false Di approval

Run a lightweight documentation consistency check.

Do NOT run or modify implementation tests unless necessary to prove that no implementation files changed.

---

# 12. FROZEN-STATE VERIFICATION

Run:

`git status`

and inspect:

`git diff`

Confirm that ONLY the two canonical governance documents changed.

Explicitly verify that none of these changed:

* `execution/`
* `testcases/`
* `testdata/`
* `automation/`
* `persistence/`
* `llm/`
* `tests/`
* `requirements/`
* `docs/CP-MVP2-03*`
* `docs/CP-MVP2-04*`
* `docs/CP-MVP2-05*`
* `docs/CP-MVP2-06*`
* Approved SRS

---

# 13. COMMIT

If and only if the reconciliation is required:

Create ONE clean governance-only commit.

Suggested commit message:

`docs: reconcile CR-001 governance state before Batch 2 gate`

Do not include unrelated files.

After commit:

* verify commit hash
* verify branch
* verify `origin/main`
* verify working tree clean

---

# 14. REQUIRED COMPLETION REPORT

Create a concise governance reconciliation report under:

`docs/claude-execution-reports/CP-MVP2-CR-001/`

Use a timestamped filename.

Include:

* starting commit
* ending commit
* files changed
* files untouched
* exact governance inconsistencies found
* exact corrections made
* RBTP correction
* Batch-1 state
* Batch-2 state
* frozen-state verification
* git status
* commit hash
* confirmation that no implementation/evidence files changed

Do NOT declare the Di final gate.

---

# 15. HUMAN-FACING FINAL MESSAGE

At the end of your terminal/session response display:

============================================================
CR-001 GOVERNANCE RECONCILIATION COMPLETE
=========================================

STATUS: COMPLETE

GOVERNANCE-ONLY: YES

IMPLEMENTATION CHANGED: NO

FROZEN ARTIFACTS CHANGED: NO

FILES CHANGED: 2 CANONICAL CR DOCUMENTS ONLY

RBTP: RISK-BASED TEST PRIORITIZATION

BATCH 1: AUTHORIZED AND COMPLETE — AWAITING DI FINAL GATE

BATCH 2: IMPLEMENTED AND EVIDENCED — AWAITING HUMAN + DI FINAL GATE

COMMIT: <actual commit hash>

WORKTREE: CLEAN

READY FOR DI VERIFICATION: YES

============================================================

# 16. COMPLETION MESSAGE BOX

After ALL work is complete and the final commit has been verified, display a desktop message box.

Preferred mechanisms, in this order:

1. `zenity --info`
2. `kdialog --msgbox`
3. another available desktop notification/message-box mechanism

Example:

`zenity --info --title="CP-MVP2 Governance" --text="CR-001 Governance Reconciliation COMPLETE\n\nImplementation unchanged.\nFrozen artifacts unchanged.\nReady for Di verification."`

The message box is a completion notification only.

Do not allow failure of the message-box command to fail the governance task.

---

# 17. SYSTEM SOUND

After the message box/notification is triggered, attempt a system sound.

Use whatever sound mechanism is actually available on the current Ubuntu environment.

Try available mechanisms such as:

* `paplay`
* `aplay`
* `pw-play`
* `canberra-gtk-play`

Before attempting, detect which command exists.

Example logic:

```bash
if command -v canberra-gtk-play >/dev/null 2>&1; then
    canberra-gtk-play -i complete
elif command -v paplay >/dev/null 2>&1; then
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga
elif command -v pw-play >/dev/null 2>&1; then
    pw-play /usr/share/sounds/freedesktop/stereo/complete.oga
elif command -v aplay >/dev/null 2>&1; then
    aplay /usr/share/sounds/alsa/Front_Center.wav
else
    printf '\a'
fi
```

Do NOT install packages merely to create the notification.

Do NOT modify system audio configuration.

If no audio mechanism is available, report:

`SYSTEM SOUND: UNAVAILABLE — no supported playback mechanism detected`

The governance task must still be considered complete.

---

# 18. ABSOLUTE RULE

This task is documentation reconciliation ONLY.

**DO NOT FIX CODE.**

**DO NOT FIX CP-06.**

**DO NOT FIX AUTOMATION ID COLLISION.**

**DO NOT FIX DATA-OQ-01.**

**DO NOT CHANGE SPECIFICATIONS.**

**DO NOT CHANGE BATCH-2 EVIDENCE.**

**DO NOT CLAIM DI APPROVAL.**

If anything outside the two canonical documents requires modification:

**STOP → REPORT → WAIT.**

Proceed continuously and complete the governance reconciliation.
