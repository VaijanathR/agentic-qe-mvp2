"""
CP-MVP2-06 — real Playwright/Chromium execution engine.

Per the frozen specification secs. 5/7/8/9: browser scope is fixed to
`chromium-headless`; this module performs GENUINE Playwright automation
against the real SUT — it is not a mock. Unit/integration tests of this
module (tests/test_cp_mvp2_06_*.py) mock the `playwright` import
boundary explicitly and are always labeled as such; this module itself
never contains a stub/mock code path — when it runs, it always attempts
a real browser launch.

Reuses the `playwright` package already installed in this project's
environment (used by CP-MVP2-01's own discovery scripts) — no new
browser-automation dependency is introduced.
"""
from __future__ import annotations

import datetime
from typing import Dict, List, Optional, Tuple

from automation.schema import ActionType, PlaywrightArtifact, PlaywrightStep, SyncStrategy
from execution.evidence import EvidenceManager, redact_field_value
from execution.schema import StepResult, StepStatus


class BrowserLaunchError(RuntimeError):
    """Raised when the real browser/context/page could not be started."""


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class BrowserExecutor:
    """One instance is used for one execution. `headless` is always
    True for MVP2 (spec sec. 5) — the constructor accepts it only so
    tests can assert the value actually passed, never to permit a
    non-headless MVP2 execution silently."""

    def __init__(self, sut_base_url: str, timeout_ms: int = 30000, headless: bool = True):
        self.sut_base_url = sut_base_url
        self.timeout_ms = timeout_ms
        self.headless = headless

    def check_infrastructure(self, evidence: EvidenceManager) -> Dict:
        """A pure environment/infrastructure capability check -- NOT tied
        to any CP-MVP2-05 artifact and NEVER reported as an artifact's
        PASS/FAIL. Launches a real browser, navigates to the SUT's home
        page, captures a real screenshot, and returns real, observed
        diagnostic facts. Used only to honestly characterize whether the
        environment itself can support execution (spec sec. 16) -- this
        is distinct from, and must never be conflated with, executing a
        governed business scenario (spec sec. 26)."""
        import playwright.sync_api as pw_sync

        start = _now()
        try:
            with pw_sync.sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                try:
                    version = browser.version
                    context = browser.new_context()
                    page = context.new_page()
                    page.set_default_timeout(self.timeout_ms)
                    response = page.goto(self.sut_base_url, wait_until="domcontentloaded")
                    status_code = response.status if response else None
                    final_url = page.url
                    shot_path = evidence.screenshot_path("infrastructure_check.png")
                    page.screenshot(path=str(shot_path))
                    context.close()
                finally:
                    browser.close()
        except Exception as exc:
            end = _now()
            return {
                "check": "browser_infrastructure",
                "passed": False,
                "error": str(exc),
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            }
        end = _now()
        return {
            "check": "browser_infrastructure",
            "passed": True,
            "browser": f"chromium/{version}",
            "http_status": status_code,
            "final_url": final_url,
            "screenshot": evidence.screenshot_relative("infrastructure_check.png"),
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "duration_seconds": (end - start).total_seconds(),
        }

    def run_steps(
        self,
        artifact: PlaywrightArtifact,
        field_values: Dict[str, object],
        evidence: EvidenceManager,
    ) -> Tuple[List[StepResult], Optional[str]]:
        """Launches a REAL browser and executes every step in order,
        stopping at the first FAIL/ERROR (a load-bearing failure makes
        the rest of the sequence meaningless -- later steps are recorded
        NOT_EXECUTED, never silently omitted). Returns
        (step_results, resolved_browser_string). Raises
        BrowserLaunchError if the browser/context/page itself could not
        be started -- this is a design distinct from a step failure."""
        import playwright.sync_api as pw_sync

        step_results: List[StepResult] = []
        resolved_browser: Optional[str] = None

        try:
            with pw_sync.sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                resolved_browser = f"chromium/{browser.version}"
                try:
                    context = browser.new_context()
                    page = context.new_page()
                    page.set_default_timeout(self.timeout_ms)
                    stopped = False
                    for step in artifact.steps:
                        if stopped:
                            step_results.append(self._not_executed(step))
                            continue
                        result = self._execute_step(page, step, field_values, evidence)
                        step_results.append(result)
                        if result.status in (StepStatus.FAIL, StepStatus.ERROR):
                            stopped = True
                    context.close()
                finally:
                    browser.close()
        except Exception as exc:
            raise BrowserLaunchError(str(exc)) from exc

        return step_results, resolved_browser

    @staticmethod
    def _not_executed(step: PlaywrightStep) -> StepResult:
        return StepResult(
            step_order=step.step_order,
            action_type=step.action_type,
            target_locator_reference=step.locator.value if step.locator else None,
            status=StepStatus.NOT_EXECUTED,
            observed_result="skipped: a prior load-bearing step failed",
        )

    def _execute_step(self, page, step: PlaywrightStep, field_values: Dict[str, object], evidence: EvidenceManager) -> StepResult:
        start = _now()
        status = StepStatus.PASS
        observed: Optional[str] = None
        error_info: Optional[str] = None
        locator_ref = step.locator.value if step.locator else None

        import playwright.sync_api as pw_sync

        try:
            if step.action_type == ActionType.NAVIGATE:
                page.goto(self.sut_base_url, wait_until="domcontentloaded")
                observed = f"navigated to {page.url}"
            elif step.action_type == ActionType.FILL:
                value = field_values.get(step.input_mapping)
                page.fill(locator_ref, str(value))
                observed = f"filled field {step.input_mapping!r} -> {redact_field_value(step.input_mapping, value)}"
            elif step.action_type == ActionType.SELECT:
                value = field_values.get(step.input_mapping)
                page.select_option(locator_ref, label=str(value))
                observed = f"selected field {step.input_mapping!r} -> {redact_field_value(step.input_mapping, value)}"
            elif step.action_type == ActionType.CLICK:
                page.click(locator_ref)
                observed = "clicked"
            elif step.action_type == ActionType.WAIT:
                if step.synchronization_strategy == SyncStrategy.WAIT_FOR_NETWORK_IDLE:
                    page.wait_for_load_state("networkidle")
                elif step.synchronization_strategy == SyncStrategy.WAIT_FOR_VISIBLE and locator_ref:
                    page.wait_for_selector(locator_ref, state="visible")
                observed = "synchronization wait complete"
            elif step.action_type == ActionType.ASSERT:
                observed = "assertion evaluation is performed separately against final page state"
            else:
                status = StepStatus.ERROR
                error_info = f"Unsupported action_type: {step.action_type!r}"
        except pw_sync.TimeoutError as exc:
            status = StepStatus.FAIL
            error_info = f"TIMEOUT: {exc}"
        except Exception as exc:
            status = StepStatus.ERROR
            error_info = str(exc)

        end = _now()
        evidence_refs: List[str] = []
        if status in (StepStatus.FAIL, StepStatus.ERROR):
            try:
                shot_name = f"step_{step.step_order}_failure.png"
                page.screenshot(path=str(evidence.screenshot_path(shot_name)))
                evidence_refs.append(evidence.screenshot_relative(shot_name))
            except Exception:
                pass  # evidence capture best-effort; never fabricated if it fails

        return StepResult(
            step_order=step.step_order,
            action_type=step.action_type,
            target_locator_reference=locator_ref,
            status=status,
            start_time=start.isoformat(),
            end_time=end.isoformat(),
            duration_seconds=(end - start).total_seconds(),
            observed_result=observed,
            evidence_references=evidence_refs,
            error_information=error_info,
        )
