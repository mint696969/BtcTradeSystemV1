# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_preflight_status.py
# desc: Broker-free Pre-Armed Dry Run approval record append execution authorization request record preflight/status from S62. Status-only; non-recording; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_preflight_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_execution_authorization_request_record_preflight_status.v1"
RECORD_PREFLIGHT_SCOPE = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_RECORD_REVIEW_ONLY"
RECORD_PREFLIGHT_TARGET = "APPROVAL_RECORD_APPEND_EXECUTION_AUTHORIZATION_REQUEST_RECORD"
REQUIRED_RECORD_PREFLIGHT_ACKS = (
    "confirm_s62_authorization_request_status_reviewed",
    "confirm_record_preflight_is_review_only",
    "confirm_this_preflight_does_not_record_authorization_request",
    "confirm_no_authorization_grant_or_append_is_authorized",
    "confirm_separate_explicit_record_slice_required_before_any_recording",
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


def build_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_preflight_status(*, authorization_request_status: Mapping[str, Any], record_preflight_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    status = dict(authorization_request_status)
    review = dict(record_preflight_review)
    status_ok = status.get("ok") is True
    authorization_request_ready = status.get("approval_record_append_execution_authorization_request_ready") is True
    authorization_request_observed = status.get("approval_record_append_execution_authorization_requested_observed") is True
    status_blockers = _as_list(status.get("authorization_request_blockers"))
    source_summary = _as_dict(status.get("source_summary"))
    request_summary = _as_dict(status.get("authorization_request_summary"))
    status_safety_ok = (
        status.get("read_only") is True
        and status.get("would_send_to_broker") is False
        and status.get("mode_changed") is False
        and status.get("approval_record_append_execution_authorization_request_recorded") is False
        and status.get("approval_record_append_execution_authorized") is False
        and status.get("approval_record_append_execution_requested") is False
        and status.get("approval_record_append_executed") is False
        and status.get("approval_record_append_request_submitted") is False
        and status.get("approval_record_append_request_persisted") is False
        and status.get("approval_record_persisted_by_this_tool") is False
        and status.get("approval_record_persisted") is False
        and status.get("approval_ledger_appended") is False
        and status.get("command_ledger_appended") is False
        and status.get("mode_change_requested") is False
        and status.get("mode_change_authorized") is False
        and status.get("pre_armed_dry_run_authorized") is False
        and status.get("live_authorized") is False
        and status.get("autotrade_resume_authorized") is False
        and status.get("status_only") is True
    )
    submitted_acks = _as_list(review.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_RECORD_PREFLIGHT_ACKS if ack not in submitted_acks]
    review_blockers: list[str] = []
    if review.get("record_preflight_reviewed") is not True:
        review_blockers.append("record_preflight_review_not_confirmed")
    if review.get("authorization_request_recording_requested") is not True:
        review_blockers.append("authorization_request_recording_request_required_for_preflight")
    if review.get("record_preflight_scope") != RECORD_PREFLIGHT_SCOPE:
        review_blockers.append("record_preflight_scope_not_review_only")
    if review.get("record_preflight_target") != RECORD_PREFLIGHT_TARGET:
        review_blockers.append("record_preflight_target_not_authorization_request_record")
    if not str(review.get("requested_by") or "").strip():
        review_blockers.append("requested_by_required")
    if not str(review.get("requested_at") or "").strip():
        review_blockers.append("requested_at_required")
    if not str(review.get("operator_identity") or "").strip():
        review_blockers.append("operator_identity_required")
    if review.get("authorization_request_recorded") is not False:
        review_blockers.append("authorization_request_recorded_must_be_false_in_preflight")
    if review.get("approval_record_append_execution_authorized") is not False:
        review_blockers.append("authorization_grant_must_be_false_in_preflight")
    if review.get("approval_record_append_execution_requested") is not False:
        review_blockers.append("append_execution_request_must_be_false_in_preflight")
    if review.get("approval_record_append_executed") is not False:
        review_blockers.append("append_execution_must_be_false_in_preflight")
    if review.get("approval_ledger_append_requested") is not False:
        review_blockers.append("approval_ledger_append_request_must_be_false_in_preflight")
    if review.get("command_ledger_append_requested") is not False:
        review_blockers.append("command_ledger_append_request_must_be_false_in_preflight")
    if review.get("mode_change_requested") is not False:
        review_blockers.append("mode_change_request_must_be_false_in_preflight")
    review_blockers.extend(f"missing_record_preflight_ack:{ack}" for ack in missing_acks)
    preflight_blockers: list[str] = []
    if not status_ok:
        preflight_blockers.append("authorization_request_status_not_ok")
    if not authorization_request_ready:
        preflight_blockers.append("authorization_request_status_not_ready")
        preflight_blockers.extend(status_blockers)
    if not authorization_request_observed:
        preflight_blockers.append("authorization_request_not_observed")
    if not status_safety_ok:
        preflight_blockers.append("authorization_request_status_safety_contract_not_clear")
    if request_summary.get("authorization_scope") != "PRE_ARMED_DRY_RUN_APPROVAL_RECORD_APPEND_REVIEW_ONLY":
        preflight_blockers.append("source_authorization_scope_not_review_only")
    if request_summary.get("authorization_target") != "APPROVAL_RECORD_APPEND_EXECUTION":
        preflight_blockers.append("source_authorization_target_not_append_execution")
    preflight_blockers.extend(review_blockers)
    preflight_blockers = _dedupe(preflight_blockers)
    preflight_ready = bool(status_ok and authorization_request_ready and authorization_request_observed and status_safety_ok and not review_blockers and not preflight_blockers)
    decision = "authorization_request_record_preflight_ready_not_recorded" if preflight_ready else "authorization_request_record_preflight_blocked_not_recorded"
    return {
        "ok": bool(status_ok and status_safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "authorization_request_record_preflight_ready": preflight_ready,
        "record_preflight_blockers": preflight_blockers,
        "authorization_request_recording_requested_observed": review.get("authorization_request_recording_requested") is True,
        "approval_record_append_execution_authorization_request_recorded": False,
        "authorization_request_recorded": False,
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
        "preflight_status_only": True,
        "record_preflight_summary": {
            "record_preflight_reviewed": review.get("record_preflight_reviewed") is True,
            "record_preflight_scope": review.get("record_preflight_scope"),
            "record_preflight_target": review.get("record_preflight_target"),
            "requested_by": review.get("requested_by"),
            "requested_at": review.get("requested_at"),
            "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
            "recording_request_input": review.get("authorization_request_recording_requested"),
            "authorization_request_recorded_input": review.get("authorization_request_recorded"),
            "authorization_grant_input": review.get("approval_record_append_execution_authorized"),
            "append_execution_request_input": review.get("approval_record_append_execution_requested"),
            "append_execution_executed_input": review.get("approval_record_append_executed"),
        },
        "source_summary": {
            "authorization_request_status_report_version": status.get("report_version"),
            "authorization_request_status_decision": status.get("decision"),
            "authorization_request_status_ready": authorization_request_ready,
            "authorization_request_observed": authorization_request_observed,
            "execution_gate_decision": source_summary.get("execution_gate_decision"),
            "execution_gate_ready": source_summary.get("execution_gate_ready"),
            "append_request_plan_decision": source_summary.get("append_request_plan_decision"),
            "preflight_decision": source_summary.get("preflight_decision"),
            "ledger_decision": source_summary.get("ledger_decision"),
            "record_id": source_summary.get("record_id"),
            "evidence_id": source_summary.get("evidence_id"),
            "approval_scope": source_summary.get("approval_scope"),
            "target_mode": source_summary.get("target_mode"),
            "authorization_scope": request_summary.get("authorization_scope"),
            "authorization_target": request_summary.get("authorization_target"),
            "requested_by": request_summary.get("requested_by"),
            "requested_at": request_summary.get("requested_at"),
            "operator_identity_present": request_summary.get("operator_identity_present") is True,
        },
        "checks": {
            "authorization_request_status_ok": status_ok,
            "authorization_request_status_ready": authorization_request_ready,
            "authorization_request_observed": authorization_request_observed,
            "authorization_request_status_safety_contract_clear": status_safety_ok,
            "record_preflight_review_valid": not review_blockers,
            "record_preflight_ready": preflight_ready,
            "record_preflight_blockers_visible_when_blocked": bool(preflight_blockers) if not preflight_ready else True,
            "authorization_request_recorded_false": True,
            "authorization_grant_false": True,
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
            "read_only_no_broker_non_authorizing": status_safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "authorization_request_record_preflight_status_is_informational_only",
            "authorization_request_recorded_false",
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
            "separate_explicit_record_slice_required_before_any_recording",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "preflight_status_only": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "approval_record_append_execution_authorization_request_recorded": False,
            "authorization_request_recorded": False,
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
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run authorization request record preflight/status from S62 JSON.")
    parser.add_argument("--authorization-request-status", required=True, help="Path to S62 authorization request/status JSON.")
    parser.add_argument("--record-preflight-review", required=True, help="Path to record preflight review JSON. This slice records nothing.")
    parser.add_argument("--out", default="", help="Optional record preflight/status output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        status = _read_json(Path(args.authorization_request_status))
        review = _read_json(Path(args.record_preflight_review))
        payload = build_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_preflight_status(authorization_request_status=status, record_preflight_review=review)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_authorization_request_record_preflight_status_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "approval_record_append_execution_authorization_request_recorded": False,
            "authorization_request_recorded": False,
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
