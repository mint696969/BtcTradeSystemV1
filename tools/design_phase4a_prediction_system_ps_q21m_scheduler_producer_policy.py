# path: ./tools/design_phase4a_prediction_system_ps_q21m_scheduler_producer_policy.py
# desc: PS-Q21M read-only scheduler/producer policy design packet after fresh one-shot recovery. No scheduler/producer enablement, no writes, no WarRoom UI trigger, no AutoTrade/broker.

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

DESIGN_VERSION = "prediction_warroom.scheduler_producer_policy_design.ps_q21m.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
DEFAULT_FRESHNESS_WARNING_AGE_SEC = 900
DEFAULT_FRESHNESS_MAX_AGE_SEC = 3600
DEFAULT_RECOMMENDED_CADENCE_SEC = 300
DEFAULT_MINIMUM_CADENCE_SEC = 60
DEFAULT_MAXIMUM_CADENCE_SEC = 900
REQUIRED_APPROVAL_GATES = (
    "operator_approval_for_recurring_runtime_writes",
    "operator_approval_for_scheduler_registration",
    "operator_approval_for_disable_rollback_plan",
)
NEXT_SAFE_SLICES = (
    "disabled_non_ui_scheduler_runner_dry_run_no_registration",
    "single_non_overlapping_runner_lock_contract",
    "failure_backoff_and_status_visibility_contract",
    "manual_recheck_before_any_enablement",
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


def _age_sec(generated_at: str, now_utc: str | None) -> int | None:
    generated = _parse_utc(generated_at)
    now = _parse_utc(now_utc) or _utc_now()
    if generated is None:
        return None
    return max(0, int((now - generated).total_seconds()))


def build_scheduler_producer_policy_design(
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
    warnings = [str(item) for item in status.get("warnings", []) if item] if isinstance(status.get("warnings"), list) else []
    blockers = [str(item) for item in status.get("blockers", []) if item] if isinstance(status.get("blockers"), list) else []
    generated_at = _generated_at(latest)
    age_sec = _age_sec(generated_at, now_utc)
    freshness_warning_age = int(status.get("freshness_warning_age_sec") or DEFAULT_FRESHNESS_WARNING_AGE_SEC)
    freshness_max_age = int(status.get("freshness_max_age_sec") or DEFAULT_FRESHNESS_MAX_AGE_SEC)
    output_count = _output_count(latest)
    latest_non_stale = bool(age_sec is not None and age_sec <= freshness_max_age and output_count > 0)
    latest_fresh = bool(age_sec is not None and age_sec <= freshness_warning_age and output_count > 0)
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
    ready_for_disabled_dry_run_design = bool(one_shot_success and latest_non_stale and disabled_boundary_preserved)
    return {
        "ok": True,
        "design_version": DESIGN_VERSION,
        "policy_design_state": "ready_for_disabled_dry_run_design_not_enablement" if ready_for_disabled_dry_run_design else "policy_design_attention_stale_or_boundary",
        "generated_at": generated_at,
        "age_sec": age_sec,
        "freshness_warning_age_sec": freshness_warning_age,
        "freshness_max_age_sec": freshness_max_age,
        "latest_prediction_fresh": latest_fresh,
        "latest_prediction_non_stale": latest_non_stale,
        "output_count": output_count,
        "one_shot_manual_write_success_observed": one_shot_success,
        "disabled_boundary_preserved": disabled_boundary_preserved,
        "status_warnings": warnings,
        "status_blockers": blockers,
        "producer_state": str(status.get("producer_state") or ""),
        "producer_enabled": status.get("producer_enabled") is True,
        "scheduler_enabled": status.get("scheduler_enabled") is True,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "ready_for_disabled_dry_run_design_slice": ready_for_disabled_dry_run_design,
        "ready_for_scheduler_enablement": False,
        "ready_for_producer_enablement": False,
        "ready_for_runtime_artifact_write_automation_enablement": False,
        "recurring_enablement_allowed_now": False,
        "policy_design": {
            "cadence_policy": {
                "recommended_cadence_sec": int(status.get("recommended_cadence_sec") or DEFAULT_RECOMMENDED_CADENCE_SEC),
                "minimum_cadence_sec": DEFAULT_MINIMUM_CADENCE_SEC,
                "maximum_cadence_sec": DEFAULT_MAXIMUM_CADENCE_SEC,
                "freshness_warning_age_sec": freshness_warning_age,
                "freshness_max_age_sec": freshness_max_age,
                "overlap_policy": "never_overlap_runs; skip_if_previous_run_active",
                "stale_policy": "show_stale_and_do_not_force_ready",
            },
            "run_lock_policy": {
                "single_non_overlapping_runner_lock_required": True,
                "lock_artifact_design_required": True,
                "stale_lock_recovery_policy_required": True,
                "enablement_allowed_without_lock": False,
            },
            "failure_backoff_policy": {
                "fail_closed_on_blockers": True,
                "consecutive_failure_soft_limit": 2,
                "consecutive_failure_hard_disable_limit": 3,
                "write_status_on_failure_required": True,
                "do_not_delete_last_successful_prediction": True,
            },
            "visibility_policy": {
                "warroom_status_display_required": True,
                "show_last_run_last_success_last_failure": True,
                "show_warnings_and_blockers": True,
                "show_safe_flags": True,
                "show_scheduler_and_producer_disabled_state": True,
            },
            "rollback_policy": {
                "disable_scheduler_first": True,
                "producer_loop_disable_required": True,
                "warroom_continues_read_only_observation": True,
                "rollback_does_not_mutate_parameters": True,
                "rollback_does_not_delete_latest_artifact": True,
            },
        },
        "required_approval_gates_before_any_enablement": list(REQUIRED_APPROVAL_GATES),
        "next_safe_slices": list(NEXT_SAFE_SLICES),
        "next_recommended_action": "Implement a disabled non-UI scheduler/producer dry-run design only; do not register or enable scheduler yet." if ready_for_disabled_dry_run_design else "Refresh latest prediction first, then re-run this read-only policy design.",
        "read_only_policy_design_only": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
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


def run_design(*, hot_root: Path | None = None) -> dict[str, Any]:
    root = Path(hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT)
    latest_path = root / LATEST_RELATIVE_PATH
    status_path = root / STATUS_RELATIVE_PATH
    latest_payload = _load_json(latest_path) if latest_path.exists() else {}
    status_payload = _load_json(status_path) if status_path.exists() else {}
    result = build_scheduler_producer_policy_design(
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
    result = run_design()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
