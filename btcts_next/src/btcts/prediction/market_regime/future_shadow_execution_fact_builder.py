# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_execution_fact_builder.py
# desc: MR-F9.13 pure builder from explicit per-trace invocation observations to validated FutureExecutionFacts.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from .future_forecast_contract import FutureForecastStatus
from .future_shadow_pair_execution_plan import FutureExecutionFacts
from .future_shadow_runtime_preflight_bridge import (
    MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION,
)

MARKET_REGIME_FUTURE_SHADOW_EXECUTION_FACT_BUILDER_VERSION = (
    "prediction.market_regime.future_shadow_execution_fact_builder.mr_f9_13.v1"
)


@dataclass(frozen=True)
class FutureExecutionObservation:
    trace_id: str
    prediction_origin: str
    feature_snapshot_ref: str
    target_horizon_sec: int
    parameter_set_id: str
    inference_mode: FutureInferenceMode
    raw_output_semantics: RawOutputSemantics
    source_freshness_state: str
    source_age_sec: float | None
    fallback_reason: str = ""
    fallback_source_ref: str = ""

    def __post_init__(self) -> None:
        missing = tuple(
            name
            for name, value in (
                ("trace_id", self.trace_id),
                ("prediction_origin", self.prediction_origin),
                ("feature_snapshot_ref", self.feature_snapshot_ref),
                ("parameter_set_id", self.parameter_set_id),
                ("source_freshness_state", self.source_freshness_state),
            )
            if not str(value).strip()
        )
        if missing:
            raise ValueError("future_execution_observation_identity_missing:" + ",".join(missing))
        if int(self.target_horizon_sec) <= 0:
            raise ValueError("future_execution_observation_horizon_invalid")
        if self.source_age_sec is not None and float(self.source_age_sec) < 0.0:
            raise ValueError("future_execution_observation_source_age_negative")
        fallback_used = self.inference_mode is FutureInferenceMode.FALLBACK
        if fallback_used and (not self.fallback_reason.strip() or not self.fallback_source_ref.strip()):
            raise ValueError("future_execution_observation_fallback_details_required")
        if not fallback_used and (self.fallback_reason or self.fallback_source_ref):
            raise ValueError("future_execution_observation_non_fallback_disallows_fallback_fields")


def _forecast_rows(preflight_report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(preflight_report, Mapping):
        raise ValueError("future_execution_fact_builder_preflight_invalid")
    if preflight_report.get("schema_version") != MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION:
        raise ValueError("future_execution_fact_builder_preflight_schema_invalid")
    if preflight_report.get("artifact_kind") != "future_shadow_runtime_preflight_report":
        raise ValueError("future_execution_fact_builder_preflight_kind_invalid")
    if preflight_report.get("runtime_source_ready") is not True:
        raise ValueError("future_execution_fact_builder_runtime_source_not_ready")
    if preflight_report.get("preflight_only") is not True:
        raise ValueError("future_execution_fact_builder_preflight_only_required")
    for field in (
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "canonical_replacement_allowed",
    ):
        if preflight_report.get(field) is not False:
            raise ValueError(f"future_execution_fact_builder_unsafe_preflight_flag:{field}")
    pairs = preflight_report.get("pairs")
    if not isinstance(pairs, Sequence) or isinstance(pairs, (str, bytes)):
        raise ValueError("future_execution_fact_builder_pairs_invalid")
    rows: list[Mapping[str, Any]] = []
    for pair in pairs:
        if not isinstance(pair, Mapping):
            raise ValueError("future_execution_fact_builder_pair_invalid")
        forecasts = pair.get("forecasts")
        if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)):
            raise ValueError("future_execution_fact_builder_forecasts_invalid")
        if len(forecasts) != 2 or any(not isinstance(row, Mapping) for row in forecasts):
            raise ValueError("future_execution_fact_builder_candidate_pair_invalid")
        rows.extend(forecasts)
    if len(rows) != 14:
        raise ValueError("future_execution_fact_builder_trace_count_invalid")
    return tuple(rows)


def build_future_shadow_execution_facts(
    *,
    preflight_report: Mapping[str, Any],
    observations: Sequence[FutureExecutionObservation],
) -> Mapping[str, Any]:
    rows = _forecast_rows(preflight_report)
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        raise ValueError("future_execution_fact_builder_observations_invalid")
    if any(not isinstance(item, FutureExecutionObservation) for item in observations):
        raise ValueError("future_execution_fact_builder_observation_contract_invalid")

    rows_by_trace = {str(row.get("trace_id") or ""): row for row in rows}
    if "" in rows_by_trace or len(rows_by_trace) != len(rows):
        raise ValueError("future_execution_fact_builder_trace_identity_invalid")
    observations_by_trace = {item.trace_id: item for item in observations}
    if len(observations_by_trace) != len(observations):
        raise ValueError("future_execution_fact_builder_observation_trace_duplicate")

    expected = set(rows_by_trace)
    observed = set(observations_by_trace)
    missing = tuple(sorted(expected - observed))
    extra = tuple(sorted(observed - expected))
    if missing:
        raise ValueError("future_execution_fact_builder_observations_missing:" + repr(missing))
    if extra:
        raise ValueError("future_execution_fact_builder_observations_extra:" + repr(extra))

    facts: dict[str, FutureExecutionFacts] = {}
    for trace_id in sorted(expected):
        row = rows_by_trace[trace_id]
        observation = observations_by_trace[trace_id]
        expected_identity = (
            str(row.get("origin_timestamp") or ""),
            str(row.get("feature_snapshot_ref") or ""),
            int(row.get("target_horizon_sec") or 0),
            str(row.get("parameter_set_id") or ""),
        )
        observed_identity = (
            observation.prediction_origin,
            observation.feature_snapshot_ref,
            int(observation.target_horizon_sec),
            observation.parameter_set_id,
        )
        if observed_identity != expected_identity:
            raise ValueError("future_execution_fact_builder_observation_identity_mismatch:" + trace_id)

        try:
            status = FutureForecastStatus(str(row.get("forecast_status") or ""))
        except ValueError as exc:
            raise ValueError("future_execution_fact_builder_forecast_status_invalid") from exc
        if status is FutureForecastStatus.ABSTAIN:
            if observation.inference_mode is not FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE:
                raise ValueError("future_execution_fact_builder_abstain_mode_mismatch:" + trace_id)
            if observation.raw_output_semantics is not RawOutputSemantics.UNSPECIFIED:
                raise ValueError("future_execution_fact_builder_abstain_raw_semantics_invalid:" + trace_id)
        elif observation.inference_mode is FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE:
            raise ValueError("future_execution_fact_builder_forecast_mode_mismatch:" + trace_id)

        raw = row.get("raw_model_score_or_probability")
        if raw is None and observation.raw_output_semantics is not RawOutputSemantics.UNSPECIFIED:
            raise ValueError("future_execution_fact_builder_missing_raw_output_semantics_invalid:" + trace_id)
        if raw is not None and observation.raw_output_semantics is RawOutputSemantics.UNSPECIFIED:
            raise ValueError("future_execution_fact_builder_raw_output_semantics_required:" + trace_id)

        facts[trace_id] = FutureExecutionFacts(
            inference_mode=observation.inference_mode,
            raw_output_semantics=observation.raw_output_semantics,
            source_freshness_state=observation.source_freshness_state,
            source_age_sec=observation.source_age_sec,
            fallback_reason=observation.fallback_reason,
            fallback_source_ref=observation.fallback_source_ref,
        )

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_EXECUTION_FACT_BUILDER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_execution_fact_build_report",
        "prediction_origin": str(preflight_report.get("prediction_origin") or ""),
        "feature_snapshot_ref": str(preflight_report.get("feature_snapshot_ref") or ""),
        "trace_count": len(facts),
        "facts_by_trace_id": MappingProxyType(facts),
        "observations_are_explicit": True,
        "facts_inferred_from_preflight": False,
        "facts_inferred_from_classifier_diagnostics": False,
        "legacy_confidence_promoted_to_probability": False,
        "would_write": False,
        "safety": MappingProxyType({
            "pure": True,
            "read_only_input": True,
            "writer_invoked": False,
            "writes_dhot": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
        }),
    })
