# CP-MVP2-CR-002 — Runtime Locator Fallback: Change Request Proposal

* **Status:** **PROPOSED — NOT IMPLEMENTED. NOT AUTHORIZED.**
* **Raised against:** the frozen `docs/CP-MVP2-06-SPECIFICATION-v1.0.md`, sec. 14 ("Failure Governance" / retry policy) and sec. 15 ("Self-Healing Boundary").
* **Trigger:** the "CONTINUE: Playwright Automation Generation + Execution" task's own requested runtime behavior (§4/§5 of that instruction): *"If [the primary locator] fails, attempt the next evidence-backed candidate... If a fallback succeeds, the business testcase may still PASS."*

## 1. Why this requires a Change Request rather than silent implementation

The frozen CP-06 specification states, in its own words, with no ambiguity or partial deferral:

> **Sec. 14:** "On any failure, CP-MVP2-06 must not: ... retry indefinitely ... **Retry policy: automatic retry is explicitly PROHIBITED in CP-MVP2-06 v1.0.** No evidence yet exists in this project ... to justify a deterministic retry rule ... it is prohibited outright, not left ambiguous. A future revision may introduce a narrowly-scoped, evidence-justified retry policy only through the same formal Change Request process governing every other rule in this document."
>
> **Sec. 15:** "**Self-healing is explicitly PROHIBITED in CP-MVP2-06.** This is a firm decision, not a 'limited' or vaguely deferred capability ... Any future locator-repair/self-healing capability is a governance-controlled capability belonging to a later, explicitly authorized checkpoint ... CP-MVP2-07 ... CP-MVP2-06 only *records* the evidence ... it does not act on it."

Attempting a pre-authorized, evidence-backed fallback locator **after a runtime failure of the primary locator** is, by CP-06's own explicit wording, a retry ("attempting the step again, this time with a different locator") — sec. 14's prohibition contains no carve-out for a retry that reuses a different, already-authorized locator versus one that reuses the same locator. It is also squarely inside the concern sec. 15 reserves for CP-MVP2-07: acting on a runtime failure by trying something else, rather than only recording it.

**Per this project's own golden rule ("never change the specification to make the implementation pass") and the explicit instruction governing this task ("if a frozen specification or contract must change: STOP implementation, produce a formal CR"), this capability is NOT implemented in this task.** Reinterpreting "retry" narrowly enough to exclude locator-fallback would itself be a silent reinterpretation of a frozen rule to make a feature fit — exactly what is prohibited.

## 2. What IS implemented instead (no conflict)

The **generation-time / persistence-time** half of the new requirement — building and persisting a deterministic, evidence-backed, priority-ordered set of locator *candidates* per load-bearing step — does not conflict with any frozen rule. It is implemented as a wholly new, additive package (`automation/multi_locator/`, see `docs/CP-MVP2-CR-002-MULTI-LOCATOR-IMPLEMENTATION.md`) that:

* never modifies `automation/{schema,generate,validate,pipeline,evidence}.py` (frozen CP-05);
* never modifies `execution/{schema,validate,evidence,engine,pipeline}.py` (frozen CP-06);
* executes, for real, **only the single, highest-priority candidate per step** — i.e., real CP-06 execution in this task behaves exactly as the frozen specification already allows (one locator per step, no retry, no fallback attempted at runtime).
* persists the full candidate set (including un-attempted fallbacks) as evidence/metadata for a future, explicitly-authorized capability to consume.

This satisfies the evidence-resilience *documentation* goal without touching CP-06's frozen execution semantics.

## 3. Proposed future scope (for a real CR-002, if authorized)

If Human + Di authorize this capability in the future, CR-002 would need to specify, at minimum:

* **Amend CP-06 sec. 14** to carve out a narrowly-scoped exception: an evidence-justified, deterministic, priority-ordered locator-candidate retry — *not* an open-ended retry, and *not* covering any other failure type (timeouts, navigation failures, assertion failures remain un-retried).
* **Amend CP-06 sec. 15** to clarify that consuming a *pre-existing, generation-time-authorized* candidate set is not "proposing a locator repair" in the sense that section prohibits (which is about *inventing* a locator in response to failure) — while preserving the prohibition on any runtime-invented locator.
* Define the exact **automation-health** vocabulary the failing task's §5 anticipates (e.g. `GREEN`/`YELLOW`/`RED` automation health, distinct from business PASS/FAIL) and where it is recorded (`ExecutionResult` would need a new, additive field — not a change to any existing field's meaning).
* Define exactly which failure types are eligible for fallback (locator-not-found only, never timeout/navigation/assertion) to keep the exception narrow, per sec. 14's own amendment path.

**This CR is not authorized by this task. No runtime fallback-retry code exists anywhere in this repository as a result of this task.**
