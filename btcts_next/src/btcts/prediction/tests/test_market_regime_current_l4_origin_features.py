# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_current_l4_origin_features.py
# desc: MR-F6.9 tests for explicit-parameter MA and volatility-threshold calculation from current L4 closes.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.features.current_l4_origin_features import (
    CurrentL4OriginFeatureParameters,
    calculate_current_l4_origin_features,
)


def _rows(count: int = 60) -> tuple[dict[str, float], ...]:
    return tuple({"close": 100.0 + index} for index in range(count))


def _parameters(**overrides: object) -> CurrentL4OriginFeatureParameters:
    values = dict(
        parameter_set_id="fixture.explicit.v1",
        fast_ma_window_rows=5,
        slow_ma_window_rows=20,
        low_volatility_threshold_bps=10.0,
        high_volatility_threshold_bps=30.0,
    )
    values.update(overrides)
    return CurrentL4OriginFeatureParameters(**values)


def test_calculates_ma_levels_from_exact_tail_windows() -> None:
    result = calculate_current_l4_origin_features(
        _rows(),
        parameters=_parameters(),
        realized_volatility_bps=20.0,
    )
    assert result["fast_ma"] == pytest.approx(sum(range(155, 160)) / 5)
    assert result["slow_ma"] == pytest.approx(sum(range(140, 160)) / 20)
    assert result["fast_ma_window_rows"] == 5
    assert result["slow_ma_window_rows"] == 20


def test_threshold_values_are_explicit_parameter_values_not_inferred() -> None:
    result = calculate_current_l4_origin_features(
        _rows(),
        parameters=_parameters(low_volatility_threshold_bps=12.5, high_volatility_threshold_bps=42.5),
        realized_volatility_bps=18.0,
    )
    assert result["low_volatility_threshold_bps"] == 12.5
    assert result["high_volatility_threshold_bps"] == 42.5
    assert result["semantic_substitution_used"] is False


def test_parameter_windows_fail_closed() -> None:
    with pytest.raises(ValueError, match="ma_window_invalid"):
        _parameters(fast_ma_window_rows=20, slow_ma_window_rows=20)
    with pytest.raises(ValueError, match="ma_window_invalid"):
        _parameters(fast_ma_window_rows=5, slow_ma_window_rows=61)


def test_threshold_order_and_non_finite_values_fail_closed() -> None:
    with pytest.raises(ValueError, match="volatility_threshold_invalid"):
        _parameters(low_volatility_threshold_bps=40.0, high_volatility_threshold_bps=30.0)
    with pytest.raises(ValueError, match="volatility_threshold_invalid"):
        _parameters(low_volatility_threshold_bps=float("nan"))


def test_rows_and_realized_volatility_fail_closed() -> None:
    with pytest.raises(ValueError, match="insufficient_rows"):
        calculate_current_l4_origin_features(_rows(10), parameters=_parameters(), realized_volatility_bps=20.0)
    bad = list(_rows()); bad[-1] = {"close": float("nan")}
    with pytest.raises(ValueError, match="close_invalid"):
        calculate_current_l4_origin_features(tuple(bad), parameters=_parameters(), realized_volatility_bps=20.0)
    with pytest.raises(ValueError, match="realized_volatility_invalid"):
        calculate_current_l4_origin_features(_rows(), parameters=_parameters(), realized_volatility_bps=-1.0)


def test_result_is_read_only_and_has_no_write_side_effect() -> None:
    result = calculate_current_l4_origin_features(_rows(), parameters=_parameters(), realized_volatility_bps=20.0)
    assert result["read_only"] is True
    assert result["write_performed"] is False
    with pytest.raises(TypeError):
        result["fast_ma"] = 0.0
