# CP-MVP2-03 — Testcase Persistence Investigation: Summary

* **Finding:** CP-03 generated testcase instances are **NOT** persisted as
  first-class artifacts. `testcases/pipeline.py`, `testcases/generate.py`,
  `testcases/validate.py`, and `llm/client.py` perform zero file I/O
  anywhere — confirmed by direct code inspection and a repository-wide
  search for persistence calls (`json.dump`, `write_text`, `open(...,"w")`,
  etc.), which found matches only in unrelated modules (CP-02 knowledge
  ingestion, CP-06 execution evidence, test fixtures).
* **The only real generated testcase in the repository** (`TC-REQ-REG-01-01`,
  from the live CP-03 pipeline verification) exists solely as a JSON
  snippet manually embedded inside a Markdown execution report — not as an
  independent, machine-consumable artifact, and not read by any code path.
* **CP-04/CP-05 handoff:** Both receive a plain in-memory
  `List[GovernedTestcase]` parameter from their caller — never a file
  read. In every actual invocation found (tests, live verification), that
  list is either freshly regenerated via a new LLM call or a hand-built
  fixture — never the specific persisted CP-03 instance.
* **Human auditability:** PARTIAL — a human can read the one execution
  report that happens to contain a real example, but there is no
  general-purpose, per-testcase artifact to open.
* **Reproducibility:** NO — retrieving the exact live testcase again
  requires re-reading that report; it cannot be re-fetched without
  re-running the LLM (and even re-running is not guaranteed to reproduce
  identical content).
* **Traceability:** PRESENT through Requirement ID → Approved SRS → Source
  Attribution; **ABSENT** from Test Data onward (no mechanism links this
  specific instance forward to any CP-04/05/06 artifact).
* **Governance classification: RED — testcase is not independently persisted.**
* **Frozen checkpoint impact:** None of CP-MVP2-03/04/05/06's FROZEN/CLOSED
  status is changed. The frozen CP-03 specification never explicitly
  required file-based testcase persistence, so this is a disclosed
  architecture gap, not a specification violation.
* **Recommendation:** A future Change Request against the frozen CP-MVP2-03
  checkpoint could add a deterministic, ID-addressed persistence step
  (e.g. `testcases/generated/<testcase_id>.json`). **Not implemented by
  this investigation** — evidence-gathering only, no code/spec change, no
  checkpoint reopened.
