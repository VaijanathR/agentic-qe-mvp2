"""
Agentic QE Orchestration -- the coordination layer over MVP2/Enhancement-01/
Enhancement-02/CR-001's already-real, already-governed capabilities
(RAG, LLM reasoning boundary, testcase/testdata generation, RBTP risk
prioritization, dependency/reusability matrix, Playwright automation,
JMeter performance, RCA/replanning/governance, reporting).

This package adds coordination, state, decision contracts, an
orchestration journal, and a governance layer on top of that existing
infrastructure. It does not reimplement RAG, LLM reasoning, testcase/
testdata generation, RCA, replanning, or governance decision logic --
see `docs/AGENTIC-QE-ORCHESTRATION-SPECIFICATION-v1.0.md` sec. 9 for the
exact responsibility boundary this package is built to.

Nothing here modifies any frozen MVP2/CP01-09/Enhancement-01/Enhancement-02
file. CR-002 (runtime locator self-healing) remains OPEN / NOT AUTHORIZED
and is never implemented here.
"""
