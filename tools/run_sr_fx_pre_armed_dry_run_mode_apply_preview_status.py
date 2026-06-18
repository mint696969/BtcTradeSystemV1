# path: ./tools/run_sr_fx_pre_armed_dry_run_mode_apply_preview_status.py
# desc: Broker-free S119 Pre-Armed Dry Run mode apply preview/status. Preview-only; no mode apply or command ledger append.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_mode_apply_preview_status"
REPORT_VERSION = "pre_armed_dry_run_mode_apply_preview_status.s119.v1"
SUPPORTED_CURRENT_MODES = ("SHADOW", "PAPER_OR_REPLAY")
SUPPORTED_TARGET_MODES = ("PRE_ARMED_DRY_RUN",)
REQUIRED_ACKS = (
    "confirm_s118_record_persistence_preflight_reviewed",
    "confirm_record_persistence_preflight_ready_is_not_mode_permission",
    "confirm_mode_apply_preview_is_read_only",
    "confirm_preview_does_not_append_command_ledger",
    "confirm_preview_does_not_append_mode_state",
    "confirm_preview_does_not_send_orders",
    "confirm_actual_mode_apply_requires_separate_slice",
)
PREFLIGHT_FALSE_FIELDS = (
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
REQUEST_FALSE_FIELDS = (
    "mode_apply_requested",
    "mode_state_append_requested",
    "command_ledger_append_requested",
    "approval_ledger_append_requested",
    "broker_execution_requested",
    "restricted_api_requested",
    "real_order_requested",
    "ui_command_button_requested",
    "watchdog_autonomous_execution_requested",
)
OUTPUT_FALSE_FIELDS = (
    "mode_apply_executed",
    "mode_state_appended",
    "mode_changed",
    "mode_change_requested",
    "command_ledger_appended",
    "approval_ledger_appended",
    "would_send_to_broker",
    "broker_execution_requested",
    "pre_armed_dry_run_authorized",
    "live_authorized",
    "autotrade_resume_authorized",
    "authorization_record_appended",
    "authorization_record_persisted",
    "record_persistence_executed",
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


def build_pre_armed_dry_run_mode_apply_preview_status(*, record_persistence_preflight: Mapping[str, Any], mode_apply_preview_request: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    preflight = dict(record_persistence_preflight)
    request = dict(mode_apply_preview_request)
    preflight_ok = preflight.get("ok") is True
    preflight_ready = preflight.get("record_persistence_preflight_ready") is True
    preflight_decision = preflight.get("decision")
    preflight_report_version = preflight.get("report_version")
    record_draft = _as_dict(preflight.get("authorization_record_draft"))

    preflight_blockers: list[str] = []
    if not preflight_ok:
        preflight_blockers.append("record_persistence_preflight_not_ok")
    if not preflight_ready:
        preflight_blockers.append("record_persistence_preflight_not_ready")
        preflight_blockers.extend(_as_list(preflight.get("record_persistence_blockers")))
    if not _nonempty(preflight_decision):
        preflight_blockers.append("record_persistence_preflight_decision_required")
    if not _nonempty(preflight_report_version):
        preflight_blockers.append("record_persistence_preflight_report_version_required")
    if preflight.get("read_only") is not True or preflight.get("preflight_status_only") is not True or preflight.get("dry_run_only") is not True:
        preflight_blockers.append("record_persistence_preflight_must_be_read_only_status_dry_run")
    if preflight.get("checks", {}).get("grant_ready_is_not_append_permission") is not True:
        preflight_blockers.append("grant_ready_is_not_append_permission_check_required")
    for key in PREFLIGHT_FALSE_FIELDS:
        if preflight.get(key) not in (None, False):
            preflight_blockers.append(f"preflight_forbidden_flag_must_be_false:{key}")
    if record_draft.get("persisted") is not False or record_draft.get("executed") is not False or record_draft.get("append_executed") is not False:
        preflight_blockers.append("authorization_record_draft_must_not_be_persisted_or_executed")

    submitted_acks = _as_list(request.get("acknowledgements"))
    missing_acks = [ack for ack in REQUIRED_ACKS if ack not in submitted_acks]
    current_mode = str(request.get("current_mode") or "")
    target_mode = str(request.get("target_mode") or "")
    request_blockers: list[str] = []
    if request.get("mode_apply_preview_reviewed") is not True:
        request_blockers.append("mode_apply_preview_review_not_confirmed")
    if request.get("source_record_persistence_preflight_ready") is not True:
        request_blockers.append("request_source_record_persistence_ready_confirmation_required")
    if request.get("source_record_persistence_preflight_decision") != preflight_decision:
        request_blockers.append("request_source_record_persistence_decision_mismatch")
    if request.get("source_record_persistence_preflight_report_version") != preflight_report_version:
        request_blockers.append("request_source_record_persistence_report_version_mismatch")
    if current_mode not in SUPPORTED_CURRENT_MODES:
        request_blockers.append("current_mode_not_supported_for_pre_armed_preview")
    if target_mode not in SUPPORTED_TARGET_MODES:
        request_blockers.append("target_mode_not_pre_armed_dry_run")
    for key in ("source_record_persistence_preflight_path", "preview_id", "requested_by", "requested_at", "operator_identity"):
        if not _nonempty(request.get(key)):
            request_blockers.append(f"{key}_required")
    request_blockers.extend(f"missing_mode_apply_preview_ack:{ack}" for ack in missing_acks)
    for key in REQUEST_FALSE_FIELDS:
        if request.get(key) not in (None, False):
            request_blockers.append(f"request_forbidden_flag_must_be_false:{key}")

    blockers = _dedupe(preflight_blockers + request_blockers)
    ready = bool(preflight_ok and preflight_ready and not blockers)
    decision = "mode_apply_preview_ready_not_applied" if ready else "mode_apply_preview_blocked_not_applied"
    payload: dict[str, Any] = {
        "ok": bool(preflight_ok),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "mode_apply_preview_ready": ready,
        "mode_apply_preview_blockers": blockers,
        "read_only": True,
        "status_only": True,
        "preview_only": True,
        "dry_run_only": True,
        "non_authorizing": True,
        "mode_transition_preview": {
            "preview_id": request.get("preview_id"),
            "current_mode": current_mode,
            "target_mode": target_mode,
            "would_apply": ready,
            "apply_executed": False,
            "mode_state_append_planned": False,
            "mode_state_append_executed": False,
            "command_ledger_append_planned": False,
            "command_ledger_append_executed": False,
            "human_visible_preview": True,
        },
        "source_summary": {
            "record_persistence_preflight_report_version": preflight_report_version,
            "record_persistence_preflight_decision": preflight_decision,
            "record_persistence_preflight_ready": preflight_ready,
            "authorization_record_id": record_draft.get("record_id"),
            "authorization_record_persisted": record_draft.get("persisted"),
            "authorization_record_executed": record_draft.get("executed"),
        },
        "preview_summary": {
            "requested_by": request.get("requested_by"),
            "requested_at": request.get("requested_at"),
            "operator_identity_present": _nonempty(request.get("operator_identity")),
            "submitted_acknowledgements": submitted_acks,
            "missing_acknowledgements": missing_acks,
        },
        "checks": {
            "record_persistence_preflight_ok": preflight_ok,
            "record_persistence_preflight_ready": preflight_ready,
            "record_persistence_ready_is_not_mode_permission": True,
            "mode_transition_supported": current_mode in SUPPORTED_CURRENT_MODES and target_mode in SUPPORTED_TARGET_MODES,
            "preview_request_valid": not request_blockers,
            "no_mode_apply_no_command_append_no_broker": True,
        },
        "warnings": [
            "mode_apply_preview_is_status_only",
            "mode_apply_preview_does_not_append_mode_state",
            "mode_apply_preview_does_not_append_command_ledger",
            "mode_apply_execution_requires_separate_slice",
            "broker_execution_requires_later_explicit_armed_or_live_boundary",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "status_only": True,
            "preview_only": True,
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
    parser = argparse.ArgumentParser(description="Build broker-free S119 Pre-Armed Dry Run mode apply preview/status.")
    parser.add_argument("--record-persistence-preflight", required=True)
    parser.add_argument("--mode-apply-preview-request", required=True)
    parser.add_argument("--out", default="")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        preflight = _read_json(Path(args.record_persistence_preflight))
        request = _read_json(Path(args.mode_apply_preview_request))
        payload = build_pre_armed_dry_run_mode_apply_preview_status(record_persistence_preflight=preflight, mode_apply_preview_request=request)
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
            "preview_only": True,
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
