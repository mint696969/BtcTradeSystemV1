# path: ./tools/design_phase4a_prediction_system_ps_q21n_disabled_non_ui_scheduler_producer_dry_run.py
# desc: PS-Q21N read-only disabled non-UI scheduler/producer dry-run design. No scheduler registration, no producer loop, no runner invocation, no artifact/status writes, no WarRoom UI trigger, no AutoTrade/broker.

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

DRY_RUN_DESIGN_VERSION = "prediction_warroom.disabled_non_ui_scheduler_producer_dry_run_design.ps_q21n.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
FRESHNESS_WARNING_AGE_SEC_DEFAULT = 900
FRESHNESS_MAX_AGE_SEC_DEFAULT = 3600
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


def build_disabled_non_ui_scheduler_producer_dry_run_design(
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
    generated_at = _generated_at(latest)
    generated_dt = _parse_utc(generated_at)
    now_dt = _parse_utc(now_utc) or _utc_now()
    age_sec = int((now_dt - generated_dt).total_seconds()) if generated_dt is not None else None
    freshness_warning_age = int(status.get("freshness_warning_age_sec") or FRESHNESS_WARNING_AGE_SEC_DEFAULT)
    freshness_max_age = int(status.get("freshness_max_age_sec") or FRESHNESS_MAX_AGE_SEC_DEFAULT)
    recommended_cadence = int(status.get("recommended_cadence_sec") or RECOMMENDED_CADENCE_SEC_DEFAULT)
    output_count = _output_count(latest)
    status_blockers = [str(item) for item in status.get("blockers", []) if item] if isinstance(status.get("blockers"), list) else []
    status_warnings = [str(item) for item in status.get("warnings", []) if item] if isinstance(status.get("warnings"), list) else []
    latest_non_stale = bool(age_sec is not None and age_sec <= freshness_max_age and output_count > 0)
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
    dry_run_design_ready = bool(status_success and latest_non_stale and disabled_boundary_preserved)
    dry_run_blockers: list[str] = []
    if not status_success:
        dry_run_blockers.append("latest_status_success_required_before_disabled_dry_run_design")
    if not latest_non_stale:
        dry_run_blockers.append("latest_prediction_non_stale_required_before_disabled_dry_run_design")
    if not disabled_boundary_preserved:
        dry_run_blockers.append("disabled_boundary_required_before_disabled_dry_run_design")
    return {
        "ok": True,
        "dry_run_design_version": DRY_RUN_DESIGN_VERSION,
        "dry_run_design_state": "disabled_non_ui_scheduler_producer_dry_run_design_ready_no_registration" if dry_run_design_ready else "disabled_non_ui_scheduler_producer_dry_run_design_blocked",
        "generated_at": generated_at,
        "age_sec": age_sec,
        "freshness_warning_age_sec": freshness_warning_age,
        "freshness_max_age_sec": freshness_max_age,
        "recommended_cadence_sec": recommended_cadence,
        "output_count": output_count,
        "latest_prediction_non_stale": latest_non_stale,
        "latest_status_success_observed": status_success,
        "disabled_boundary_preserved": disabled_boundary_preserved,
        "status_blockers": status_blockers,
        "status_warnings": status_warnings,
        "dry_run_design_ready": dry_run_design_ready,
        "dry_run_design_blockers": dry_run_blockers,
        "producer_state": str(status.get("producer_state") or ""),
        "producer_enabled": status.get("producer_enabled") is True,
        "scheduler_enabled": status.get("scheduler_enabled") is True,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "disabled_dry_run_plan": {
            "tick_source": "manual_cli_or_test_only_no_scheduler_registration",
            "would_check_clean_tree": True,
            "would_check_single_non_overlapping_lock": True,
            "would_check_latest_prediction_non_stale": True,
            "would_check_status_success": True,
            "would_check_disabled_boundaries": True,
            "would_plan_next_run_window_sec": recommended_cadence,
            "would_skip_if_previous_run_active": True,
            "would_skip_if_latest_is_stale_before_policy_review": True,
            "would_emit_stdout_json_only": True,
        },
        "dry_run_execution_result": {
            "scheduler_registered": False,
            "scheduler_started": False,
            "scheduled_loop_enabled": False,
            "producer_loop_enabled": False,
            "producer_runner_invoked": False,
            "bounded_manual_refresh_invoked": False,
            "actual_export_runner_invoked": False,
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "warroom_ui_trigger_invoked": False,
        },
        "next_recommended_action": "Implement run-lock contract or disabled dry-run smoke only; still no scheduler registration or producer enablement." if dry_run_design_ready else "Refresh latest prediction and restore disabled boundaries before dry-run design.",
        "read_only_dry_run_design_only": True,
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


def run_design(*, hot_root: Path | None = None) -> dict[str, Any]:
    root = Path(hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT)
    latest_path = root / LATEST_RELATIVE_PATH
    status_path = root / STATUS_RELATIVE_PATH
    latest_payload = _load_json(latest_path) if latest_path.exists() else {}
    status_payload = _load_json(status_path) if status_path.exists() else {}
    result = build_disabled_non_ui_scheduler_producer_dry_run_design(
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
