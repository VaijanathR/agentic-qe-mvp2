"""
Agentic QE Orchestration -- CLI entry point (governing instruction
sec. 49).

Usage:
    python -m orchestration.cli orchestrate-requirement REQ-BRW-01 --dry-run
    python -m orchestration.cli orchestrate-requirement REQ-BRW-01 --real
    python -m orchestration.cli orchestrate-batch REQ-BRW-01 REQ-SRCH-01 REQ-WISH-01 --dry-run
    python -m orchestration.cli orchestrate-batch REQ-BRW-01 REQ-SRCH-01 REQ-WISH-01 --real
    python -m orchestration.cli orchestrate-capability "Wishlist" "Search" --dry-run
    python -m orchestration.cli orchestrate-capability "Wishlist" "Search" --real
    python -m orchestration.cli resume ORCH-... --real
    python -m orchestration.cli orchestrate-regression REQ-BRW-01
    python -m orchestration.cli orchestrate-testcase REQ-BRW-01
    python -m orchestration.cli orchestrate-performance REQ-BRW-01
    python -m orchestration.cli show-status ORCH-...
    python -m orchestration.cli show-traceability REQ-BRW-01
    python -m orchestration.cli show-approvals
    python -m orchestration.cli show-evidence ORCH-...

REAL_EXECUTION mode (`--real`) requires a real Windows Playwright
environment (this repository's `.venv`) -- it launches a real Chromium
browser. DRY_RUN mode (`--dry-run`, the default) never touches the SUT.
"""
from __future__ import annotations

import argparse
import json
import sys

from orchestration import impact, requirement_intelligence, risk, test_strategy, traceability_orchestration
from orchestration.approval import ApprovalDecision
from orchestration.execution_planning import ExecutionMode
from orchestration.journal import JOURNAL_ROOT, list_journal_ids, load_journal
from orchestration.orchestrator import Orchestrator


def _print(obj) -> None:
    """Real bug found and fixed this task: the default Windows console
    codepage (cp1252) cannot encode every real character this
    orchestrator's own text can legitimately contain (e.g. a real
    Unicode arrow in RCA/replanning rationale text) -- `print()`'s
    default `sys.stdout` then raises `UnicodeEncodeError` and the whole
    CLI invocation crashes AFTER a real orchestration run has already
    completed and been persisted, losing only the final printed summary,
    never any real evidence. Writes UTF-8 bytes directly to the real
    stdout buffer instead, sidestepping the console codepage entirely."""
    text = json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    sys.stdout.buffer.write((text + "\n").encode("utf-8"))
    sys.stdout.flush()


def cmd_orchestrate_requirement(args: argparse.Namespace) -> int:
    mode = ExecutionMode.REAL_EXECUTION if args.real else ExecutionMode.DRY_RUN
    orchestrator = Orchestrator()

    page, browser_version = None, None
    if mode == ExecutionMode.REAL_EXECUTION:
        from playwright.sync_api import sync_playwright

        from automation.playwright.config import DEFAULT_CONFIG

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=DEFAULT_CONFIG.headless)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(DEFAULT_CONFIG.default_timeout_ms)
            browser_version = browser.version
            result = orchestrator.run(
                args.requirement_id, mode=mode, page=page, browser_version=browser_version,
                controlled_failure=args.controlled_failure, run_performance=args.performance,
            )
            context.close()
            browser.close()
    else:
        result = orchestrator.run(args.requirement_id, mode=mode)

    _print(result.to_dict())
    return 0 if result.final_status not in ("BLOCKED",) else 1


def cmd_orchestrate_batch(args: argparse.Namespace) -> int:
    mode = ExecutionMode.REAL_EXECUTION if args.real else ExecutionMode.DRY_RUN
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(args.requirement_ids, mode=mode, real_parallel_workers=args.workers, force_full_regression=args.full_regression)
    _print(result.to_dict())
    return 0 if result.final_status not in ("BLOCKED",) else 1


def cmd_orchestrate_capability(args: argparse.Namespace) -> int:
    from orchestration.capability_discovery import discover_requirement_ids

    requirement_ids = discover_requirement_ids(args.capabilities)
    if not requirement_ids:
        print(f"No real requirements discovered for capabilities {args.capabilities}", file=sys.stderr)
        return 1
    mode = ExecutionMode.REAL_EXECUTION if args.real else ExecutionMode.DRY_RUN
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(requirement_ids, mode=mode, real_parallel_workers=args.workers)
    _print({"capabilities": args.capabilities, "discovered_requirement_ids": requirement_ids, **result.to_dict()})
    return 0 if result.final_status not in ("BLOCKED",) else 1


def cmd_resume(args: argparse.Namespace) -> int:
    mode = ExecutionMode.REAL_EXECUTION if args.real else ExecutionMode.DRY_RUN
    orchestrator = Orchestrator()
    outcome = orchestrator.resume_batch(args.orchestration_id, mode=mode)
    _print(outcome)
    return 0 if outcome.get("resumed") is not False or outcome["plan"]["resume_state"] != "NOT_FOUND" else 1


def cmd_orchestrate_testcase(args: argparse.Namespace) -> int:
    _print(test_strategy.determine_strategy(args.requirement_id))
    return 0


def cmd_orchestrate_performance(args: argparse.Namespace) -> int:
    from orchestration import performance_execution

    if args.real:
        _print(performance_execution.execute_real(args.requirement_id))
    else:
        _print({
            "requirement_id": args.requirement_id,
            "performance_relevant": performance_execution.is_performance_relevant(args.requirement_id),
            "note": "DRY_RUN -- pass --real to invoke real Windows JMeter.",
        })
    return 0


def cmd_orchestrate_regression(args: argparse.Namespace) -> int:
    from orchestration import regression

    impact_result = impact.analyze(args.requirement_id)
    risk_result = risk.assess(args.requirement_id)
    _print(regression.select_scope(impact_result, risk_result, force_full=args.full))
    return 0


def cmd_show_status(args: argparse.Namespace) -> int:
    if args.orchestration_id:
        journal = load_journal(args.orchestration_id)
        if journal is None:
            print(f"No journal found for {args.orchestration_id}", file=sys.stderr)
            return 1
        _print(journal)
    else:
        _print({"journal_ids": list_journal_ids()})
    return 0


def cmd_show_traceability(args: argparse.Namespace) -> int:
    chain = traceability_orchestration.build_chain(args.requirement_id)
    validation = traceability_orchestration.validate(chain)
    _print({"chain": chain, "validation": validation})
    return 0


def cmd_show_approvals(args: argparse.Namespace) -> int:
    ids = list_journal_ids()
    approvals = {}
    for jid in ids:
        j = load_journal(jid)
        if j and j.get("approval_state"):
            approvals[jid] = j["approval_state"]
    _print(approvals)
    return 0


def cmd_show_evidence(args: argparse.Namespace) -> int:
    journal = load_journal(args.orchestration_id)
    if journal is None:
        print(f"No journal found for {args.orchestration_id}", file=sys.stderr)
        return 1
    evidence = [e for e in journal["entries"] if e.get("evidence_references")]
    _print(evidence)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orchestration.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("orchestrate-requirement")
    p1.add_argument("requirement_id")
    p1.add_argument("--real", action="store_true", help="REAL_EXECUTION mode (default: DRY_RUN)")
    p1.add_argument("--dry-run", action="store_true", help="DRY_RUN mode (default)")
    p1.add_argument("--controlled-failure", action="store_true", help="Drive the CONTROLLED TEST FAILURE fixture instead of the real business action.")
    p1.add_argument("--performance", action="store_true", help="Also run real JMeter performance execution if the requirement is performance-relevant.")
    p1.set_defaults(func=cmd_orchestrate_requirement)

    p2 = sub.add_parser("orchestrate-change")
    p2.add_argument("requirement_id")
    p2.add_argument("--real", action="store_true")
    p2.set_defaults(func=cmd_orchestrate_requirement)

    pb = sub.add_parser("orchestrate-batch")
    pb.add_argument("requirement_ids", nargs="+", help="One or more requirement IDs to orchestrate together.")
    pb.add_argument("--real", action="store_true", help="REAL_EXECUTION mode (default: DRY_RUN)")
    pb.add_argument("--dry-run", action="store_true", help="DRY_RUN mode (default)")
    pb.add_argument("--workers", type=int, default=2, help="Real local pytest -n worker count for the SAFE_PARALLEL/PREREQUISITE_DEPENDENT group (default 2).")
    pb.add_argument("--full-regression", action="store_true", help="Force FULL_REGRESSION scope instead of intelligent selection.")
    pb.set_defaults(func=cmd_orchestrate_batch)

    pc = sub.add_parser("orchestrate-capability")
    pc.add_argument("capabilities", nargs="+", help="One or more real capability categories to dynamically discover requirements for.")
    pc.add_argument("--real", action="store_true")
    pc.add_argument("--dry-run", action="store_true")
    pc.add_argument("--workers", type=int, default=2)
    pc.set_defaults(func=cmd_orchestrate_capability)

    pr = sub.add_parser("resume")
    pr.add_argument("orchestration_id")
    pr.add_argument("--real", action="store_true")
    pr.set_defaults(func=cmd_resume)

    p3 = sub.add_parser("orchestrate-regression")
    p3.add_argument("requirement_id")
    p3.add_argument("--full", action="store_true")
    p3.set_defaults(func=cmd_orchestrate_regression)

    p4 = sub.add_parser("orchestrate-testcase")
    p4.add_argument("requirement_id")
    p4.set_defaults(func=cmd_orchestrate_testcase)

    p5 = sub.add_parser("orchestrate-performance")
    p5.add_argument("requirement_id")
    p5.add_argument("--real", action="store_true")
    p5.set_defaults(func=cmd_orchestrate_performance)

    p6 = sub.add_parser("show-status")
    p6.add_argument("orchestration_id", nargs="?")
    p6.set_defaults(func=cmd_show_status)

    p7 = sub.add_parser("show-traceability")
    p7.add_argument("requirement_id")
    p7.set_defaults(func=cmd_show_traceability)

    p8 = sub.add_parser("show-approvals")
    p8.set_defaults(func=cmd_show_approvals)

    p9 = sub.add_parser("show-evidence")
    p9.add_argument("orchestration_id")
    p9.set_defaults(func=cmd_show_evidence)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
