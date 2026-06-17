# path: ./tools/run_sr_fx_pre_armed_dry_run_authorization_request_execution_authorization_request_preflight_status.py
# desc: Broker-free Pre-Armed Dry Run authorization request preflight/status from S82 authorization request/status. Preflight/status only; non-recording; non-executing; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_authorization_request_execution_authorization_request_preflight_status"
REPORT_VERSION = "pre_armed_dry_run_authorization_request_execution_authorization_request_preflight_status.s83.v1"
AUTHORIZATION_SCOPE = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_PREFLIGHT_REVIEW_ONLY"
AUTHORIZATION_TARGET = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_STATUS_REVIEW"
REQUIRED_PREFLIGHT_ACKS = (
    "confirm_s82_authorization_request_status_reviewed",
    "confirm_authorization_request_preflight_is_review_only",
    "confirm_this_preflight_does_not_record_execute_or_authorize_authorization_request",
    "confirm_no_authorization_grant_append_or_mode_change_is_authorized",
    "confirm_separate_explicit_authorization_slice_required_before_any_authorization",
)
FALSE_FIELDS = (
    "authorization_request_preflight_authorized",
    "authorization_request_preflight_requested",
    "authorization_request_preflight_executed",
    "authorization_request_status_authorized",
    "authorization_request_status_requested",
    "authorization_request_status_executed",
    "authorization_request_execution_gate_authorized",
    "authorization_request_execution_gate_requested",
    "authorization_request_execution_gate_executed",
    "authorization_request_dry_run_plan_authorized",
    "authorization_request_dry_run_plan_requested",
    "authorization_request_dry_run_plan_executed",
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


def build_pre_armed_dry_run_authorization_request_execution_authorization_request_preflight_status(*, authorization_request_status: Mapping[str, Any], authorization_request_preflight_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    status = dict(authorization_request_status)
    review = dict(authorization_request_preflight_review)
    status_ok = status.get("ok") is True
    status_ready = status.get("authorization_request_status_ready") is True
    status_blockers = _as_list(status.get("authorization_request_status_blockers"))
    status_safety_ok = (
        status.get("read_only") is True
        and status.get("would_send_to_broker") is False
        and status.get("mode_changed") is False
        and status.get("status_only") is True
        and all(status.get(name) is False for name in FALSE_FIELDS if name in status)
    )
    status_lock = _as_dict(status.get("operator_safety_lock"))
    status_lock_ok = (
        status_lock.get("non_authorizing") is True
        and status_lock.get("status_only") is True
        and status_lock.get("read_only") is True
        and status_lock.get("would_send_to_broker") is False
        and status_lock.get("mode_changed") is False
    )

    submitted_acks = _as_list(review.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_PREFLIGHT_ACKS if ack not in submitted_acks]
    review_blockers: list[str] = []
    if review.get("authorization_request_preflight_reviewed") is not True:
        review_blockers.append("authorization_request_preflight_review_not_confirmed")
    if review.get("authorization_request_preflight_requested") is not True:
        review_blockers.append("authorization_request_preflight_request_not_observed")
    if review.get("authorization_scope") != AUTHORIZATION_SCOPE:
        review_blockers.append("authorization_scope_not_preflight_review_only")
    if review.get("authorization_target") != AUTHORIZATION_TARGET:
        review_blockers.append("authorization_target_not_authorization_request_status_review")
    for key in ("requested_by", "requested_at", "operator_identity"):
        if not str(review.get(key) or "").strip():
            review_blockers.append(f"{key}_required")
    false_inputs = {
        "authorization_request_preflight_authorized": "authorization_request_preflight_authorization_must_be_false",
        "authorization_request_preflight_executed": "authorization_request_preflight_execution_must_be_false",
        "authorization_request_status_authorized": "authorization_request_status_authorization_must_be_false",
        "authorization_request_status_executed": "authorization_request_status_execution_must_be_false",
        "authorization_request_execution_gate_authorized": "authorization_request_execution_gate_authorization_must_be_false",
        "authorization_request_execution_gate_executed": "authorization_request_execution_gate_execution_must_be_false",
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
    review_blockers.extend(f"missing_authorization_request_preflight_ack:{ack}" for ack in missing_acks)

    preflight_blockers: list[str] = []
    if not status_ok:
        preflight_blockers.append("authorization_request_status_not_ok")
    if not status_ready:
        preflight_blockers.append("authorization_request_status_not_ready")
        preflight_blockers.extend(status_blockers)
    if not status_safety_ok:
        preflight_blockers.append("authorization_request_status_safety_contract_not_clear")
    if not status_lock_ok:
        preflight_blockers.append("authorization_request_status_operator_safety_lock_not_clear")
    preflight_blockers.extend(review_blockers)
    preflight_blockers = _dedupe(preflight_blockers)
    ready = bool(status_ok and status_ready and status_safety_ok and status_lock_ok and not review_blockers and not preflight_blockers)
    decision = "authorization_request_preflight_status_ready_not_authorized_not_recorded_not_executed" if ready else "authorization_request_preflight_status_blocked_not_authorized_not_recorded_not_executed"
    source_summary = _as_dict(status.get("source_summary"))
    payload = {
        "ok": bool(status_ok and status_safety_ok and status_lock_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "authorization_request_preflight_status_ready": ready,
        "authorization_request_preflight_blockers": preflight_blockers,
        "authorization_request_preflight_requested_observed": review.get("authorization_request_preflight_requested") is True,
        "authorization_request_preflight_authorized": False,
        "authorization_request_preflight_requested": False,
        "authorization_request_preflight_executed": False,
        "authorization_request_status_authorized": False,
        "authorization_request_status_requested": False,
        "authorization_request_status_executed": False,
        "authorization_request_execution_gate_authorized": False,
        "authorization_request_execution_gate_requested": False,
        "authorization_request_execution_gate_executed": False,
        "authorization_request_record_execution_authorized": False,
        "authorization_request_record_execution_requested": False,
        "authorization_request_record_executed": False,
        "authorization_request_recorded": False,
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
        "preflight_status_only": True,
        "authorization_request_preflight_summary": {
            "authorization_scope": review.get("authorization_scope"),
            "authorization_target": review.get("authorization_target"),
            "requested_by": review.get("requested_by"),
            "requested_at": review.get("requested_at"),
            "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
        },
        "source_summary": {
            "authorization_request_status_report_version": status.get("report_version"),
            "authorization_request_status_decision": status.get("decision"),
            "authorization_request_status_ready": status_ready,
            "authorization_request_execution_gate_decision": source_summary.get("authorization_request_execution_gate_decision"),
            "authorization_request_execution_gate_ready": source_summary.get("authorization_request_execution_gate_ready"),
            "authorization_request_dry_run_plan_decision": source_summary.get("authorization_request_dry_run_plan_decision"),
            "authorization_request_dry_run_plan_ready": source_summary.get("authorization_request_dry_run_plan_ready"),
            "authorization_request_preflight_decision": source_summary.get("authorization_request_preflight_decision"),
            "authorization_request_preflight_ready": source_summary.get("authorization_request_preflight_ready"),
            "evidence_id": source_summary.get("evidence_id"),
        },
        "checks": {
            "authorization_request_status_ok": status_ok,
            "authorization_request_status_ready": status_ready,
            "authorization_request_status_safety_contract_clear": status_safety_ok,
            "authorization_request_status_operator_safety_lock_clear": status_lock_ok,
            "authorization_request_preflight_review_valid": not review_blockers,
            "authorization_request_preflight_status_ready": ready,
            "read_only_no_broker_non_authorizing": status_safety_ok and status_lock_ok,
            "no_record_execution_no_grant_no_append_no_mode_request": True,
        },
        "warnings": [
            "authorization_request_preflight_status_is_informational_only",
            "authorization_request_preflight_authorized_false",
            "authorization_request_preflight_requested_false",
            "authorization_request_preflight_executed_false",
            "authorization_request_status_authorized_false",
            "authorization_request_status_requested_false",
            "authorization_request_status_executed_false",
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
            "preflight_status_only": True,
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
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run authorization request preflight/status from S82 status JSON.")
    parser.add_argument("--authorization-request-status", required=True)
    parser.add_argument("--authorization-request-preflight-review", required=True)
    parser.add_argument("--out", default="")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        status = _read_json(Path(args.authorization_request_status))
        review = _read_json(Path(args.authorization_request_preflight_review))
        payload = build_pre_armed_dry_run_authorization_request_execution_authorization_request_preflight_status(authorization_request_status=status, authorization_request_preflight_review=review)
    except Exception as exc:
        payload = {"ok": False, "tool": TOOL, "report_version": REPORT_VERSION, "generated_at": _utc_now_iso(), "error": str(exc), "error_class": exc.__class__.__name__, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "preflight_status_only": True}
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
