# path: ./btcts_next/src/btcts/prediction/market_regime/calibration_read_model.py
# desc: Market-regime calibration read-model artifact. Projects daily calibration summary/table into a compact display/read model that keeps observation sources separated. No raw market read, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .calibration_summary import calibration_daily_summary_relpath, calibration_table_relpath

MARKET_REGIME_CALIBRATION_READ_MODEL_VERSION = "prediction.market_regime.calibration_read_model.2026_07_08.v1"
CALIBRATION_LATEST_READ_MODEL_RELPATH = "prediction/market_regime/calibration/latest_read_model.json"
PRIMARY_OBSERVATION_SOURCE = "candle_summary"
FALLBACK_OBSERVATION_SOURCE = "latest_cards_current"


def _month_from_date(value: str) -> str:
    return value[:7] if len(value) >= 7 and value[4:5] == "-" else "unknown-month"


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except Exception:
        return None


def _safe_int(value: object) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return dict(payload) if isinstance(payload, Mapping) else {}


def _bucket_view(bucket: Mapping[str, Any]) -> dict[str, Any]:
    counts = bucket.get("counts") if isinstance(bucket.get("counts"), Mapping) else {}
    return {
        "key": str(bucket.get("key") or ""),
        "total": _safe_int(bucket.get("total")),
        "known_total": _safe_int(bucket.get("known_total")),
        "counts": {
            "hit": _safe_int(counts.get("hit")),
            "partial": _safe_int(counts.get("partial")),
            "miss": _safe_int(counts.get("miss")),
            "unknown": _safe_int(counts.get("unknown")),
            "invalidated": _safe_int(counts.get("invalidated")),
        },
        "hit_rate": _safe_float(bucket.get("hit_rate")),
        "partial_rate": _safe_float(bucket.get("partial_rate")),
        "miss_rate": _safe_float(bucket.get("miss_rate")),
        "calibration_score": _safe_float(bucket.get("calibration_score")),
        "avg_confidence_percent": _safe_float(bucket.get("avg_confidence_percent")),
        "sample_trace_refs": list(bucket.get("sample_trace_refs") or [])[:5],
    }


def _items_by_key(items: object) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, Mapping):
            continue
        key = str(item.get("key") or "")
        if key:
            result[key] = _bucket_view(item)
    return result


def _primary_source(source_buckets: Mapping[str, Mapping[str, Any]]) -> str:
    if PRIMARY_OBSERVATION_SOURCE in source_buckets and _safe_int(source_buckets[PRIMARY_OBSERVATION_SOURCE].get("known_total")) > 0:
        return PRIMARY_OBSERVATION_SOURCE
    if FALLBACK_OBSERVATION_SOURCE in source_buckets:
        return FALLBACK_OBSERVATION_SOURCE
    return sorted(source_buckets.keys())[0] if source_buckets else "none"


def build_market_regime_calibration_read_model(
    *,
    daily_summary: Mapping[str, Any],
    calibration_table: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    daily = dict(daily_summary or {})
    table = dict(calibration_table or {})
    source_buckets = _items_by_key(daily.get("by_observation_source"))
    source_horizon_buckets = _items_by_key(daily.get("by_observation_source_horizon"))
    primary = _primary_source(source_buckets)
    primary_bucket = dict(source_buckets.get(primary, {}))
    fallback_bucket = dict(source_buckets.get(FALLBACK_OBSERVATION_SOURCE, {}))
    source_rows = [dict(item) for item in table.get("observation_source_rows", []) if isinstance(item, Mapping)]
    calibration_trust = daily.get("calibration_trust") if isinstance(daily.get("calibration_trust"), Mapping) else {}
    trust_view = {
        "primary_observation_source": str(calibration_trust.get("primary_observation_source") or primary),
        "trusted_observation_source": str(calibration_trust.get("trusted_observation_source") or PRIMARY_OBSERVATION_SOURCE),
        "reference_only_observation_source": str(calibration_trust.get("reference_only_observation_source") or FALLBACK_OBSERVATION_SOURCE),
        "latest_cards_current_is_reference_only": bool(calibration_trust.get("latest_cards_current_is_reference_only", True)),
        "promotion_candidates_use_observation_source": str(calibration_trust.get("promotion_candidates_use_observation_source") or PRIMARY_OBSERVATION_SOURCE),
        "promotion_candidates_require_parameter_set_comparison": bool(calibration_trust.get("promotion_candidates_require_parameter_set_comparison", True)),
        "trusted_parameter_set_count": _safe_int(calibration_trust.get("trusted_parameter_set_count")),
        "trusted_row_count": _safe_int(calibration_trust.get("trusted_row_count")),
        "reference_only_row_count": _safe_int(calibration_trust.get("reference_only_row_count")),
        "overall_includes_reference_rows_for_compatibility": bool(calibration_trust.get("overall_includes_reference_rows_for_compatibility", True)),
    }
    return {
        "schema_version": "market_regime_calibration_read_model.2026_07_08.v1",
        "calibration_read_model_version": MARKET_REGIME_CALIBRATION_READ_MODEL_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "calibration_read_model",
        "prediction_family_id": "market_regime",
        "date": str(daily.get("date") or ""),
        "month": str(table.get("month") or _month_from_date(str(daily.get("date") or ""))),
        "primary_observation_source": primary,
        "primary_observation_note": "candle_summary is the preferred calibration view when available; latest_cards_current is kept as compatibility/reference evidence.",
        "calibration_trust": trust_view,
        "primary": primary_bucket,
        "latest_cards_current_reference": fallback_bucket,
        "by_observation_source": [source_buckets[key] for key in sorted(source_buckets)],
        "by_observation_source_horizon": [source_horizon_buckets[key] for key in sorted(source_horizon_buckets)],
        "table_observation_source_row_count": len(source_rows),
        "table_observation_source_rows": [_bucket_view(row) | {"date": str(row.get("date") or "")} for row in source_rows],
        "overall": _bucket_view(daily.get("overall") if isinstance(daily.get("overall"), Mapping) else {}),
        "source_refs": {
            "daily_summary_json": calibration_daily_summary_relpath(str(daily.get("date") or "unknown-date")),
            "calibration_table_json": calibration_table_relpath(str(table.get("month") or _month_from_date(str(daily.get("date") or "unknown-date")))),
        },
        "safety": _safety(),
    }


def calibration_latest_read_model_relpath() -> str:
    return CALIBRATION_LATEST_READ_MODEL_RELPATH


def write_market_regime_calibration_read_model(root: str | Path, *, date: str) -> dict[str, Any]:
    base = Path(root)
    month = _month_from_date(date)
    daily_relpath = calibration_daily_summary_relpath(date)
    table_relpath = calibration_table_relpath(month)
    daily = _load_json(base / daily_relpath)
    table = _load_json(base / table_relpath)
    if not daily:
        raise FileNotFoundError(f"market-regime calibration daily summary not found: {base / daily_relpath}")
    read_model = build_market_regime_calibration_read_model(daily_summary=daily, calibration_table=table)
    relpath = calibration_latest_read_model_relpath()
    path = base / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(read_model, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return {
        "ok": True,
        "calibration_read_model_version": MARKET_REGIME_CALIBRATION_READ_MODEL_VERSION,
        "date": date,
        "month": month,
        "calibration_read_model_json": relpath,
        "primary_observation_source": read_model.get("primary_observation_source"),
        "primary_calibration_score": (read_model.get("primary") or {}).get("calibration_score") if isinstance(read_model.get("primary"), Mapping) else None,
        "source_refs": read_model.get("source_refs"),
        "safety": _safety(),
    }


def _safety() -> dict[str, Any]:
    return {
        "read_only_calibration_inputs": True,
        "writes_read_model_artifact_only": True,
        "raw_market_data_read": False,
        "raw_market_data_duplicated": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "would_send_to_broker": False,
    }
