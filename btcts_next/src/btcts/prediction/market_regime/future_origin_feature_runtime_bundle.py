# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_feature_runtime_bundle.py
# desc: MR-F6.15 pure read-only runtime feature bundle from canonical L4 candles and an explicit shadow parameter set.

from __future__ import annotations

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .contracts import FeatureGroup, FreshnessState
from .features import MarketRegimeFeatureBundle
from .features.current_l4_origin_feature_shadow_registry import (
    get_current_l4_origin_feature_shadow_candidate,
)
from .features.current_l4_origin_features import calculate_current_l4_origin_features
from .future_origin_evidence_adapter import MarketRegimeOriginFeatureInputs
from .future_origin_evidence_runtime_source import build_market_regime_origin_runtime_source

MARKET_REGIME_ORIGIN_FEATURE_RUNTIME_BUNDLE_VERSION = (
    "prediction.market_regime.origin_feature_runtime_bundle.mr_f6_15.v1"
)


def _epoch(value: Any, field: str) -> float:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"origin_feature_runtime_bundle_timestamp_missing:{field}")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"origin_feature_runtime_bundle_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"origin_feature_runtime_bundle_timestamp_timezone_missing:{field}")
    return parsed.astimezone(timezone.utc).timestamp()


def _validate_candle_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_timestamp: str,
) -> tuple[Mapping[str, Any], ...]:
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise ValueError("origin_feature_runtime_bundle_candle_rows_invalid")
    normalized = tuple(dict(row) for row in rows)
    if len(normalized) != 60:
        raise ValueError("origin_feature_runtime_bundle_candle_row_count_not_sixty")
    epochs = tuple(
        _epoch(row.get("time_utc"), f"candle_rows[{index}].time_utc")
        for index, row in enumerate(normalized)
    )
    for previous, current in zip(epochs, epochs[1:]):
        if current <= previous:
            raise ValueError("origin_feature_runtime_bundle_candle_time_not_increasing")
        if abs((current - previous) - 60.0) > 1e-6:
            raise ValueError("origin_feature_runtime_bundle_candle_gap_detected")
    if epochs[-1] > _epoch(source_timestamp, "source_timestamp"):
        raise ValueError("origin_feature_runtime_bundle_candle_lookahead_detected")
    return normalized


def _source_quality_blockers(
    feature_bundle: MarketRegimeFeatureBundle,
) -> tuple[str, ...]:
    blockers: list[str] = []
    if feature_bundle.source_snapshot_ok is not True:
        blockers.append("origin_feature_runtime_bundle_source_snapshot_not_ok")
    required_groups = (
        FeatureGroup.SOURCE_QUALITY,
        FeatureGroup.PRICE_STRUCTURE,
        FeatureGroup.VOLATILITY,
    )
    for group in required_groups:
        matches = tuple(
            item for item in feature_bundle.coverage
            if item.feature_group is group
        )
        if len(matches) != 1:
            blockers.append(
                f"origin_feature_runtime_bundle_coverage_count_invalid:{group.value}"
            )
            continue
        coverage = matches[0]
        if coverage.available is not True:
            blockers.append(
                f"origin_feature_runtime_bundle_coverage_unavailable:{group.value}"
            )
        if coverage.freshness_state is not FreshnessState.LIVE:
            blockers.append(
                f"origin_feature_runtime_bundle_coverage_not_live:{group.value}:"
                f"{coverage.freshness_state.value}"
            )
    return tuple(blockers)


def build_market_regime_origin_feature_runtime_bundle(
    *,
    feature_bundle: MarketRegimeFeatureBundle,
    previous_current_state: Mapping[str, Any] | None,
    canonical_current_l4_candle_rows: Sequence[Mapping[str, Any]],
    shadow_candidate_id: str,
) -> Mapping[str, Any]:
    if not isinstance(feature_bundle, MarketRegimeFeatureBundle):
        raise ValueError("origin_feature_runtime_bundle_feature_bundle_invalid")
    candidate = get_current_l4_origin_feature_shadow_candidate(shadow_candidate_id)
    if candidate.registry_state != "shadow":
        raise ValueError("origin_feature_runtime_bundle_candidate_not_shadow")
    if candidate.selected_for_runtime is not False:
        raise ValueError("origin_feature_runtime_bundle_candidate_runtime_selected")
    if candidate.live_parameter_apply_allowed is not False:
        raise ValueError("origin_feature_runtime_bundle_candidate_live_apply_allowed")

    source_quality_blockers = _source_quality_blockers(feature_bundle)
    base = build_market_regime_origin_runtime_source(
        feature_bundle=feature_bundle,
        previous_current_state=previous_current_state,
    )
    extracted = base["extracted_values"]
    source_timestamp = extracted.get("source_timestamp")
    realized_volatility = extracted.get("realized_volatility")
    if source_timestamp is None:
        raise ValueError("origin_feature_runtime_bundle_source_timestamp_missing")
    if realized_volatility is None:
        raise ValueError("origin_feature_runtime_bundle_realized_volatility_missing")

    rows = _validate_candle_rows(
        canonical_current_l4_candle_rows,
        source_timestamp=str(source_timestamp),
    )
    calculated = calculate_current_l4_origin_features(
        rows,
        parameters=candidate.parameters,
        realized_volatility_bps=float(realized_volatility) * 10000.0,
    )

    completed = {
        **dict(extracted),
        "fast_ma": calculated["fast_ma"],
        "slow_ma": calculated["slow_ma"],
        "low_volatility_threshold": calculated["low_volatility_threshold_bps"] / 10000.0,
        "high_volatility_threshold": calculated["high_volatility_threshold_bps"] / 10000.0,
    }
    missing = tuple(
        field for field, value in completed.items()
        if value is None
    )
    blockers = source_quality_blockers + tuple(
        f"origin_feature_runtime_bundle_missing:{field}" for field in missing
    )
    feature_inputs = None
    if not blockers:
        feature_inputs = MarketRegimeOriginFeatureInputs(
            source_timestamp=str(completed["source_timestamp"]),
            previous_state=completed["previous_state"],
            recent_return=completed["recent_return"],
            fast_ma=completed["fast_ma"],
            slow_ma=completed["slow_ma"],
            realized_volatility=completed["realized_volatility"],
            low_volatility_threshold=completed["low_volatility_threshold"],
            high_volatility_threshold=completed["high_volatility_threshold"],
            current_forecast_label_selection=completed["current_forecast_label_selection"],
        )

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_FEATURE_RUNTIME_BUNDLE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_feature_runtime_bundle_readiness",
        "shadow_candidate_id": candidate.candidate_id,
        "parameter_set_id": candidate.parameters.parameter_set_id,
        "runtime_source_ready": not blockers,
        "source_quality_ready": not source_quality_blockers,
        "blockers": blockers,
        "feature_inputs": feature_inputs,
        "calculated_features": calculated,
        "provenance": MappingProxyType({
            **dict(base["provenance"]),
            "fast_ma": "canonical_current_l4_candle_rows.close + explicit_shadow_parameter_set",
            "slow_ma": "canonical_current_l4_candle_rows.close + explicit_shadow_parameter_set",
            "low_volatility_threshold": "explicit_shadow_parameter_set.low_volatility_threshold_bps/10000",
            "high_volatility_threshold": "explicit_shadow_parameter_set.high_volatility_threshold_bps/10000",
        }),
        "candle_row_count": len(rows),
        "semantic_substitution_used": False,
        "explicit_candidate_required": True,
        "candidate_selection_performed": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
