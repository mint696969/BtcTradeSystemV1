# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_gate_dry_run_status.py
# desc: Broker-free Pre-Armed Dry Run approval record append execution gate dry-run/status from S60 plan. Gate/status only; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_execution_gate_dry_run_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_execution_gate_dry_run_status.v1"
REQUIRED_GATE_ACKS = (
    "confirm_s60_append_request_plan_reviewed",
    "confirm_no_approval_record_append_is_authorized_by_this_gate",
    "confirm_no_command_ledger_append_or_mode_change_is_authorized_by_this_gate",
    "confirm_duplicate_ledger_status_reviewed_before_any_future_append",
    "confirm_separate_explicit_execution_slice_required_before_any_recording",
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


def build_pre_armed_dry_run_approval_record_append_execution_gate_dry_run_status(*, append_request_plan: Mapping[str, Any], execution_gate_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    plan = dict(append_request_plan)
    review = dict(execution_gate_review)
    plan_ok = plan.get("ok") is True
    plan_ready = plan.get("approval_record_append_request_plan_ready") is True
    plan_blockers = _as_list(plan.get("plan_blockers"))
    draft = _as_dict(plan.get("append_request_draft"))
    source_summary = _as_dict(plan.get("source_summary"))
    submitted_false = plan.get("approval_record_append_request_submitted") is False
    persisted_false = plan.get("approval_record_append_request_persisted") is False
    plan_safety_ok = (
        plan.get("read_only") is True
        and plan.get("would_send_to_broker") is False
        and plan.get("mode_changed") is False
        and plan.get("approval_record_append_request_submitted") is False
        and plan.get("approval_record_append_request_persisted") is False
        and plan.get("approval_record_persisted_by_this_tool") is False
        and plan.get("approval_record_persisted") is False
        and plan.get("approval_ledger_appended") is False
        and plan.get("command_ledger_appended") is False
        and plan.get("mode_change_requested") is False
        and plan.get("mode_change_authorized") is False
        and plan.get("pre_armed_dry_run_authorized") is False
        and plan.get("live_authorized") is False
        and plan.get("autotrade_resume_authorized") is False
        and plan.get("dry_run_plan_only") is True
    )
    submitted_acks = _as_list(review.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_GATE_ACKS if ack not in submitted_acks]
    review_blockers: list[str] = []
    if review.get("execution_gate_reviewed") is not True:
        review_blockers.append("execution_gate_review_not_confirmed")
    if not str(review.get("operator_identity") or "").strip():
        review_blockers.append("operator_identity_required")
    if review.get("approval_record_append_execution_requested") is not False:
        review_blockers.append("approval_record_append_execution_request_must_be_false_in_dry_run_gate")
    if review.get("command_ledger_append_requested") is not False:
        review_blockers.append("command_ledger_append_request_must_be_false_in_dry_run_gate")
    if review.get("mode_change_requested") is not False:
        review_blockers.append("mode_change_request_must_be_false_in_dry_run_gate")
    review_blockers.extend(f"missing_gate_ack:{ack}" for ack in missing_acks)
    gate_blockers: list[str] = []
    if not plan_ok:
        gate_blockers.append("append_request_plan_not_ok")
    if not plan_ready:
        gate_blockers.append("append_request_plan_not_ready")
        gate_blockers.extend(plan_blockers)
    if not submitted_false:
        gate_blockers.append("append_request_already_submitted")
    if not persisted_false:
        gate_blockers.append("append_request_already_persisted")
    if not plan_safety_ok:
        gate_blockers.append("append_request_plan_safety_contract_not_clear")
    if str(draft.get("request_kind") or "") != "pre_armed_dry_run_approval_record_append_request_draft":
        gate_blockers.append("append_request_draft_missing_or_invalid")
    if str(draft.get("approval_scope") or "") != "PRE_ARMED_DRY_RUN_REVIEW_ONLY":
        gate_blockers.append("approval_scope_not_review_only")
    if str(draft.get("target_mode") or "") != "PRE_ARMED_DRY_RUN":
        gate_blockers.append("target_mode_not_pre_armed_dry_run")
    if not str(draft.get("evidence_id") or "").startswith("approval_evidence_"):
        gate_blockers.append("invalid_or_missing_evidence_id")
    if not draft.get("operator_identity_present"):
        gate_blockers.append("source_operator_identity_not_present")
    gate_blockers.extend(review_blockers)
    gate_blockers = _dedupe(gate_blockers)
    gate_ready = bool(plan_ok and plan_ready and plan_safety_ok and submitted_false and persisted_false and not review_blockers and not gate_blockers)
    decision = "approval_record_append_execution_gate_dry_run_ready_not_executed" if gate_ready else "approval_record_append_execution_gate_dry_run_blocked_not_executed"
    return {
        "ok": bool(plan_ok and plan_safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "approval_record_append_execution_gate_ready": gate_ready,
        "execution_gate_blockers": gate_blockers,
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
        "dry_run_gate_only": True,
        "gate_review_summary": {
            "execution_gate_reviewed": review.get("execution_gate_reviewed") is True,
            "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
            "approval_record_append_execution_requested_input": review.get("approval_record_append_execution_requested"),
            "command_ledger_append_requested_input": review.get("command_ledger_append_requested"),
            "mode_change_requested_input": review.get("mode_change_requested"),
        },
        "append_request_draft": {
            "request_kind": draft.get("request_kind"),
            "record_kind": draft.get("record_kind"),
            "record_id": draft.get("record_id"),
            "evidence_id": draft.get("evidence_id"),
            "approval_scope": draft.get("approval_scope"),
            "target_mode": draft.get("target_mode"),
            "requested_by": draft.get("requested_by"),
            "requested_at": draft.get("requested_at"),
            "operator_identity_present": bool(draft.get("operator_identity_present")),
            "reason_codes": _as_list(draft.get("reason_codes")),
            "dry_run_only": True,
            "submitted": False,
            "persisted": False,
            "executed": False,
        },
        "source_summary": {
            "append_request_plan_report_version": plan.get("report_version"),
            "append_request_plan_decision": plan.get("decision"),
            "append_request_plan_ready": plan_ready,
            "preflight_decision": source_summary.get("preflight_decision"),
            "ledger_decision": source_summary.get("ledger_decision"),
            "existing_record_observed": source_summary.get("existing_record_observed"),
            "latest_valid_record_id": source_summary.get("latest_valid_record_id"),
            "source_status_decision": source_summary.get("source_status_decision"),
            "source_ready_for_human_review": source_summary.get("source_ready_for_human_review"),
        },
        "checks": {
            "append_request_plan_ok": plan_ok,
            "append_request_plan_ready": plan_ready,
            "append_request_plan_safety_contract_clear": plan_safety_ok,
            "append_request_not_submitted": submitted_false,
            "append_request_not_persisted": persisted_false,
            "execution_gate_review_valid": not review_blockers,
            "execution_gate_ready": gate_ready,
            "execution_gate_blockers_visible_when_blocked": bool(gate_blockers) if not gate_ready else True,
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
            "read_only_no_broker_non_authorizing": plan_safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "approval_record_append_execution_gate_dry_run_status_is_informational_only",
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
            "dry_run_gate_only": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run approval record append execution gate dry-run/status from S60 plan JSON.")
    parser.add_argument("--append-request-plan", required=True, help="Path to S60 approval record append request dry-run plan JSON.")
    parser.add_argument("--execution-gate-review", required=True, help="Path to execution gate review JSON. Must request no execution in this dry-run slice.")
    parser.add_argument("--out", default="", help="Optional dry-run gate output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        plan = _read_json(Path(args.append_request_plan))
        review = _read_json(Path(args.execution_gate_review))
        payload = build_pre_armed_dry_run_approval_record_append_execution_gate_dry_run_status(append_request_plan=plan, execution_gate_review=review)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_approval_record_append_execution_gate_dry_run_status_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
