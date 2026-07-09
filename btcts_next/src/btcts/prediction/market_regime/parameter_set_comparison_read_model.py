# path: ./btcts_next/src/btcts/prediction/market_regime/parameter_set_comparison_read_model.py
# desc: Market-regime parameter-set comparison read model. Builds trusted, display-only comparison views from outcome rows without D-hot writes, parameter mutation, broker, AutoTrade, or UI inference.

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping

MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_VERSION = "prediction.market_regime.parameter_set_comparison_read_model.2026_07_09.v1"
TRUSTED_OBSERVATION_SOURCE = "candle_summary"
REFERENCE_ONLY_OBSERVATION_SOURCE = "latest_cards_current"
_ALLOWED_OUTCOME_LABELS = ("hit", "partial", "miss", "invalidated", "unknown")
_SCORE = {"hit": 1.0, "partial": 0.5, "miss": 0.0, "invalidated": 0.0, "unknown": 0.0}
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


def _normalize_observation_source(value: object) -> str:
    source = str(value or "").strip().lower()
    if source in {"candle", "candles", "candle_summary", "derived_candles"}:
        return TRUSTED_OBSERVATION_SOURCE
    if source in {"latest_cards", "current", "latest_current", "latest_cards_current", ""}:
        return REFERENCE_ONLY_OBSERVATION_SOURCE
    return source


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


def _safe_int(value: object) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except Exception:
        return None


def _confidence_bucket(value: object) -> str:
    confidence = _safe_int(value)
    if confidence <= 0:
        return "000_unavailable"
    if confidence < 25:
        return "001_024"
    if confidence < 50:
        return "025_049"
    if confidence < 70:
        return "050_069"
    if confidence < 85:
        return "070_084"
    if confidence < 95:
        return "085_094"
    return "095_099"


def _empty_counts() -> dict[str, int]:
    return {label: 0 for label in _ALLOWED_OUTCOME_LABELS}


def _bucket() -> dict[str, Any]:
    return {
        "total": 0,
        "counts": _empty_counts(),
        "score_sum": 0.0,
        "confidence_sum": 0.0,
        "confidence_count": 0,
        "sample_outcome_ids": [],
        "sample_trace_refs": [],
    }


def _known_total(bucket: Mapping[str, Any]) -> int:
    counts = bucket.get("counts") if isinstance(bucket.get("counts"), Mapping) else {}
    return int(bucket.get("total") or 0) - int(counts.get("unknown") or 0)


def _update_bucket(bucket: dict[str, Any], row: Mapping[str, Any]) -> None:
    label = str(row.get("outcome_label") or "unknown")
    if label not in _ALLOWED_OUTCOME_LABELS:
        label = "unknown"
    bucket["total"] += 1
    bucket["counts"][label] += 1
    bucket["score_sum"] += _SCORE[label]
    confidence = row.get("confidence_percent")
    if isinstance(confidence, int | float):
        bucket["confidence_sum"] += float(confidence)
        bucket["confidence_count"] += 1
    outcome_id = str(row.get("outcome_id") or "")
    if outcome_id and outcome_id not in bucket["sample_outcome_ids"] and len(bucket["sample_outcome_ids"]) < 5:
        bucket["sample_outcome_ids"].append(outcome_id)
    trace_ref = str(row.get("trace_part_jsonl") or "")
    if trace_ref and trace_ref not in bucket["sample_trace_refs"] and len(bucket["sample_trace_refs"]) < 5:
        bucket["sample_trace_refs"].append(trace_ref)


def _finalize_bucket(key: str, bucket: Mapping[str, Any], *, min_trusted_samples: int) -> dict[str, Any]:
    total = int(bucket.get("total") or 0)
    counts = dict(bucket.get("counts") or _empty_counts())
    known_total = total - int(counts.get("unknown") or 0)
    confidence_count = int(bucket.get("confidence_count") or 0)
    confidence_sum = float(bucket.get("confidence_sum") or 0.0)
    score_sum = float(bucket.get("score_sum") or 0.0)
    return {
        "key": key,
        "total": total,
        "known_total": known_total,
        "trusted_sample_count": known_total,
        "insufficient_sample": known_total < int(min_trusted_samples),
        "minimum_trusted_sample_count": int(min_trusted_samples),
        "counts": {label: int(counts.get(label) or 0) for label in _ALLOWED_OUTCOME_LABELS},
        "hit_rate": round(counts.get("hit", 0) / known_total, 4) if known_total > 0 else None,
        "partial_rate": round(counts.get("partial", 0) / known_total, 4) if known_total > 0 else None,
        "miss_rate": round(counts.get("miss", 0) / known_total, 4) if known_total > 0 else None,
        "calibration_score": round(score_sum / known_total, 4) if known_total > 0 else None,
        "avg_confidence_percent": round(confidence_sum / confidence_count, 2) if confidence_count > 0 else None,
        "sample_outcome_ids": list(bucket.get("sample_outcome_ids") or []),
        "sample_trace_refs": list(bucket.get("sample_trace_refs") or []),
    }


def _row_observation_source(row: Mapping[str, Any]) -> str:
    if row.get("observation_source"):
        return _normalize_observation_source(row.get("observation_source"))
    summary = row.get("observation_summary") if isinstance(row.get("observation_summary"), Mapping) else {}
    if summary.get("observation_source"):
        return _normalize_observation_source(summary.get("observation_source"))
    if row.get("observation_evaluator_version") or summary.get("observation_evaluator_version"):
        return TRUSTED_OBSERVATION_SOURCE
    return REFERENCE_ONLY_OBSERVATION_SOURCE


def _safe_row(row: Mapping[str, Any]) -> dict[str, Any]:
    label = str(row.get("outcome_label") or "unknown")
    if label not in _ALLOWED_OUTCOME_LABELS:
        label = "unknown"
    horizon_key = str(row.get("horizon_key") or "unknown_horizon")
    parameter_set_id = str(row.get("parameter_set_id") or "unknown_parameter_set")
    predicted = str(row.get("predicted_regime_code") or "UNKNOWN").upper()
    observed = str(row.get("observed_regime_code") or "UNKNOWN").upper()
    outcome_id = str(row.get("outcome_id") or "")
    return {
        "outcome_id": outcome_id,
        "outcome_id_contains_parameter_set_id": bool(parameter_set_id and parameter_set_id in outcome_id),
        "run_id": str(row.get("run_id") or ""),
        "generated_at": str(row.get("generated_at") or ""),
        "resolved_at": str(row.get("resolved_at") or ""),
        "horizon_key": horizon_key,
        "horizon_sec": _safe_int(row.get("horizon_sec")),
        "predicted_regime_code": predicted,
        "observed_regime_code": observed,
        "outcome_label": label,
        "confidence_percent": row.get("confidence_percent"),
        "confidence_bucket": _confidence_bucket(row.get("confidence_percent")),
        "parameter_set_id": parameter_set_id,
        "observation_source": _row_observation_source(row),
        "trace_part_jsonl": str(row.get("trace_part_jsonl") or ""),
    }


def _outcome_identity_audit(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    with_parameter_set = sum(1 for row in rows if bool(row.get("outcome_id_contains_parameter_set_id")))
    without_parameter_set = total - with_parameter_set
    return {
        "identity_source": "parameter_set_id_field",
        "outcome_id_used_for_grouping": False,
        "parameter_set_id_field_required": True,
        "trusted_row_count": total,
        "outcome_id_contains_parameter_set_id_count": with_parameter_set,
        "legacy_outcome_id_without_parameter_set_count": without_parameter_set,
        "legacy_outcome_id_without_parameter_set_present": without_parameter_set > 0,
        "note": "parameter_set comparison groups by parameter_set_id field, not by outcome_id string; legacy outcome_id rows are allowed but audited.",
    }


def _recommendations(parameter_sets: list[dict[str, Any]], *, active_parameter_set_id: str, comparison_ready: bool) -> list[dict[str, Any]]:
    if not parameter_sets:
        return []
    best_score = max((item.get("calibration_score") for item in parameter_sets if isinstance(item.get("calibration_score"), float)), default=None)
    recommendations: list[dict[str, Any]] = []
    for item in parameter_sets:
        parameter_set_id = str(item.get("parameter_set_id") or item.get("key") or "")
        score = item.get("calibration_score")
        known_total = int(item.get("known_total") or 0)
        if bool(item.get("insufficient_sample")):
            action = "insufficient_sample"
            reason = "not_enough_trusted_outcomes"
        elif not comparison_ready:
            action = "keep_testing"
            reason = "comparison_not_ready"
        elif best_score is not None and isinstance(score, float) and score >= best_score:
            action = "keep_testing"
            reason = "best_trusted_score_in_current_view"
        elif active_parameter_set_id and parameter_set_id == active_parameter_set_id:
            action = "rollback_candidate_review"
            reason = "active_set_underperformed_best_trusted_comparable_set"
        else:
            action = "shadow_only"
            reason = "underperformed_best_trusted_comparable_set"
        recommendations.append({
            "parameter_set_id": parameter_set_id,
            "recommendation": action,
            "reason": reason,
            "trusted_sample_count": known_total,
            "calibration_score": score,
            "human_gate_required": True,
            "auto_apply_allowed": False,
            "auto_promotion_allowed": False,
            "recommendation_shape_only": True,
        })
    return recommendations


def build_market_regime_parameter_set_comparison_read_model_from_outcome_rows(
    *,
    rows: Iterable[Mapping[str, Any]],
    date_range: Mapping[str, Any] | None = None,
    active_parameter_set_id: str = "",
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    safe_rows: list[dict[str, Any]] = []
    rejected_rows: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            rejected_rows.append(f"row_{index}_not_mapping")
            continue
        if _has_forbidden_raw_keys(row):
            rejected_rows.append(f"row_{index}_forbidden_raw_payload_key_present")
            continue
        safe_rows.append(_safe_row(row))

    trusted_rows = [row for row in safe_rows if row["observation_source"] == TRUSTED_OBSERVATION_SOURCE]
    reference_rows = [row for row in safe_rows if row["observation_source"] == REFERENCE_ONLY_OBSERVATION_SOURCE]
    identity_audit = _outcome_identity_audit(trusted_rows)
    by_parameter: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_parameter_horizon: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_parameter_predicted_observed: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_parameter_confidence_bucket: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_horizon: dict[str, dict[str, Any]] = defaultdict(_bucket)

    for row in trusted_rows:
        parameter = row["parameter_set_id"] or "unknown_parameter_set"
        horizon = row["horizon_key"] or "unknown_horizon"
        predicted = row["predicted_regime_code"] or "UNKNOWN"
        observed = row["observed_regime_code"] or "UNKNOWN"
        confidence_bucket = row["confidence_bucket"] or "unknown_bucket"
        _update_bucket(by_parameter[parameter], row)
        _update_bucket(by_parameter_horizon[f"{parameter}|{horizon}"], row)
        _update_bucket(by_parameter_predicted_observed[f"{parameter}|{predicted}|{observed}"], row)
        _update_bucket(by_parameter_confidence_bucket[f"{parameter}|{confidence_bucket}"], row)
        _update_bucket(by_horizon[horizon], row)

    parameter_sets = []
    for key in sorted(by_parameter):
        view = _finalize_bucket(key, by_parameter[key], min_trusted_samples=min_trusted_samples)
        view["parameter_set_id"] = key
        view["is_active_parameter_set"] = bool(active_parameter_set_id and key == active_parameter_set_id)
        parameter_sets.append(view)
    parameter_sets.sort(key=lambda item: (item.get("calibration_score") is not None, item.get("calibration_score") or -1.0, item.get("known_total") or 0), reverse=True)

    comparable = [item for item in parameter_sets if not bool(item.get("insufficient_sample")) and int(item.get("known_total") or 0) > 0]
    comparison_ready = len(comparable) >= 2
    trust = {
        "trusted_observation_source": TRUSTED_OBSERVATION_SOURCE,
        "reference_only_observation_source": REFERENCE_ONLY_OBSERVATION_SOURCE,
        "latest_cards_current_is_reference_only": True,
        "trusted_row_count": len(trusted_rows),
        "reference_only_row_count": len(reference_rows),
        "trusted_parameter_set_count": sum(1 for item in parameter_sets if int(item.get("known_total") or 0) > 0),
        "comparable_parameter_set_count": len(comparable),
        "minimum_trusted_sample_count": int(min_trusted_samples),
        "comparison_ready": comparison_ready,
        "comparison_blockers": [] if comparison_ready else ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"],
        "outcome_identity_audit": identity_audit,
    }
    read_model = {
        "schema_version": "market_regime_parameter_set_comparison_read_model.2026_07_09.v1",
        "comparison_read_model_version": MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "parameter_set_comparison_read_model",
        "prediction_family_id": "market_regime",
        "date_range": dict(date_range or {}),
        "active_parameter_set_id": str(active_parameter_set_id or ""),
        "comparison_scope": "trusted_candle_summary_outcomes_only",
        "comparison_ready": comparison_ready,
        "comparison_blockers": list(trust["comparison_blockers"]),
        "calibration_trust": trust,
        "outcome_identity_audit": identity_audit,
        "parameter_sets": parameter_sets,
        "by_parameter_set_horizon": [_finalize_bucket(key, by_parameter_horizon[key], min_trusted_samples=min_trusted_samples) for key in sorted(by_parameter_horizon)],
        "by_parameter_set_predicted_observed": [_finalize_bucket(key, by_parameter_predicted_observed[key], min_trusted_samples=min_trusted_samples) for key in sorted(by_parameter_predicted_observed)],
        "by_parameter_set_confidence_bucket": [_finalize_bucket(key, by_parameter_confidence_bucket[key], min_trusted_samples=min_trusted_samples) for key in sorted(by_parameter_confidence_bucket)],
        "by_horizon": [_finalize_bucket(key, by_horizon[key], min_trusted_samples=min_trusted_samples) for key in sorted(by_horizon)],
        "recommendations": _recommendations(parameter_sets, active_parameter_set_id=str(active_parameter_set_id or ""), comparison_ready=comparison_ready),
        "promotion_candidates": [],
        "input_rejected_row_count": len(rejected_rows),
        "input_rejected_rows": rejected_rows,
        "safety": _safety(),
    }
    validation = validate_market_regime_parameter_set_comparison_read_model(read_model)
    if not validation["ok"]:
        raise ValueError(f"market-regime parameter-set comparison read model validation failed: {validation}")
    return read_model


def build_market_regime_parameter_set_comparison_read_model_from_calibration_summary(
    *,
    daily_summary: Mapping[str, Any],
    calibration_table: Mapping[str, Any] | None = None,
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    """Build a conservative view from aggregate summaries.

    Current daily/table summaries do not preserve parameter_set x observation_source
    rows. Returning comparison_ready=false avoids treating reference-only rows as
    trusted parameter-set comparison evidence.
    """
    daily = dict(daily_summary or {})
    table = dict(calibration_table or {})
    trust = daily.get("calibration_trust") if isinstance(daily.get("calibration_trust"), Mapping) else {}
    rows = [dict(item) for item in table.get("rows", []) if isinstance(item, Mapping)]
    return {
        "schema_version": "market_regime_parameter_set_comparison_read_model.2026_07_09.v1",
        "comparison_read_model_version": MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "parameter_set_comparison_read_model",
        "prediction_family_id": "market_regime",
        "date_range": {"date": str(daily.get("date") or ""), "month": str(table.get("month") or "")},
        "active_parameter_set_id": "",
        "comparison_scope": "calibration_summary_aggregate_safety_view",
        "comparison_ready": False,
        "comparison_blockers": ["parameter_set_by_observation_source_rows_not_available_in_summary"],
        "outcome_identity_audit": {
            "identity_source": "parameter_set_id_field",
            "outcome_id_used_for_grouping": False,
            "parameter_set_id_field_required": True,
            "trusted_row_count": _safe_int(trust.get("trusted_row_count")),
            "outcome_id_contains_parameter_set_id_count": 0,
            "legacy_outcome_id_without_parameter_set_count": 0,
            "legacy_outcome_id_without_parameter_set_present": False,
            "note": "aggregate summary input cannot audit row-level outcome_id identity; comparison remains not ready.",
        },
        "calibration_trust": {
            "trusted_observation_source": str(trust.get("trusted_observation_source") or TRUSTED_OBSERVATION_SOURCE),
            "reference_only_observation_source": str(trust.get("reference_only_observation_source") or REFERENCE_ONLY_OBSERVATION_SOURCE),
            "latest_cards_current_is_reference_only": bool(trust.get("latest_cards_current_is_reference_only", True)),
            "trusted_row_count": _safe_int(trust.get("trusted_row_count")),
            "reference_only_row_count": _safe_int(trust.get("reference_only_row_count")),
            "trusted_parameter_set_count": _safe_int(trust.get("trusted_parameter_set_count")),
            "comparable_parameter_set_count": 0,
            "minimum_trusted_sample_count": int(min_trusted_samples),
            "comparison_ready": False,
            "comparison_blockers": ["aggregate_summary_cannot_filter_parameter_sets_to_trusted_source"],
        },
        "parameter_sets": [],
        "by_parameter_set_horizon": rows,
        "by_parameter_set_predicted_observed": [],
        "by_parameter_set_confidence_bucket": [],
        "by_horizon": [],
        "recommendations": [],
        "promotion_candidates": [],
        "input_rejected_row_count": 0,
        "input_rejected_rows": [],
        "safety": _safety(),
    }


def validate_market_regime_parameter_set_comparison_read_model(read_model: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if read_model.get("artifact_kind") != "parameter_set_comparison_read_model":
        failures.append("artifact_kind_mismatch")
    if read_model.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    if _has_forbidden_raw_keys(read_model):
        failures.append("forbidden_raw_payload_key_present")
    trust = read_model.get("calibration_trust") if isinstance(read_model.get("calibration_trust"), Mapping) else {}
    if trust.get("trusted_observation_source") != TRUSTED_OBSERVATION_SOURCE:
        failures.append("trusted_observation_source_not_candle_summary")
    if trust.get("latest_cards_current_is_reference_only") is not True:
        failures.append("latest_cards_current_reference_boundary_missing")
    identity = read_model.get("outcome_identity_audit") if isinstance(read_model.get("outcome_identity_audit"), Mapping) else {}
    if identity.get("identity_source") != "parameter_set_id_field":
        failures.append("outcome_identity_source_not_parameter_set_id_field")
    if identity.get("outcome_id_used_for_grouping") is not False:
        failures.append("outcome_id_used_for_grouping_not_false")
    if identity.get("parameter_set_id_field_required") is not True:
        failures.append("parameter_set_id_field_required_not_true")
    safety = read_model.get("safety") if isinstance(read_model.get("safety"), Mapping) else {}
    for key in (
        "read_only_inputs",
        "display_read_model_only",
        "human_gate_required_for_parameter_change",
    ):
        if safety.get(key) is not True:
            failures.append(f"safety_{key}_not_true")
    for key in (
        "writes_dhot",
        "producer_enabled",
        "scheduler_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_intent_submitted",
        "parameter_auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    for item in read_model.get("recommendations", []):
        if not isinstance(item, Mapping):
            failures.append("recommendation_not_mapping")
            continue
        if item.get("auto_apply_allowed") is not False:
            failures.append("recommendation_auto_apply_not_false")
        if item.get("auto_promotion_allowed") is not False:
            failures.append("recommendation_auto_promotion_not_false")
        if item.get("human_gate_required") is not True:
            failures.append("recommendation_human_gate_required_not_true")
    return {
        "ok": not failures,
        "comparison_read_model_version": MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "comparison_ready": bool(read_model.get("comparison_ready")),
    }


def _safety() -> dict[str, Any]:
    return {
        "read_only_inputs": True,
        "display_read_model_only": True,
        "writes_dhot": False,
        "raw_market_data_read": False,
        "raw_market_data_duplicated": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "human_gate_required_for_parameter_change": True,
        "would_send_to_broker": False,
    }
