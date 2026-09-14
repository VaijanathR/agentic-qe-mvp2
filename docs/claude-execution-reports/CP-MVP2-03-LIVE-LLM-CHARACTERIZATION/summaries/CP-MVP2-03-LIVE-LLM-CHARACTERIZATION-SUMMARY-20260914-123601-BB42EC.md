CHARACTERIZATION STUDY: 5 real Claude invocations, REQ-REG-01, identical production prompt/argv construction, no retries.

CASE: CASE 1 — All five clean JSON

RESULTS:
5/5 successful invocations (exit 0)
5/5 outer envelope parsed as JSON, is_error=false
5/5 inner "result" directly parsed as JSON
Format breakdown: FORMAT-A = 5, FORMAT-B = 0, FORMAT-C = 0, FORMAT-D = 0, FORMAT-E = 0

The previous live-smoke parsing failure ("Expecting value: line 1 column 1 (char 0)") was NOT reproduced in this sample.

ADDITIONAL OBSERVATION (content-level, not a format/parsing issue): calls 1 and 4 of 5 returned a valid-but-empty JSON array "[]" — zero candidates — for the same requirement/evidence that calls 2, 3, and 5 used to produce a populated POSITIVE candidate. This is reported as a fact for Di's awareness, not diagnosed or acted on.

Confirmed vs hypothesis: CONFIRMED — this specific 5-call sample never encountered a non-JSON or fence-wrapped response. HYPOTHESIS/UNKNOWN — whether the original failure mode can recur at some rate; a 0/5 sample cannot statistically rule that out.

Regression: 67 passed, 0 failed (pre- and post-study, identical).

Repository integrity: starting HEAD 477373b45d72fa5935f578362b27f2f76884d6d2, unchanged by this task. Frozen specification, provider decision doc, llm/, testcases/, tests/, requirements/, knowledge/ all confirmed unchanged. Only this report and its detailed companion were added.

Governance: no parser patch, no prompt change, no provider change, no specification change, no retries of any of the 5 planned calls. CP-MVP2-04: NOT STARTED.

This report does not make an implementation decision. It ends after the 5-call characterization, evidence, regression, and Git commit/push, per this task's own scope boundary. The next action is Human + Di's independent review of both this study and the prior single-call investigation to decide whether a governed-resilience change (if any) is warranted.
