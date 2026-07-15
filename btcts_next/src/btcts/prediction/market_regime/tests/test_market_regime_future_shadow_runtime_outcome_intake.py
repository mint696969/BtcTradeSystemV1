# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_runtime_outcome_intake.py
# desc: MR-F8.10 tests for explicit point-in-time runtime outcome intake without historical inference.

from __future__ import annotations

from copy import deepcopy

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_shadow_runtime_outcome_intake import (
    FutureShadowPointObservation,
    build_runtime_outcome_intake_report,
)
from btcts.prediction.market_regime.future_trace_identity import (
    MarketRegimeFutureTraceIdentity,
    _trace_id_from_parts,
)
from btcts.prediction.market_regime.future_forecast_contract import FutureForecastStatus


def trace(horizon: int, parameter_set: str, state: str = "RANGE", status: str = "FORECAST") -> dict:
    origin = "2026-07-15T09:12:33Z"
    expiry = {
        300: "2026-07-15T09:17:33Z", 900: "2026-07-15T09:27:33Z",
        1800: "2026-07-15T09:42:33Z", 3600: "2026-07-15T10:12:33Z",
        21600: "2026-07-15T15:12:33Z", 43200: "2026-07-15T21:12:33Z",
        86400: "2026-07-16T09:12:33Z",
    }[horizon]
    predicted_state = MarketRegimeCode(state)
    forecast_status = FutureForecastStatus(status)
    trace_id = _trace_id_from_parts(
        origin_timestamp=origin,
        target_horizon_sec=horizon,
        target_definition_version=f"market_regime_target.{horizon}s.v1",
        model_id="model",
        logic_version="logic",
        parameter_set_id=parameter_set,
        feature_snapshot_ref="snapshot",
        predicted_future_state=predicted_state,
        forecast_status=forecast_status,
    )
    tmp = MarketRegimeFutureTraceIdentity(
        trace_id=trace_id,
        origin_timestamp=origin,
        expiry_at=expiry,
        target_horizon_sec=horizon,
        target_horizon_key=f"{horizon}s",
        target_definition_version=f"market_regime_target.{horizon}s.v1",
        model_id="model",
        logic_version="logic",
        parameter_set_id=parameter_set,
        feature_snapshot_ref="snapshot",
        predicted_future_state=predicted_state,
        forecast_status=forecast_status,
    )
    return tmp.to_dict()


def report() -> dict:
    pairs = []
    for horizon in (300, 900, 1800, 3600, 21600, 43200, 86400):
        active = trace(horizon, "active")
        shadow = trace(horizon, "shadow")
        pairs.append({
            "pair_id": f"pair:{horizon}",
            "source_bundle_id": f"bundle:{horizon}",
            "slot_identity": {"target_horizon_sec": horizon},
            "trace_plan": {"persistence_plan": {"rows": [active, shadow]}},
        })
    return {
        "source_snapshot_ok": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "preflight_report": {
            "runtime_source_ready": True,
            "prediction_origin": "2026-07-15T09:12:33Z",
            "feature_snapshot_ref": "snapshot",
            "pairs": pairs,
        },
    }


def test_partial_observation_keeps_other_horizons_unresolved() -> None:
    result = build_runtime_outcome_intake_report(
        runtime_preflight_result=report(),
        observations_by_horizon={
            300: FutureShadowPointObservation(
                target_horizon_sec=300,
                observed_at="2026-07-15T09:18:00Z",
                observed_future_state=MarketRegimeCode.RANGE,
                observation_source_ref="source:canonical-state:300",
            )
        },
        resolved_at="2026-07-15T09:20:00Z",
    )
    assert result["pair_count"] == 7
    assert result["trace_count"] == 14
    assert result["observed_horizon_count"] == 1
    assert result["full_horizon_window_complete"] is False
    assert result["status_counts"]["CORRECT"] == 2
    assert result["status_counts"]["UNRESOLVED"] == 12
    assert result["safety"]["historical_state_inference_forbidden"] is True


def test_all_horizons_accept_explicit_observations_and_preserve_trace_identity() -> None:
    observations = {
        horizon: FutureShadowPointObservation(
            target_horizon_sec=horizon,
            observed_at={
                300: "2026-07-15T09:18:00Z", 900: "2026-07-15T09:28:00Z",
                1800: "2026-07-15T09:43:00Z", 3600: "2026-07-15T10:13:00Z",
                21600: "2026-07-15T15:13:00Z", 43200: "2026-07-15T21:13:00Z",
                86400: "2026-07-16T09:13:00Z",
            }[horizon],
            observed_future_state=MarketRegimeCode.RANGE,
            observation_source_ref=f"source:canonical-state:{horizon}",
        )
        for horizon in (300, 900, 1800, 3600, 21600, 43200, 86400)
    }
    result = build_runtime_outcome_intake_report(
        runtime_preflight_result=report(),
        observations_by_horizon=observations,
        resolved_at="2026-07-16T10:00:00Z",
    )
    assert result["full_horizon_window_complete"] is True
    assert result["trace_count"] == 14
    assert len({row["trace_id"] for row in result["outcome_rows"]}) == 14


def test_rejects_unsafe_outer_report_and_unknown_observation_horizon() -> None:
    unsafe = deepcopy(report())
    unsafe["writes_dhot"] = True
    with pytest.raises(ValueError, match="outer_safety_invalid:writes_dhot"):
        build_runtime_outcome_intake_report(
            runtime_preflight_result=unsafe,
            observations_by_horizon={},
            resolved_at="2026-07-15T09:20:00Z",
        )
    with pytest.raises(ValueError, match="unknown_observation_horizon"):
        build_runtime_outcome_intake_report(
            runtime_preflight_result=report(),
            observations_by_horizon={1: object()},
            resolved_at="2026-07-15T09:20:00Z",
        )
