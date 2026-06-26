# path: ./tools/design_phase4a_prediction_system_ps_q21o_single_run_lock_contract.py
# desc: PS-Q21O read-only single non-overlapping run-lock contract. No lock file creation, no scheduler registration, no producer loop, no runner invocation, no artifact/status writes, no AutoTrade/broker.

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

LOCK_CONTRACT_VERSION = "prediction_warroom.single_non_overlapping_run_lock_contract.ps_q21o.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
LOCK_RELATIVE_PATH = Path("prediction/runtime/non_ui_scheduler_producer.lock.json")
FRESHNESS_MAX_AGE_SEC_DEFAULT = 3600
LOCK_STALE_AFTER_SEC_DEFAULT = 900
RECOMMENDED_CADENCE_SEC_DEFAULT = 300


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
    data = json.loads(path.read_text(encoding="utf-8-sig"))
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


def build_single_run_lock_contract(
    *,
    latest_payload: Mapping[str, Any] | None,
    status_payload: Mapping[str, Any] | None,
    latest_meta: Mapping[str, Any],
    status_meta: Mapping[str, Any],
    lock_meta: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    latest = _as_mapping(latest_payload or {})
    status = _as_mapping(status_payload or {})
    lock = _as_mapping(lock_meta or {})
    safe_flags = _as_mapping(status.get("safe_flags"))
    generated_at = _generated_at(latest)
    generated_dt = _parse_utc(generated_at)
    now_dt = _parse_utc(now_utc) or _utc_now()
    age_sec = int((now_dt - generated_dt).total_seconds()) if generated_dt is not None else None
    max_age = int(status.get("freshness_max_age_sec") or FRESHNESS_MAX_AGE_SEC_DEFAULT)
    recommended_cadence = int(status.get("recommended_cadence_sec") or RECOMMENDED_CADENCE_SEC_DEFAULT)
    output_count = _output_count(latest)
    status_blockers = [str(item) for item in status.get("blockers", []) if item] if isinstance(status.get("blockers"), list) else []
    status_warnings = [str(item) for item in status.get("warnings", []) if item] if isinstance(status.get("warnings"), list) else []
    latest_non_stale = bool(age_sec is not None and age_sec <= max_age and output_count > 0)
    status_success = bool(
        latest_meta.get("exists")
        and status_meta.get("exists")
        and status.get("producer_state") == "manual_refresh_exported_status_written"
        and status.get("last_success_generated_at") == generated_at
        and status.get("last_failure_at") in (None, "")
        and not status_blockers
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
    lock_contract_ready = bool(status_success and latest_non_stale and disabled_boundary_preserved)
    blockers: list[str] = []
    if not status_success:
        blockers.append("latest_status_success_required_before_run_lock_contract")
    if not latest_non_stale:
        blockers.append("latest_prediction_non_stale_required_before_run_lock_contract")
    if not disabled_boundary_preserved:
        blockers.append("disabled_boundary_required_before_run_lock_contract")
    return {
        "ok": True,
        "lock_contract_version": LOCK_CONTRACT_VERSION,
        "lock_contract_state": "single_non_overlapping_run_lock_contract_ready_no_file_creation" if lock_contract_ready else "single_non_overlapping_run_lock_contract_blocked",
        "generated_at": generated_at,
        "age_sec": age_sec,
        "freshness_max_age_sec": max_age,
        "recommended_cadence_sec": recommended_cadence,
        "output_count": output_count,
        "latest_prediction_non_stale": latest_non_stale,
        "latest_status_success_observed": status_success,
        "disabled_boundary_preserved": disabled_boundary_preserved,
        "lock_contract_ready": lock_contract_ready,
        "lock_contract_blockers": blockers,
        "status_blockers": status_blockers,
        "status_warnings": status_warnings,
        "lock_artifact_exists_before_contract": bool(lock.get("exists")),
        "lock_relative_path_design": str(LOCK_RELATIVE_PATH).replace("\\", "/"),
        "producer_state": str(status.get("producer_state") or ""),
        "producer_enabled": status.get("producer_enabled") is True,
        "scheduler_enabled": status.get("scheduler_enabled") is True,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "run_lock_contract": {
            "single_non_overlapping_runner_lock_required": True,
            "lock_relative_path_design": str(LOCK_RELATIVE_PATH).replace("\\", "/"),
            "lock_owner_fields": ["run_id", "pid", "host", "started_at_utc", "expires_at_utc", "reason"],
            "lock_stale_after_sec": LOCK_STALE_AFTER_SEC_DEFAULT,
            "acquire_policy": "future_runner_must_acquire_lock_before_actual_read_or_export",
            "release_policy": "future_runner_must_release_lock_after_success_or_failure",
            "stale_lock_recovery_policy": "future_runner_may_recover_only_after_stale_age_and_status_visibility",
            "overlap_policy": "skip_or_fail_closed_if_lock_active_never_overlap_runs",
            "enablement_allowed_without_lock": False,
            "lock_contract_only": True,
        },
        "lock_execution_result": {
            "lock_file_created": False,
            "lock_file_written": False,
            "lock_acquire_attempted": False,
            "lock_acquired": False,
            "lock_release_attempted": False,
            "lock_released": False,
            "stale_lock_deleted": False,
            "scheduler_registered": False,
            "scheduler_started": False,
            "producer_loop_enabled": False,
            "producer_runner_invoked": False,
            "bounded_manual_refresh_invoked": False,
            "actual_export_runner_invoked": False,
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "warroom_ui_trigger_invoked": False,
        },
        "next_recommended_action": "Implement disabled lock smoke with temp/mock lock path only; still no scheduler registration, producer loop, or artifact writes." if lock_contract_ready else "Refresh latest prediction and restore disabled boundaries before run-lock contract.",
        "read_only_lock_contract_only": True,
        "lock_file_creation_allowed": False,
        "lock_file_write_allowed": False,
        "lock_acquire_allowed_now": False,
        "lock_release_allowed_now": False,
        "scheduler_registration_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "producer_loop_allowed": False,
        "recurring_enablement_allowed_now": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def run_contract(*, hot_root: Path | None = None) -> dict[str, Any]:
    root = Path(hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT)
    latest_path = root / LATEST_RELATIVE_PATH
    status_path = root / STATUS_RELATIVE_PATH
    lock_path = root / LOCK_RELATIVE_PATH
    latest_payload = _load_json(latest_path) if latest_path.exists() else {}
    status_payload = _load_json(status_path) if status_path.exists() else {}
    result = build_single_run_lock_contract(
        latest_payload=latest_payload,
        status_payload=status_payload,
        latest_meta=_file_meta(latest_path),
        status_meta=_file_meta(status_path),
        lock_meta=_file_meta(lock_path),
    )
    result["hot_root"] = str(root)
    result["latest_prediction_artifact_path"] = str(latest_path)
    result["status_artifact_path"] = str(status_path)
    result["lock_artifact_path_design"] = str(lock_path)
    return result


def main() -> int:
    result = run_contract()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
