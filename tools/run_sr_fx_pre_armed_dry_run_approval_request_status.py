# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_request_status.py
# desc: Broker-free Pre-Armed Dry Run approval-request/status packet from S55 human review packet. Request/status only; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_request_status"
REPORT_VERSION = "pre_armed_dry_run_approval_request_status.v1"


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


def build_pre_armed_dry_run_approval_request_status(*, human_review_packet: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    packet = dict(human_review_packet)
    review_ready = bool(packet.get("human_review_packet_ready"))
    packet_ok = packet.get("ok") is True
    blockers = _as_list(packet.get("blocker_rollup"))
    runtime_blockers = _as_list(packet.get("runtime_control_blockers"))
    remaining_execution_blockers = _as_list(packet.get("remaining_execution_blockers"))
    actions = _as_list(packet.get("operator_required_actions"))
    checklist = _as_list(packet.get("human_acknowledgement_checklist"))
    review_items = _as_list(packet.get("review_required_items"))
    blocking_items = _as_list(packet.get("blocking_review_items"))
    safety_ok = (
        packet.get("read_only") is True
        and packet.get("would_send_to_broker") is False
        and packet.get("mode_changed") is False
        and packet.get("autotrade_resume_authorized") is False
        and packet.get("pre_armed_dry_run_authorized") is False
        and packet.get("live_authorized") is False
        and packet.get("human_review_recorded") is False
        and packet.get("operator_acknowledgement_recorded") is False
    )
    request_status = (
        "approval_request_status_ready_for_human_review_not_recorded"
        if packet_ok and safety_ok and review_ready
        else "approval_request_status_blocked_not_recorded"
    )
    request_blockers = [] if request_status.endswith("ready_for_human_review_not_recorded") else _dedupe([
        *blocking_items,
        *runtime_blockers,
        *remaining_execution_blockers,
    ])
    if not checklist:
        request_blockers.append("human_acknowledgement_checklist_missing")
    if not actions:
        request_blockers.append("operator_required_actions_missing")
    request_blockers = _dedupe(request_blockers)

    approval_request = {
        "status": request_status,
        "ready_for_human_review": bool(packet_ok and safety_ok and review_ready),
        "blocked_by": request_blockers,
        "review_required_items": review_items,
        "operator_required_actions": actions,
        "human_acknowledgement_checklist": checklist,
        "approval_recorded": False,
        "human_approval_recorded": False,
        "operator_acknowledgement_recorded": False,
        "approval_ledger_appended": False,
        "command_ledger_appended": False,
        "mode_change_requested": False,
        "mode_change_authorized": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
    }

    status_packet_ok = bool(packet_ok and safety_ok and checklist and actions)
    return {
        "ok": status_packet_ok,
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": request_status,
        "approval_request_status_packet_ready": status_packet_ok,
        "approval_request": approval_request,
        "approval_recorded": False,
        "human_approval_recorded": False,
        "operator_acknowledgement_recorded": False,
        "approval_ledger_appended": False,
        "command_ledger_appended": False,
        "mode_change_requested": False,
        "mode_change_authorized": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
        "autotrade_resume_authorized": False,
        "mode_changed": False,
        "read_only": True,
        "would_send_to_broker": False,
        "human_review_packet_ready": review_ready,
        "human_review_recorded": False,
        "source_summary": {
            "source_report_version": packet.get("report_version"),
            "source_decision": packet.get("decision"),
            "source_packet_ok": packet_ok,
            "source_human_review_packet_ready": review_ready,
            "source_human_review_recorded": packet.get("human_review_recorded"),
            "source_operator_acknowledgement_recorded": packet.get("operator_acknowledgement_recorded"),
            "runtime_control_clearance_prerequisites_met": packet.get("runtime_control_clearance_prerequisites_met"),
        },
        "request_blockers": request_blockers,
        "runtime_control_blockers": runtime_blockers,
        "remaining_execution_blockers": remaining_execution_blockers,
        "operator_required_actions": actions,
        "human_acknowledgement_checklist": checklist,
        "checks": {
            "source_packet_ok": packet_ok,
            "human_review_packet_ready_visible": isinstance(packet.get("human_review_packet_ready"), bool),
            "approval_request_status_present": bool(request_status),
            "request_blockers_visible_when_blocked": bool(request_blockers) if not review_ready else True,
            "human_acknowledgement_checklist_present": bool(checklist),
            "operator_actions_present": bool(actions),
            "approval_recorded_false": True,
            "human_approval_recorded_false": True,
            "operator_acknowledgement_recorded_false": True,
            "approval_ledger_appended_false": True,
            "command_ledger_appended_false": True,
            "mode_change_requested_false": True,
            "mode_change_authorized_false": True,
            "read_only_no_broker_non_authorizing": safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "approval_request_status_packet_is_informational_only",
            "human_approval_recorded_false",
            "operator_acknowledgement_recorded_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
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
            "approval_recorded": False,
            "human_approval_recorded": False,
            "operator_acknowledgement_recorded": False,
            "approval_ledger_appended": False,
            "command_ledger_appended": False,
            "mode_change_requested": False,
            "mode_change_authorized": False,
            "final_human_review_required": True,
        },
        "paths": _as_dict(packet.get("paths")),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run approval-request/status packet from S55 human review packet JSON.")
    parser.add_argument("--human-review-packet", required=True, help="Path to S55 human review packet JSON.")
    parser.add_argument("--out", default="", help="Optional approval-request/status output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        packet = _read_json(Path(args.human_review_packet))
        payload = build_pre_armed_dry_run_approval_request_status(human_review_packet=packet)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_approval_request_status_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "pre_armed_dry_run_authorized": False,
                "live_authorized": False,
                "approval_recorded": False,
                "human_approval_recorded": False,
                "operator_acknowledgement_recorded": False,
                "approval_ledger_appended": False,
                "command_ledger_appended": False,
                "mode_change_requested": False,
                "mode_change_authorized": False,
                "final_human_review_required": True,
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "approval_recorded": False,
            "human_approval_recorded": False,
            "operator_acknowledgement_recorded": False,
            "approval_ledger_appended": False,
            "command_ledger_appended": False,
            "mode_change_requested": False,
            "mode_change_authorized": False,
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
