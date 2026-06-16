# path: ./tools/run_sr_fx_runtime_control_clearance_runbook_report.py
# desc: Broker-free runtime_control clearance/runbook report from S52 evidence. Read-only; non-authorizing; no broker calls/no mode changes.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_runtime_control_clearance_runbook_report"
REPORT_VERSION = "runtime_control_clearance_runbook_report.v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


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


def _actions_for_blockers(blockers: list[str], evidence: Mapping[str, Any]) -> list[str]:
    actions: list[str] = []
    propagation = _as_dict(_as_dict(evidence.get("evidence")).get("propagation"))
    handoff_actions = _as_list(propagation.get("handoff_next_actions"))
    actions.extend(handoff_actions)

    if any(item.startswith("kill_switch_action:") for item in blockers) or "kill_switch_active" in blockers:
        actions.append("keep_autotrade_halted_until_kill_switch_is_cleared_by_protocol")
        actions.append("clear_or_acknowledge_kill_switch_with_explicit_human_protocol")
        actions.append("rerun_runtime_control_sequence_after_kill_switch_clearance")
    if "heartbeat_stale" in blockers or "heartbeat_missing" in blockers:
        actions.append("observe_fresh_runtime_heartbeat_and_rerun_runtime_control_sequence")
    if "open_incident_present" in blockers:
        actions.append("resolve_or_explicitly_close_runtime_incident_before_live_review")
    if not blockers:
        actions.append("record_runtime_control_clearance_evidence_for_final_human_review")
    actions.append("rerun_s51_wrapper_and_s52_evidence_report_after_any_clearance_work")
    actions.append("require_final_human_review_before_any_mode_change")
    return _dedupe(actions)


def build_clearance_runbook_report(*, evidence_report: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    evidence = dict(evidence_report)
    runtime_blockers = _as_list(evidence.get("runtime_control_blocked_by"))
    evidence_body = _as_dict(evidence.get("evidence"))
    heartbeat = _as_dict(evidence_body.get("heartbeat"))
    kill_switch = _as_dict(evidence_body.get("kill_switch"))
    incidents = _as_dict(evidence_body.get("incidents"))
    command_ledger = _as_dict(evidence_body.get("command_ledger"))
    propagation = _as_dict(evidence_body.get("propagation"))
    checks = _as_dict(evidence.get("checks"))

    evidence_ok = evidence.get("ok") is True
    runtime_control_clear = evidence.get("runtime_control_clear") is True and not runtime_blockers
    safety_ok = (
        evidence.get("read_only") is True
        and evidence.get("would_send_to_broker") is False
        and evidence.get("mode_changed") is False
        and evidence.get("autotrade_resume_authorized") is False
    )
    prerequisites_met = bool(evidence_ok and runtime_control_clear and safety_ok)
    operator_actions = _actions_for_blockers(runtime_blockers, evidence)

    clearance_state = (
        "runtime_control_clearance_prerequisites_met_not_authorized"
        if prerequisites_met
        else "runtime_control_clearance_blocked_not_authorized"
    )
    blocked_by = [] if prerequisites_met else _dedupe([
        "runtime_control_clearance_prerequisites_not_met",
        *runtime_blockers,
    ])

    return {
        "ok": bool(evidence_ok and safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "clearance_state": clearance_state,
        "runtime_control_clearance_prerequisites_met": prerequisites_met,
        "runtime_control_clear": runtime_control_clear,
        "runtime_control_blocked_by": runtime_blockers,
        "operator_required_actions": operator_actions,
        "operator_runbook": {
            "summary": "Runtime-control evidence is converted into operator prerequisites only; this report never authorizes mode change, Armed Dry Run, Live, or broker execution.",
            "clearance_prerequisites": {
                "evidence_report_ok": evidence_ok,
                "runtime_control_clear": runtime_control_clear,
                "no_runtime_control_blockers": not runtime_blockers,
                "read_only_non_authorizing_contract": safety_ok,
                "final_review_runtime_control_present": bool(checks.get("runtime_control_present_in_final_review")),
                "handoff_runtime_control_present": bool(checks.get("runtime_control_present_in_handoff")),
            },
            "runtime_evidence": {
                "heartbeat": {
                    "fresh": heartbeat.get("fresh"),
                    "component": heartbeat.get("component"),
                    "observed_at": heartbeat.get("observed_at"),
                    "age_sec": heartbeat.get("age_sec"),
                    "max_age_sec": heartbeat.get("max_age_sec"),
                    "blocked_by": _as_list(heartbeat.get("blocked_by")),
                },
                "kill_switch": {
                    "active": bool(kill_switch.get("active")),
                    "action": kill_switch.get("action"),
                    "reason": kill_switch.get("reason"),
                    "source": kill_switch.get("source"),
                    "command_id": kill_switch.get("command_id"),
                },
                "incidents": {
                    "count": incidents.get("count"),
                    "open_count": incidents.get("open_count"),
                },
                "command_ledger": {
                    "exists": command_ledger.get("exists"),
                    "latest_command_id": command_ledger.get("latest_command_id"),
                    "latest_command_type": command_ledger.get("latest_command_type"),
                    "latest_target": command_ledger.get("latest_target"),
                    "latest_accepted": command_ledger.get("latest_accepted"),
                    "read_only": command_ledger.get("read_only", True),
                    "would_send_to_broker": command_ledger.get("would_send_to_broker", False),
                },
                "propagation": {
                    "final_review_blocked_by": _as_list(propagation.get("final_review_blocked_by")),
                    "handoff_runtime_blocked_by": _as_list(propagation.get("handoff_runtime_blocked_by")),
                    "handoff_next_actions": _as_list(propagation.get("handoff_next_actions")),
                },
            },
        },
        "checks": {
            "evidence_report_ok": evidence_ok,
            "runtime_control_clearance_prerequisites_met": prerequisites_met,
            "runtime_control_clear": runtime_control_clear,
            "no_runtime_control_blockers": not runtime_blockers,
            "heartbeat_fresh": heartbeat.get("fresh") is True,
            "kill_switch_inactive": kill_switch.get("active") is False,
            "no_open_incidents": int(incidents.get("open_count") or 0) == 0,
            "final_review_runtime_control_present": bool(checks.get("runtime_control_present_in_final_review")),
            "handoff_runtime_control_present": bool(checks.get("runtime_control_present_in_handoff")),
            "read_only_no_broker_non_authorizing": safety_ok,
        },
        "blocked_by": blocked_by,
        "warnings": [
            "clearance_prerequisites_are_not_mode_change_authorization",
            "armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "final_human_review_required_before_any_mode_change",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "armed_dry_run_authorized": False,
            "live_authorized": False,
            "final_human_review_required": True,
        },
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
        "autotrade_resume_authorized": False,
        "armed_dry_run_authorized": False,
        "live_authorized": False,
        "final_human_review_required": True,
        "source_report_version": evidence.get("report_version"),
        "source_generated_at": evidence.get("generated_at"),
        "paths": dict(evidence.get("paths") or {}),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free runtime_control clearance/runbook report from S52 evidence JSON.")
    parser.add_argument("--evidence-report", required=True, help="Path to S52 operational evidence report JSON.")
    parser.add_argument("--out", default="", help="Optional clearance/runbook report output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        evidence = _read_json(Path(args.evidence_report))
        payload = build_clearance_runbook_report(evidence_report=evidence)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["runtime_control_clearance_runbook_report_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "armed_dry_run_authorized": False,
                "live_authorized": False,
                "final_human_review_required": True,
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "armed_dry_run_authorized": False,
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
