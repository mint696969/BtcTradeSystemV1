# path: ./tools/run_sr_fx_pre_armed_dry_run_authorization_grant_status.py
# desc: Broker-free S117 Pre-Armed Dry Run authorization grant/status packet. Status-only; non-persisting; non-mode-applying; non-executing.

from __future__ import annotations



from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()



import argparse

import json

from datetime import datetime, timezone

from pathlib import Path

from typing import Any, Mapping



TOOL = "run_sr_fx_pre_armed_dry_run_authorization_grant_status"

REPORT_VERSION = "pre_armed_dry_run_authorization_grant_status.s117.v1"

SUPPORTED_GRANT_SCOPES = (

    "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_REVIEW_ONLY",

    "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_PREVIEW_ONLY",

    "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_APPEND_PRECHECK_ONLY",

)

REQUIRED_ACKS = (

    "confirm_s114_authorization_request_status_reviewed",

    "confirm_ready_status_is_not_itself_approval",

    "confirm_grant_is_explicit_human_decision",

    "confirm_grant_does_not_send_orders",

    "confirm_grant_does_not_apply_mode",

    "confirm_grant_does_not_append_command_ledger",

    "confirm_record_persistence_or_mode_apply_requires_separate_slice",

    "confirm_broker_execution_requires_later_explicit_armed_or_live_boundary",

)

SOURCE_FALSE_FIELDS = (

    "authorization_grant_granted",

    "authorization_grant_executed",

    "authorization_grant_recorded",

    "authorization_request_recorded",

    "authorization_request_record_executed",

    "approval_record_append_execution_authorized",

    "approval_record_append_execution_requested",

    "approval_record_append_executed",

    "approval_ledger_appended",

    "command_ledger_appended",

    "mode_change_requested",

    "mode_change_authorized",

    "mode_changed",

    "would_send_to_broker",

    "pre_armed_dry_run_authorized",

    "live_authorized",

    "autotrade_resume_authorized",

)

REVIEW_FALSE_FIELDS = (

    "grant_append_requested",

    "authorization_grant_execution_requested",

    "record_persistence_requested",

    "authorization_record_append_requested",

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

    return list(dict.fromkeys(item for item in items if item))





def _nonempty(value: Any) -> bool:

    return bool(str(value or "").strip())





def _safety_snapshot_clear(snapshot: Mapping[str, Any]) -> tuple[bool, list[str]]:

    data = dict(snapshot)

    required_true = (

        "broker_free",

        "no_broker_execution",

        "no_real_orders",

        "no_mode_apply",

        "no_ui_command_buttons",

        "no_watchdog_loop",

        "separate_record_persistence_slice_required",

        "separate_mode_apply_slice_required",

    )

    blockers = [f"safety_boundary_snapshot_missing_or_false:{key}" for key in required_true if data.get(key) is not True]

    required_false = (

        "armed_dry_run_authorized",

        "live_authorized",

        "broker_execution_permitted",

        "mode_apply_permitted",

        "grant_append_execution_permitted",

    )

    blockers.extend(f"safety_boundary_snapshot_must_be_false:{key}" for key in required_false if data.get(key) is not False)

    return not blockers, blockers





def build_pre_armed_dry_run_authorization_grant_status(*, source_authorization_request_status: Mapping[str, Any], grant_review: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:

    source = dict(source_authorization_request_status)

    review = dict(grant_review)

    source_ok = source.get("ok") is True

    source_ready = source.get("authorization_request_status_ready") is True

    source_decision = source.get("decision")

    source_report_version = source.get("report_version")

    source_commit_head = source.get("source_commit_head") or source.get("commit_head") or source.get("head")

    submitted_acks = _as_list(review.get("acknowledgements"))

    missing_acks = [ack for ack in REQUIRED_ACKS if ack not in submitted_acks]



    source_blockers: list[str] = []

    if not source_ok:

        source_blockers.append("source_authorization_request_status_not_ok")

    if not source_ready:

        source_blockers.append("source_authorization_request_status_not_ready")

    if not _nonempty(source_decision):

        source_blockers.append("source_authorization_request_status_decision_required")

    if not _nonempty(source_report_version):

        source_blockers.append("source_authorization_request_status_report_version_required")

    if not _nonempty(source_commit_head):

        source_blockers.append("source_commit_head_required")

    if source.get("read_only") is not True or source.get("status_only") is not True:

        source_blockers.append("source_status_must_be_read_only_status_only")

    for key in SOURCE_FALSE_FIELDS:

        if source.get(key) not in (None, False):

            source_blockers.append(f"source_forbidden_flag_must_be_false:{key}")



    review_blockers: list[str] = []

    if review.get("grant_reviewed") is not True:

        review_blockers.append("grant_review_not_confirmed")

    if review.get("source_authorization_request_status_ready") is not True:

        review_blockers.append("review_source_ready_confirmation_required")

    if review.get("source_authorization_request_status_decision") != source_decision:

        review_blockers.append("review_source_decision_mismatch")

    if review.get("source_authorization_request_status_report_version") != source_report_version:

        review_blockers.append("review_source_report_version_mismatch")

    if _nonempty(source_commit_head) and review.get("source_commit_head") != source_commit_head:

        review_blockers.append("review_source_commit_head_mismatch")

    if review.get("requested_scope") not in SUPPORTED_GRANT_SCOPES:

        review_blockers.append("requested_scope_not_supported")

    for key in ("source_authorization_request_status_path", "operator_identity", "granted_by", "requested_at", "granted_at"):

        if not _nonempty(review.get(key)):

            review_blockers.append(f"{key}_required")

    if not (_nonempty(review.get("grant_expires_at")) or review.get("grant_non_expiring_policy_marker") == "explicit_non_expiring_review_only"):

        review_blockers.append("grant_expiry_or_explicit_non_expiring_marker_required")

    review_blockers.extend(f"missing_grant_ack:{ack}" for ack in missing_acks)

    for key in REVIEW_FALSE_FIELDS:

        if review.get(key) not in (None, False):

            review_blockers.append(f"review_forbidden_request_must_be_false:{key}")

    snapshot_ok, snapshot_blockers = _safety_snapshot_clear(_as_dict(review.get("safety_boundary_snapshot")))

    if not snapshot_ok:

        review_blockers.extend(snapshot_blockers)



    blockers = _dedupe(source_blockers + review_blockers)

    ready = bool(source_ok and source_ready and not blockers)

    decision = "authorization_grant_status_ready_not_granted_not_recorded_not_executed" if ready else "authorization_grant_status_blocked_not_granted_not_recorded_not_executed"

    payload: dict[str, Any] = {

        "ok": bool(source_ok),

        "tool": TOOL,

        "report_version": REPORT_VERSION,

        "generated_at": generated_at or _utc_now_iso(),

        "decision": decision,

        "authorization_grant_ready": ready,

        "authorization_grant_blockers": blockers,

        "read_only": True,

        "status_only": True,

        "dry_run_only": True,

        "non_authorizing": True,

        "source_summary": {

            "source_authorization_request_status_path": review.get("source_authorization_request_status_path"),

            "source_authorization_request_status_report_version": source_report_version,

            "source_authorization_request_status_decision": source_decision,

            "source_authorization_request_status_ready": source_ready,

            "source_commit_head": source_commit_head,

        },

        "grant_summary": {

            "requested_scope": review.get("requested_scope"),

            "operator_identity_present": _nonempty(review.get("operator_identity")),

            "granted_by_present": _nonempty(review.get("granted_by")),

            "requested_at": review.get("requested_at"),

            "granted_at": review.get("granted_at"),

            "grant_expires_at": review.get("grant_expires_at"),

            "grant_non_expiring_policy_marker": review.get("grant_non_expiring_policy_marker"),

            "submitted_acknowledgements": submitted_acks,

            "missing_acknowledgements": missing_acks,

        },

        "checks": {

            "source_authorization_request_status_ok": source_ok,

            "source_authorization_request_status_ready": source_ready,

            "grant_review_shape_valid": not review_blockers,

            "safety_boundary_snapshot_clear": snapshot_ok,

            "ready_is_not_approval": True,

            "no_append_no_persistence_no_mode_no_broker": True,

        },

        "warnings": [

            "authorization_grant_status_is_readiness_only",

            "authorization_grant_ready_is_not_authorization_granted",

            "record_persistence_requires_separate_slice",

            "mode_apply_requires_separate_slice",

            "broker_execution_requires_later_explicit_armed_or_live_boundary",

        ],

        "operator_safety_lock": {

            "non_authorizing": True,

            "status_only": True,

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

    parser = argparse.ArgumentParser(description="Build broker-free S117 Pre-Armed Dry Run authorization grant/status packet.")

    parser.add_argument("--source-authorization-request-status", required=True)

    parser.add_argument("--grant-review", required=True)

    parser.add_argument("--out", default="")

    return parser





def main() -> int:

    args = _build_arg_parser().parse_args()

    try:

        source = _read_json(Path(args.source_authorization_request_status))

        review = _read_json(Path(args.grant_review))

        payload = build_pre_armed_dry_run_authorization_grant_status(source_authorization_request_status=source, grant_review=review)

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
