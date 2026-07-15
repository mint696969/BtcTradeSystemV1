# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_comparison_row_adapter.py
# desc: MR-F8.4 pure join from paired forecasts, origin evidence, and resolved outcomes to comparison rows.

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping, Sequence, Tuple

from .contracts import MarketRegimeCode
from .future_mandatory_baseline_comparison import MandatoryBaselineComparisonRow
from .future_shadow_outcome import MARKET_REGIME_FUTURE_SHADOW_OUTCOME_VERSION

MARKET_REGIME_FUTURE_SHADOW_ROW_ADAPTER_VERSION = (
    "prediction.market_regime.future_shadow_comparison_row_adapter.mr_f8_4.v1"
)
_RESOLVED_OUTCOMES = {"CORRECT", "PARTIAL", "INCORRECT"}


def _required_text(payload: Mapping[str, Any], key: str, prefix: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise ValueError(f"{prefix}_identity_missing:{key}")
    return value


def _probabilities(bundle: Mapping[str, Any]) -> Mapping[MarketRegimeCode, float]:
    raw = bundle.get("candidate_probability_by_state")
    if not isinstance(raw, Mapping) or not raw:
        raise ValueError("shadow_row_adapter_probability_distribution_missing")
    values: dict[MarketRegimeCode, float] = {}
    for raw_state, raw_value in raw.items():
        state = raw_state if isinstance(raw_state, MarketRegimeCode) else MarketRegimeCode(str(raw_state))
        if state is MarketRegimeCode.UNKNOWN:
            continue
        values[state] = float(raw_value)
    return MappingProxyType(values)


def build_future_shadow_comparison_rows(
    *,
    pair: Mapping[str, Any],
    origin_evidence_bundle: Mapping[str, Any],
    outcome_rows: Sequence[Mapping[str, Any]],
    evaluation_window_ref: str,
    outcome_resolver_version: str = MARKET_REGIME_FUTURE_SHADOW_OUTCOME_VERSION,
) -> Tuple[MandatoryBaselineComparisonRow, ...]:
    if pair.get("artifact_kind") != "future_shadow_candidate_pair":
        raise ValueError("shadow_row_adapter_pair_kind_invalid")
    window = str(evaluation_window_ref).strip()
    resolver = str(outcome_resolver_version).strip()
    if not window or not resolver:
        raise ValueError("shadow_row_adapter_comparison_identity_missing")
    slot = pair.get("slot_identity")
    forecasts = pair.get("forecasts")
    if not isinstance(slot, Mapping) or not isinstance(forecasts, (tuple, list)) or len(forecasts) < 2:
        raise ValueError("shadow_row_adapter_pair_payload_invalid")

    for key in ("prediction_origin", "feature_snapshot_ref", "target_horizon_sec", "target_definition_version"):
        pair_key = "origin_timestamp" if key == "prediction_origin" else key
        if origin_evidence_bundle.get(key) != slot.get(pair_key):
            raise ValueError(f"shadow_row_adapter_origin_evidence_slot_mismatch:{key}")
    feature_snapshot = origin_evidence_bundle.get("feature_snapshot")
    if not isinstance(feature_snapshot, Mapping):
        raise ValueError("shadow_row_adapter_feature_snapshot_missing")
    source_ref = _required_text(origin_evidence_bundle, "feature_snapshot_ref", "shadow_row_adapter")
    probabilities = _probabilities(origin_evidence_bundle)

    outcomes_by_trace: dict[str, Mapping[str, Any]] = {}
    for outcome in outcome_rows:
        if not isinstance(outcome, Mapping):
            raise ValueError("shadow_row_adapter_outcome_row_invalid")
        trace_id = _required_text(outcome, "trace_id", "shadow_row_adapter_outcome")
        if trace_id in outcomes_by_trace:
            raise ValueError("shadow_row_adapter_duplicate_outcome_trace")
        outcomes_by_trace[trace_id] = outcome

    rows = []
    for forecast in forecasts:
        if not isinstance(forecast, Mapping):
            raise ValueError("shadow_row_adapter_forecast_invalid")
        trace_id = _required_text(forecast, "trace_id", "shadow_row_adapter_forecast")
        outcome = outcomes_by_trace.get(trace_id)
        status = str(forecast.get("forecast_status") or "")
        prediction_available = status == "FORECAST"
        predicted_state = MarketRegimeCode(str(forecast.get("predicted_future_state") or "UNKNOWN"))
        if prediction_available == (predicted_state is MarketRegimeCode.UNKNOWN):
            raise ValueError("shadow_row_adapter_forecast_status_state_mismatch")

        observation_available = False
        observed_state = MarketRegimeCode.UNKNOWN
        if outcome is not None:
            for key in (
                "origin_timestamp", "target_horizon_sec", "target_definition_version",
                "model_id", "logic_version", "parameter_set_id", "feature_snapshot_ref",
            ):
                forecast_key = "origin_timestamp" if key == "origin_timestamp" else key
                if outcome.get(key) != forecast.get(forecast_key):
                    raise ValueError(f"shadow_row_adapter_outcome_identity_mismatch:{key}")
            outcome_status = str(outcome.get("outcome_status") or "")
            if outcome_status in _RESOLVED_OUTCOMES:
                observed_state = MarketRegimeCode(str(outcome.get("observed_future_state") or "UNKNOWN"))
                observation_available = observed_state is not MarketRegimeCode.UNKNOWN

        rows.append(MandatoryBaselineComparisonRow(
            trace_id=trace_id,
            candidate_id=_required_text(forecast, "parameter_set_id", "shadow_row_adapter_forecast"),
            prediction_origin=_required_text(forecast, "origin_timestamp", "shadow_row_adapter_forecast"),
            evaluation_window_ref=window,
            source_snapshot_ref=source_ref,
            target_horizon_sec=int(forecast.get("target_horizon_sec") or 0),
            target_definition_version=_required_text(forecast, "target_definition_version", "shadow_row_adapter_forecast"),
            outcome_resolver_version=resolver,
            predicted_state=predicted_state,
            observed_state=observed_state,
            probability_by_state=probabilities,
            observation_available=observation_available,
            prediction_available=prediction_available,
            avoidable_unknown=False,
        ))
    if len({row.candidate_id for row in rows}) != len(rows):
        raise ValueError("shadow_row_adapter_duplicate_candidate")
    if len({row.comparison_key for row in rows}) != 1:
        raise ValueError("shadow_row_adapter_identical_slot_mismatch")
    return tuple(rows)
