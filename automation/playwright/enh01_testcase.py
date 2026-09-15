"""
Post-MVP2 Enhancement 01 -- a NEW, explicit, fidelity-appropriate testcase
for REQ-REG-01, created because the historical `TC-REQ-REG-01-01` (frozen,
MVP2 baseline `33b9946`) carries only the disclosed generic placeholder
steps ("Perform the action described by the approved requirement." /
"Observe the resulting system behavior."). Per the governing instruction
sec. 18: "If an existing testcase is too generic for reliable automation:
do not silently rewrite the historical testcase. Create a post-MVP
enhancement artifact." This IS that artifact -- `TC-REQ-REG-01-01` itself
is never modified, edited, or reinterpreted anywhere in this enhancement.

Business steps below are grounded directly in REQ-REG-01's own Approved
SRS acceptance criteria (`requirements/MVP2_SRS_v1.0_APPROVED.md` line 94):
"Given all fields blank, when submitted, then all required-field messages
show and no account is created." Nothing here was invented beyond that
approved text. This scenario is also deliberately non-state-mutating (no
real account is ever created by submitting blank fields), consistent with
this project's established practice of avoiding repeated, real,
state-mutating traffic against the shared, public, third-party SUT.
"""
from __future__ import annotations

ENH01_TC_REQ_REG_01_BLANK_VALIDATION = {
    "testcase_id": "ENH01-TC-REQ-REG-01-BLANK-VALIDATION",
    "requirement_ids": ["REQ-REG-01"],
    "title": "Registration rejects submission with all mandatory fields blank",
    "preconditions": [
        "The real SUT registration page (https://demowebshop.tricentis.com/register) is reachable.",
    ],
    "business_steps": [
        "Navigate to the home page.",
        "Select the 'Register' navigation link.",
        "Leave First name blank.",
        "Leave Last name blank.",
        "Leave Email blank.",
        "Leave Password blank.",
        "Leave Confirm password blank.",
        "Submit the registration form.",
        "Observe the resulting page for per-field 'is required' validation messages.",
    ],
    "expected_result": (
        "REQ-REG-01 (Approved SRS): all required-field validation messages are shown and "
        "no account is created."
    ),
    "test_type": "EXCEPTIONAL",
    "priority": "MEDIUM",
    "dataset_references": ["TD-TC-REQ-REG-01-01-02", "TD-TC-REQ-REG-01-01-06"],
    "historical_testcase_reference": "TC-REQ-REG-01-01 (frozen MVP2 baseline 33b9946; not modified by this artifact)",
    "status": "NEW -- POST-MVP2 ENHANCEMENT 01",
}
