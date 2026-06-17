# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_preflight_status.py
# desc: Broker-free Pre-Armed Dry Run authorization request record execution authorization request record preflight/status from S66. Preflight/status only; non-recording; non-executing; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_preflight_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_preflight_status.v1"
PREFLIGHT_SCOPE = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_RECORD_EXECUTION_AUTHORIZATION_REQUEST_RECORD_REVIEW_ONLY"
PREFLIGHT_TARGET = "APPROVAL_RECORD_APPEND_EXECUTION_AUTHORIZATION_REQUEST_RECORD_EXECUTION_AUTHORIZATION_REQUEST_RECORD"
REQUIRED_PREFLIGHT_ACKS = (
    "confirm_s66_record_execution_authorization_request_status_reviewed",
    "confirm_record_execution_authorization_request_record_preflight_is_review_only",
    "confirm_this_preflight_does_not_record_authorization_request",
    "confirm_no_record_execution_authorization_grant_append_or_mode_change_is_authorized",
    "confirm_separate_explicit_record_execution_slice_required_before_any_recording",
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


def build_pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_preflight_status(*, record_execution_authorization_request_status: Mapping[str, Any], record_execution_authorization_request_record_preflight_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    status = dict(record_execution_authorization_request_status)
    review = dict(record_execution_authorization_request_record_preflight_review)
    status_ok = status.get("ok") is True
    request_ready = status.get("authorization_request_record_execution_authorization_request_ready") is True
    request_observed = status.get("authorization_request_record_execution_authorization_requested_observed") is True
    status_blockers = _as_list(status.get("record_execution_authorization_request_blockers"))
    draft = _as_dict(status.get("authorization_request_record_draft"))
    source_summary = _as_dict(status.get("source_summary"))
    request_summary = _as_dict(status.get("record_execution_authorization_request_summary"))
    status_safety_ok = (
        status.get("read_only") is True
        and status.get("would_send_to_broker") is False
        and status.get("mode_changed") is False
        and status.get("authorization_request_record_execution_authorized") is False
        and status.get("authorization_request_record_execution_requested") is False
        and status.get("authorization_request_record_executed") is False
        and status.get("approval_record_append_execution_authorization_request_recorded") is False
        and status.get("authorization_request_recorded") is False
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
    missing_acks = [ack for ack in REQUIRED_PREFLIGHT_ACKS if ack not in submitted_acks]
    review_blockers: list[str] = []
    if review.get("record_execution_authorization_request_record_preflight_reviewed") is not True:
        review_blockers.append("record_execution_authorization_request_record_preflight_review_not_confirmed")
    if review.get("record_execution_authorization_request_recording_requested") is not True:
        review_blockers.append("record_execution_authorization_request_recording_request_required_for_preflight")
    if review.get("record_preflight_scope") != PREFLIGHT_SCOPE:
        review_blockers.append("record_preflight_scope_not_review_only")
    if review.get("record_preflight_target") != PREFLIGHT_TARGET:
        review_blockers.append("record_preflight_target_not_authorization_request_record_execution_authorization_request_record")
    if not str(review.get("requested_by") or "").strip():
        review_blockers.append("requested_by_required")
    if not str(review.get("requested_at") or "").strip():
        review_blockers.append("requested_at_required")
    if not str(review.get("operator_identity") or "").strip():
        review_blockers.append("operator_identity_required")
    false_only = {
        "authorization_request_record_execution_authorization_request_recorded": "record_execution_authorization_request_recorded_must_be_false_in_preflight",
        "authorization_request_record_execution_authorized": "record_execution_authorization_grant_must_be_false_in_preflight",
        "authorization_request_record_execution_requested": "record_execution_request_must_be_false_in_preflight",
        "authorization_request_record_executed": "record_execution_must_be_false_in_preflight",
        "authorization_request_recorded": "authorization_request_recorded_must_be_false_in_preflight",
        "approval_record_append_execution_authorized": "append_execution_authorization_grant_must_be_false_in_preflight",
        "approval_record_append_execution_requested": "append_execution_request_must_be_false_in_preflight",
        "approval_record_append_executed": "append_execution_must_be_false_in_preflight",
        "approval_ledger_append_requested": "approval_ledger_append_request_must_be_false_in_preflight",
        "command_ledger_append_requested": "command_ledger_append_request_must_be_false_in_preflight",
        "mode_change_requested": "mode_change_request_must_be_false_in_preflight",
    }
    for key, blocker in false_only.items():
        if review.get(key) is not False:
            review_blockers.append(blocker)
    review_blockers.extend(f"missing_record_execution_authorization_request_record_preflight_ack:{ack}" for ack in missing_acks)

    preflight_blockers: list[str] = []
    if not status_ok:
        preflight_blockers.append("record_execution_authorization_request_status_not_ok")
    if not request_ready:
        preflight_blockers.append("record_execution_authorization_request_not_ready")
        preflight_blockers.extend(status_blockers)
    if not request_observed:
        preflight_blockers.append("record_execution_authorization_request_not_observed")
    if not status_safety_ok:
        preflight_blockers.append("record_execution_authorization_request_safety_contract_not_clear")
    if request_summary.get("authorization_scope") != "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_RECORD_EXECUTION_REVIEW_ONLY":
        preflight_blockers.append("source_authorization_scope_not_review_only")
    if request_summary.get("authorization_target") != "APPROVAL_RECORD_APPEND_EXECUTION_AUTHORIZATION_REQUEST_RECORD_EXECUTION":
        preflight_blockers.append("source_authorization_target_not_record_execution")
    if draft.get("recorded") is not False or draft.get("persisted") is not False or draft.get("authorized") is not False or draft.get("executed") is not False:
        preflight_blockers.append("authorization_request_record_draft_not_dry_run_safe")
    preflight_blockers.extend(review_blockers)
    preflight_blockers = _dedupe(preflight_blockers)
    preflight_ready = bool(status_ok and request_ready and request_observed and status_safety_ok and not review_blockers and not preflight_blockers)
    decision = "authorization_request_record_execution_authorization_request_record_preflight_ready_not_recorded" if preflight_ready else "authorization_request_record_execution_authorization_request_record_preflight_blocked_not_recorded"
    return {
        "ok": bool(status_ok and status_safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "authorization_request_record_execution_authorization_request_record_preflight_ready": preflight_ready,
        "record_execution_authorization_request_record_preflight_blockers": preflight_blockers,
        "record_execution_authorization_request_recording_requested_observed": review.get("record_execution_authorization_request_recording_requested") is True,
        "authorization_request_record_execution_authorization_request_recorded": False,
        "authorization_request_record_execution_authorized": False,
        "authorization_request_record_execution_requested": False,
        "authorization_request_record_executed": False,
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
        "record_execution_authorization_request_record_preflight_summary": {
            "record_execution_authorization_request_record_preflight_reviewed": review.get("record_execution_authorization_request_record_preflight_reviewed") is True,
            "record_preflight_scope": review.get("record_preflight_scope"),
            "record_preflight_target": review.get("record_preflight_target"),
            "requested_by": review.get("requested_by"),
            "requested_at": review.get("requested_at"),
            "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
            "recording_request_input": review.get("record_execution_authorization_request_recording_requested"),
            "recorded_input": review.get("authorization_request_record_execution_authorization_request_recorded"),
            "record_execution_authorization_grant_input": review.get("authorization_request_record_execution_authorized"),
            "record_execution_request_input": review.get("authorization_request_record_execution_requested"),
            "record_execution_executed_input": review.get("authorization_request_record_executed"),
        },
        "authorization_request_record_draft": {
            "record_kind": draft.get("record_kind"),
            "record_id": draft.get("record_id"),
            "evidence_id": draft.get("evidence_id"),
            "authorization_scope": draft.get("authorization_scope"),
            "authorization_target": draft.get("authorization_target"),
            "dry_run_only": True,
            "planned": True,
            "recorded": False,
            "persisted": False,
            "authorized": False,
            "executed": False,
        },
        "source_summary": {
            "record_execution_authorization_request_report_version": status.get("report_version"),
            "record_execution_authorization_request_decision": status.get("decision"),
            "record_execution_authorization_request_ready": request_ready,
            "record_execution_authorization_request_observed": request_observed,
            "record_execution_gate_decision": source_summary.get("record_execution_gate_decision"),
            "record_execution_gate_ready": source_summary.get("record_execution_gate_ready"),
            "record_dry_run_plan_decision": source_summary.get("record_dry_run_plan_decision"),
            "record_dry_run_plan_ready": source_summary.get("record_dry_run_plan_ready"),
            "record_preflight_decision": source_summary.get("record_preflight_decision"),
            "record_preflight_ready": source_summary.get("record_preflight_ready"),
            "evidence_id": source_summary.get("evidence_id"),
            "authorization_scope": source_summary.get("authorization_scope"),
            "authorization_target": source_summary.get("authorization_target"),
            "requested_by": source_summary.get("requested_by"),
            "requested_at": source_summary.get("requested_at"),
        },
        "checks": {
            "record_execution_authorization_request_status_ok": status_ok,
            "record_execution_authorization_request_ready": request_ready,
            "record_execution_authorization_request_observed": request_observed,
            "record_execution_authorization_request_safety_contract_clear": status_safety_ok,
            "record_execution_authorization_request_record_preflight_review_valid": not review_blockers,
            "record_execution_authorization_request_record_preflight_ready": preflight_ready,
            "record_execution_authorization_request_recorded_false": True,
            "authorization_request_record_execution_authorized_false": True,
            "authorization_request_record_execution_requested_false": True,
            "authorization_request_record_executed_false": True,
            "authorization_request_recorded_false": True,
            "approval_record_append_execution_authorized_false": True,
            "approval_record_append_execution_requested_false": True,
            "approval_record_append_executed_false": True,
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
            "authorization_request_record_execution_authorization_request_record_preflight_status_is_informational_only",
            "authorization_request_record_execution_authorization_request_recorded_false",
            "authorization_request_record_execution_authorized_false",
            "authorization_request_record_execution_requested_false",
            "authorization_request_record_executed_false",
            "authorization_request_recorded_false",
            "approval_record_append_execution_authorized_false",
            "approval_record_append_execution_requested_false",
            "approval_record_append_executed_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
            "mode_change_authorized_false",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "separate_explicit_record_execution_slice_required_before_any_recording",
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
            "authorization_request_record_execution_authorization_request_recorded": False,
            "authorization_request_record_execution_authorized": False,
            "authorization_request_record_execution_requested": False,
            "authorization_request_record_executed": False,
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
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run authorization request record execution authorization request record preflight/status from S66 JSON.")
    parser.add_argument("--record-execution-authorization-request-status", required=True, help="Path to S66 authorization request record execution authorization request/status JSON.")
    parser.add_argument("--record-execution-authorization-request-record-preflight-review", required=True, help="Path to record preflight review JSON. This slice records and executes nothing.")
    parser.add_argument("--out", default="", help="Optional preflight/status output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        status = _read_json(Path(args.record_execution_authorization_request_status))
        review = _read_json(Path(args.record_execution_authorization_request_record_preflight_review))
        payload = build_pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_preflight_status(record_execution_authorization_request_status=status, record_execution_authorization_request_record_preflight_review=review)
    except Exception as exc:
        payload = {"ok": False, "tool": TOOL, "report_version": REPORT_VERSION, "generated_at": _utc_now_iso(), "error": str(exc), "error_class": exc.__class__.__name__, "blocked_by": ["pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_preflight_status_failed"], "read_only": True, "would_send_to_broker": False, "mode_changed": False, "autotrade_resume_authorized": False, "pre_armed_dry_run_authorized": False, "live_authorized": False, "authorization_request_record_execution_authorization_request_recorded": False, "authorization_request_record_execution_authorized": False, "authorization_request_record_execution_requested": False, "authorization_request_record_executed": False, "authorization_request_recorded": False, "approval_record_append_execution_authorized": False, "approval_record_append_execution_requested": False, "approval_record_append_executed": False, "approval_ledger_appended": False, "command_ledger_appended": False, "mode_change_requested": False, "mode_change_authorized": False}
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
