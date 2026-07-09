# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_parameter_set_registry.py
# desc: Tests for market-regime parameter-set registry and MR-A4 current L4 threshold contract.

def test_mr_a4_default_parameter_set_includes_current_l4_thresholds() -> None:
    from btcts.prediction.market_regime.parameter_set import build_default_market_regime_parameter_set

    parameter_set = build_default_market_regime_parameter_set()
    thresholds = parameter_set.thresholds["current_l4_candle_window"]
    assert thresholds["threshold_set_id"] == "market_regime.current_l4_candle_thresholds.v1"
    assert thresholds["directional_abs_net_bps_min"] == 25.0
    assert thresholds["directional_abs_net_range_ratio_min"] == 0.45
    assert parameter_set.live_parameter_apply_allowed is False
