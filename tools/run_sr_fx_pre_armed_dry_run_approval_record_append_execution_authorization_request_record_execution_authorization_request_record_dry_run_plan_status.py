# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_dry_run_plan_status.py
# desc: Broker-free Pre-Armed Dry Run authorization request record execution authorization request record dry-run plan/status from S67. Plan/status only; non-recording; non-executing; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_dry_run_plan_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_dry_run_plan_status.v1"
PLAN_SCOPE = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_RECORD_EXECUTION_AUTHORIZATION_REQUEST_RECORD_PLAN_REVIEW_ONLY"
PLAN_TARGET = "APPROVAL_RECORD_APPEND_EXECUTION_AUTHORIZATION_REQUEST_RECORD_EXECUTION_AUTHORIZATION_REQUEST_RECORD_DRY_RUN_PLAN"
REQUIRED_PLAN_ACKS = (
    "confirm_s67_record_execution_authorization_request_record_preflight_status_reviewed",
    "confirm_record_execution_authorization_request_record_dry_run_plan_is_review_only",
    "confirm_this_plan_does_not_record_authorization_request",
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


def build_pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_dry_run_plan_status(*, record_execution_authorization_request_record_preflight_status: Mapping[str, Any], record_dry_run_plan_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    preflight = dict(record_execution_authorization_request_record_preflight_status)
    review = dict(record_dry_run_plan_review)
    preflight_ok = preflight.get("ok") is True
    preflight_ready = preflight.get("authorization_request_record_execution_authorization_request_record_preflight_ready") is True
    recording_observed = preflight.get("record_execution_authorization_request_recording_requested_observed") is True
    preflight_blockers = _as_list(preflight.get("record_execution_authorization_request_record_preflight_blockers"))
    source_summary = _as_dict(preflight.get("source_summary"))
    source_draft = _as_dict(preflight.get("authorization_request_record_draft"))
    preflight_safety_ok = (
        preflight.get("read_only") is True
        and preflight.get("would_send_to_broker") is False
        and preflight.get("mode_changed") is False
        and preflight.get("authorization_request_record_execution_authorization_request_recorded") is False
        and preflight.get("authorization_request_record_execution_authorized") is False
        and preflight.get("authorization_request_record_execution_requested") is False
        and preflight.get("authorization_request_record_executed") is False
        and preflight.get("approval_record_append_execution_authorization_request_recorded") is False
        and preflight.get("authorization_request_recorded") is False
        and preflight.get("approval_record_append_execution_authorized") is False
        and preflight.get("approval_record_append_execution_requested") is False
        and preflight.get("approval_record_append_executed") is False
        and preflight.get("approval_record_append_request_submitted") is False
        and preflight.get("approval_record_append_request_persisted") is False
        and preflight.get("approval_record_persisted_by_this_tool") is False
        and preflight.get("approval_record_persisted") is False
        and preflight.get("approval_ledger_appended") is False
        and preflight.get("command_ledger_appended") is False
        and preflight.get("mode_change_requested") is False
        and preflight.get("mode_change_authorized") is False
        and preflight.get("pre_armed_dry_run_authorized") is False
        and preflight.get("live_authorized") is False
        and preflight.get("autotrade_resume_authorized") is False
        and preflight.get("preflight_status_only") is True
    )
    submitted_acks = _as_list(review.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_PLAN_ACKS if ack not in submitted_acks]
    review_blockers: list[str] = []
    if review.get("record_dry_run_plan_reviewed") is not True:
        review_blockers.append("record_dry_run_plan_review_not_confirmed")
    if review.get("authorization_request_record_execution_authorization_request_record_dry_run_plan_requested") is not True:
        review_blockers.append("record_execution_authorization_request_record_dry_run_plan_request_required")
    if review.get("record_dry_run_plan_scope") != PLAN_SCOPE:
        review_blockers.append("record_dry_run_plan_scope_not_review_only")
    if review.get("record_dry_run_plan_target") != PLAN_TARGET:
        review_blockers.append("record_dry_run_plan_target_not_authorization_request_record_execution_authorization_request_record_plan")
    if not str(review.get("requested_by") or "").strip():
        review_blockers.append("requested_by_required")
    if not str(review.get("requested_at") or "").strip():
        review_blockers.append("requested_at_required")
    if not str(review.get("operator_identity") or "").strip():
        review_blockers.append("operator_identity_required")
    false_only = {
        "authorization_request_record_execution_authorization_request_recorded": "record_execution_authorization_request_recorded_must_be_false_in_plan",
        "authorization_request_record_execution_authorized": "record_execution_authorization_grant_must_be_false_in_plan",
        "authorization_request_record_execution_requested": "record_execution_request_must_be_false_in_plan",
        "authorization_request_record_executed": "record_execution_must_be_false_in_plan",
        "authorization_request_recorded": "authorization_request_recorded_must_be_false_in_plan",
        "approval_record_append_execution_authorized": "append_execution_authorization_grant_must_be_false_in_plan",
        "approval_record_append_execution_requested": "append_execution_request_must_be_false_in_plan",
        "approval_record_append_executed": "append_execution_must_be_false_in_plan",
        "approval_ledger_append_requested": "approval_ledger_append_request_must_be_false_in_plan",
        "command_ledger_append_requested": "command_ledger_append_request_must_be_false_in_plan",
        "mode_change_requested": "mode_change_request_must_be_false_in_plan",
    }
    for key, blocker in false_only.items():
        if review.get(key) is not False:
            review_blockers.append(blocker)
    review_blockers.extend(f"missing_record_execution_authorization_request_record_plan_ack:{ack}" for ack in missing_acks)

    plan_blockers: list[str] = []
    if not preflight_ok:
        plan_blockers.append("record_execution_authorization_request_record_preflight_status_not_ok")
    if not preflight_ready:
        plan_blockers.append("record_execution_authorization_request_record_preflight_not_ready")
        plan_blockers.extend(preflight_blockers)
    if not recording_observed:
        plan_blockers.append("record_execution_authorization_request_recording_request_not_observed")
    if not preflight_safety_ok:
        plan_blockers.append("record_execution_authorization_request_record_preflight_safety_contract_not_clear")
    if source_summary.get("record_execution_authorization_request_ready") is not True:
        plan_blockers.append("source_record_execution_authorization_request_not_ready")
    if source_draft.get("recorded") is not False or source_draft.get("persisted") is not False or source_draft.get("authorized") is not False or source_draft.get("executed") is not False:
        plan_blockers.append("authorization_request_record_draft_not_dry_run_safe")
    plan_blockers.extend(review_blockers)
    plan_blockers = _dedupe(plan_blockers)
    plan_ready = bool(preflight_ok and preflight_ready and recording_observed and preflight_safety_ok and not review_blockers and not plan_blockers)
    decision = "authorization_request_record_execution_authorization_request_record_dry_run_plan_ready_not_recorded" if plan_ready else "authorization_request_record_execution_authorization_request_record_dry_run_plan_blocked_not_recorded"
    draft = {
        "record_kind": "pre_armed_dry_run_append_execution_authorization_request_record_execution_authorization_request_record_draft",
        "record_id": source_draft.get("record_id"),
        "evidence_id": source_draft.get("evidence_id"),
        "authorization_scope": source_draft.get("authorization_scope"),
        "authorization_target": source_draft.get("authorization_target"),
        "planned_by": review.get("requested_by"),
        "planned_at": review.get("requested_at"),
        "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
        "dry_run_only": True,
        "planned": plan_ready,
        "recorded": False,
        "persisted": False,
        "authorized": False,
        "executed": False,
    }
    return {
        "ok": bool(preflight_ok and preflight_safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "authorization_request_record_execution_authorization_request_record_dry_run_plan_ready": plan_ready,
        "record_execution_authorization_request_record_dry_run_plan_blockers": plan_blockers,
        "record_execution_authorization_request_record_dry_run_plan_requested_observed": review.get("authorization_request_record_execution_authorization_request_record_dry_run_plan_requested") is True,
        "authorization_request_record_execution_authorization_request_record_draft": draft,
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
        "dry_run_plan_only": True,
        "record_dry_run_plan_review_summary": {
            "record_dry_run_plan_reviewed": review.get("record_dry_run_plan_reviewed") is True,
            "record_dry_run_plan_scope": review.get("record_dry_run_plan_scope"),
            "record_dry_run_plan_target": review.get("record_dry_run_plan_target"),
            "requested_by": review.get("requested_by"),
            "requested_at": review.get("requested_at"),
            "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
        },
        "source_summary": {
            "record_preflight_report_version": preflight.get("report_version"),
            "record_preflight_decision": preflight.get("decision"),
            "record_preflight_ready": preflight_ready,
            "recording_request_observed": recording_observed,
            "record_execution_authorization_request_decision": source_summary.get("record_execution_authorization_request_decision"),
            "record_execution_authorization_request_ready": source_summary.get("record_execution_authorization_request_ready"),
            "record_execution_gate_decision": source_summary.get("record_execution_gate_decision"),
            "record_execution_gate_ready": source_summary.get("record_execution_gate_ready"),
            "record_dry_run_plan_decision": source_summary.get("record_dry_run_plan_decision"),
            "record_dry_run_plan_ready": source_summary.get("record_dry_run_plan_ready"),
            "evidence_id": source_summary.get("evidence_id"),
            "authorization_scope": source_summary.get("authorization_scope"),
            "authorization_target": source_summary.get("authorization_target"),
            "requested_by": source_summary.get("requested_by"),
            "requested_at": source_summary.get("requested_at"),
        },
        "checks": {
            "record_preflight_status_ok": preflight_ok,
            "record_preflight_ready": preflight_ready,
            "recording_request_observed": recording_observed,
            "record_preflight_safety_contract_clear": preflight_safety_ok,
            "record_dry_run_plan_review_valid": not review_blockers,
            "record_dry_run_plan_ready": plan_ready,
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
            "read_only_no_broker_non_authorizing": preflight_safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "authorization_request_record_execution_authorization_request_record_dry_run_plan_status_is_informational_only",
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
            "dry_run_plan_only": True,
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
            "approval_ledger_appended": False,
            "command_ledger_appended": False,
            "mode_change_requested": False,
            "mode_change_authorized": False,
            "final_human_review_required": True,
        },
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run authorization request record execution authorization request record dry-run plan/status from S67 JSON.")
    parser.add_argument("--record-preflight-status", required=True, help="Path to S67 authorization request record execution authorization request record preflight/status JSON.")
    parser.add_argument("--record-dry-run-plan-review", required=True, help="Path to dry-run plan review JSON. This slice records and executes nothing.")
    parser.add_argument("--out", default="", help="Optional dry-run plan/status output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        preflight = _read_json(Path(args.record_preflight_status))
        review = _read_json(Path(args.record_dry_run_plan_review))
        payload = build_pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_dry_run_plan_status(record_execution_authorization_request_record_preflight_status=preflight, record_dry_run_plan_review=review)
    except Exception as exc:
        payload = {"ok": False, "tool": TOOL, "report_version": REPORT_VERSION, "generated_at": _utc_now_iso(), "error": str(exc), "error_class": exc.__class__.__name__, "blocked_by": ["pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_dry_run_plan_status_failed"], "read_only": True, "would_send_to_broker": False, "mode_changed": False, "autotrade_resume_authorized": False, "pre_armed_dry_run_authorized": False, "live_authorized": False, "authorization_request_record_execution_authorization_request_recorded": False, "authorization_request_record_execution_authorized": False, "authorization_request_record_execution_requested": False, "authorization_request_record_executed": False, "authorization_request_recorded": False, "approval_record_append_execution_authorized": False, "approval_record_append_execution_requested": False, "approval_record_append_executed": False, "approval_ledger_appended": False, "command_ledger_appended": False, "mode_change_requested": False, "mode_change_authorized": False}
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
