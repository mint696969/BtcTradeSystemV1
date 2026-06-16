# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_append_preflight_status.py
# desc: Broker-free Pre-Armed Dry Run approval record append preflight/status from S57 validator. Preflight/status only; non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_append_preflight_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_append_preflight_status.v1"


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


def build_pre_armed_dry_run_approval_record_append_preflight_status(*, approval_evidence_validator: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    validator = dict(approval_evidence_validator)
    validator_ok = validator.get("ok") is True
    evidence_valid = validator.get("approval_evidence_valid") is True
    validation_blockers = _as_list(validator.get("validation_blockers"))
    source_summary = _as_dict(validator.get("source_summary"))
    evidence_summary = _as_dict(validator.get("evidence_summary"))
    checks = _as_dict(validator.get("checks"))
    safety_ok = (
        validator.get("read_only") is True
        and validator.get("would_send_to_broker") is False
        and validator.get("mode_changed") is False
        and validator.get("autotrade_resume_authorized") is False
        and validator.get("pre_armed_dry_run_authorized") is False
        and validator.get("live_authorized") is False
        and validator.get("approval_recorded") is False
        and validator.get("human_approval_recorded") is False
        and validator.get("operator_acknowledgement_recorded") is False
        and validator.get("approval_ledger_appended") is False
        and validator.get("command_ledger_appended") is False
        and validator.get("mode_change_requested") is False
        and validator.get("mode_change_authorized") is False
        and validator.get("dry_run_only") is True
    )
    preflight_blockers: list[str] = []
    if not validator_ok:
        preflight_blockers.append("approval_evidence_validator_not_ok")
    if not evidence_valid:
        preflight_blockers.append("approval_evidence_not_valid")
        preflight_blockers.extend(validation_blockers)
    if not safety_ok:
        preflight_blockers.append("validator_safety_contract_not_clear")
    if str(evidence_summary.get("approval_scope") or "") != "PRE_ARMED_DRY_RUN_REVIEW_ONLY":
        preflight_blockers.append("approval_scope_not_review_only")
    if str(evidence_summary.get("target_mode") or "") != "PRE_ARMED_DRY_RUN":
        preflight_blockers.append("target_mode_not_pre_armed_dry_run")
    if not str(evidence_summary.get("evidence_id") or "").startswith("approval_evidence_"):
        preflight_blockers.append("invalid_or_missing_evidence_id")
    if not evidence_summary.get("operator_identity_present"):
        preflight_blockers.append("operator_identity_not_present")
    preflight_blockers = _dedupe(preflight_blockers)
    preflight_ready = bool(validator_ok and evidence_valid and safety_ok and not preflight_blockers)
    decision = "approval_record_append_preflight_ready_not_appended" if preflight_ready else "approval_record_append_preflight_blocked_not_appended"
    return {
        "ok": bool(validator_ok and safety_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "approval_record_append_preflight_ready": preflight_ready,
        "preflight_blockers": preflight_blockers,
        "approval_record_proposed": preflight_ready,
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
        "source_summary": {
            "source_report_version": validator.get("report_version"),
            "source_decision": validator.get("decision"),
            "source_validator_ok": validator_ok,
            "source_approval_evidence_valid": evidence_valid,
            "source_approval_evidence_dry_run_ready": validator.get("approval_evidence_dry_run_ready"),
            "source_human_approval_recorded": validator.get("human_approval_recorded"),
            "source_approval_ledger_appended": validator.get("approval_ledger_appended"),
            "source_command_ledger_appended": validator.get("command_ledger_appended"),
            "source_mode_change_requested": validator.get("mode_change_requested"),
            "source_status_decision": source_summary.get("source_decision"),
            "source_ready_for_human_review": source_summary.get("source_ready_for_human_review"),
        },
        "approval_record_draft": {
            "record_kind": "pre_armed_dry_run_review_approval_record_draft",
            "evidence_id": evidence_summary.get("evidence_id"),
            "approval_scope": evidence_summary.get("approval_scope"),
            "target_mode": evidence_summary.get("target_mode"),
            "requested_by": evidence_summary.get("requested_by"),
            "requested_at": evidence_summary.get("requested_at"),
            "operator_identity_present": bool(evidence_summary.get("operator_identity_present")),
            "reason_codes": _as_list(evidence_summary.get("reason_codes")),
            "persisted": False,
            "status_only": True,
        },
        "checks": {
            "source_validator_ok": validator_ok,
            "source_evidence_valid": evidence_valid,
            "source_safety_contract_clear": safety_ok,
            "preflight_ready": preflight_ready,
            "preflight_blockers_visible_when_blocked": bool(preflight_blockers) if not preflight_ready else True,
            "approval_record_persisted_false": True,
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
            "source_s57_checks": checks,
        },
        "warnings": [
            "approval_record_append_preflight_status_is_informational_only",
            "approval_record_persisted_false",
            "human_approval_recorded_false",
            "operator_acknowledgement_recorded_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
            "mode_change_authorized_false",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "broker_send_remains_disabled",
            "separate_explicit_append_slice_required_before_any_recording",
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
        "paths": _as_dict(validator.get("paths")),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free Pre-Armed Dry Run approval record append preflight/status from S57 validator JSON.")
    parser.add_argument("--approval-evidence-validator", required=True, help="Path to S57 approval evidence dry-run validator JSON.")
    parser.add_argument("--out", default="", help="Optional preflight/status output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        validator = _read_json(Path(args.approval_evidence_validator))
        payload = build_pre_armed_dry_run_approval_record_append_preflight_status(approval_evidence_validator=validator)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_approval_record_append_preflight_status_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "preflight_status_only": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "pre_armed_dry_run_authorized": False,
                "live_authorized": False,
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
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
