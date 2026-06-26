# path: ./tools/verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility.py
# desc: PS-Q21Q read-only lock/scheduler status visibility packet. Reads D-hot latest/status/lock metadata only; no lock creation/acquire/release, no scheduler/producer enablement, no runner invocation, no artifact writes, no AutoTrade/broker.

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

VISIBILITY_VERSION = "prediction_warroom.read_only_lock_scheduler_status_visibility.ps_q21q.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
LOCK_RELATIVE_PATH = Path("prediction/runtime/non_ui_scheduler_producer.lock.json")
DEFAULT_FRESHNESS_MAX_AGE_SEC = 3600


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


def _age_sec(generated_at: str, now_utc: str | None) -> int | None:
    generated = _parse_utc(generated_at)
    now = _parse_utc(now_utc) or _utc_now()
    if generated is None:
        return None
    return max(0, int((now - generated).total_seconds()))


def build_lock_scheduler_status_visibility_packet(
    *,
    latest_payload: Mapping[str, Any] | None,
    status_payload: Mapping[str, Any] | None,
    latest_meta: Mapping[str, Any],
    status_meta: Mapping[str, Any],
    lock_meta: Mapping[str, Any],
    now_utc: str | None = None,
) -> dict[str, Any]:
    latest = _as_mapping(latest_payload or {})
    status = _as_mapping(status_payload or {})
    safe_flags = _as_mapping(status.get("safe_flags"))
    generated_at = _generated_at(latest)
    age_sec = _age_sec(generated_at, now_utc)
    max_age = int(status.get("freshness_max_age_sec") or DEFAULT_FRESHNESS_MAX_AGE_SEC)
    output_count = _output_count(latest)
    status_blockers = [str(item) for item in status.get("blockers", []) if item] if isinstance(status.get("blockers"), list) else []
    status_warnings = [str(item) for item in status.get("warnings", []) if item] if isinstance(status.get("warnings"), list) else []
    latest_non_stale = bool(age_sec is not None and age_sec <= max_age and output_count > 0)
    latest_status_success = bool(
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
    lock_absent = lock_meta.get("exists") is False
    visibility_ok = bool(latest_meta.get("exists") and status_meta.get("exists") and disabled_boundary_preserved)
    visibility_attention_reasons: list[str] = []
    if not latest_meta.get("exists"):
        visibility_attention_reasons.append("latest_prediction_artifact_missing")
    if not status_meta.get("exists"):
        visibility_attention_reasons.append("producer_status_artifact_missing")
    if not latest_non_stale:
        visibility_attention_reasons.append("latest_prediction_stale_or_unknown")
    if not latest_status_success:
        visibility_attention_reasons.append("latest_status_not_success_or_has_blockers")
    if not disabled_boundary_preserved:
        visibility_attention_reasons.append("disabled_boundary_not_preserved")
    if not lock_absent:
        visibility_attention_reasons.append("d_hot_runtime_lock_file_exists_attention")
    visibility_state = "lock_scheduler_status_visible_non_stale_disabled_no_lock" if not visibility_attention_reasons else "lock_scheduler_status_visible_attention"
    operator_summary_ja = (
        "scheduler/producer は無効、D-hot lock は未作成、最新予測は non-stale です。"
        if visibility_state == "lock_scheduler_status_visible_non_stale_disabled_no_lock"
        else "scheduler/producer は有効化しません。状態に attention があるため、表示のみで確認してください。"
    )
    return {
        "ok": True,
        "visibility_version": VISIBILITY_VERSION,
        "visibility_state": visibility_state,
        "visibility_ok_for_operator_display": visibility_ok,
        "visibility_attention_reasons": visibility_attention_reasons,
        "operator_summary_ja": operator_summary_ja,
        "generated_at": generated_at,
        "age_sec": age_sec,
        "freshness_max_age_sec": max_age,
        "latest_prediction_non_stale": latest_non_stale,
        "output_count": output_count,
        "latest_prediction_artifact_exists": bool(latest_meta.get("exists")),
        "latest_prediction_artifact_mtime_utc": str(latest_meta.get("mtime_utc") or ""),
        "latest_prediction_artifact_size_bytes": latest_meta.get("size_bytes"),
        "latest_status_success_observed": latest_status_success,
        "status_artifact_exists": bool(status_meta.get("exists")),
        "status_artifact_mtime_utc": str(status_meta.get("mtime_utc") or ""),
        "status_artifact_size_bytes": status_meta.get("size_bytes"),
        "producer_state": str(status.get("producer_state") or ""),
        "producer_enabled": status.get("producer_enabled") is True,
        "scheduler_enabled": status.get("scheduler_enabled") is True,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "last_success_at": str(status.get("last_success_at") or ""),
        "last_success_generated_at": str(status.get("last_success_generated_at") or ""),
        "last_failure_at": status.get("last_failure_at"),
        "last_blocker_count": int(status.get("last_blocker_count") or 0),
        "last_warning_count": int(status.get("last_warning_count") or len(status_warnings)),
        "status_blockers": status_blockers,
        "status_warnings": status_warnings,
        "disabled_boundary_preserved": disabled_boundary_preserved,
        "d_hot_lock_artifact_exists": bool(lock_meta.get("exists")),
        "d_hot_lock_artifact_mtime_utc": str(lock_meta.get("mtime_utc") or ""),
        "d_hot_lock_artifact_size_bytes": lock_meta.get("size_bytes"),
        "lock_status_visible": True,
        "scheduler_status_visible": True,
        "producer_status_visible": True,
        "read_only_status_visibility_packet_only": True,
        "d_hot_lock_file_creation_allowed": False,
        "d_hot_lock_file_write_allowed": False,
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
    }


def run_visibility(*, hot_root: Path | None = None) -> dict[str, Any]:
    root = Path(hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT)
    latest_path = root / LATEST_RELATIVE_PATH
    status_path = root / STATUS_RELATIVE_PATH
    lock_path = root / LOCK_RELATIVE_PATH
    latest_payload = _load_json(latest_path) if latest_path.exists() else {}
    status_payload = _load_json(status_path) if status_path.exists() else {}
    result = build_lock_scheduler_status_visibility_packet(
        latest_payload=latest_payload,
        status_payload=status_payload,
        latest_meta=_file_meta(latest_path),
        status_meta=_file_meta(status_path),
        lock_meta=_file_meta(lock_path),
    )
    result["hot_root"] = str(root)
    result["latest_prediction_artifact_path"] = str(latest_path)
    result["status_artifact_path"] = str(status_path)
    result["d_hot_lock_artifact_path"] = str(lock_path)
    return result


def main() -> int:
    result = run_visibility()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
