# path: ./tools/run_sr_fx_pre_armed_dry_run_auth_request_status_s98.py
# desc: Broker-free Pre-Armed Dry Run authorization request/status from S97 execution gate. Request/status only; non-recording; non-executing; non-authorizing. Short path avoids Windows MAX_PATH.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_status"
REPORT_VERSION = "pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_status.s98.v1"
AUTHORIZATION_SCOPE = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_STATUS_REVIEW_ONLY"
AUTHORIZATION_TARGET = "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_EXECUTION_GATE_REVIEW"
REQUIRED_AUTHORIZATION_ACKS = (
    "confirm_s97_authorization_request_execution_gate_status_reviewed",
    "confirm_authorization_request_status_is_review_only",
    "confirm_this_status_does_not_record_execute_or_authorize_authorization_request",
    "confirm_no_authorization_grant_append_or_mode_change_is_authorized",
    "confirm_separate_explicit_authorization_slice_required_before_any_authorization",
)
FALSE_FIELDS = (
    "authorization_request_status_authorized",
    "authorization_request_status_requested",
    "authorization_request_status_executed",
    "authorization_request_execution_gate_authorized",
    "authorization_request_execution_gate_requested",
    "authorization_request_execution_gate_executed",
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


def build_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_status(*, authorization_request_execution_gate_status: Mapping[str, Any], authorization_request_status_request: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    gate = dict(authorization_request_execution_gate_status)
    request = dict(authorization_request_status_request)
    gate_ok = gate.get("ok") is True
    gate_ready = gate.get("authorization_request_execution_gate_ready") is True
    gate_blockers = _as_list(gate.get("authorization_request_execution_gate_blockers"))
    gate_safety_ok = (
        gate.get("read_only") is True
        and gate.get("would_send_to_broker") is False
        and gate.get("mode_changed") is False
        and gate.get("dry_run_gate_only") is True
        and all(gate.get(name) is False for name in FALSE_FIELDS if name in gate)
    )
    lock = _as_dict(gate.get("operator_safety_lock"))
    lock_ok = (
        lock.get("non_authorizing") is True
        and lock.get("dry_run_gate_only") is True
        and lock.get("read_only") is True
        and lock.get("would_send_to_broker") is False
        and lock.get("mode_changed") is False
    )
    submitted_acks = _as_list(request.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_AUTHORIZATION_ACKS if ack not in submitted_acks]
    request_blockers: list[str] = []
    if request.get("authorization_request_status_reviewed") is not True:
        request_blockers.append("authorization_request_status_review_not_confirmed")
    if request.get("authorization_request_status_requested") is not True:
        request_blockers.append("authorization_request_status_request_not_observed")
    if request.get("authorization_scope") != AUTHORIZATION_SCOPE:
        request_blockers.append("authorization_scope_not_status_review_only")
    if request.get("authorization_target") != AUTHORIZATION_TARGET:
        request_blockers.append("authorization_target_not_authorization_request_execution_gate_review")
    for key in ("requested_by", "requested_at", "operator_identity"):
        if not str(request.get(key) or "").strip():
            request_blockers.append(f"{key}_required")
    false_inputs = {
        "authorization_request_status_authorized": "authorization_request_status_authorization_must_be_false",
        "authorization_request_status_executed": "authorization_request_status_execution_must_be_false",
        "authorization_request_execution_gate_authorized": "authorization_request_execution_gate_authorization_must_be_false",
        "authorization_request_execution_gate_executed": "authorization_request_execution_gate_execution_must_be_false",
        "authorization_request_dry_run_plan_authorized": "authorization_request_dry_run_plan_authorization_must_be_false",
        "authorization_request_dry_run_plan_executed": "authorization_request_dry_run_plan_execution_must_be_false",
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
        if request.get(key) is not False:
            request_blockers.append(blocker)
    request_blockers.extend(f"missing_authorization_request_status_ack:{ack}" for ack in missing_acks)

    status_blockers: list[str] = []
    if not gate_ok:
        status_blockers.append("authorization_request_execution_gate_status_not_ok")
    if not gate_ready:
        status_blockers.append("authorization_request_execution_gate_not_ready")
        status_blockers.extend(gate_blockers)
    if not gate_safety_ok:
        status_blockers.append("authorization_request_execution_gate_safety_contract_not_clear")
    if not lock_ok:
        status_blockers.append("authorization_request_execution_gate_operator_safety_lock_not_clear")
    status_blockers.extend(request_blockers)
    status_blockers = _dedupe(status_blockers)
    ready = bool(gate_ok and gate_ready and gate_safety_ok and lock_ok and not request_blockers and not status_blockers)
    decision = "authorization_request_status_ready_not_authorized_not_recorded_not_executed" if ready else "authorization_request_status_blocked_not_authorized_not_recorded_not_executed"
    source_summary = _as_dict(gate.get("source_summary"))
    payload = {
        "ok": bool(gate_ok and gate_safety_ok and lock_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "authorization_request_status_ready": ready,
        "authorization_request_status_blockers": status_blockers,
        "authorization_request_status_requested_observed": request.get("authorization_request_status_requested") is True,
        "authorization_request_status_authorized": False,
        "authorization_request_status_requested": False,
        "authorization_request_status_executed": False,
        "authorization_request_execution_gate_authorized": False,
        "authorization_request_execution_gate_requested": False,
        "authorization_request_execution_gate_executed": False,
        "authorization_request_dry_run_plan_authorized": False,
        "authorization_request_dry_run_plan_requested": False,
        "authorization_request_dry_run_plan_executed": False,
        "authorization_request_record_execution_authorized": False,
        "authorization_request_record_execution_requested": False,
        "authorization_request_record_executed": False,
        "authorization_request_recorded": False,
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
        "status_only": True,
        "authorization_request_status_summary": {
            "authorization_scope": request.get("authorization_scope"),
            "authorization_target": request.get("authorization_target"),
            "requested_by": request.get("requested_by"),
            "requested_at": request.get("requested_at"),
            "operator_identity_present": bool(str(request.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
        },
        "source_summary": {
            "authorization_request_execution_gate_report_version": gate.get("report_version"),
            "authorization_request_execution_gate_decision": gate.get("decision"),
            "authorization_request_execution_gate_ready": gate_ready,
            "authorization_request_dry_run_plan_decision": source_summary.get("authorization_request_dry_run_plan_decision"),
            "authorization_request_dry_run_plan_ready": source_summary.get("authorization_request_dry_run_plan_ready"),
            "authorization_request_preflight_decision": source_summary.get("authorization_request_preflight_decision"),
            "authorization_request_preflight_ready": source_summary.get("authorization_request_preflight_ready"),
            "authorization_request_status_decision": source_summary.get("authorization_request_status_decision"),
            "authorization_request_status_ready": source_summary.get("authorization_request_status_ready"),
            "evidence_id": source_summary.get("evidence_id"),
        },
        "checks": {
            "authorization_request_execution_gate_status_ok": gate_ok,
            "authorization_request_execution_gate_ready": gate_ready,
            "authorization_request_execution_gate_safety_contract_clear": gate_safety_ok,
            "authorization_request_execution_gate_operator_safety_lock_clear": lock_ok,
            "authorization_request_status_request_valid": not request_blockers,
            "authorization_request_status_ready": ready,
            "read_only_no_broker_non_authorizing": gate_safety_ok and lock_ok,
            "no_record_execution_no_grant_no_append_no_mode_request": True,
        },
        "warnings": [
            "authorization_request_status_is_informational_only",
            "authorization_request_status_authorized_false",
            "authorization_request_status_requested_false",
            "authorization_request_status_executed_false",
            "authorization_request_execution_gate_authorized_false",
            "authorization_request_execution_gate_requested_false",
            "authorization_request_execution_gate_executed_false",
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
            "status_only": True,
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
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run authorization request/status from S97 gate JSON.")
    parser.add_argument("--authorization-request-execution-gate-status", required=True)
    parser.add_argument("--authorization-request-status-request", required=True)
    parser.add_argument("--out", default="")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        gate = _read_json(Path(args.authorization_request_execution_gate_status))
        request = _read_json(Path(args.authorization_request_status_request))
        payload = build_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_status(authorization_request_execution_gate_status=gate, authorization_request_status_request=request)
    except Exception as exc:
        payload = {"ok": False, "tool": TOOL, "report_version": REPORT_VERSION, "generated_at": _utc_now_iso(), "error": str(exc), "error_class": exc.__class__.__name__, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "status_only": True}
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
