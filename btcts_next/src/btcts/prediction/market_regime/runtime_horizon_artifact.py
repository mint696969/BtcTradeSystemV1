# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_artifact.py
# desc: MR-F9.18A pure canonical artifact contract joining one current-state fact and seven horizon-specific future forecasts. No I/O, scheduler, UI, broker, or AutoTrade behavior.

from __future__ import annotations

from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import MarketRegimePrediction
from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC, FutureForecastStatus
from .future_shadow_adapter import MarketRegimeFutureShadowPacket
from .future_trace_identity import build_market_regime_future_trace_set

MARKET_REGIME_RUNTIME_HORIZON_ARTIFACT_VERSION = "prediction.market_regime.runtime_horizon_artifact.mr_f9_18a.v1"
MARKET_REGIME_RUNTIME_HORIZON_ARTIFACT_KIND = "market_regime_runtime_horizon_snapshot"


def _current_trace_id(current: MarketRegimePrediction, generated_at: str) -> str:
    diagnostic = dict(current.diagnostic_record)
    identity = "|".join((
        generated_at,
        "0",
        current.regime_code.value,
        str(diagnostic.get("current_state_source_cutoff_time") or ""),
        str(diagnostic.get("current_state_label_source") or diagnostic.get("selected_label_source") or ""),
        str(current.feature_bundle_hash or ""),
    ))
    return "market_regime_current_trace:" + sha256(identity.encode("utf-8")).hexdigest()


def _current_row(current: MarketRegimePrediction, generated_at: str) -> dict[str, Any]:
    if int(current.horizon_sec) != 0:
        raise ValueError("runtime_horizon_current_prediction_required")
    diagnostic = dict(current.diagnostic_record)
    source_kind = str(diagnostic.get("current_state_label_source") or diagnostic.get("selected_label_source") or "current_state_estimator")
    source_age = diagnostic.get("current_state_window_age_sec")
    return {
        "horizon_key": "current",
        "horizon_sec": 0,
        "prediction_origin": generated_at,
        "trace_id": _current_trace_id(current, generated_at),
        "label": current.regime_code.value,
        "status": "OBSERVED_ESTIMATE",
        "inference_mode": "current_state_estimation",
        "model_id": str(diagnostic.get("current_state_estimator_version") or "market_regime.current_state_estimator"),
        "logic_version": str(diagnostic.get("classifier_version") or ""),
        "parameter_set_id": current.parameter_set_id,
        "target_definition_version": "market_regime_target.current.v1",
        "feature_snapshot_ref": str(current.feature_bundle_hash or ""),
        "raw_output_value": diagnostic.get("current_state_change_point_probability"),
        "raw_output_semantics": "change_point_probability" if diagnostic.get("current_state_change_point_probability_calibrated") else "diagnostic_score_or_none",
        "calibrated_probability_claim": False,
        "display_confidence_percent": None,
        "confidence_semantics": "not_promoted_for_runtime_display",
        "source_kind": source_kind,
        "source_timestamp": str(diagnostic.get("current_state_source_cutoff_time") or ""),
        "source_age_sec": source_age,
        "source_age_semantics": "age_reported_by_current_state_source",
        "source_currentness_verified": bool(diagnostic.get("current_state_source_currentness_verified", False)),
        "source_freshness_state": current.freshness_state.value,
        "display_freshness_claim_allowed": bool(diagnostic.get("current_state_source_currentness_verified", False)),
        "fallback_used": bool(diagnostic.get("current_state_transition_policy_legacy_fallback_used", False)),
        "fallback_reason": "legacy_current_state_fallback" if diagnostic.get("current_state_transition_policy_legacy_fallback_used", False) else "",
        "abstain_reason": "",
        "warnings": list(current.warnings),
        "read_only": True,
    }


def _future_rows(packet: MarketRegimeFutureShadowPacket) -> list[dict[str, Any]]:
    traces = {item.target_horizon_sec: item for item in build_market_regime_future_trace_set(packet)}
    rows = []
    for forecast in sorted(packet.forecasts, key=lambda item: int(item.target_horizon_sec)):
        trace = traces[int(forecast.target_horizon_sec)]
        metadata = dict(forecast.metadata)
        status = forecast.status.value
        rows.append({
            "horizon_key": forecast.target_horizon_key,
            "horizon_sec": int(forecast.target_horizon_sec),
            "prediction_origin": forecast.origin_timestamp,
            "trace_id": trace.trace_id,
            "label": forecast.predicted_future_state.value,
            "status": status,
            "inference_mode": "horizon_specific_future_model",
            "model_id": forecast.model_id,
            "logic_version": forecast.logic_version,
            "parameter_set_id": forecast.parameter_set_id,
            "target_definition_version": forecast.target_definition_version,
            "feature_snapshot_ref": forecast.feature_snapshot_ref,
            "raw_output_value": forecast.raw_model_score_or_probability,
            "raw_output_semantics": "normalized_model_support_score_not_calibrated_probability",
            "calibrated_probability_claim": bool(forecast.calibrated_probability_claim),
            "display_confidence_percent": None if forecast.calibration_display_confidence is None else round(float(forecast.calibration_display_confidence) * 100.0, 2),
            "confidence_semantics": "calibrated_probability" if forecast.calibrated_probability_claim else "not_promoted_for_runtime_display",
            "source_kind": "horizon_specific_model_artifact",
            "source_timestamp": forecast.origin_timestamp,
            "source_age_sec": 0,
            "source_age_semantics": "age_at_prediction_origin_only",
            "source_currentness_verified": True,
            "source_freshness_state": "LIVE_AT_ORIGIN",
            "display_freshness_claim_allowed": False,
            "fallback_used": False,
            "fallback_reason": "",
            "abstained": status == FutureForecastStatus.ABSTAIN.value,
            "abstain_reason": forecast.abstain_reason,
            "transition_path_candidate": [item.to_dict() for item in forecast.transition_path_candidate],
            "invalidation_conditions": list(forecast.invalidation_conditions),
            "metadata": metadata,
            "read_only": True,
        })
    return rows


def build_market_regime_runtime_horizon_artifact(
    *,
    current_prediction: MarketRegimePrediction,
    future_packet: MarketRegimeFutureShadowPacket,
) -> Mapping[str, Any]:
    if future_packet.generated_at.strip() == "":
        raise ValueError("runtime_horizon_prediction_origin_missing")
    rows = [_current_row(current_prediction, future_packet.generated_at), *_future_rows(future_packet)]
    expected = (0, *FUTURE_MARKET_REGIME_HORIZONS_SEC)
    actual = tuple(int(item["horizon_sec"]) for item in rows)
    if actual != expected:
        raise ValueError(f"runtime_horizon_coverage_mismatch:expected={expected}:actual={actual}")
    trace_ids = tuple(str(item["trace_id"]) for item in rows)
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("runtime_horizon_trace_id_collision")
    if any(item["display_confidence_percent"] is not None and not item["calibrated_probability_claim"] for item in rows):
        raise ValueError("runtime_horizon_uncalibrated_display_confidence_forbidden")
    return MappingProxyType({
        "schema_version": MARKET_REGIME_RUNTIME_HORIZON_ARTIFACT_VERSION,
        "artifact_kind": MARKET_REGIME_RUNTIME_HORIZON_ARTIFACT_KIND,
        "prediction_family": "market_regime",
        "generated_at": future_packet.generated_at,
        "prediction_origin": future_packet.generated_at,
        "horizon_count": len(rows),
        "horizons": tuple(MappingProxyType(dict(item)) for item in rows),
        "runtime_card_confidence_replacement": False,
        "runtime_card_freshness_replacement": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "push_ready": True,
        "push_topic": "prediction.family.market_regime",
        "safety": MappingProxyType({
            "pure_projection": True,
            "writes_dhot": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "websocket_opened": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_submission_allowed": False,
            "canonical_replacement": False,
        }),
    })
