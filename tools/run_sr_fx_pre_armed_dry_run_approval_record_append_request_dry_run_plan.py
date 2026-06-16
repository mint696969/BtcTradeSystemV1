# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_request_dry_run_plan.py
# desc: Broker-free Pre-Armed Dry Run approval record append request dry-run plan from S58/S59. Plan/status only; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_request_dry_run_plan"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_request_dry_run_plan.v1"
RECORD_KIND = "pre_armed_dry_run_review_approval_record"


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


def build_pre_armed_dry_run_approval_record_append_request_dry_run_plan(*, append_preflight_status: Mapping[str, Any], approval_record_ledger_status: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    preflight = dict(append_preflight_status)
    ledger = dict(approval_record_ledger_status)
    preflight_ready = preflight.get("approval_record_append_preflight_ready") is True
    preflight_ok = preflight.get("ok") is True
    ledger_ok = ledger.get("ok") is True
    ledger_status_ready = ledger.get("approval_record_ledger_status_ready") is True
    existing_record_observed = ledger.get("ledger_human_approval_records_observed") is True or int(ledger.get("valid_record_count") or 0) > 0
    preflight_blockers = _as_list(preflight.get("preflight_blockers"))
    latest_valid = _as_dict(ledger.get("latest_valid_approval_record"))
    draft = _as_dict(preflight.get("approval_record_draft"))
    source_summary = _as_dict(preflight.get("source_summary"))
    preflight_safety_ok = (
        preflight.get("read_only") is True
        and preflight.get("would_send_to_broker") is False
        and preflight.get("mode_changed") is False
        and preflight.get("approval_record_persisted") is False
        and preflight.get("approval_ledger_appended") is False
        and preflight.get("command_ledger_appended") is False
        and preflight.get("mode_change_requested") is False
        and preflight.get("mode_change_authorized") is False
        and preflight.get("pre_armed_dry_run_authorized") is False
        and preflight.get("live_authorized") is False
        and preflight.get("autotrade_resume_authorized") is False
    )
    ledger_safety_ok = (
        ledger.get("read_only") is True
        and ledger.get("would_send_to_broker") is False
        and ledger.get("mode_changed") is False
        and ledger.get("approval_record_persisted_by_this_tool") is False
        and ledger.get("approval_record_persisted") is False
        and ledger.get("approval_ledger_appended") is False
        and ledger.get("command_ledger_appended") is False
        and ledger.get("mode_change_requested") is False
        and ledger.get("mode_change_authorized") is False
        and ledger.get("pre_armed_dry_run_authorized") is False
        and ledger.get("live_authorized") is False
        and ledger.get("autotrade_resume_authorized") is False
    )
    plan_blockers: list[str] = []
    if not preflight_ok:
        plan_blockers.append("append_preflight_status_not_ok")
    if not preflight_ready:
        plan_blockers.append("append_preflight_not_ready")
        plan_blockers.extend(preflight_blockers)
    if not ledger_ok:
        plan_blockers.append("approval_record_ledger_status_not_ok")
    if not ledger_status_ready:
        plan_blockers.append("approval_record_ledger_status_not_ready")
    if not preflight_safety_ok:
        plan_blockers.append("append_preflight_safety_contract_not_clear")
    if not ledger_safety_ok:
        plan_blockers.append("ledger_status_safety_contract_not_clear")
    if existing_record_observed:
        plan_blockers.append("approval_record_already_observed_in_ledger")
    if str(draft.get("record_kind") or "") != "pre_armed_dry_run_review_approval_record_draft":
        plan_blockers.append("approval_record_draft_missing_or_invalid")
    if str(draft.get("approval_scope") or "") != "PRE_ARMED_DRY_RUN_REVIEW_ONLY":
        plan_blockers.append("approval_scope_not_review_only")
    if str(draft.get("target_mode") or "") != "PRE_ARMED_DRY_RUN":
        plan_blockers.append("target_mode_not_pre_armed_dry_run")
    if not str(draft.get("evidence_id") or "").startswith("approval_evidence_"):
        plan_blockers.append("invalid_or_missing_evidence_id")
    if not draft.get("operator_identity_present"):
        plan_blockers.append("operator_identity_not_present")
    plan_blockers = _dedupe(plan_blockers)
    plan_ready = bool(preflight_ok and preflight_ready and ledger_ok and ledger_status_ready and preflight_safety_ok and ledger_safety_ok and not existing_record_observed and not plan_blockers)
    decision = "approval_record_append_request_dry_run_plan_ready_not_submitted" if plan_ready else "approval_record_append_request_dry_run_plan_blocked_not_submitted"
    record_id = "approval_record_dry_run_plan_" + str(draft.get("evidence_id") or "missing_evidence")
    return {
        "ok": bool(preflight_ok and ledger_ok and preflight_safety_ok and ledger_safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "approval_record_append_request_plan_ready": plan_ready,
        "plan_blockers": plan_blockers,
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
        "append_request_draft": {
            "request_kind": "pre_armed_dry_run_approval_record_append_request_draft",
            "record_kind": RECORD_KIND,
            "record_id": record_id,
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
        },
        "source_summary": {
            "preflight_report_version": preflight.get("report_version"),
            "preflight_decision": preflight.get("decision"),
            "preflight_ready": preflight_ready,
            "ledger_report_version": ledger.get("report_version"),
            "ledger_decision": ledger.get("decision"),
            "ledger_status_ready": ledger_status_ready,
            "existing_record_observed": existing_record_observed,
            "latest_valid_record_id": latest_valid.get("record_id"),
            "source_status_decision": source_summary.get("source_status_decision"),
            "source_ready_for_human_review": source_summary.get("source_ready_for_human_review"),
        },
        "checks": {
            "append_preflight_ok": preflight_ok,
            "append_preflight_ready": preflight_ready,
            "ledger_status_ok": ledger_ok,
            "ledger_status_ready": ledger_status_ready,
            "no_existing_valid_approval_record": not existing_record_observed,
            "preflight_safety_contract_clear": preflight_safety_ok,
            "ledger_safety_contract_clear": ledger_safety_ok,
            "plan_ready": plan_ready,
            "plan_blockers_visible_when_blocked": bool(plan_blockers) if not plan_ready else True,
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
            "read_only_no_broker_non_authorizing": preflight_safety_ok and ledger_safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "approval_record_append_request_dry_run_plan_is_informational_only",
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
            "dry_run_plan_only": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run approval record append request dry-run plan/status from S58/S59 JSON.")
    parser.add_argument("--append-preflight-status", required=True, help="Path to S58 approval record append preflight/status JSON.")
    parser.add_argument("--approval-record-ledger-status", required=True, help="Path to S59 approval record ledger status JSON.")
    parser.add_argument("--out", default="", help="Optional dry-run plan output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        preflight = _read_json(Path(args.append_preflight_status))
        ledger = _read_json(Path(args.approval_record_ledger_status))
        payload = build_pre_armed_dry_run_approval_record_append_request_dry_run_plan(append_preflight_status=preflight, approval_record_ledger_status=ledger)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_approval_record_append_request_dry_run_plan_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
