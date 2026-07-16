# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_horizon_dependency.py
# desc: MR-F9.18A7 causal horizon dependency guards.

from __future__ import annotations

from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_horizon_dependency import build_horizon_dependency_contexts


def _rows():
    return {
        horizon: {
            "status": "FORECAST",
            "probability_by_state": {"RANGE": 0.6, "UP_TREND": 0.4},
            "score_margin": 0.2,
            "transition_path_candidate": ({"regime": "RANGE", "earliest_offset_sec": horizon},),
            "uncertainty_state": "UNCALIBRATED",
        }
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
    }


def test_five_minute_change_invalidates_every_later_horizon_only() -> None:
    contexts = build_horizon_dependency_contexts(horizon_results=_rows(), changed_horizon_sec=300)
    by_h = {item.target_horizon_sec: item for item in contexts}
    assert by_h[300].re_evaluation_required is False
    assert all(by_h[h].re_evaluation_required is True for h in FUTURE_MARKET_REGIME_HORIZONS_SEC if h > 300)


def test_one_hour_change_invalidates_only_later_horizons() -> None:
    contexts = build_horizon_dependency_contexts(horizon_results=_rows(), changed_horizon_sec=3600)
    by_h = {item.target_horizon_sec: item for item in contexts}
    assert all(by_h[h].re_evaluation_required is False for h in (300, 900, 1800, 3600))
    assert all(by_h[h].re_evaluation_required is True for h in (21600, 43200, 86400))


def test_context_carries_distribution_not_copied_label() -> None:
    contexts = build_horizon_dependency_contexts(horizon_results=_rows())
    row = next(item for item in contexts if item.target_horizon_sec == 900).to_dict()
    assert row["direct_predecessor_horizon_sec"] == 300
    assert row["predecessor_distribution"] == {"RANGE": 0.6, "UP_TREND": 0.4}
    assert row["label_copy_allowed"] is False
    assert row["distribution_context_only"] is True
    assert row["runtime_activation_allowed"] is False
