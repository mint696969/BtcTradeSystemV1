# path: ./tools/run_sr_fx_pre_armed_dry_run_approval_record_ledger_status.py
# desc: Broker-free Pre-Armed Dry Run approval record ledger status reader. Read-only; no append, no mode request, non-authorizing.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL = "run_sr_fx_pre_armed_dry_run_approval_record_ledger_status"
REPORT_VERSION = "pre_armed_dry_run_approval_record_ledger_status.v1"
RECORD_KIND = "pre_armed_dry_run_review_approval_record"
REQUIRED_REASON_CODES = ("operator_final_human_review", "pre_armed_dry_run_review_only")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _read_lines(path: Path, *, max_lines: int | None) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if max_lines is not None and max_lines >= 0:
        return lines[-max_lines:]
    return lines


def _validate_record(obj: dict[str, Any], *, line_number: int) -> dict[str, Any]:
    reasons: list[str] = []
    reason_codes = _as_list(obj.get("reason_codes"))
    acknowledgements = _as_list(obj.get("acknowledgements"))
    if obj.get("record_kind") != RECORD_KIND:
        reasons.append("record_kind_not_pre_armed_review_approval")
    if not str(obj.get("record_id") or "").startswith("approval_record_"):
        reasons.append("invalid_record_id")
    if not str(obj.get("evidence_id") or "").startswith("approval_evidence_"):
        reasons.append("invalid_evidence_id")
    if obj.get("approval_scope") != "PRE_ARMED_DRY_RUN_REVIEW_ONLY":
        reasons.append("approval_scope_not_review_only")
    if obj.get("target_mode") != "PRE_ARMED_DRY_RUN":
        reasons.append("target_mode_not_pre_armed_dry_run")
    if not str(obj.get("requested_by") or "").strip():
        reasons.append("requested_by_required")
    if not str(obj.get("requested_at") or "").strip():
        reasons.append("requested_at_required")
    if not str(obj.get("recorded_at") or "").strip():
        reasons.append("recorded_at_required")
    if not str(obj.get("operator_identity") or "").strip():
        reasons.append("operator_identity_required")
    if obj.get("approval_record_persisted") is not True:
        reasons.append("approval_record_persisted_true_required_for_ledger_row")
    for code in REQUIRED_REASON_CODES:
        if code not in reason_codes:
            reasons.append(f"missing_reason_code:{code}")
    if obj.get("pre_armed_dry_run_authorized") is True:
        reasons.append("approval_record_must_not_authorize_pre_armed_dry_run")
    if obj.get("live_authorized") is True:
        reasons.append("approval_record_must_not_authorize_live")
    if obj.get("autotrade_resume_authorized") is True:
        reasons.append("approval_record_must_not_authorize_autotrade_resume")
    if obj.get("mode_change_requested") is True:
        reasons.append("approval_record_must_not_request_mode_change")
    if obj.get("mode_change_authorized") is True:
        reasons.append("approval_record_must_not_authorize_mode_change")
    if obj.get("command_ledger_appended") is True:
        reasons.append("approval_record_must_not_append_command_ledger")
    return {
        "line_number": line_number,
        "valid": not reasons,
        "invalid_reasons": _dedupe(reasons),
        "record_id": obj.get("record_id"),
        "record_kind": obj.get("record_kind"),
        "evidence_id": obj.get("evidence_id"),
        "approval_scope": obj.get("approval_scope"),
        "target_mode": obj.get("target_mode"),
        "requested_by": obj.get("requested_by"),
        "requested_at": obj.get("requested_at"),
        "recorded_at": obj.get("recorded_at"),
        "operator_identity_present": bool(str(obj.get("operator_identity") or "").strip()),
        "reason_codes": reason_codes,
        "acknowledgement_count": len(acknowledgements),
        "approval_record_persisted_observed": obj.get("approval_record_persisted") is True,
        "pre_armed_dry_run_authorized_observed": obj.get("pre_armed_dry_run_authorized") is True,
        "live_authorized_observed": obj.get("live_authorized") is True,
        "mode_change_requested_observed": obj.get("mode_change_requested") is True,
        "command_ledger_appended_observed": obj.get("command_ledger_appended") is True,
    }


def build_pre_armed_dry_run_approval_record_ledger_status(*, approval_record_ledger: Path, max_lines: int | None = 1000, generated_at: str | None = None) -> dict[str, Any]:
    parsed_records: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []
    for index, line in enumerate(_read_lines(approval_record_ledger, max_lines=max_lines), start=1):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
            if not isinstance(obj, dict):
                raise ValueError("row_not_object")
            parsed_records.append(_validate_record(obj, line_number=index))
        except Exception as exc:
            skipped_rows.append({"line_number": index, "error_class": exc.__class__.__name__})
    valid_records = [row for row in parsed_records if row.get("valid") is True]
    invalid_records = [row for row in parsed_records if row.get("valid") is not True]
    latest_valid = valid_records[-1] if valid_records else None
    invalid_reason_counts: dict[str, int] = {}
    for row in invalid_records:
        for reason in _as_list(row.get("invalid_reasons")):
            invalid_reason_counts[reason] = invalid_reason_counts.get(reason, 0) + 1
    if not approval_record_ledger.exists():
        decision = "approval_record_ledger_status_read_only_missing"
    elif valid_records and not invalid_records and not skipped_rows:
        decision = "approval_record_ledger_status_read_only_records_present"
    elif valid_records or invalid_records or skipped_rows:
        decision = "approval_record_ledger_status_read_only_with_warnings"
    else:
        decision = "approval_record_ledger_status_read_only_empty"
    return {
        "ok": True,
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "approval_record_ledger_status_ready": True,
        "approval_record_ledger_path": str(approval_record_ledger),
        "approval_record_ledger_exists": approval_record_ledger.exists(),
        "total_parsed_rows": len(parsed_records),
        "valid_record_count": len(valid_records),
        "invalid_record_count": len(invalid_records),
        "skipped_row_count": len(skipped_rows),
        "ledger_human_approval_records_observed": bool(valid_records),
        "approval_record_observed_count": len(valid_records),
        "latest_valid_approval_record": latest_valid or {},
        "invalid_records": invalid_records[:20],
        "skipped_rows": skipped_rows[:20],
        "invalid_reason_counts": invalid_reason_counts,
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
        "status_reader_only": True,
        "checks": {
            "ledger_read_attempted": True,
            "ledger_missing_fail_soft": not approval_record_ledger.exists(),
            "valid_records_visible": bool(valid_records),
            "invalid_records_visible_when_present": bool(invalid_records) if invalid_records else True,
            "skipped_rows_visible_when_present": bool(skipped_rows) if skipped_rows else True,
            "approval_record_persisted_by_this_tool_false": True,
            "approval_recorded_false": True,
            "human_approval_recorded_false": True,
            "operator_acknowledgement_recorded_false": True,
            "approval_ledger_appended_false": True,
            "command_ledger_appended_false": True,
            "mode_change_requested_false": True,
            "mode_change_authorized_false": True,
            "read_only_no_broker_non_authorizing": True,
            "pre_armed_dry_run_not_authorized": True,
            "live_not_authorized": True,
            "mode_not_changed": True,
        },
        "warnings": [
            "approval_record_ledger_status_reader_is_read_only",
            "approval_record_persisted_by_this_tool_false",
            "approval_recorded_false",
            "human_approval_recorded_false",
            "operator_acknowledgement_recorded_false",
            "approval_ledger_appended_false",
            "command_ledger_appended_false",
            "mode_change_requested_false",
            "mode_change_authorized_false",
            "pre_armed_dry_run_authorization_remains_false",
            "live_authorization_remains_false",
            "broker_send_remains_disabled",
        ],
        "operator_safety_lock": {
            "non_authorizing": True,
            "status_reader_only": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
    parser = argparse.ArgumentParser(description="Read broker-free Pre-Armed Dry Run approval record ledger status. Read-only; never appends.")
    parser.add_argument("--approval-record-ledger", required=True, help="Path to approval record JSONL ledger to read. May be absent.")
    parser.add_argument("--max-lines", type=int, default=1000, help="Read at most recent N lines; negative reads all.")
    parser.add_argument("--out", default="", help="Optional status output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        max_lines = None if args.max_lines is not None and args.max_lines < 0 else args.max_lines
        payload = build_pre_armed_dry_run_approval_record_ledger_status(approval_record_ledger=Path(args.approval_record_ledger), max_lines=max_lines)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["pre_armed_dry_run_approval_record_ledger_status_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "status_reader_only": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "pre_armed_dry_run_authorized": False,
                "live_authorized": False,
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
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "pre_armed_dry_run_authorized": False,
            "live_authorized": False,
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
