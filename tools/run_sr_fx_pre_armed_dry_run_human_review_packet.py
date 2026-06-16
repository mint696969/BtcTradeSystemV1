# path: ./tools/run_sr_fx_pre_armed_dry_run_human_review_packet.py
# desc: Broker-free Pre-Armed Dry Run human review packet from S54 readiness rollup. Informational only; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_human_review_packet"
REPORT_VERSION = "pre_armed_dry_run_human_review_packet.v1"


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


def _has_token(items: list[str], token: str) -> bool:
    return any(token in item for item in items)


def _review_item(item_id: str, title: str, status: str, evidence: Any, required_action: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "title": title,
        "status": status,
        "evidence": evidence,
        "required_action": required_action,
    }


def build_pre_armed_dry_run_human_review_packet(*, readiness_rollup: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    rollup = dict(readiness_rollup)
    blockers = _as_list(rollup.get("blocker_rollup"))
    actions = _as_list(rollup.get("operator_required_actions"))
    source_summary = _as_dict(rollup.get("source_summary"))
    checks = _as_dict(rollup.get("checks"))
    safety_ok = (
        rollup.get("read_only") is True
        and rollup.get("would_send_to_broker") is False
        and rollup.get("mode_changed") is False
        and rollup.get("autotrade_resume_authorized") is False
        and rollup.get("pre_armed_dry_run_authorized") is False
        and rollup.get("live_authorized") is False
    )
    runtime_clearance_met = bool(rollup.get("runtime_control_clearance_prerequisites_met"))
    runtime_blockers = [item for item in blockers if item.startswith("runtime_control:") or item.startswith("clearance_runbook:")]
    remaining_execution_blockers = [
        item for item in blockers
        if item.startswith("final_review:")
        or item.startswith("handoff:")
        or item in {"live_readiness_contract:not_ready", "execution_safety_harness:not_ready", "pre_live_blocker_report:not_clear"}
    ]
    explicit_not_in_slice = _has_token(blockers, "armed_dry_run_authorization:not_in_this_slice")
    human_review_required = _has_token(blockers, "human_review:required_before_any_mode_change") or "require_final_human_review_before_any_mode_change" in actions

    review_items = [
        _review_item(
            "source_rollup_present",
            "S54 readiness blocker rollup is present and parseable",
            "pass" if rollup.get("ok") is True else "block",
            {"source_report_version": rollup.get("report_version"), "decision": rollup.get("decision")},
            "rerun_s54_pre_armed_dry_run_readiness_blocker_rollup",
        ),
        _review_item(
            "runtime_control_clearance",
            "Runtime-control clearance prerequisites are visible",
            "pass" if runtime_clearance_met else "block",
            {"runtime_control_clearance_prerequisites_met": runtime_clearance_met, "runtime_blockers": runtime_blockers},
            "clear_runtime_control_heartbeat_kill_switch_incident_blockers_and_rerun_s51_s55_chain",
        ),
        _review_item(
            "execution_boundary_blockers",
            "Remaining execution-boundary blockers are visible before any Armed Dry Run decision",
            "review_required" if remaining_execution_blockers else "pass",
            {"remaining_execution_blockers": remaining_execution_blockers},
            "resolve_or_explicitly_accept_each_remaining_execution_blocker_before_any_authorization_request",
        ),
        _review_item(
            "operator_actions_review",
            "Operator action chain is visible and must be completed outside this packet",
            "review_required" if actions else "block",
            {"operator_required_actions": actions},
            "complete_required_actions_then_rerun_s51_s55_chain",
        ),
        _review_item(
            "non_authorization_boundary",
            "This packet does not authorize Pre-Armed Dry Run, Live, broker send, or mode change",
            "pass" if safety_ok and explicit_not_in_slice else "block",
            {
                "pre_armed_dry_run_authorized": False,
                "live_authorized": False,
                "autotrade_resume_authorized": False,
                "mode_changed": False,
                "explicit_not_in_this_slice": explicit_not_in_slice,
            },
            "do_not_apply_mode_change_from_this_packet",
        ),
        _review_item(
            "human_review_required",
            "Final human review remains required before any mode change",
            "pass" if human_review_required else "block",
            {"human_review_required": human_review_required},
            "record_separate_human_approval_in_a_later_authorization_slice_only_after_all_blockers_clear",
        ),
    ]
    blocking_items = [item["id"] for item in review_items if item["status"] == "block"]
    review_required_items = [item["id"] for item in review_items if item["status"] == "review_required"]
    packet_ok = bool(rollup.get("ok") is True and safety_ok)
    # A blocked runtime_control case should still produce a valid informational packet.
    # Readiness is separate from packet generation success and remains false when blockers exist.
    packet_ready = bool(packet_ok and not blocking_items)

    return {
        "ok": packet_ok,
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": "pre_armed_dry_run_human_review_packet_ready_not_authorized" if packet_ready else "pre_armed_dry_run_human_review_packet_blocked_not_authorized",
        "human_review_packet_ready": packet_ready,
        "human_review_required": True,
        "human_review_recorded": False,
        "operator_acknowledgement_recorded": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
        "autotrade_resume_authorized": False,
        "mode_changed": False,
        "read_only": True,
        "would_send_to_broker": False,
        "runtime_control_clearance_prerequisites_met": runtime_clearance_met,
        "review_items": review_items,
        "blocking_review_items": blocking_items,
        "review_required_items": review_required_items,
        "blocker_rollup": blockers,
        "runtime_control_blockers": runtime_blockers,
        "remaining_execution_blockers": remaining_execution_blockers,
        "operator_required_actions": actions,
        "human_acknowledgement_checklist": [
            "review_all_runtime_control_evidence",
            "review_all_remaining_execution_boundary_blockers",
            "confirm_no_broker_send_or_mode_change_is_authorized_by_this_packet",
            "confirm_pre_armed_dry_run_authorization_requires_separate_later_slice",
            "confirm_final_human_review_required_before_any_mode_change",
        ],
        "source_summary": {
            "source_report_version": rollup.get("report_version"),
            "source_decision": rollup.get("decision"),
            "final_review_present": bool(source_summary.get("final_review_present")),
            "handoff_present": bool(source_summary.get("handoff_present")),
            "live_readiness_contract_ready": bool(source_summary.get("live_readiness_contract_ready")),
            "execution_safety_harness_ready": bool(source_summary.get("execution_safety_harness_ready")),
            "pre_live_blocker_report_clear": bool(source_summary.get("pre_live_blocker_report_clear")),
            "runtime_control_clear": bool(source_summary.get("runtime_control_clear")),
        },
        "checks": {
            "source_rollup_ok": rollup.get("ok") is True,
            "runtime_control_clearance_prerequisites_met": runtime_clearance_met,
            "remaining_execution_blockers_visible": bool(remaining_execution_blockers),
            "operator_actions_visible": bool(actions),
            "non_authorization_boundary_explicit": safety_ok and explicit_not_in_slice,
            "human_review_required_visible": human_review_required,
            "human_review_recorded_false": True,
            "operator_acknowledgement_recorded_false": True,
            "read_only_no_broker_non_authorizing": safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
            "source_s54_checks": checks,
        },
        "warnings": [
            "human_review_packet_is_informational_only",
            "human_review_recorded_false",
            "operator_acknowledgement_recorded_false",
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
            "human_review_recorded": False,
            "operator_acknowledgement_recorded": False,
            "final_human_review_required": True,
        },
        "paths": _as_dict(rollup.get("paths")),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run human review packet from S54 readiness rollup JSON.")
    parser.add_argument("--readiness-rollup", required=True, help="Path to S54 Pre-Armed Dry Run readiness rollup JSON.")
    parser.add_argument("--out", default="", help="Optional human review packet output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        rollup = _read_json(Path(args.readiness_rollup))
        payload = build_pre_armed_dry_run_human_review_packet(readiness_rollup=rollup)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_human_review_packet_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "pre_armed_dry_run_authorized": False,
                "live_authorized": False,
                "human_review_recorded": False,
                "operator_acknowledgement_recorded": False,
                "final_human_review_required": True,
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "human_review_recorded": False,
            "operator_acknowledgement_recorded": False,
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
