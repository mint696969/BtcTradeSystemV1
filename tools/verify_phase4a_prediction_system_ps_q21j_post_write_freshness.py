# path: ./tools/verify_phase4a_prediction_system_ps_q21j_post_write_freshness.py
# desc: PS-Q21J read-only post-write verification for D-hot latest prediction artifact freshness and producer status safety flags. No writes, no scheduler/producer enablement, no AutoTrade/broker.

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

VERIFY_VERSION = "prediction_warroom.post_write_freshness_verification.ps_q21j.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
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
    direct = payload.get("generated_at")
    if direct:
        return str(direct)
    identity = _as_mapping(payload.get("run_identity"))
    if identity.get("generated_at"):
        return str(identity.get("generated_at"))
    outputs = payload.get("outputs") if isinstance(payload.get("outputs"), list) else []
    for row in outputs:
        mapped = _as_mapping(row)
        if mapped.get("generated_at"):
            return str(mapped.get("generated_at"))
    return ""


def _run_id(payload: Mapping[str, Any]) -> str:
    identity = _as_mapping(payload.get("run_identity"))
    return str(identity.get("prediction_run_id") or payload.get("prediction_run_id") or "")


def _market_uid(payload: Mapping[str, Any]) -> str:
    identity = _as_mapping(payload.get("run_identity"))
    return str(identity.get("market_uid") or payload.get("market_uid") or "")


def _output_count(payload: Mapping[str, Any]) -> int:
    outputs = payload.get("outputs")
    if isinstance(outputs, list):
        return len(outputs)
    try:
        return int(payload.get("output_count") or payload.get("prediction_row_count") or 0)
    except Exception:
        return 0


def build_post_write_freshness_verification(
    *,
    latest_payload: Mapping[str, Any] | None,
    status_payload: Mapping[str, Any] | None,
    latest_meta: Mapping[str, Any],
    status_meta: Mapping[str, Any],
    now_utc: str | None = None,
) -> dict[str, Any]:
    latest = _as_mapping(latest_payload or {})
    status = _as_mapping(status_payload or {})
    generated_at = _generated_at(latest)
    now_dt = _parse_utc(now_utc) or _utc_now()
    generated_dt = _parse_utc(generated_at)
    age_sec = int((now_dt - generated_dt).total_seconds()) if generated_dt is not None else None
    max_age = int(status.get("freshness_max_age_sec") or DEFAULT_FRESHNESS_MAX_AGE_SEC)
    output_count = _output_count(latest)
    blockers = [str(item) for item in (status.get("blockers") or []) if item] if isinstance(status.get("blockers"), list) else []
    warnings = [str(item) for item in (status.get("warnings") or []) if item] if isinstance(status.get("warnings"), list) else []
    safe_flags = _as_mapping(status.get("safe_flags"))
    fresh = bool(age_sec is not None and age_sec <= max_age and output_count > 0)
    status_success = bool(
        status.get("producer_state") == "manual_refresh_exported_status_written"
        and status.get("last_success_at")
        and status.get("last_success_generated_at") == generated_at
        and not blockers
    )
    safety_preserved = bool(
        status.get("producer_enabled") is False
        and status.get("scheduler_enabled") is False
        and safe_flags.get("producer_enabled_false") is True
        and safe_flags.get("scheduler_enabled_false") is True
        and safe_flags.get("warroom_ui_trigger_false") is True
        and safe_flags.get("autotrade_trigger_allowed_false") is True
        and safe_flags.get("broker_private_api_allowed_false") is True
        and safe_flags.get("would_send_to_broker_false") is True
    )
    ok = bool(latest_meta.get("exists") and status_meta.get("exists") and fresh and status_success and safety_preserved)
    return {
        "ok": ok,
        "verify_version": VERIFY_VERSION,
        "verification_state": "post_write_fresh" if ok else "post_write_verification_attention",
        "latest_prediction_artifact_exists": bool(latest_meta.get("exists")),
        "latest_prediction_artifact_size_bytes": latest_meta.get("size_bytes"),
        "latest_prediction_artifact_mtime_utc": str(latest_meta.get("mtime_utc") or ""),
        "status_artifact_exists": bool(status_meta.get("exists")),
        "status_artifact_size_bytes": status_meta.get("size_bytes"),
        "status_artifact_mtime_utc": str(status_meta.get("mtime_utc") or ""),
        "generated_at": generated_at,
        "prediction_run_id": _run_id(latest),
        "market_uid": _market_uid(latest),
        "output_count": output_count,
        "age_sec": age_sec,
        "freshness_max_age_sec": max_age,
        "freshness_state": "fresh" if fresh else "stale_or_unknown",
        "post_write_status_success": status_success,
        "producer_state": str(status.get("producer_state") or ""),
        "last_success_at": str(status.get("last_success_at") or ""),
        "last_success_generated_at": str(status.get("last_success_generated_at") or ""),
        "last_failure_at": status.get("last_failure_at"),
        "last_blocker_count": int(status.get("last_blocker_count") or 0),
        "last_warning_count": int(status.get("last_warning_count") or 0),
        "blockers": blockers,
        "warnings": warnings,
        "producer_enabled": status.get("producer_enabled") is True,
        "scheduler_enabled": status.get("scheduler_enabled") is True,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "safety_preserved": safety_preserved,
        "safe_flags": dict(safe_flags),
        "warroom_expected_data_freshness_badge_state": "fresh" if ok else "attention",
        "read_only_verification_only": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def run_verification(*, hot_root: Path | None = None) -> dict[str, Any]:
    root = Path(hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT)
    latest_path = root / LATEST_RELATIVE_PATH
    status_path = root / STATUS_RELATIVE_PATH
    latest_payload = _load_json(latest_path) if latest_path.exists() else {}
    status_payload = _load_json(status_path) if status_path.exists() else {}
    result = build_post_write_freshness_verification(
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
    result = run_verification()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
