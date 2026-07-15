# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_pair_execution_plan.py
# desc: Pure MR-F9.1B bridge from MR-F8 paired forecast artifacts plus explicit execution facts to immutable evidence rows.

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_execution_evidence import (
    FutureInferenceMode,
    MarketRegimeFutureExecutionEvidence,
    RawOutputSemantics,
)
from .future_forecast_contract import FutureForecastStatus

MARKET_REGIME_FUTURE_SHADOW_PAIR_EXECUTION_PLAN_VERSION = (
    "prediction.market_regime.future_shadow_pair_execution_plan.mr_f9_1b.v1"
)


@dataclass(frozen=True)
class FutureExecutionFacts:
    inference_mode: FutureInferenceMode
    raw_output_semantics: RawOutputSemantics
    source_freshness_state: str
    source_age_sec: float | None
    fallback_reason: str = ""
    fallback_source_ref: str = ""

    def __post_init__(self) -> None:
        if not self.source_freshness_state.strip():
            raise ValueError("future_execution_facts_freshness_state_required")
        if self.source_age_sec is not None and float(self.source_age_sec) < 0.0:
            raise ValueError("future_execution_facts_source_age_negative")
        fallback_used = self.inference_mode is FutureInferenceMode.FALLBACK
        if fallback_used and (not self.fallback_reason.strip() or not self.fallback_source_ref.strip()):
            raise ValueError("future_execution_facts_fallback_details_required")
        if not fallback_used and (self.fallback_reason or self.fallback_source_ref):
            raise ValueError("future_execution_facts_non_fallback_disallows_fallback_fields")


def _required_text(row: Mapping[str, Any], *keys: str) -> None:
    missing = tuple(key for key in keys if not str(row.get(key) or "").strip())
    if missing:
        raise ValueError("future_shadow_pair_execution_row_identity_missing:" + ",".join(missing))


def _fingerprint(*, trace_id: str, facts: FutureExecutionFacts, raw_output: float | None) -> str:
    basis = "|".join((
        trace_id,
        facts.inference_mode.value,
        facts.raw_output_semantics.value,
        "" if raw_output is None else repr(float(raw_output)),
        facts.fallback_reason,
        facts.fallback_source_ref,
    ))
    return "market_regime_future_calculation:" + sha256(basis.encode("utf-8")).hexdigest()


def _evidence_from_row(
    *, row: Mapping[str, Any], facts: FutureExecutionFacts
) -> MarketRegimeFutureExecutionEvidence:
    _required_text(
        row,
        "trace_id", "origin_timestamp", "model_id", "logic_version", "parameter_set_id",
        "feature_snapshot_ref", "target_definition_version", "forecast_status",
    )
    try:
        status = FutureForecastStatus(str(row.get("forecast_status")))
        horizon = int(row.get("target_horizon_sec") or 0)
        raw = row.get("raw_model_score_or_probability")
        raw_output = None if raw is None else float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("future_shadow_pair_execution_row_contract_invalid") from exc
    abstain_reason = str(row.get("abstain_reason") or "")
    return MarketRegimeFutureExecutionEvidence(
        trace_id=str(row["trace_id"]),
        prediction_origin=str(row["origin_timestamp"]),
        generated_at=str(row["origin_timestamp"]),
        target_horizon_sec=horizon,
        model_id=str(row["model_id"]),
        logic_version=str(row["logic_version"]),
        parameter_set_id=str(row["parameter_set_id"]),
        feature_snapshot_ref=str(row["feature_snapshot_ref"]),
        target_definition_version=str(row["target_definition_version"]),
        forecast_status=status,
        inference_mode=facts.inference_mode,
        raw_model_score_or_probability=raw_output,
        raw_output_semantics=facts.raw_output_semantics,
        source_freshness_state=facts.source_freshness_state,
        source_age_sec=facts.source_age_sec,
        abstention_decision=status is FutureForecastStatus.ABSTAIN,
        abstain_reason=abstain_reason,
        fallback_used=facts.inference_mode is FutureInferenceMode.FALLBACK,
        fallback_reason=facts.fallback_reason,
        fallback_source_ref=facts.fallback_source_ref,
        calculation_fingerprint=_fingerprint(trace_id=str(row["trace_id"]), facts=facts, raw_output=raw_output),
    )


def build_future_shadow_pair_execution_plan(
    *, pair: Mapping[str, Any], facts_by_trace_id: Mapping[str, FutureExecutionFacts]
) -> Mapping[str, Any]:
    if pair.get("artifact_kind") != "future_shadow_candidate_pair":
        raise ValueError("future_shadow_pair_execution_pair_kind_invalid")
    pair_id = str(pair.get("pair_id") or "")
    if not pair_id:
        raise ValueError("future_shadow_pair_execution_pair_id_missing")
    forecasts = pair.get("forecasts")
    if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)):
        raise ValueError("future_shadow_pair_execution_forecasts_invalid")
    if len(forecasts) < 2 or any(not isinstance(row, Mapping) for row in forecasts):
        raise ValueError("future_shadow_pair_execution_forecast_rows_invalid")
    if not isinstance(facts_by_trace_id, Mapping):
        raise ValueError("future_shadow_pair_execution_facts_invalid")

    trace_ids = tuple(str(row.get("trace_id") or "") for row in forecasts)
    if any(not item for item in trace_ids) or len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_pair_execution_trace_ids_invalid")
    fact_ids = tuple(str(item) for item in facts_by_trace_id.keys())
    missing = tuple(sorted(set(trace_ids) - set(fact_ids)))
    extra = tuple(sorted(set(fact_ids) - set(trace_ids)))
    if missing:
        raise ValueError("future_shadow_pair_execution_facts_missing:" + ",".join(missing))
    if extra:
        raise ValueError("future_shadow_pair_execution_facts_extra:" + ",".join(extra))
    if any(not isinstance(facts_by_trace_id[item], FutureExecutionFacts) for item in trace_ids):
        raise ValueError("future_shadow_pair_execution_fact_contract_invalid")

    rows = tuple(sorted(
        (_evidence_from_row(row=row, facts=facts_by_trace_id[str(row["trace_id"])]) for row in forecasts),
        key=lambda item: item.trace_id,
    ))
    origins = {item.prediction_origin for item in rows}
    horizons = {item.target_horizon_sec for item in rows}
    snapshots = {item.feature_snapshot_ref for item in rows}
    if len(origins) != 1 or len(horizons) != 1 or len(snapshots) != 1:
        raise ValueError("future_shadow_pair_execution_slot_identity_mismatch")
    if len({item.parameter_set_id for item in rows}) != len(rows):
        raise ValueError("future_shadow_pair_execution_parameter_set_duplicate")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_PAIR_EXECUTION_PLAN_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_pair_execution_plan",
        "pair_id": pair_id,
        "generated_at": rows[0].generated_at,
        "target_horizon_sec": rows[0].target_horizon_sec,
        "feature_snapshot_ref": rows[0].feature_snapshot_ref,
        "evidence_count": len(rows),
        "trace_ids": tuple(item.trace_id for item in rows),
        "rows": tuple(item.to_dict() for item in rows),
        "would_write": False,
        "safety": MappingProxyType({
            "pure": True,
            "facts_are_explicit": True,
            "facts_inferred_from_display": False,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        }),
    })
