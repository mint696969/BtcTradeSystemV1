# path: ./tools/run_sr_fx_pre_armed_dry_run_authorization_record_persistence_preflight_status.py
# desc: Broker-free S118 authorization record persistence schema and append preflight/status. Status-only; no append execution.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_authorization_record_persistence_preflight_status"
REPORT_VERSION = "pre_armed_dry_run_authorization_record_persistence_preflight_status.s118.v1"
SCHEMA_VERSION = "pre_armed_dry_run_authorization_record.v1"
SUPPORTED_RECORD_KINDS = ("pre_armed_dry_run_authorization_grant_record",)
SUPPORTED_APPEND_SCOPES = (
    "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_PREVIEW_ONLY",
    "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_APPEND_PRECHECK_ONLY",
)
REQUIRED_ACKS = (
    "confirm_s117_authorization_grant_status_reviewed",
    "confirm_authorization_grant_ready_is_not_append_permission",
    "confirm_record_persistence_schema_reviewed",
    "confirm_append_preflight_does_not_write_records",
    "confirm_approval_and_command_ledgers_are_not_appended",
    "confirm_mode_apply_requires_separate_slice",
    "confirm_broker_execution_requires_later_explicit_armed_or_live_boundary",
)
GRANT_FALSE_FIELDS = (
    "authorization_grant_granted",
    "authorization_grant_executed",
    "authorization_grant_recorded",
    "approval_ledger_appended",
    "command_ledger_appended",
    "mode_change_requested",
    "mode_changed",
    "would_send_to_broker",
    "pre_armed_dry_run_authorized",
    "live_authorized",
    "autotrade_resume_authorized",
    "authorization_request_recorded",
    "authorization_record_appended",
    "record_persistence_executed",
    "mode_apply_executed",
)
REQUEST_FALSE_FIELDS = (
    "append_execution_requested",
    "record_write_requested",
    "approval_ledger_append_requested",
    "command_ledger_append_requested",
    "mode_change_requested",
    "mode_apply_requested",
    "broker_execution_requested",
    "restricted_api_requested",
    "real_order_requested",
    "ui_command_button_requested",
    "watchdog_autonomous_execution_requested",
)
OUTPUT_FALSE_FIELDS = (
    "authorization_record_appended",
    "authorization_record_persisted",
    "record_persistence_executed",
    "authorization_grant_recorded",
    "approval_ledger_appended",
    "command_ledger_appended",
    "mode_change_requested",
    "mode_changed",
    "would_send_to_broker",
    "pre_armed_dry_run_authorized",
    "live_authorized",
    "autotrade_resume_authorized",
    "broker_execution_requested",
    "mode_apply_executed",
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


def _nonempty(value: Any) -> bool:
    return bool(str(value or "").strip())


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _append_path_safe(value: Any) -> bool:
    text = str(value or "").replace("\\", "/")
    return bool(text) and text.startswith("tmp/autotrade/authorization_records/") and text.endswith(".jsonl") and ".." not in text


def _schema() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "record_kind": "pre_armed_dry_run_authorization_grant_record",
        "append_only": True,
        "required_fields": [
            "record_id",
            "idempotency_key",
            "source_authorization_grant_status_report_version",
            "source_authorization_grant_status_decision",
            "source_authorization_grant_ready",
            "source_commit_head",
            "requested_scope",
            "operator_identity_present",
            "granted_by_present",
            "safety_boundary_snapshot",
            "created_at",
            "recorded",
            "persisted",
            "executed",
        ],
        "false_fields": list(OUTPUT_FALSE_FIELDS),
    }


def build_pre_armed_dry_run_authorization_record_persistence_preflight_status(*, authorization_grant_status: Mapping[str, Any], record_persistence_request: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    grant = dict(authorization_grant_status)
    request = dict(record_persistence_request)
    grant_ready = grant.get("authorization_grant_ready") is True
    grant_ok = grant.get("ok") is True
    grant_decision = grant.get("decision")
    grant_report_version = grant.get("report_version")
    source_summary = _as_dict(grant.get("source_summary"))
    grant_summary = _as_dict(grant.get("grant_summary"))
    checks = _as_dict(grant.get("checks"))

    grant_blockers: list[str] = []
    if not grant_ok:
        grant_blockers.append("authorization_grant_status_not_ok")
    if not grant_ready:
        grant_blockers.append("authorization_grant_status_not_ready")
        grant_blockers.extend(_as_list(grant.get("authorization_grant_blockers")))
    if not _nonempty(grant_decision):
        grant_blockers.append("authorization_grant_status_decision_required")
    if not _nonempty(grant_report_version):
        grant_blockers.append("authorization_grant_status_report_version_required")
    if grant.get("read_only") is not True or grant.get("status_only") is not True or grant.get("dry_run_only") is not True:
        grant_blockers.append("authorization_grant_status_must_be_read_only_status_dry_run")
    if checks.get("ready_is_not_approval") is not True:
        grant_blockers.append("grant_status_ready_is_not_approval_check_required")
    for key in GRANT_FALSE_FIELDS:
        if grant.get(key) not in (None, False):
            grant_blockers.append(f"grant_forbidden_flag_must_be_false:{key}")

    submitted_acks = _as_list(request.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_ACKS if ack not in submitted_acks]
    request_blockers: list[str] = []
    if request.get("record_persistence_preflight_reviewed") is not True:
        request_blockers.append("record_persistence_preflight_review_not_confirmed")
    if request.get("source_authorization_grant_ready") is not True:
        request_blockers.append("request_source_grant_ready_confirmation_required")
    if request.get("source_authorization_grant_status_decision") != grant_decision:
        request_blockers.append("request_source_grant_decision_mismatch")
    if request.get("source_authorization_grant_status_report_version") != grant_report_version:
        request_blockers.append("request_source_grant_report_version_mismatch")
    if request.get("record_kind") not in SUPPORTED_RECORD_KINDS:
        request_blockers.append("record_kind_not_supported")
    if request.get("requested_append_scope") not in SUPPORTED_APPEND_SCOPES:
        request_blockers.append("requested_append_scope_not_precheck_or_preview")
    if request.get("schema_version") not in (None, SCHEMA_VERSION):
        request_blockers.append("schema_version_mismatch")
    for key in ("source_authorization_grant_status_path", "idempotency_key", "record_id", "requested_by", "requested_at", "operator_identity"):
        if not _nonempty(request.get(key)):
            request_blockers.append(f"{key}_required")
    if not _append_path_safe(request.get("append_only_path")):
        request_blockers.append("append_only_path_must_be_tmp_authorization_records_jsonl")
    request_blockers.extend(f"missing_record_persistence_ack:{ack}" for ack in missing_acks)
    for key in REQUEST_FALSE_FIELDS:
        if request.get(key) not in (None, False):
            request_blockers.append(f"request_forbidden_flag_must_be_false:{key}")

    blockers = _dedupe(grant_blockers + request_blockers)
    ready = bool(grant_ok and grant_ready and not blockers)
    decision = "authorization_record_persistence_preflight_ready_not_appended" if ready else "authorization_record_persistence_preflight_blocked_not_appended"
    schema = _schema()
    payload: dict[str, Any] = {
        "ok": bool(grant_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "record_persistence_preflight_ready": ready,
        "record_persistence_blockers": blockers,
        "read_only": True,
        "status_only": True,
        "preflight_status_only": True,
        "dry_run_only": True,
        "non_authorizing": True,
        "authorization_record_schema": schema,
        "authorization_record_draft": {
            "schema_version": SCHEMA_VERSION,
            "record_kind": request.get("record_kind"),
            "record_id": request.get("record_id"),
            "idempotency_key": request.get("idempotency_key"),
            "append_only_path": request.get("append_only_path"),
            "source_authorization_grant_status_report_version": grant_report_version,
            "source_authorization_grant_status_decision": grant_decision,
            "source_authorization_grant_ready": grant_ready,
            "source_commit_head": source_summary.get("source_commit_head"),
            "requested_scope": grant_summary.get("requested_scope"),
            "operator_identity_present": bool(grant_summary.get("operator_identity_present")),
            "granted_by_present": bool(grant_summary.get("granted_by_present")),
            "created_at": generated_at or _utc_now_iso(),
            "recorded": False,
            "persisted": False,
            "executed": False,
            "append_planned": ready,
            "append_executed": False,
        },
        "source_summary": {
            "authorization_grant_status_report_version": grant_report_version,
            "authorization_grant_status_decision": grant_decision,
            "authorization_grant_ready": grant_ready,
            "source_authorization_request_status_report_version": source_summary.get("source_authorization_request_status_report_version"),
            "source_authorization_request_status_decision": source_summary.get("source_authorization_request_status_decision"),
            "source_commit_head": source_summary.get("source_commit_head"),
        },
        "preflight_summary": {
            "record_kind": request.get("record_kind"),
            "requested_append_scope": request.get("requested_append_scope"),
            "append_only_path": request.get("append_only_path"),
            "idempotency_key_present": _nonempty(request.get("idempotency_key")),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
        },
        "checks": {
            "authorization_grant_status_ok": grant_ok,
            "authorization_grant_ready": grant_ready,
            "grant_ready_is_not_append_permission": True,
            "record_schema_present": True,
            "append_only_path_safe": _append_path_safe(request.get("append_only_path")),
            "record_persistence_request_valid": not request_blockers,
            "no_append_no_ledger_no_mode_no_broker": True,
        },
        "warnings": [
            "record_persistence_preflight_is_status_only",
            "authorization_record_schema_is_preview_only",
            "authorization_record_draft_not_persisted",
            "append_execution_requires_separate_slice",
            "mode_apply_requires_separate_slice",
            "broker_execution_requires_later_explicit_armed_or_live_boundary",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "status_only": True,
            "preflight_status_only": True,
            "read_only": True,
            "dry_run_only": True,
            "final_human_review_required": True,
        },
    }
    for key in OUTPUT_FALSE_FIELDS:
        payload[key] = False
        payload["operator_safety_lock"][key] = False
    return payload


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free S118 authorization record persistence schema/preflight status.")
    parser.add_argument("--authorization-grant-status", required=True)
    parser.add_argument("--record-persistence-request", required=True)
    parser.add_argument("--out", default="")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        grant = _read_json(Path(args.authorization_grant_status))
        request = _read_json(Path(args.record_persistence_request))
        payload = build_pre_armed_dry_run_authorization_record_persistence_preflight_status(authorization_grant_status=grant, record_persistence_request=request)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "read_only": True,
            "status_only": True,
            "preflight_status_only": True,
            "dry_run_only": True,
            "non_authorizing": True,
        }
        for key in OUTPUT_FALSE_FIELDS:
            payload[key] = False
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
