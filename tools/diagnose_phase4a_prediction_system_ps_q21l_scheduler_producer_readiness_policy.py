# path: ./tools/diagnose_phase4a_prediction_system_ps_q21l_scheduler_producer_readiness_policy.py
# desc: PS-Q21L read-only policy diagnostic for whether scheduler/producer recurring prediction generation should be enabled. No enablement, no writes, no WarRoom UI trigger, no AutoTrade/broker.

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

DIAGNOSTIC_VERSION = "prediction_warroom.scheduler_producer_readiness_policy.ps_q21l.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
REQUIRED_POLICY_GATES = (
    "operator_approval_for_recurring_runtime_writes",
    "single_non_overlapping_runner_lock_design",
    "scheduler_registration_and_disable_rollback_plan",
    "freshness_and_failure_backoff_policy",
    "status_visibility_and_alerting_review",
    "shadow_or_manual_recheck_after_one_shot_write",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _parse_utc(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    return _as_mapping(data)


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": ""}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _generated_at(payload: Mapping[str, Any]) -> str:
    identity = _as_mapping(payload.get("run_identity"))
    if identity.get("generated_at"):
        return str(identity.get("generated_at"))
    batch = _as_mapping(payload.get("forecast_batch"))
    if batch.get("generated_at"):
        return str(batch.get("generated_at"))
    return str(payload.get("generated_at") or "")


def _output_count(payload: Mapping[str, Any]) -> int:
    batch = _as_mapping(payload.get("forecast_batch"))
    records = batch.get("records")
    if isinstance(records, list):
        return len(records)
    outputs = payload.get("outputs")
    if isinstance(outputs, list):
        return len(outputs)
    try:
        return int(batch.get("record_count") or payload.get("output_count") or 0)
    except Exception:
        return 0


def build_scheduler_producer_readiness_policy(
    *,
    latest_payload: Mapping[str, Any] | None,
    status_payload: Mapping[str, Any] | None,
    latest_meta: Mapping[str, Any],
    status_meta: Mapping[str, Any],
    now_utc: str | None = None,
) -> dict[str, Any]:
    latest = _as_mapping(latest_payload or {})
    status = _as_mapping(status_payload or {})
    safe_flags = _as_mapping(status.get("safe_flags"))
    blockers = [str(item) for item in status.get("blockers", []) if item] if isinstance(status.get("blockers"), list) else []
    warnings = [str(item) for item in status.get("warnings", []) if item] if isinstance(status.get("warnings"), list) else []
    generated_at = _generated_at(latest)
    now_dt = _parse_utc(now_utc) or _utc_now()
    generated_dt = _parse_utc(generated_at)
    age_sec = int((now_dt - generated_dt).total_seconds()) if generated_dt is not None else None
    max_age = int(status.get("freshness_max_age_sec") or 3600)
    latest_non_stale = bool(age_sec is not None and age_sec <= max_age and _output_count(latest) > 0)
    one_shot_success = bool(
        latest_meta.get("exists")
        and status_meta.get("exists")
        and status.get("producer_state") == "manual_refresh_exported_status_written"
        and status.get("last_success_generated_at") == generated_at
        and status.get("last_failure_at") in (None, "")
        and not blockers
    )
    disabled_boundary_preserved = bool(
        status.get("producer_enabled") is False
        and status.get("scheduler_enabled") is False
        and safe_flags.get("producer_enabled_false") is True
        and safe_flags.get("scheduler_enabled_false") is True
        and safe_flags.get("scheduled_loop_enabled_false") is True
        and safe_flags.get("warroom_ui_trigger_false") is True
        and safe_flags.get("autotrade_trigger_allowed_false") is True
        and safe_flags.get("broker_private_api_allowed_false") is True
        and safe_flags.get("would_send_to_broker_false") is True
    )
    recurring_policy_blockers = list(REQUIRED_POLICY_GATES)
    ready_for_recurring_enablement = False
    ready_for_policy_design_slice = bool(one_shot_success and latest_non_stale and disabled_boundary_preserved)
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "diagnosis_state": "ready_for_read_only_scheduler_producer_policy_design_not_enablement" if ready_for_policy_design_slice else "not_ready_for_scheduler_producer_policy_design",
        "latest_prediction_artifact_exists": bool(latest_meta.get("exists")),
        "latest_prediction_artifact_mtime_utc": str(latest_meta.get("mtime_utc") or ""),
        "latest_prediction_artifact_size_bytes": latest_meta.get("size_bytes"),
        "status_artifact_exists": bool(status_meta.get("exists")),
        "status_artifact_mtime_utc": str(status_meta.get("mtime_utc") or ""),
        "status_artifact_size_bytes": status_meta.get("size_bytes"),
        "generated_at": generated_at,
        "age_sec": age_sec,
        "freshness_max_age_sec": max_age,
        "latest_prediction_non_stale": latest_non_stale,
        "output_count": _output_count(latest),
        "one_shot_manual_write_success_observed": one_shot_success,
        "producer_state": str(status.get("producer_state") or ""),
        "last_success_at": str(status.get("last_success_at") or ""),
        "last_success_generated_at": str(status.get("last_success_generated_at") or ""),
        "last_failure_at": status.get("last_failure_at"),
        "last_blocker_count": int(status.get("last_blocker_count") or 0),
        "last_warning_count": int(status.get("last_warning_count") or 0),
        "status_blockers": blockers,
        "status_warnings": warnings,
        "disabled_boundary_preserved": disabled_boundary_preserved,
        "producer_enabled": status.get("producer_enabled") is True,
        "scheduler_enabled": status.get("scheduler_enabled") is True,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "ready_for_scheduler_enablement": ready_for_recurring_enablement,
        "ready_for_producer_enablement": ready_for_recurring_enablement,
        "ready_for_runtime_artifact_write_automation_enablement": ready_for_recurring_enablement,
        "ready_for_read_only_policy_design_slice": ready_for_policy_design_slice,
        "recurring_enablement_allowed_now": False,
        "recurring_enablement_blockers": recurring_policy_blockers,
        "next_recommended_action": "Create a separate read-only scheduler/producer policy design before any recurring enablement.",
        "read_only_policy_diagnostic_only": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def run_diagnostic(*, hot_root: Path | None = None) -> dict[str, Any]:
    root = Path(hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT)
    latest_path = root / LATEST_RELATIVE_PATH
    status_path = root / STATUS_RELATIVE_PATH
    latest_payload = _load_json(latest_path) if latest_path.exists() else {}
    status_payload = _load_json(status_path) if status_path.exists() else {}
    result = build_scheduler_producer_readiness_policy(
        latest_payload=latest_payload,
        status_payload=status_payload,
        latest_meta=_file_meta(latest_path),
        status_meta=_file_meta(status_path),
    )
    result["hot_root"] = str(root)
    result["latest_prediction_artifact_path"] = str(latest_path)
    result["status_artifact_path"] = str(status_path)
    return result


def main() -> int:
    result = run_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
