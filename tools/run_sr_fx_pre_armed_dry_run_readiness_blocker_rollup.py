# path: ./tools/run_sr_fx_pre_armed_dry_run_readiness_blocker_rollup.py
# desc: Broker-free Pre-Armed Dry Run readiness blocker rollup from runtime_control clearance and final/handoff artifacts. Informational only; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_readiness_blocker_rollup"
REPORT_VERSION = "pre_armed_dry_run_readiness_blocker_rollup.v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def _read_optional(raw: Any) -> dict[str, Any] | None:
    text = str(raw or "").strip()
    if not text:
        return None
    path = Path(text)
    if not path.exists():
        return None
    return _read_json(path)


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _nested(payload: Mapping[str, Any] | None, key: str) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    value = payload.get(key)
    return dict(value) if isinstance(value, Mapping) else {}


def _add_prefixed(out: list[str], prefix: str, values: list[str]) -> None:
    for value in values:
        out.append(f"{prefix}:{value}")


def build_pre_armed_dry_run_readiness_blocker_rollup(*, clearance_runbook: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    clearance = dict(clearance_runbook)
    paths = _as_dict(clearance.get("paths"))
    final_review = _read_optional(paths.get("final_review_package"))
    handoff = _read_optional(paths.get("data_ui_gate_handoff"))
    final_checks = _as_dict(final_review.get("checks")) if isinstance(final_review, Mapping) else {}
    handoff_boundary = _as_dict(handoff.get("execution_boundary")) if isinstance(handoff, Mapping) else {}

    clearance_blockers = _as_list(clearance.get("blocked_by"))
    runtime_blockers = _as_list(clearance.get("runtime_control_blocked_by"))
    final_blockers = _as_list(final_review.get("execution_boundary_blocked_by")) if isinstance(final_review, Mapping) else []
    handoff_blockers = _as_list(handoff_boundary.get("blocked_by"))
    handoff_actions = _as_list(handoff_boundary.get("next_actions"))
    runbook_actions = _as_list(clearance.get("operator_required_actions"))

    blocker_rollup: list[str] = []
    _add_prefixed(blocker_rollup, "runtime_control", runtime_blockers)
    _add_prefixed(blocker_rollup, "clearance_runbook", clearance_blockers)
    _add_prefixed(blocker_rollup, "final_review", final_blockers)
    _add_prefixed(blocker_rollup, "handoff", handoff_blockers)
    if not final_review:
        blocker_rollup.append("final_review:missing")
    if not handoff:
        blocker_rollup.append("handoff:missing")
    if final_checks and not bool(final_checks.get("live_readiness_contract_ready")):
        blocker_rollup.append("live_readiness_contract:not_ready")
    if final_checks and not bool(final_checks.get("execution_safety_harness_ready")):
        blocker_rollup.append("execution_safety_harness:not_ready")
    if final_checks and not bool(final_checks.get("pre_live_blocker_report_clear")):
        blocker_rollup.append("pre_live_blocker_report:not_clear")
    if final_checks and not bool(final_checks.get("runtime_control_clear")):
        blocker_rollup.append("runtime_control:not_clear")
    blocker_rollup.append("armed_dry_run_authorization:not_in_this_slice")
    blocker_rollup.append("human_review:required_before_any_mode_change")
    blocker_rollup = _dedupe(blocker_rollup)

    operator_actions = _dedupe([
        *handoff_actions,
        *runbook_actions,
        "review_pre_armed_dry_run_blocker_rollup_with_human_operator",
        "rerun_s51_s52_s53_s54_chain_after_any_clearance_work",
        "require_final_human_review_before_any_mode_change",
    ])

    clearance_met = bool(clearance.get("runtime_control_clearance_prerequisites_met"))
    final_present = final_review is not None
    handoff_present = handoff is not None
    safety_contract_ok = (
        clearance.get("read_only") is True
        and clearance.get("would_send_to_broker") is False
        and clearance.get("mode_changed") is False
        and clearance.get("autotrade_resume_authorized") is False
        and clearance.get("armed_dry_run_authorized") is False
        and clearance.get("live_authorized") is False
    )
    # S54 is a rollup/review packet only. Even if prerequisites look good, it does not authorize Armed Dry Run.
    ready_for_human_pre_armed_review = bool(clearance.get("ok") is True and final_present and handoff_present and safety_contract_ok)

    return {
        "ok": ready_for_human_pre_armed_review,
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": "pre_armed_dry_run_readiness_blocker_rollup_complete_not_authorized" if ready_for_human_pre_armed_review else "pre_armed_dry_run_readiness_blocker_rollup_incomplete_not_authorized",
        "pre_armed_dry_run_review_ready": ready_for_human_pre_armed_review,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
        "autotrade_resume_authorized": False,
        "mode_changed": False,
        "read_only": True,
        "would_send_to_broker": False,
        "final_human_review_required": True,
        "runtime_control_clearance_prerequisites_met": clearance_met,
        "blocker_rollup": blocker_rollup,
        "operator_required_actions": operator_actions,
        "source_summary": {
            "clearance_state": clearance.get("clearance_state"),
            "clearance_report_version": clearance.get("report_version"),
            "final_review_present": final_present,
            "handoff_present": handoff_present,
            "final_review_execution_boundary_clear": bool(final_review.get("execution_boundary_clear")) if isinstance(final_review, Mapping) else False,
            "handoff_execution_boundary_clear": bool(handoff_boundary.get("clear")),
            "live_readiness_contract_ready": bool(final_checks.get("live_readiness_contract_ready")),
            "execution_safety_harness_ready": bool(final_checks.get("execution_safety_harness_ready")),
            "pre_live_blocker_report_clear": bool(final_checks.get("pre_live_blocker_report_clear")),
            "runtime_control_clear": bool(final_checks.get("runtime_control_clear")),
        },
        "checks": {
            "clearance_runbook_ok": clearance.get("ok") is True,
            "runtime_control_clearance_prerequisites_met": clearance_met,
            "final_review_present": final_present,
            "handoff_present": handoff_present,
            "readiness_blocker_rollup_present": bool(blocker_rollup),
            "operator_actions_present": bool(operator_actions),
            "read_only_no_broker_non_authorizing": safety_contract_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "pre_armed_dry_run_review_packet_is_informational_only",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "broker_send_remains_disabled",
            "final_human_review_required_before_any_mode_change",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "final_human_review_required": True,
        },
        "paths": paths,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run readiness blocker rollup from S53 clearance/runbook JSON.")
    parser.add_argument("--clearance-runbook", required=True, help="Path to S53 clearance/runbook JSON.")
    parser.add_argument("--out", default="", help="Optional rollup output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        clearance = _read_json(Path(args.clearance_runbook))
        payload = build_pre_armed_dry_run_readiness_blocker_rollup(clearance_runbook=clearance)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_readiness_blocker_rollup_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "pre_armed_dry_run_authorized": False,
                "live_authorized": False,
                "final_human_review_required": True,
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "final_human_review_required": True,
        }
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
