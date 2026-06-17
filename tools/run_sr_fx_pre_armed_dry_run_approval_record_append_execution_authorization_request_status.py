# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_status.py
# desc: Broker-free Pre-Armed Dry Run approval record append execution authorization request/status from S61 gate. Status-only; non-recording; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_execution_authorization_request_status.v1"
AUTHORIZATION_SCOPE = "PRE_ARMED_DRY_RUN_APPROVAL_RECORD_APPEND_REVIEW_ONLY"
AUTHORIZATION_TARGET = "APPROVAL_RECORD_APPEND_EXECUTION"
REQUIRED_AUTHORIZATION_ACKS = (
    "confirm_s61_execution_gate_reviewed",
    "confirm_authorization_request_is_review_only",
    "confirm_this_status_does_not_append_or_record",
    "confirm_no_command_ledger_append_or_mode_change_is_authorized",
    "confirm_separate_explicit_append_execution_slice_required_before_any_recording",
)


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


def build_pre_armed_dry_run_approval_record_append_execution_authorization_request_status(*, execution_gate_status: Mapping[str, Any], authorization_request: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    gate = dict(execution_gate_status)
    request = dict(authorization_request)
    gate_ok = gate.get("ok") is True
    gate_ready = gate.get("approval_record_append_execution_gate_ready") is True
    gate_blockers = _as_list(gate.get("execution_gate_blockers"))
    gate_draft = _as_dict(gate.get("append_request_draft"))
    gate_summary = _as_dict(gate.get("source_summary"))
    gate_safety_ok = (
        gate.get("read_only") is True
        and gate.get("would_send_to_broker") is False
        and gate.get("mode_changed") is False
        and gate.get("approval_record_append_execution_requested") is False
        and gate.get("approval_record_append_executed") is False
        and gate.get("approval_record_append_request_submitted") is False
        and gate.get("approval_record_append_request_persisted") is False
        and gate.get("approval_record_persisted_by_this_tool") is False
        and gate.get("approval_record_persisted") is False
        and gate.get("approval_ledger_appended") is False
        and gate.get("command_ledger_appended") is False
        and gate.get("mode_change_requested") is False
        and gate.get("mode_change_authorized") is False
        and gate.get("pre_armed_dry_run_authorized") is False
        and gate.get("live_authorized") is False
        and gate.get("autotrade_resume_authorized") is False
        and gate.get("dry_run_gate_only") is True
    )
    submitted_acks = _as_list(request.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_AUTHORIZATION_ACKS if ack not in submitted_acks]
    request_blockers: list[str] = []
    if request.get("authorization_request_reviewed") is not True:
        request_blockers.append("authorization_request_review_not_confirmed")
    if request.get("approval_record_append_execution_authorization_requested") is not True:
        request_blockers.append("approval_record_append_execution_authorization_request_required")
    if request.get("authorization_scope") != AUTHORIZATION_SCOPE:
        request_blockers.append("authorization_scope_not_review_only")
    if request.get("authorization_target") != AUTHORIZATION_TARGET:
        request_blockers.append("authorization_target_not_append_execution")
    if not str(request.get("requested_by") or "").strip():
        request_blockers.append("requested_by_required")
    if not str(request.get("requested_at") or "").strip():
        request_blockers.append("requested_at_required")
    if not str(request.get("operator_identity") or "").strip():
        request_blockers.append("operator_identity_required")
    if request.get("approval_record_append_execution_authorized") is not False:
        request_blockers.append("authorization_grant_must_be_false_in_status_slice")
    if request.get("approval_record_append_execution_requested") is not False:
        request_blockers.append("append_execution_request_must_be_false_in_status_slice")
    if request.get("approval_record_append_executed") is not False:
        request_blockers.append("append_execution_must_be_false_in_status_slice")
    if request.get("approval_ledger_append_requested") is not False:
        request_blockers.append("approval_ledger_append_request_must_be_false_in_status_slice")
    if request.get("command_ledger_append_requested") is not False:
        request_blockers.append("command_ledger_append_request_must_be_false_in_status_slice")
    if request.get("mode_change_requested") is not False:
        request_blockers.append("mode_change_request_must_be_false_in_status_slice")
    request_blockers.extend(f"missing_authorization_ack:{ack}" for ack in missing_acks)
    status_blockers: list[str] = []
    if not gate_ok:
        status_blockers.append("execution_gate_status_not_ok")
    if not gate_ready:
        status_blockers.append("execution_gate_not_ready")
        status_blockers.extend(gate_blockers)
    if not gate_safety_ok:
        status_blockers.append("execution_gate_safety_contract_not_clear")
    if str(gate_draft.get("request_kind") or "") != "pre_armed_dry_run_approval_record_append_request_draft":
        status_blockers.append("append_request_draft_missing_or_invalid")
    if str(gate_draft.get("approval_scope") or "") != "PRE_ARMED_DRY_RUN_REVIEW_ONLY":
        status_blockers.append("approval_scope_not_review_only")
    if str(gate_draft.get("target_mode") or "") != "PRE_ARMED_DRY_RUN":
        status_blockers.append("target_mode_not_pre_armed_dry_run")
    if not str(gate_draft.get("evidence_id") or "").startswith("approval_evidence_"):
        status_blockers.append("invalid_or_missing_evidence_id")
    status_blockers.extend(request_blockers)
    status_blockers = _dedupe(status_blockers)
    request_ready = bool(gate_ok and gate_ready and gate_safety_ok and not request_blockers and not status_blockers)
    decision = "approval_record_append_execution_authorization_request_ready_not_authorized_not_recorded" if request_ready else "approval_record_append_execution_authorization_request_blocked_not_authorized_not_recorded"
    return {
        "ok": bool(gate_ok and gate_safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "approval_record_append_execution_authorization_request_ready": request_ready,
        "authorization_request_blockers": status_blockers,
        "approval_record_append_execution_authorization_requested_observed": request.get("approval_record_append_execution_authorization_requested") is True,
        "approval_record_append_execution_authorization_request_recorded": False,
        "approval_record_append_execution_authorized": False,
        "approval_record_append_execution_requested": False,
        "approval_record_append_executed": False,
        "approval_record_append_request_submitted": False,
        "approval_record_append_request_persisted": False,
        "approval_record_persisted_by_this_tool": False,
        "approval_record_persisted": False,
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
        "status_only": True,
        "authorization_request_summary": {
            "authorization_request_reviewed": request.get("authorization_request_reviewed") is True,
            "authorization_scope": request.get("authorization_scope"),
            "authorization_target": request.get("authorization_target"),
            "requested_by": request.get("requested_by"),
            "requested_at": request.get("requested_at"),
            "operator_identity_present": bool(str(request.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
            "authorization_requested_input": request.get("approval_record_append_execution_authorization_requested"),
            "authorization_grant_input": request.get("approval_record_append_execution_authorized"),
            "append_execution_request_input": request.get("approval_record_append_execution_requested"),
            "append_execution_executed_input": request.get("approval_record_append_executed"),
        },
        "source_summary": {
            "execution_gate_report_version": gate.get("report_version"),
            "execution_gate_decision": gate.get("decision"),
            "execution_gate_ready": gate_ready,
            "append_request_plan_decision": gate_summary.get("append_request_plan_decision"),
            "preflight_decision": gate_summary.get("preflight_decision"),
            "ledger_decision": gate_summary.get("ledger_decision"),
            "existing_record_observed": gate_summary.get("existing_record_observed"),
            "source_status_decision": gate_summary.get("source_status_decision"),
            "source_ready_for_human_review": gate_summary.get("source_ready_for_human_review"),
            "record_id": gate_draft.get("record_id"),
            "evidence_id": gate_draft.get("evidence_id"),
            "approval_scope": gate_draft.get("approval_scope"),
            "target_mode": gate_draft.get("target_mode"),
        },
        "checks": {
            "execution_gate_ok": gate_ok,
            "execution_gate_ready": gate_ready,
            "execution_gate_safety_contract_clear": gate_safety_ok,
            "authorization_request_valid": not request_blockers,
            "authorization_request_ready": request_ready,
            "authorization_request_blockers_visible_when_blocked": bool(status_blockers) if not request_ready else True,
            "authorization_request_recorded_false": True,
            "approval_record_append_execution_authorized_false": True,
            "approval_record_append_execution_requested_false": True,
            "approval_record_append_executed_false": True,
            "approval_record_append_request_submitted_false": True,
            "approval_record_append_request_persisted_false": True,
            "approval_record_persisted_by_this_tool_false": True,
            "approval_recorded_false": True,
            "human_approval_recorded_false": True,
            "operator_acknowledgement_recorded_false": True,
            "approval_ledger_appended_false": True,
            "command_ledger_appended_false": True,
            "mode_change_requested_false": True,
            "mode_change_authorized_false": True,
            "read_only_no_broker_non_authorizing": gate_safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "approval_record_append_execution_authorization_request_status_is_informational_only",
            "approval_record_append_execution_authorization_request_recorded_false",
            "approval_record_append_execution_authorized_false",
            "approval_record_append_execution_requested_false",
            "approval_record_append_executed_false",
            "approval_record_append_request_submitted_false",
            "approval_record_append_request_persisted_false",
            "approval_record_persisted_by_this_tool_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
            "mode_change_authorized_false",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "broker_send_remains_disabled",
            "separate_explicit_append_execution_slice_required_before_any_recording",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "status_only": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "approval_record_append_execution_authorization_request_recorded": False,
            "approval_record_append_execution_authorized": False,
            "approval_record_append_execution_requested": False,
            "approval_record_append_executed": False,
            "approval_record_append_request_submitted": False,
            "approval_record_append_request_persisted": False,
            "approval_record_persisted_by_this_tool": False,
            "approval_record_persisted": False,
            "approval_recorded": False,
            "human_approval_recorded": False,
            "operator_acknowledgement_recorded": False,
            "approval_ledger_appended": False,
            "command_ledger_appended": False,
            "mode_change_requested": False,
            "mode_change_authorized": False,
            "final_human_review_required": True,
        },
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run approval record append execution authorization request/status from S61 gate JSON.")
    parser.add_argument("--execution-gate-status", required=True, help="Path to S61 approval record append execution gate dry-run/status JSON.")
    parser.add_argument("--authorization-request", required=True, help="Path to authorization request JSON. This slice records no authorization.")
    parser.add_argument("--out", default="", help="Optional authorization request/status output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        gate = _read_json(Path(args.execution_gate_status))
        request = _read_json(Path(args.authorization_request))
        payload = build_pre_armed_dry_run_approval_record_append_execution_authorization_request_status(execution_gate_status=gate, authorization_request=request)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_approval_record_append_execution_authorization_request_status_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "approval_record_append_execution_authorization_request_recorded": False,
            "approval_record_append_execution_authorized": False,
            "approval_record_append_execution_requested": False,
            "approval_record_append_executed": False,
            "approval_record_append_request_submitted": False,
            "approval_record_append_request_persisted": False,
            "approval_record_persisted_by_this_tool": False,
            "approval_record_persisted": False,
            "approval_recorded": False,
            "human_approval_recorded": False,
            "operator_acknowledgement_recorded": False,
            "approval_ledger_appended": False,
            "command_ledger_appended": False,
            "mode_change_requested": False,
            "mode_change_authorized": False,
        }
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
