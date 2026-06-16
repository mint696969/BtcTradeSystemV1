# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_evidence_dry_run_validator.py
# desc: Broker-free Pre-Armed Dry Run approval evidence dry-run validator from S56 approval-request/status. Validation only; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_evidence_dry_run_validator"
REPORT_VERSION = "pre_armed_dry_run_approval_evidence_dry_run_validator.v1"
REQUIRED_ACKS = (
    "review_all_runtime_control_evidence",
    "review_all_remaining_execution_boundary_blockers",
    "confirm_no_broker_send_or_mode_change_is_authorized_by_this_packet",
    "confirm_pre_armed_dry_run_authorization_requires_separate_later_slice",
    "confirm_final_human_review_required_before_any_mode_change",
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


def build_pre_armed_dry_run_approval_evidence_dry_run_validator(*, approval_request_status: Mapping[str, Any], approval_evidence: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    status = dict(approval_request_status)
    evidence = dict(approval_evidence)
    request = _as_dict(status.get("approval_request"))
    checklist = _as_list(status.get("human_acknowledgement_checklist") or request.get("human_acknowledgement_checklist"))
    submitted_acks = _as_list(evidence.get("acknowledgements"))
    reason_codes = _as_list(evidence.get("reason_codes"))
    source_ready = bool(request.get("ready_for_human_review"))
    status_ok = status.get("ok") is True
    safety_ok = (
        status.get("read_only") is True
        and status.get("would_send_to_broker") is False
        and status.get("mode_changed") is False
        and status.get("autotrade_resume_authorized") is False
        and status.get("pre_armed_dry_run_authorized") is False
        and status.get("live_authorized") is False
        and status.get("human_approval_recorded") is False
        and status.get("operator_acknowledgement_recorded") is False
        and status.get("approval_ledger_appended") is False
        and status.get("command_ledger_appended") is False
        and status.get("mode_change_requested") is False
        and status.get("mode_change_authorized") is False
    )

    validation_blockers: list[str] = []
    if not status_ok:
        validation_blockers.append("approval_request_status_not_ok")
    if not source_ready:
        validation_blockers.append("approval_request_status_not_ready_for_human_review")
    if not safety_ok:
        validation_blockers.append("source_status_safety_contract_not_clear")
    if str(evidence.get("evidence_id") or "").startswith("approval_evidence_") is False:
        validation_blockers.append("invalid_evidence_id")
    if str(evidence.get("approval_scope") or "") != "PRE_ARMED_DRY_RUN_REVIEW_ONLY":
        validation_blockers.append("approval_scope_not_pre_armed_review_only")
    if str(evidence.get("target_mode") or "") != "PRE_ARMED_DRY_RUN":
        validation_blockers.append("target_mode_not_pre_armed_dry_run")
    if not str(evidence.get("requested_by") or "").strip():
        validation_blockers.append("requested_by_required")
    if not str(evidence.get("requested_at") or "").strip():
        validation_blockers.append("requested_at_required")
    if not str(evidence.get("operator_identity") or "").strip():
        validation_blockers.append("operator_identity_required")
    if evidence.get("human_review_packet_ready") is not True:
        validation_blockers.append("evidence_does_not_confirm_human_review_packet_ready")
    if evidence.get("approval_recording_requested") is not False:
        validation_blockers.append("approval_recording_must_not_be_requested_in_dry_run")
    if evidence.get("command_ledger_append_requested") is not False:
        validation_blockers.append("command_ledger_append_must_not_be_requested_in_dry_run")
    if evidence.get("mode_change_requested") is not False:
        validation_blockers.append("mode_change_must_not_be_requested_in_dry_run")
    missing_acks = [item for item in REQUIRED_ACKS if item not in submitted_acks]
    if missing_acks:
        validation_blockers.extend(f"missing_ack:{item}" for item in missing_acks)
    if checklist and not set(checklist).issubset(set(submitted_acks)):
        validation_blockers.append("submitted_acknowledgements_do_not_cover_source_checklist")
    if "operator_final_human_review" not in reason_codes:
        validation_blockers.append("reason_code_operator_final_human_review_required")
    if "pre_armed_dry_run_review_only" not in reason_codes:
        validation_blockers.append("reason_code_pre_armed_review_only_required")

    validation_blockers = _dedupe(validation_blockers)
    evidence_valid = not validation_blockers
    dry_run_decision = "approval_evidence_dry_run_valid_not_recorded" if evidence_valid else "approval_evidence_dry_run_blocked_not_recorded"
    return {
        "ok": bool(status_ok and safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": dry_run_decision,
        "approval_evidence_valid": evidence_valid,
        "approval_evidence_dry_run_ready": evidence_valid,
        "validation_blockers": validation_blockers,
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
        "dry_run_only": True,
        "source_summary": {
            "source_report_version": status.get("report_version"),
            "source_decision": status.get("decision"),
            "source_status_ok": status_ok,
            "source_ready_for_human_review": source_ready,
            "source_human_approval_recorded": status.get("human_approval_recorded"),
            "source_approval_ledger_appended": status.get("approval_ledger_appended"),
            "source_command_ledger_appended": status.get("command_ledger_appended"),
            "source_mode_change_requested": status.get("mode_change_requested"),
        },
        "evidence_summary": {
            "evidence_id": evidence.get("evidence_id"),
            "approval_scope": evidence.get("approval_scope"),
            "target_mode": evidence.get("target_mode"),
            "requested_by": evidence.get("requested_by"),
            "requested_at": evidence.get("requested_at"),
            "operator_identity_present": bool(str(evidence.get("operator_identity") or "").strip()),
            "acknowledgement_count": len(submitted_acks),
            "reason_codes": reason_codes,
        },
        "required_acknowledgements": list(REQUIRED_ACKS),
        "submitted_acknowledgements": submitted_acks,
        "checks": {
            "source_status_ok": status_ok,
            "source_ready_for_human_review": source_ready,
            "source_safety_contract_clear": safety_ok,
            "evidence_id_valid": str(evidence.get("evidence_id") or "").startswith("approval_evidence_"),
            "approval_scope_review_only": str(evidence.get("approval_scope") or "") == "PRE_ARMED_DRY_RUN_REVIEW_ONLY",
            "target_mode_pre_armed_dry_run": str(evidence.get("target_mode") or "") == "PRE_ARMED_DRY_RUN",
            "required_acknowledgements_present": not missing_acks,
            "approval_recorded_false": True,
            "human_approval_recorded_false": True,
            "operator_acknowledgement_recorded_false": True,
            "approval_ledger_appended_false": True,
            "command_ledger_appended_false": True,
            "mode_change_requested_false": True,
            "mode_change_authorized_false": True,
            "read_only_no_broker_non_authorizing": safety_ok,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "approval_evidence_validator_is_dry_run_only",
            "human_approval_recorded_false",
            "operator_acknowledgement_recorded_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
            "mode_change_authorized_false",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "broker_send_remains_disabled",
            "final_human_review_required_before_any_mode_change",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "dry_run_only": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
            "approval_recorded": False,
            "human_approval_recorded": False,
            "operator_acknowledgement_recorded": False,
            "approval_ledger_appended": False,
            "command_ledger_appended": False,
            "mode_change_requested": False,
            "mode_change_authorized": False,
            "final_human_review_required": True,
        },
        "paths": _as_dict(status.get("paths")),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run validate Pre-Armed Dry Run approval evidence from S56 approval-request/status JSON.")
    parser.add_argument("--approval-request-status", required=True, help="Path to S56 approval-request/status JSON.")
    parser.add_argument("--approval-evidence", required=True, help="Path to proposed approval evidence JSON. Read-only; never appended.")
    parser.add_argument("--out", default="", help="Optional validator output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        status = _read_json(Path(args.approval_request_status))
        evidence = _read_json(Path(args.approval_evidence))
        payload = build_pre_armed_dry_run_approval_evidence_dry_run_validator(approval_request_status=status, approval_evidence=evidence)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_approval_evidence_dry_run_validator_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "dry_run_only": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "pre_armed_dry_run_authorized": False,
                "live_authorized": False,
                "approval_recorded": False,
                "human_approval_recorded": False,
                "operator_acknowledgement_recorded": False,
                "approval_ledger_appended": False,
                "command_ledger_appended": False,
                "mode_change_requested": False,
                "mode_change_authorized": False,
                "final_human_review_required": True,
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
