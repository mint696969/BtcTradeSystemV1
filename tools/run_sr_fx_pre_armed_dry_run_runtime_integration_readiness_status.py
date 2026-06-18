# path: ./tools/run_sr_fx_pre_armed_dry_run_runtime_integration_readiness_status.py
# desc: Broker-free S120 runtime integration readiness packet for S117/S118/S119 outputs. Status-only; no execution or append.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_pre_armed_dry_run_runtime_integration_readiness_status"
REPORT_VERSION = "pre_armed_dry_run_runtime_integration_readiness_status.s120.v1"
EXPECTED_GRANT_REPORT = "pre_armed_dry_run_authorization_grant_status.s117.v1"
EXPECTED_RECORD_REPORT = "pre_armed_dry_run_authorization_record_persistence_preflight_status.s118.v1"
EXPECTED_MODE_PREVIEW_REPORT = "pre_armed_dry_run_mode_apply_preview_status.s119.v1"
FALSE_FIELDS = (
    "authorization_grant_granted",
    "authorization_grant_executed",
    "authorization_grant_recorded",
    "authorization_record_appended",
    "authorization_record_persisted",
    "record_persistence_executed",
    "mode_apply_executed",
    "mode_state_appended",
    "mode_changed",
    "mode_change_requested",
    "approval_ledger_appended",
    "command_ledger_appended",
    "would_send_to_broker",
    "pre_armed_dry_run_authorized",
    "live_authorized",
    "autotrade_resume_authorized",
    "broker_execution_requested",
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


def _blocked(name: str, payload: Mapping[str, Any], ready_key: str, expected_report: str, blocker_key: str) -> list[str]:
    out: list[str] = []
    if payload.get("ok") is not True:
        out.append(f"{name}_not_ok")
    if payload.get("report_version") != expected_report:
        out.append(f"{name}_report_version_unexpected")
    if payload.get(ready_key) is not True:
        out.append(f"{name}_not_ready")
        out.extend(f"{name}:{item}" for item in _as_list(payload.get(blocker_key)))
    if payload.get("read_only") is not True:
        out.append(f"{name}_must_be_read_only")
    for key in FALSE_FIELDS:
        if payload.get(key) not in (None, False):
            out.append(f"{name}_forbidden_flag_must_be_false:{key}")
    return out


def build_pre_armed_dry_run_runtime_integration_readiness_status(*, authorization_grant_status: Mapping[str, Any], record_persistence_preflight: Mapping[str, Any], mode_apply_preview: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    grant = dict(authorization_grant_status)
    record = dict(record_persistence_preflight)
    mode = dict(mode_apply_preview)

    blockers: list[str] = []
    blockers.extend(_blocked("authorization_grant_status", grant, "authorization_grant_ready", EXPECTED_GRANT_REPORT, "authorization_grant_blockers"))
    blockers.extend(_blocked("record_persistence_preflight", record, "record_persistence_preflight_ready", EXPECTED_RECORD_REPORT, "record_persistence_blockers"))
    blockers.extend(_blocked("mode_apply_preview", mode, "mode_apply_preview_ready", EXPECTED_MODE_PREVIEW_REPORT, "mode_apply_preview_blockers"))

    record_source = _as_dict(record.get("source_summary"))
    mode_source = _as_dict(mode.get("source_summary"))
    grant_decision = grant.get("decision")
    record_source_grant_decision = record_source.get("authorization_grant_status_decision")
    record_decision = record.get("decision")
    mode_source_record_decision = mode_source.get("record_persistence_preflight_decision")
    if record_source_grant_decision != grant_decision:
        blockers.append("record_preflight_does_not_reference_grant_status_decision")
    if mode_source_record_decision != record_decision:
        blockers.append("mode_preview_does_not_reference_record_preflight_decision")

    readiness_ready = not blockers
    decision = "runtime_integration_readiness_ready_not_authorized_not_executed" if readiness_ready else "runtime_integration_readiness_blocked_not_authorized_not_executed"
    mode_preview = _as_dict(mode.get("mode_transition_preview"))
    payload: dict[str, Any] = {
        "ok": bool(grant.get("ok") is True and record.get("ok") is True and mode.get("ok") is True),
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": decision,
        "runtime_integration_readiness_ready": readiness_ready,
        "runtime_integration_blockers": _dedupe(blockers),
        "read_only": True,
        "status_only": True,
        "dry_run_only": True,
        "non_authorizing": True,
        "operator_readiness_summary": {
            "authorization_grant_ready": grant.get("authorization_grant_ready"),
            "record_persistence_preflight_ready": record.get("record_persistence_preflight_ready"),
            "mode_apply_preview_ready": mode.get("mode_apply_preview_ready"),
            "current_mode": mode_preview.get("current_mode"),
            "target_mode": mode_preview.get("target_mode"),
            "mode_transition_preview_visible": bool(mode_preview),
            "human_final_review_required": True,
        },
        "source_reports": {
            "authorization_grant_status": {"report_version": grant.get("report_version"), "decision": grant_decision},
            "record_persistence_preflight": {"report_version": record.get("report_version"), "decision": record_decision},
            "mode_apply_preview": {"report_version": mode.get("report_version"), "decision": mode.get("decision")},
        },
        "checks": {
            "authorization_grant_status_ready": grant.get("authorization_grant_ready") is True,
            "record_persistence_preflight_ready": record.get("record_persistence_preflight_ready") is True,
            "mode_apply_preview_ready": mode.get("mode_apply_preview_ready") is True,
            "chain_decision_links_consistent": record_source_grant_decision == grant_decision and mode_source_record_decision == record_decision,
            "no_execution_no_append_no_broker": True,
        },
        "warnings": [
            "runtime_integration_readiness_is_operator_summary_only",
            "ready_is_not_armed_dry_run_authorization",
            "mode_apply_requires_separate_explicit_slice",
            "record_append_execution_requires_separate_explicit_slice",
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
    for key in FALSE_FIELDS:
        payload[key] = False
        payload["operator_safety_lock"][key] = False
    return payload


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build S120 Pre-Armed Dry Run runtime integration readiness/status from S117/S118/S119 JSON.")
    parser.add_argument("--authorization-grant-status", required=True)
    parser.add_argument("--record-persistence-preflight", required=True)
    parser.add_argument("--mode-apply-preview", required=True)
    parser.add_argument("--out", default="")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        grant = _read_json(Path(args.authorization_grant_status))
        record = _read_json(Path(args.record_persistence_preflight))
        mode = _read_json(Path(args.mode_apply_preview))
        payload = build_pre_armed_dry_run_runtime_integration_readiness_status(authorization_grant_status=grant, record_persistence_preflight=record, mode_apply_preview=mode)
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
        for key in FALSE_FIELDS:
            payload[key] = False
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
