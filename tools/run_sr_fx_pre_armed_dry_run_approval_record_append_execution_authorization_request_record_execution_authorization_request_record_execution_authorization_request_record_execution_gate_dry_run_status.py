# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_status.py
# desc: Broker-free Pre-Armed Dry Run authorization request record execution authorization request record execution authorization request record execution gate dry-run/status from S72 plan. Gate/status only; non-recording; non-executing; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_status.v1"
REQUIRED_GATE_ACKS = (
    "confirm_s72_record_execution_authorization_request_record_execution_authorization_request_record_dry_run_plan_status_reviewed",
    "confirm_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_is_review_only",
    "confirm_this_gate_does_not_record_or_execute_authorization_request",
    "confirm_no_record_execution_authorization_grant_append_or_mode_change_is_authorized",
    "confirm_separate_explicit_record_execution_slice_required_before_any_recording",
)
FALSE_FIELDS = (
    "authorization_request_record_execution_authorization_request_record_execution_authorization_request_recorded",
    "authorization_request_record_execution_authorization_request_record_execution_authorized",
    "authorization_request_record_execution_authorization_request_record_execution_requested",
    "authorization_request_record_execution_authorization_request_record_executed",
    "authorization_request_record_execution_authorization_request_recorded",
    "authorization_request_record_execution_authorized",
    "authorization_request_record_execution_requested",
    "authorization_request_record_executed",
    "approval_record_append_execution_authorization_request_recorded",
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


def build_pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_status(*, record_dry_run_plan_status: Mapping[str, Any], record_execution_gate_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    plan = dict(record_dry_run_plan_status)
    review = dict(record_execution_gate_review)
    plan_ok = plan.get("ok") is True
    plan_ready = plan.get("authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_dry_run_plan_ready") is True
    plan_request_observed = plan.get("record_execution_authorization_request_record_dry_run_plan_requested_observed") is True
    plan_blockers = _as_list(plan.get("record_execution_authorization_request_record_dry_run_plan_blockers"))
    draft = _as_dict(plan.get("authorization_request_record_execution_authorization_request_record_draft"))
    source_summary = _as_dict(plan.get("source_summary"))
    plan_safety_ok = (
        plan.get("read_only") is True
        and plan.get("would_send_to_broker") is False
        and plan.get("mode_changed") is False
        and plan.get("dry_run_plan_only") is True
        and all(plan.get(name) is False for name in FALSE_FIELDS if name in plan)
    )
    submitted_acks = _as_list(review.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_GATE_ACKS if ack not in submitted_acks]
    review_blockers: list[str] = []
    if review.get("record_execution_gate_reviewed") is not True:
        review_blockers.append("record_execution_gate_review_not_confirmed")
    if not str(review.get("operator_identity") or "").strip():
        review_blockers.append("operator_identity_required")
    false_inputs = {
        "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_requested": "record_execution_request_must_be_false_in_dry_run_gate",
        "authorization_request_record_execution_authorization_request_record_execution_authorization_request_recorded": "authorization_request_record_recorded_must_be_false_in_dry_run_gate",
        "authorization_request_record_execution_authorization_request_record_execution_authorized": "record_execution_authorization_grant_must_be_false_in_dry_run_gate",
        "authorization_request_record_execution_authorization_request_record_execution_requested": "record_execution_request_must_be_false_in_dry_run_gate",
        "authorization_request_record_execution_authorization_request_record_executed": "record_execution_must_be_false_in_dry_run_gate",
        "authorization_request_recorded": "authorization_request_recorded_must_be_false_in_dry_run_gate",
        "approval_record_append_execution_authorized": "append_execution_authorization_grant_must_be_false_in_dry_run_gate",
        "approval_record_append_execution_requested": "append_execution_request_must_be_false_in_dry_run_gate",
        "approval_record_append_executed": "append_execution_must_be_false_in_dry_run_gate",
        "approval_ledger_append_requested": "approval_ledger_append_request_must_be_false_in_dry_run_gate",
        "command_ledger_append_requested": "command_ledger_append_request_must_be_false_in_dry_run_gate",
        "mode_change_requested": "mode_change_request_must_be_false_in_dry_run_gate",
    }
    for key, blocker in false_inputs.items():
        if review.get(key) is not False:
            review_blockers.append(blocker)
    review_blockers.extend(f"missing_record_execution_gate_ack:{ack}" for ack in missing_acks)

    gate_blockers: list[str] = []
    if not plan_ok:
        gate_blockers.append("record_execution_authorization_request_record_dry_run_plan_status_not_ok")
    if not plan_ready:
        gate_blockers.append("record_execution_authorization_request_record_dry_run_plan_not_ready")
        gate_blockers.extend(plan_blockers)
    if not plan_request_observed:
        gate_blockers.append("record_execution_authorization_request_record_dry_run_plan_request_not_observed")
    if not plan_safety_ok:
        gate_blockers.append("record_execution_authorization_request_record_dry_run_plan_safety_contract_not_clear")
    if draft.get("recorded") is not False or draft.get("persisted") is not False or draft.get("authorized") is not False or draft.get("executed") is not False:
        gate_blockers.append("authorization_request_record_execution_authorization_request_record_draft_not_dry_run_safe")
    gate_blockers.extend(review_blockers)
    gate_blockers = _dedupe(gate_blockers)
    gate_ready = bool(plan_ok and plan_ready and plan_request_observed and plan_safety_ok and not review_blockers and not gate_blockers)
    decision = "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_ready_not_executed" if gate_ready else "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_blocked_not_executed"
    payload = {
        "ok": bool(plan_ok and plan_safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_ready": gate_ready,
        "record_execution_gate_blockers": gate_blockers,
        "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_requested": False,
        "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_executed": False,
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
        "dry_run_gate_only": True,
        "record_execution_gate_review_summary": {
            "record_execution_gate_reviewed": review.get("record_execution_gate_reviewed") is True,
            "operator_identity_present": bool(str(review.get("operator_identity") or "").strip()),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
        },
        "authorization_request_record_execution_authorization_request_record_draft": {
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
            "record_dry_run_plan_report_version": plan.get("report_version"),
            "record_dry_run_plan_decision": plan.get("decision"),
            "record_dry_run_plan_ready": plan_ready,
            "record_dry_run_plan_request_observed": plan_request_observed,
            "record_preflight_decision": source_summary.get("record_preflight_decision"),
            "record_preflight_ready": source_summary.get("record_preflight_ready"),
            "record_execution_authorization_request_decision": source_summary.get("record_execution_authorization_request_decision"),
            "record_execution_authorization_request_ready": source_summary.get("record_execution_authorization_request_ready"),
            "record_execution_gate_decision": source_summary.get("record_execution_gate_decision"),
            "record_execution_gate_ready": source_summary.get("record_execution_gate_ready"),
            "evidence_id": source_summary.get("evidence_id"),
        },
        "checks": {
            "record_dry_run_plan_status_ok": plan_ok,
            "record_dry_run_plan_ready": plan_ready,
            "record_dry_run_plan_request_observed": plan_request_observed,
            "record_dry_run_plan_safety_contract_clear": plan_safety_ok,
            "record_execution_gate_review_valid": not review_blockers,
            "record_execution_gate_ready": gate_ready,
            "read_only_no_broker_non_authorizing": plan_safety_ok,
            "no_record_execution_no_grant_no_append_no_mode_request": True,
        },
        "warnings": [
            "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_status_is_informational_only",
            "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_requested_false",
            "authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_executed_false",
            "authorization_request_record_execution_authorization_request_record_execution_authorization_request_recorded_false",
            "authorization_request_record_execution_authorization_request_record_execution_authorized_false",
            "authorization_request_recorded_false",
            "approval_record_append_execution_authorized_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "separate_explicit_record_execution_slice_required_before_any_recording",
        ],
        "operator_safety_lock": {"non_authorizing": True, "dry_run_gate_only": True, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "final_human_review_required": True},
    }
    for name in FALSE_FIELDS:
        payload[name] = False
        payload["operator_safety_lock"][name] = False
    return payload


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run authorization request record execution authorization request record execution authorization request record execution gate dry-run/status from S72 JSON.")
    parser.add_argument("--record-dry-run-plan-status", required=True)
    parser.add_argument("--record-execution-gate-review", required=True)
    parser.add_argument("--out", default="")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        plan = _read_json(Path(args.record_dry_run_plan_status))
        review = _read_json(Path(args.record_execution_gate_review))
        payload = build_pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_gate_dry_run_status(record_dry_run_plan_status=plan, record_execution_gate_review=review)
    except Exception as exc:
        payload = {"ok": False, "tool": TOOL, "report_version": REPORT_VERSION, "generated_at": _utc_now_iso(), "error": str(exc), "error_class": exc.__class__.__name__, "read_only": True, "would_send_to_broker": False, "mode_changed": False}
        for name in FALSE_FIELDS:
            payload[name] = False
        payload["authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_execution_requested"] = False
        payload["authorization_request_record_execution_authorization_request_record_execution_authorization_request_record_executed"] = False
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
