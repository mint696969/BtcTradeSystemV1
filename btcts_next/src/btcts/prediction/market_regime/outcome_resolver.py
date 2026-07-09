# path: ./btcts_next/src/btcts/prediction/market_regime/outcome_resolver.py
# desc: Market-regime outcome resolver MVP. Builds/appends compact outcome JSONL rows from prediction refs and observation summaries. No raw market duplication, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from .artifact_contracts import MARKET_REGIME_OUTCOME_SCHEMA_VERSION

MARKET_REGIME_OUTCOME_RESOLVER_VERSION = "prediction.market_regime.outcome_resolver.2026_07_08.v1"
MARKET_REGIME_OUTCOME_RULE_VERSION = "market_regime_outcome_rule.2026_07_08.v1"
OUTCOME_PART_FILENAME = "part-00001.jsonl"
OUTCOME_META_FILENAME = "part-00001.meta.json"
_MAX_OUTCOME_ROW_BYTES = 64 * 1024
_ALLOWED_OUTCOME_LABELS = {"hit", "partial", "miss", "invalidated", "unknown"}
_FORBIDDEN_RAW_KEYS = {
    "raw_candles",
    "raw_orderbook",
    "raw_trades",
    "raw_executions",
    "raw_market_payload",
    "raw_source_payload",
    "bids",
    "asks",
    "trades",
    "executions",
}
_COMPATIBLE_PARTIALS = {
    "RANGE": {"REVERSAL_WATCH", "LOW_VOL_COMPRESSION"},
    "REVERSAL_WATCH": {"RANGE", "HIGH_VOL_CHOP"},
    "BREAKOUT": {"UP_TREND", "DOWN_TREND", "HIGH_VOL_CHOP"},
    "UP_TREND": {"BREAKOUT"},
    "DOWN_TREND": {"BREAKOUT"},
    "LOW_VOL_COMPRESSION": {"RANGE", "BREAKOUT"},
    "HIGH_VOL_CHOP": {"BREAKOUT", "REVERSAL_WATCH"},
}


def _parse_ts(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _date(value: str) -> str:
    dt = _parse_ts(value)
    if dt is None:
        return "unknown-date"
    return _iso(dt)[:10]


def outcome_part_relpath(generated_at: str) -> str:
    return f"prediction/market_regime/outcomes/date={_date(generated_at)}/{OUTCOME_PART_FILENAME}"


def outcome_meta_relpath(generated_at: str) -> str:
    return f"prediction/market_regime/outcomes/date={_date(generated_at)}/{OUTCOME_META_FILENAME}"


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _regime(value: object) -> str:
    return str(value or "UNKNOWN").strip().upper() or "UNKNOWN"


def _identity_part(value: object, *, default: str = "unknown") -> str:
    text = str(value or default).strip() or default
    return text.replace(":", "_").replace("|", "_")


def _market_regime_outcome_id(*, run_id: str, generated_at: str, horizon_key: str, parameter_set_id: str) -> str:
    base = run_id or generated_at or "unknown_generated_at"
    parameter = parameter_set_id or "unknown_parameter_set"
    return f"{_identity_part(base)}:{_identity_part(horizon_key)}:{_identity_part(parameter)}:outcome"


def _normalize_observation_source(value: object) -> str:
    source = str(value or "").strip().lower()
    if source in {"candle", "candles", "candle_summary", "derived_candles"}:
        return "candle_summary"
    if source in {"latest_cards", "current", "latest_current", "latest_cards_current", ""}:
        return "latest_cards_current"
    return source


def _observation_source(observation: Mapping[str, Any]) -> str:
    explicit = observation.get("observation_source")
    if explicit:
        return _normalize_observation_source(explicit)
    summary = str(observation.get("summary") or "")
    if observation.get("observation_evaluator_version") or summary.startswith("candle_summary_observation"):
        return "candle_summary"
    return "latest_cards_current"


def _observation_evaluator_version(observation: Mapping[str, Any]) -> str:
    return str(observation.get("observation_evaluator_version") or "")

def _prediction_fields(prediction: Mapping[str, Any]) -> dict[str, Any]:
    detail = prediction.get("detail") if isinstance(prediction.get("detail"), Mapping) else {}
    generated_at = str(prediction.get("generated_at") or prediction.get("prediction_generated_at") or detail.get("generated_at") or "")
    horizon_sec = _as_int(prediction.get("horizon_sec") or detail.get("horizon_sec") or 0)
    generated_dt = _parse_ts(generated_at)
    expiry_at = _iso(generated_dt + timedelta(seconds=max(horizon_sec, 0))) if generated_dt is not None else ""
    return {
        "run_id": str(prediction.get("run_id") or detail.get("run_id") or ""),
        "prediction_id": str(prediction.get("prediction_id") or detail.get("prediction_id") or ""),
        "generated_at": generated_at,
        "horizon": str(prediction.get("horizon") or prediction.get("horizon_label") or ""),
        "horizon_sec": horizon_sec,
        "horizon_key": str(prediction.get("horizon_key") or detail.get("horizon_key") or ("current" if horizon_sec == 0 else f"{horizon_sec}s")),
        "predicted_regime_code": _regime(prediction.get("regime_code") or prediction.get("primary_regime") or detail.get("primary_regime")),
        "confidence_percent": _as_int(prediction.get("confidence_percent") or detail.get("confidence_percent") or 0),
        "evidence_quality": str(prediction.get("evidence_quality") or detail.get("evidence_quality") or ""),
        "freshness_badge": str(prediction.get("freshness_badge") or prediction.get("freshness_state") or detail.get("freshness_state") or ""),
        "parameter_set_id": str(prediction.get("parameter_set_id") or detail.get("active_parameter_set_id") or detail.get("parameter_set_id") or ""),
        "trace_part_jsonl": str(prediction.get("trace_part_jsonl") or detail.get("trace_part_jsonl") or ""),
        "expiry_at": expiry_at,
    }


def resolve_market_regime_outcome_label(*, predicted_regime_code: str, observation: Mapping[str, Any], expiry_at: str) -> tuple[str, str]:
    if bool(observation.get("invalidated")):
        return "invalidated", str(observation.get("invalidation_reason") or "observation_invalidated_prediction")
    if not bool(observation.get("observation_available", True)):
        return "unknown", "observation_unavailable"
    observed_at = _parse_ts(observation.get("observation_at") or observation.get("observed_at"))
    expiry_dt = _parse_ts(expiry_at)
    if observed_at is None or expiry_dt is None:
        return "unknown", "observation_or_expiry_timestamp_missing"
    if observed_at < expiry_dt:
        return "unknown", "prediction_horizon_not_expired"
    predicted = _regime(predicted_regime_code)
    observed = _regime(observation.get("observed_regime_code") or observation.get("regime_code"))
    if observed == "UNKNOWN":
        return "unknown", "observed_regime_unknown"
    if observed == predicted:
        return "hit", "observed_regime_matches_prediction"
    if bool(observation.get("partial_match")):
        return "partial", "observation_marked_partial_match"
    if observed in _COMPATIBLE_PARTIALS.get(predicted, set()):
        return "partial", "observed_regime_is_compatible_partial"
    return "miss", "observed_regime_differs_from_prediction"


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in _FORBIDDEN_RAW_KEYS:
                return True
            if _has_forbidden_raw_keys(nested):
                return True
    elif isinstance(value, list):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def build_market_regime_outcome_row(
    *,
    prediction: Mapping[str, Any],
    observation: Mapping[str, Any],
    resolved_at: str,
) -> Dict[str, Any]:
    fields = _prediction_fields(prediction)
    label, reason = resolve_market_regime_outcome_label(
        predicted_regime_code=fields["predicted_regime_code"],
        observation=observation,
        expiry_at=fields["expiry_at"],
    )
    observed_regime = _regime(observation.get("observed_regime_code") or observation.get("regime_code"))
    observation_source = _observation_source(observation)
    observation_evaluator_version = _observation_evaluator_version(observation)
    run_id = fields["run_id"]
    horizon_key = fields["horizon_key"]
    outcome_id = _market_regime_outcome_id(
        run_id=run_id,
        generated_at=fields["generated_at"],
        horizon_key=horizon_key,
        parameter_set_id=fields["parameter_set_id"],
    )
    row = {
        "schema_version": MARKET_REGIME_OUTCOME_SCHEMA_VERSION,
        "outcome_resolver_version": MARKET_REGIME_OUTCOME_RESOLVER_VERSION,
        "outcome_rule_version": MARKET_REGIME_OUTCOME_RULE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "outcome_row",
        "prediction_family_id": "market_regime",
        "event_type": "market_regime_prediction_outcome",
        "outcome_id": outcome_id,
        "run_id": run_id,
        "prediction_id": fields["prediction_id"],
        "generated_at": fields["generated_at"],
        "resolved_at": resolved_at,
        "horizon": fields["horizon"],
        "horizon_sec": fields["horizon_sec"],
        "horizon_key": horizon_key,
        "expiry_at": fields["expiry_at"],
        "predicted_regime_code": fields["predicted_regime_code"],
        "observed_regime_code": observed_regime,
        "observation_source": observation_source,
        "observation_evaluator_version": observation_evaluator_version,
        "outcome_label": label,
        "outcome_reason": reason,
        "confidence_percent": fields["confidence_percent"],
        "evidence_quality": fields["evidence_quality"],
        "freshness_badge": fields["freshness_badge"],
        "parameter_set_id": fields["parameter_set_id"],
        "trace_part_jsonl": fields["trace_part_jsonl"],
        "observation_summary": {
            "observation_at": str(observation.get("observation_at") or observation.get("observed_at") or ""),
            "observation_available": bool(observation.get("observation_available", True)),
            "observed_regime_code": observed_regime,
            "observation_source": observation_source,
            "observation_evaluator_version": observation_evaluator_version,
            "invalidated": bool(observation.get("invalidated")),
            "invalidation_reason": str(observation.get("invalidation_reason") or ""),
            "partial_match": bool(observation.get("partial_match")),
            "source_refs": list(observation.get("source_refs") or []),
            "summary": str(observation.get("summary") or ""),
        },
        "safety": {
            "read_only_sources": True,
            "outcome_ledger_append_only": True,
            "raw_market_data_duplicated": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "parameter_auto_promotion_allowed": False,
            "would_send_to_broker": False,
        },
    }
    validation = validate_market_regime_outcome_row(row)
    if not validation.get("ok"):
        raise ValueError(f"market-regime outcome row validation failed: {validation}")
    encoded = json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(encoded) > _MAX_OUTCOME_ROW_BYTES:
        raise ValueError(f"outcome row too large: {len(encoded)} bytes")
    return row


def validate_market_regime_outcome_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    failures: list[str] = []
    if row.get("schema_version") != MARKET_REGIME_OUTCOME_SCHEMA_VERSION:
        failures.append("schema_version_mismatch")
    if row.get("artifact_kind") != "outcome_row":
        failures.append("artifact_kind_mismatch")
    if row.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    if row.get("outcome_label") not in _ALLOWED_OUTCOME_LABELS:
        failures.append("outcome_label_invalid")
    for key in ("generated_at", "resolved_at", "horizon_key", "expiry_at", "predicted_regime_code"):
        if not row.get(key):
            failures.append(f"{key}_missing")
    if not isinstance(row.get("observation_summary"), Mapping):
        failures.append("observation_summary_missing")
    if _has_forbidden_raw_keys(row):
        failures.append("forbidden_raw_payload_key_present")
    safety = row.get("safety") if isinstance(row.get("safety"), Mapping) else {}
    for key in (
        "scheduler_enabled",
        "producer_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_intent_submitted",
        "parameter_auto_promotion_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    if safety.get("outcome_ledger_append_only") is not True:
        failures.append("safety_outcome_ledger_append_only_not_true")
    return {
        "ok": not failures,
        "outcome_resolver_version": MARKET_REGIME_OUTCOME_RESOLVER_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "outcome_label": str(row.get("outcome_label") or ""),
    }


def append_market_regime_outcome_row_once(root: str | Path, row: Mapping[str, Any]) -> Dict[str, Any]:
    validation = validate_market_regime_outcome_row(row)
    if not validation.get("ok"):
        raise ValueError(f"market-regime outcome row validation failed: {validation}")
    base = Path(root)
    generated_at = str(row.get("generated_at") or "")
    relpath = outcome_part_relpath(generated_at)
    path = base / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n"
    line_bytes = len(line.encode("utf-8"))
    if line_bytes > _MAX_OUTCOME_ROW_BYTES:
        raise ValueError(f"outcome row too large: {line_bytes} bytes")
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
    row_count = 0
    first_ts = ""
    last_ts = ""
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            row_count += 1
            try:
                payload = json.loads(raw)
                ts = str(payload.get("resolved_at") or payload.get("generated_at") or "")
            except Exception:
                ts = ""
            if ts and not first_ts:
                first_ts = ts
            if ts:
                last_ts = ts
    meta_relpath = outcome_meta_relpath(generated_at)
    meta = {
        "schema_version": "market_regime_outcome_part_meta.2026_07_08.v1",
        "outcome_resolver_version": MARKET_REGIME_OUTCOME_RESOLVER_VERSION,
        "part_jsonl": relpath,
        "row_count": row_count,
        "bytes": path.stat().st_size,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "max_outcome_row_bytes": _MAX_OUTCOME_ROW_BYTES,
        "closed": False,
        "raw_market_data_duplicated": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }
    meta_path = base / meta_relpath
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "outcome_resolver_version": MARKET_REGIME_OUTCOME_RESOLVER_VERSION,
        "outcome_part_jsonl": relpath,
        "outcome_part_meta_json": meta_relpath,
        "bytes_appended": line_bytes,
        "row_count": row_count,
        "raw_market_data_duplicated": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }
