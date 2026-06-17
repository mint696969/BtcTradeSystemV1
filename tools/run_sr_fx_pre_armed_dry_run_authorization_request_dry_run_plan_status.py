# path: ./tools/run_sr_fx_pre_armed_dry_run_authorization_request_dry_run_plan_status.py
# desc: Broker-free Pre-Armed Dry Run authorization request dry-run plan/status from S79 preflight/status. Plan/status only; non-recording; non-executing; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_authorization_request_dry_run_plan_status"
REPORT_VERSION = "pre_armed_dry_run_authorization_request_dry_run_plan_status.s80.v1"
PLAN_SCOPE = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_DRY_RUN_PLAN_REVIEW_ONLY"
PLAN_TARGET = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_PREFLIGHT_STATUS_REVIEW"
REQUIRED_PLAN_ACKS = (
    "confirm_s79_authorization_request_preflight_status_reviewed",
    "confirm_authorization_request_dry_run_plan_is_review_only",
    "confirm_this_plan_does_not_record_execute_or_authorize_authorization_request",
    "confirm_no_authorization_grant_append_or_mode_change_is_authorized",
    "confirm_separate_explicit_authorization_slice_required_before_any_authorization",
)
FALSE_FIELDS = (
    "authorization_request_dry_run_plan_authorized",
    "authorization_request_dry_run_plan_requested",
    "authorization_request_dry_run_plan_executed",
    "authorization_request_preflight_authorized",
    "authorization_request_preflight_requested",
    "authorization_request_preflight_executed",
    "authorization_request_record_execution_authorization_requested",
    "authorization_request_record_execution_authorized",
    "authorization_request_record_execution_requested",
    "authorization_request_record_executed",
    "authorization_request_recorded",
    "approval_record_append_execution_authorized",
    "approval_record_append_execution_requested",
    "approval_record_append_executed",
    "approval_ledger_appended",
    "command_ledger_appended",
    "mode_change_requested",
    "mode_change_authorized",
    "pre_armed_dry_run_authorized",
    "live_authorized",
    "autotrade_resume_authorized",
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


def build_pre_armed_dry_run_authorization_request_dry_run_plan_status(*, authorization_request_preflight_status: Mapping[str, Any], authorization_request_dry_run_plan_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    preflight = dict(authorization_request_preflight_status)
    review = dict(authorization_request_dry_run_plan_review)
    preflight_ok = preflight.get("ok") is True
    preflight_ready = preflight.get("authorization_request_preflight_status_ready") is True
    preflight_blockers = _as_list(preflight.get("authorization_request_preflight_blockers"))
    preflight_safety_ok = (
        preflight.get("read_only") is True
        and preflight.get("would_send_to_broker") is False
        and preflight.get("mode_changed") is False
        and preflight.get("preflight_status_only") is True
        and all(preflight.get(name) is False for name in FALSE_FIELDS if name in preflight)
    )
    lock = _as_dict(preflight.get("operator_safety_lock"))
    lock_ok = (
        lock.get("non_authorizing") is True
        and lock.get("preflight_status_only") is True
        and lock.get("read_only") is True
        and lock.get("would_send_to_broker") is False
        and lock.get("mode_changed") is False
    )
    submitted_acks = _as_list(review.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_PLAN_ACKS if ack not in submitted_acks]
    review_blockers: list[str] = []
    if review.get("authorization_request_dry_run_plan_reviewed") is not True:
        review_blockers.append("authorization_request_dry_run_plan_review_not_confirmed")
    if review.get("authorization_request_dry_run_plan_requested") is not True:
        review_blockers.append("authorization_request_dry_run_plan_request_not_observed")
    if review.get("authorization_scope") != PLAN_SCOPE:
        review_blockers.append("authorization_scope_not_dry_run_plan_review_only")
    if review.get("authorization_target") != PLAN_TARGET:
        review_blockers.append("authorization_target_not_authorization_request_preflight_status_review")
    for key in ("requested_by", "requested_at", "operator_identity"):
        if not str(review.get(key) or "").strip():
            review_blockers.append(f"{key}_required")
    false_inputs = {
        "authorization_request_dry_run_plan_authorized": "authorization_request_dry_run_plan_authorization_must_be_false",
        "authorization_request_dry_run_plan_executed": "authorization_request_dry_run_plan_execution_must_be_false",
        "authorization_request_preflight_authorized": "authorization_request_preflight_authorization_must_be_false",
        "authorization_request_preflight_executed": "authorization_request_preflight_execution_must_be_false",
        "authorization_request_record_execution_authorized": "record_execution_authorization_grant_must_be_false",
        "authorization_request_record_execution_requested": "record_execution_request_must_be_false",
        "authorization_request_record_executed": "record_execution_must_be_false",
        "authorization_request_recorded": "authorization_request_recorded_must_be_false",
        "approval_record_append_execution_authorized": "append_execution_authorization_grant_must_be_false",
        "approval_record_append_execution_requested": "append_execution_request_must_be_false",
        "approval_record_append_executed": "append_execution_must_be_false",
        "approval_ledger_append_requested": "approval_ledger_append_request_must_be_false",
        "command_ledger_append_requested": "command_ledger_append_request_must_be_false",
        "mode_change_requested": "mode_change_request_must_be_false",
    }
    for key, blocker in false_inputs.items():
        if review.get(key) is not False:
            review_blockers.append(blocker)
    review_blockers.extend(f"missing_authorization_request_dry_run_plan_ack:{ack}" for ack in missing_acks)

    plan_blockers: list[str] = []
    if not preflight_ok:
        plan_blockers.append("authorization_request_preflight_status_not_ok")
    if not preflight_ready:
        plan_blockers.append("authorization_request_preflight_status_not_ready")
        plan_blockers.extend(preflight_blockers)
    if not preflight_safety_ok:
        plan_blockers.append("authorization_request_preflight_safety_contract_not_clear")
    if not lock_ok:
        plan_blockers.append("authorization_request_preflight_operator_safety_lock_not_clear")
    plan_blockers.extend(review_blockers)
    plan_blockers = _dedupe(plan_blockers)
    ready = bool(preflight_ok and preflight_ready and preflight_safety_ok and lock_ok and not review_blockers and not plan_blockers)
    decision = "authorization_request_dry_run_plan_status_ready_not_authorized_not_recorded_not_executed" if ready else "authorization_request_dry_run_plan_status_blocked_not_authorized_not_recorded_not_executed"
    source_summary = _as_dict(preflight.get("source_summary"))
    payload = {
        "ok": bool(preflight_ok and preflight_safety_ok and lock_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "authorization_request_dry_run_plan_status_ready": ready,
        "authorization_request_dry_run_plan_blockers": plan_blockers,
        "authorization_request_dry_run_plan_requested_observed": review.get("authorization_request_dry_run_plan_requested") is True,
        "authorization_request_dry_run_plan_authorized": False,
        "authorization_request_dry_run_plan_requested": False,
        "authorization_request_dry_run_plan_executed": False,
        "authorization_request_preflight_authorized": False,
        "authorization_request_preflight_requested": False,
        "authorization_request_preflight_executed": False,
        "authorization_request_record_execution_authorized": False,
        "authorization_request_record_execution_requested": False,
        "authorization_request_record_executed": False,
        "authorization_request_recorded": False,
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
        "dry_run_plan_only": True,
        "authorization_request_dry_run_plan_summary": {
            "authorization_scope": review.get("authorization_scope"),
            "authorization_target": review.get("authorization_target"),
            "requested_by": review.get("requested_by"),
            "requested_at": review.get("requested_at"),
            "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
        },
        "source_summary": {
            "authorization_request_preflight_report_version": preflight.get("report_version"),
            "authorization_request_preflight_decision": preflight.get("decision"),
            "authorization_request_preflight_ready": preflight_ready,
            "authorization_request_status_report_version": source_summary.get("authorization_request_status_report_version"),
            "authorization_request_status_decision": source_summary.get("authorization_request_status_decision"),
            "authorization_request_status_ready": source_summary.get("authorization_request_status_ready"),
            "record_execution_gate_decision": source_summary.get("record_execution_gate_decision"),
            "record_execution_gate_ready": source_summary.get("record_execution_gate_ready"),
            "record_dry_run_plan_decision": source_summary.get("record_dry_run_plan_decision"),
            "record_dry_run_plan_ready": source_summary.get("record_dry_run_plan_ready"),
            "evidence_id": source_summary.get("evidence_id"),
        },
        "checks": {
            "authorization_request_preflight_status_ok": preflight_ok,
            "authorization_request_preflight_status_ready": preflight_ready,
            "authorization_request_preflight_safety_contract_clear": preflight_safety_ok,
            "authorization_request_preflight_operator_safety_lock_clear": lock_ok,
            "authorization_request_dry_run_plan_review_valid": not review_blockers,
            "authorization_request_dry_run_plan_status_ready": ready,
            "read_only_no_broker_non_authorizing": preflight_safety_ok and lock_ok,
            "no_record_execution_no_grant_no_append_no_mode_request": True,
        },
        "warnings": [
            "authorization_request_dry_run_plan_status_is_informational_only",
            "authorization_request_dry_run_plan_authorized_false",
            "authorization_request_dry_run_plan_requested_false",
            "authorization_request_dry_run_plan_executed_false",
            "authorization_request_preflight_authorized_false",
            "authorization_request_preflight_requested_false",
            "authorization_request_preflight_executed_false",
            "authorization_request_recorded_false",
            "approval_record_append_execution_authorized_false",
            "approval_record_append_execution_requested_false",
            "approval_record_append_executed_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "separate_explicit_authorization_slice_required_before_any_authorization",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "dry_run_plan_only": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "final_human_review_required": True,
        },
    }
    for name in FALSE_FIELDS:
        payload[name] = False
        payload["operator_safety_lock"][name] = False
    return payload


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run authorization request dry-run plan/status from S79 preflight JSON.")
    parser.add_argument("--authorization-request-preflight-status", required=True)
    parser.add_argument("--authorization-request-dry-run-plan-review", required=True)
    parser.add_argument("--out", default="")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        preflight = _read_json(Path(args.authorization_request_preflight_status))
        review = _read_json(Path(args.authorization_request_dry_run_plan_review))
        payload = build_pre_armed_dry_run_authorization_request_dry_run_plan_status(authorization_request_preflight_status=preflight, authorization_request_dry_run_plan_review=review)
    except Exception as exc:
        payload = {"ok": False, "tool": TOOL, "report_version": REPORT_VERSION, "generated_at": _utc_now_iso(), "error": str(exc), "error_class": exc.__class__.__name__, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "dry_run_plan_only": True}
        for name in FALSE_FIELDS:
            payload[name] = False
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
