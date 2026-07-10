# path: ./btcts_next/src/btcts/prediction/market_regime/source_scorecard_read_model.py
# desc: Pure/read-only MR-VS4 source scorecard read model. Joins trusted outcomes with compact source-attribution rows; no runtime reads/writes or parameter mutation.

from __future__ import annotations

from collections import defaultdict
from math import isfinite
from typing import Any, Iterable, Mapping

MARKET_REGIME_SOURCE_SCORECARD_READ_MODEL_VERSION = "prediction.market_regime.source_scorecard_read_model.2026_07_10.v1"
TRUSTED_OBSERVATION_SOURCE = "candle_summary"
_ALLOWED_OUTCOME_LABELS = {"hit", "partial", "miss", "invalidated", "unknown"}
_OUTCOME_SCORE = {"hit": 1.0, "partial": 0.5, "miss": 0.0, "invalidated": 0.0, "unknown": 0.0}
_FORBIDDEN_RAW_KEYS = {
    "raw_candles", "raw_orderbook", "raw_trades", "raw_executions",
    "raw_market_payload", "raw_source_payload", "bids", "asks", "trades", "executions",
}


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(str(key) in _FORBIDDEN_RAW_KEYS or _has_forbidden_raw_keys(nested) for key, nested in value.items())
    if isinstance(value, list):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def _observation_source(row: Mapping[str, Any]) -> str:
    value = str(row.get("observation_source") or "").strip().lower()
    if value in {"candle", "candles", "derived_candles", "candle_summary"}:
        return TRUSTED_OBSERVATION_SOURCE
    summary = row.get("observation_summary") if isinstance(row.get("observation_summary"), Mapping) else {}
    nested = str(summary.get("observation_source") or "").strip().lower()
    if nested in {"candle", "candles", "derived_candles", "candle_summary"}:
        return TRUSTED_OBSERVATION_SOURCE
    return value or nested or "latest_cards_current"


def _join_key(row: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("run_id") or ""),
        str(row.get("horizon_key") or ""),
        str(row.get("parameter_set_id") or row.get("active_parameter_set_id") or ""),
    )


def _safe_percent(value: object, *, field_name: str) -> int:
    try:
        raw = float(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not isfinite(raw):
        raise ValueError(f"{field_name} must be finite")
    return max(0, min(int(round(raw)), 100))


def _new_bucket() -> dict[str, Any]:
    return {
        "total": 0,
        "known_total": 0,
        "counts": {label: 0 for label in sorted(_ALLOWED_OUTCOME_LABELS)},
        "score_sum": 0.0,
        "signal_strength_sum": 0,
        "freshness_sum": 0,
        "quality_sum": 0,
        "supporting_count": 0,
        "contradicting_count": 0,
        "sample_outcome_ids": [],
    }


def _update(bucket: dict[str, Any], *, outcome: Mapping[str, Any], signal: Mapping[str, Any], predicted_regime: str) -> None:
    label = str(outcome.get("outcome_label") or "unknown")
    if label not in _ALLOWED_OUTCOME_LABELS:
        label = "unknown"
    bucket["total"] += 1
    bucket["counts"][label] += 1
    if label != "unknown":
        bucket["known_total"] += 1
        bucket["score_sum"] += _OUTCOME_SCORE[label]
    direction = str(signal.get("direction") or "unknown")
    if direction == predicted_regime:
        bucket["supporting_count"] += 1
    elif direction not in {"", "unknown", "UNKNOWN"}:
        bucket["contradicting_count"] += 1
    bucket["signal_strength_sum"] += _safe_percent(
        signal.get("signal_strength_percent"), field_name="signal_strength_percent"
    )
    bucket["freshness_sum"] += _safe_percent(
        signal.get("freshness_percent"), field_name="freshness_percent"
    )
    bucket["quality_sum"] += _safe_percent(
        signal.get("quality_percent"), field_name="quality_percent"
    )
    outcome_id = str(outcome.get("outcome_id") or "")
    if outcome_id and outcome_id not in bucket["sample_outcome_ids"] and len(bucket["sample_outcome_ids"]) < 5:
        bucket["sample_outcome_ids"].append(outcome_id)


def _finalize(key: str, bucket: Mapping[str, Any], *, min_trusted_samples: int) -> dict[str, Any]:
    total = int(bucket.get("total") or 0)
    known = int(bucket.get("known_total") or 0)
    counts = dict(bucket.get("counts") or {})
    insufficient = known < int(min_trusted_samples)
    calibration_score = round(float(bucket.get("score_sum") or 0.0) / known, 4) if known else None
    reliability_percent = None if insufficient or calibration_score is None else int(round(calibration_score * 100.0))
    return {
        "key": key,
        "total": total,
        "known_total": known,
        "trusted_sample_count": known,
        "minimum_trusted_sample_count": int(min_trusted_samples),
        "insufficient_sample": insufficient,
        "counts": {label: int(counts.get(label) or 0) for label in sorted(_ALLOWED_OUTCOME_LABELS)},
        "calibration_score": calibration_score,
        "reliability_percent": reliability_percent,
        "avg_signal_strength_percent": round(float(bucket.get("signal_strength_sum") or 0) / total, 2) if total else None,
        "avg_freshness_percent": round(float(bucket.get("freshness_sum") or 0) / total, 2) if total else None,
        "avg_quality_percent": round(float(bucket.get("quality_sum") or 0) / total, 2) if total else None,
        "supporting_count": int(bucket.get("supporting_count") or 0),
        "contradicting_count": int(bucket.get("contradicting_count") or 0),
        "sample_outcome_ids": list(bucket.get("sample_outcome_ids") or []),
    }


def build_market_regime_source_scorecard_read_model(
    *,
    outcome_rows: Iterable[Mapping[str, Any]],
    attribution_rows: Iterable[Mapping[str, Any]],
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    """Build source scorecards from trusted outcomes and matching shadow-attribution rows."""

    if int(min_trusted_samples) <= 0:
        raise ValueError("min_trusted_samples must be positive")

    trusted_outcomes: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    rejected: list[str] = []
    for index, row in enumerate(outcome_rows):
        if not isinstance(row, Mapping):
            rejected.append(f"outcome_{index}_not_mapping")
            continue
        if _has_forbidden_raw_keys(row):
            rejected.append(f"outcome_{index}_forbidden_raw_payload")
            continue
        if _observation_source(row) != TRUSTED_OBSERVATION_SOURCE:
            continue
        key = _join_key(row)
        if not all(key):
            rejected.append(f"outcome_{index}_join_key_missing")
            continue
        if key in trusted_outcomes:
            rejected.append(f"outcome_{index}_duplicate_join_key")
            continue
        trusted_outcomes[key] = row

    attribution_by_key: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    for index, row in enumerate(attribution_rows):
        if not isinstance(row, Mapping):
            rejected.append(f"attribution_{index}_not_mapping")
            continue
        if _has_forbidden_raw_keys(row):
            rejected.append(f"attribution_{index}_forbidden_raw_payload")
            continue
        key = _join_key(row)
        if not all(key):
            rejected.append(f"attribution_{index}_join_key_missing")
            continue
        if key in attribution_by_key:
            rejected.append(f"attribution_{index}_duplicate_join_key")
            continue
        attribution_by_key[key] = row

    by_source: dict[str, dict[str, Any]] = defaultdict(_new_bucket)
    by_source_horizon: dict[str, dict[str, Any]] = defaultdict(_new_bucket)
    matched = 0
    unmatched_outcomes = 0
    for key, outcome in trusted_outcomes.items():
        attribution = attribution_by_key.get(key)
        if attribution is None:
            unmatched_outcomes += 1
            continue
        signals = attribution.get("source_signals")
        if not isinstance(signals, Mapping):
            rejected.append(f"attribution_source_signals_missing:{'|'.join(key)}")
            continue
        predicted = str(outcome.get("predicted_regime_code") or attribution.get("predicted_regime") or "UNKNOWN")
        matched += 1
        for source_id, signal in signals.items():
            source_key = str(source_id).strip()
            if not source_key:
                rejected.append(f"attribution_source_id_missing:{'|'.join(key)}")
                continue
            if not isinstance(signal, Mapping):
                rejected.append(f"attribution_signal_not_mapping:{'|'.join(key)}:{source_key}")
                continue
            try:
                _update(by_source[source_key], outcome=outcome, signal=signal, predicted_regime=predicted)
                _update(by_source_horizon[f"{source_key}|{key[1]}"], outcome=outcome, signal=signal, predicted_regime=predicted)
            except ValueError as exc:
                rejected.append(f"attribution_signal_invalid:{'|'.join(key)}:{source_key}:{exc}")

    source_scorecards = [_finalize(key, by_source[key], min_trusted_samples=min_trusted_samples) | {"source_id": key} for key in sorted(by_source)]
    ready_sources = [row for row in source_scorecards if not row["insufficient_sample"]]
    comparison_ready = (
        bool(source_scorecards)
        and bool(ready_sources)
        and unmatched_outcomes == 0
        and not rejected
    )
    blockers: list[str] = []
    if not trusted_outcomes:
        blockers.append("no_trusted_outcomes")
    if unmatched_outcomes:
        blockers.append("trusted_outcomes_missing_source_attribution")
    if source_scorecards and not ready_sources:
        blockers.append("no_source_with_minimum_trusted_samples")
    if not source_scorecards and trusted_outcomes:
        blockers.append("no_matched_source_scorecards")
    if rejected:
        blockers.append("input_rows_rejected")

    read_model = {
        "schema_version": "market_regime_source_scorecard_read_model.2026_07_10.v1",
        "source_scorecard_read_model_version": MARKET_REGIME_SOURCE_SCORECARD_READ_MODEL_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "source_scorecard_read_model",
        "prediction_family_id": "market_regime",
        "trusted_observation_source": TRUSTED_OBSERVATION_SOURCE,
        "trusted_outcome_count": len(trusted_outcomes),
        "matched_outcome_count": matched,
        "unmatched_trusted_outcome_count": unmatched_outcomes,
        "source_scorecard_count": len(source_scorecards),
        "comparison_ready": comparison_ready,
        "comparison_blockers": blockers,
        "source_scorecards": source_scorecards,
        "by_source_horizon": [_finalize(key, by_source_horizon[key], min_trusted_samples=min_trusted_samples) for key in sorted(by_source_horizon)],
        "input_rejected_row_count": len(rejected),
        "input_rejected_rows": rejected,
        "reliability_update_mode": "read_model_only_human_review_required",
        "auto_apply_allowed": False,
        "auto_promotion_allowed": False,
        "safety": {
            "read_only_inputs": True,
            "display_read_model_only": True,
            "writes_dhot": False,
            "raw_market_data_read": False,
            "producer_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        },
    }
    validation = validate_market_regime_source_scorecard_read_model(read_model)
    if not validation["ok"]:
        raise ValueError(f"source scorecard read model validation failed: {validation}")
    return read_model


def validate_market_regime_source_scorecard_read_model(read_model: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if read_model.get("artifact_kind") != "source_scorecard_read_model":
        failures.append("artifact_kind_mismatch")
    if read_model.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    if read_model.get("trusted_observation_source") != TRUSTED_OBSERVATION_SOURCE:
        failures.append("trusted_observation_source_mismatch")
    if _has_forbidden_raw_keys(read_model):
        failures.append("forbidden_raw_payload")
    if read_model.get("auto_apply_allowed") is not False:
        failures.append("auto_apply_not_false")
    if read_model.get("auto_promotion_allowed") is not False:
        failures.append("auto_promotion_not_false")
    safety = read_model.get("safety") if isinstance(read_model.get("safety"), Mapping) else {}
    for key in ("read_only_inputs", "display_read_model_only", "human_gate_required"):
        if safety.get(key) is not True:
            failures.append(f"safety_{key}_not_true")
    for key in ("writes_dhot", "raw_market_data_read", "producer_enabled", "broker_private_api_allowed", "autotrade_trigger_allowed", "order_intent_submitted", "parameter_auto_promotion_allowed", "live_parameter_apply_allowed"):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    return {"ok": not failures, "failure_count": len(failures), "failures": failures, "comparison_ready": bool(read_model.get("comparison_ready"))}
