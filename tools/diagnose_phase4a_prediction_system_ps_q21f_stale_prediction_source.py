# path: ./tools/diagnose_phase4a_prediction_system_ps_q21f_stale_prediction_source.py
# desc: PS-Q21F read-only diagnosis for stale WarRoom prediction source artifacts. Prints stdout JSON only; no writes, no scheduler, no AutoTrade, no broker.

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

DIAGNOSTIC_VERSION = "prediction_warroom.stale_prediction_source_diagnostic.ps_q21f.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
FRESHNESS_MAX_AGE_SEC = 3600


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


def _iso(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    return _as_mapping(data)


def _candidate_generated_at(payload: Mapping[str, Any]) -> str:
    direct = payload.get("generated_at")
    if direct:
        return str(direct)
    candidates = payload.get("predictions") or payload.get("prediction_rows") or payload.get("outputs") or []
    if isinstance(candidates, list):
        for row in candidates:
            mapped = _as_mapping(row)
            if mapped.get("generated_at"):
                return str(mapped.get("generated_at"))
    return ""


def _candidate_row_count(payload: Mapping[str, Any]) -> int:
    for key in ("predictions", "prediction_rows", "outputs", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)
    try:
        return int(payload.get("prediction_row_count") or payload.get("record_count") or 0)
    except Exception:
        return 0


def build_stale_prediction_source_diagnostic(
    *,
    latest_payload: Mapping[str, Any] | None,
    status_payload: Mapping[str, Any] | None,
    latest_path_exists: bool,
    latest_mtime_utc: str = "",
    now_utc: str | None = None,
) -> dict[str, Any]:
    latest = _as_mapping(latest_payload or {})
    status = _as_mapping(status_payload or {})
    now_dt = _parse_utc(now_utc) or _utc_now()
    generated_at = _candidate_generated_at(latest)
    generated_dt = _parse_utc(generated_at)
    age_sec = int((now_dt - generated_dt).total_seconds()) if generated_dt is not None else None
    blockers = [str(item) for item in (status.get("blockers") or []) if item]
    warnings = [str(item) for item in (status.get("warnings") or []) if item]
    producer_enabled = status.get("producer_enabled") is True
    scheduler_enabled = status.get("scheduler_enabled") is True
    last_failure_at = str(status.get("last_failure_at") or "")
    producer_state = str(status.get("producer_state") or "missing_status_artifact")
    stale_by_age = bool(age_sec is None or age_sec > int(status.get("freshness_max_age_sec") or FRESHNESS_MAX_AGE_SEC))
    last_manual_refresh_blocked = bool(blockers or "blocked" in producer_state or status.get("last_success_at") in (None, "", "null"))
    actual_export_did_not_write = any("actual_export_runner_did_not_write_latest_prediction_artifact" == item for item in blockers)
    source_mapping_blocked = any("source_mapping" in item or "ps_q9z_probe_not_ready" in item for item in blockers)
    trust_blocked = any("market_overview_trust_state" in item or "interpretation_bucket" in item for item in blockers)
    if not latest_path_exists:
        diagnosis_state = "latest_prediction_artifact_missing"
    elif stale_by_age and last_manual_refresh_blocked:
        diagnosis_state = "prediction_artifact_stale_because_last_manual_refresh_blocked"
    elif stale_by_age and not producer_enabled and not scheduler_enabled:
        diagnosis_state = "prediction_artifact_stale_because_producer_scheduler_disabled"
    elif stale_by_age:
        diagnosis_state = "prediction_artifact_stale_age_exceeds_policy"
    else:
        diagnosis_state = "prediction_artifact_fresh_or_within_policy"
    next_recommended_action = (
        "Fix/read-only diagnose source mapping and trust blockers before scheduler or producer enablement."
        if last_manual_refresh_blocked
        else "If freshness is acceptable, no source refresh action is required."
    )
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "diagnosis_state": diagnosis_state,
        "latest_prediction_artifact_exists": bool(latest_path_exists),
        "latest_prediction_artifact_mtime_utc": latest_mtime_utc,
        "latest_prediction_generated_at": generated_at,
        "latest_prediction_age_sec": age_sec,
        "latest_prediction_row_count": _candidate_row_count(latest),
        "freshness_max_age_sec": int(status.get("freshness_max_age_sec") or FRESHNESS_MAX_AGE_SEC),
        "prediction_artifact_stale": stale_by_age,
        "producer_status_artifact_present": bool(status_payload),
        "producer_version": str(status.get("producer_version") or ""),
        "producer_state": producer_state,
        "producer_enabled": producer_enabled,
        "scheduler_enabled": scheduler_enabled,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "last_run_started_at": str(status.get("last_run_started_at") or ""),
        "last_run_finished_at": str(status.get("last_run_finished_at") or ""),
        "last_success_at": str(status.get("last_success_at") or ""),
        "last_failure_at": last_failure_at,
        "last_success_generated_at": str(status.get("last_success_generated_at") or ""),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "last_manual_refresh_blocked": last_manual_refresh_blocked,
        "actual_export_runner_did_not_write_latest_prediction_artifact": actual_export_did_not_write,
        "source_mapping_blocked": source_mapping_blocked,
        "market_overview_trust_or_interpretation_blocked": trust_blocked,
        "panel_refresh_liveness_not_same_as_prediction_data_freshness": True,
        "next_recommended_action": next_recommended_action,
        "read_only_diagnostic_only": True,
        "runtime_enablement_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def run_diagnostic(*, hot_root: Path | None = None) -> dict[str, Any]:
    # BtcTradeSystem policy: default to hot/current D:\btc_ts_hot.
    # Avoid generic data-root environment variables here because they may point to cold/archive E:\btc_ts.
    root_hint = hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT
    root = Path(root_hint)
    if root.name == "data" and root.parent.name:
        root = root.parent
    latest_path = root / LATEST_RELATIVE_PATH
    status_path = root / STATUS_RELATIVE_PATH
    latest_exists = latest_path.exists()
    latest_payload = _load_json(latest_path) if latest_exists else {}
    status_payload = _load_json(status_path) if status_path.exists() else {}
    latest_mtime = ""
    if latest_exists:
        latest_mtime = _iso(datetime.fromtimestamp(latest_path.stat().st_mtime, tz=timezone.utc))
    result = build_stale_prediction_source_diagnostic(
        latest_payload=latest_payload,
        status_payload=status_payload,
        latest_path_exists=latest_exists,
        latest_mtime_utc=latest_mtime,
    )
    result["hot_root"] = str(root)
    result["latest_prediction_artifact_path"] = str(latest_path)
    result["producer_status_artifact_path"] = str(status_path)
    return result


def main() -> int:
    result = run_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
