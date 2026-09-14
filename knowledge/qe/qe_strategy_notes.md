# QE Strategy Notes (MVP2)

**source_type:** `qe_strategy` (authority tier 3 — methodology only; never a requirements source). Drawn from `README.md`'s stated core principles and from the Approved SRS's own data/traceability sections — no new methodology is introduced here beyond what MVP2 has already committed to.

## Prioritization
- Business value → QE impact → feasibility/technical complexity (established discovery-phase prioritization, carried into the five frozen journeys J-01…J-05 in Approved SRS §5).
- Negative/exceptional behavior is a first-class citizen, not an afterthought — see Approved SRS §7 (NEG-01…09) and the explicit negative-path emphasis in every CP-MVP2-01 discovery pass.

## Traceability discipline
- Every requirement used by later checkpoints must resolve to a `REQ-*`/`NEG-*` ID in the Approved SRS and a `J-*` journey (Approved SRS §14). CP-MVP2-02's manifest (`knowledge/requirements/approved/srs_v1.0/manifest.json`) is the machine-checkable form of that same table.
- Test-case and automation IDs are explicitly "not yet created" in the Approved SRS traceability table — CP-MVP2-02 does not invent them; that is CP-MVP2-03/05 work.

## Test-data discipline (from Approved SRS §10)
- Registration requires a unique email per run.
- Discovery-session-specific values (the discovery test account, the order number produced, sampled product IDs) must never be hard-coded as fixtures or golden values in future test cases or automation.
- Any future test data must be clearly synthetic.

## Evidence-aware test design
- A requirement's `evidence_strength` (e.g. `AGENT_INFERENCE` on REQ-GCO-03) should inform how a future test case is framed — an inference-backed requirement may warrant an exploratory/confirmatory test before a strict pass/fail assertion is written against it, whereas a `DIRECT_SYSTEM_EVIDENCE` requirement can go straight to a deterministic assertion.
- PARKED items (Approved SRS §13) are explicitly out of test scope until promoted through the SRS's own versioned change-control process — they must not be quietly covered by a test case as if they were approved.
