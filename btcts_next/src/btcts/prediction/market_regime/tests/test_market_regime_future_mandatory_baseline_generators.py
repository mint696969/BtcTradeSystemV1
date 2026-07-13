# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_mandatory_baseline_generators.py
# desc: MR-F6.2 tests for deterministic no-lookahead mandatory baseline generators.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_comparison import MANDATORY_BASELINE_IDS
from btcts.prediction.market_regime.future_mandatory_baseline_generators import (
    MandatoryBaselineEvidence,
    generate_mandatory_baselines,
)


def _evidence(**overrides: object) -> MandatoryBaselineEvidence:
    values = dict(
        prediction_origin="2026-07-14T00:00:00Z",
        prediction_origin_epoch_sec=1000.0,
        source_snapshot_ref="snapshot:test",
        source_timestamp_epoch_sec=999.0,
        target_horizon_sec=300,
        current_state=MarketRegimeCode.RANGE,
        previous_state=MarketRegimeCode.DOWN_TREND,
        recent_return=0.01,
        fast_ma=101.0,
        slow_ma=100.0,
        realized_volatility=0.02,
        low_volatility_threshold=0.01,
        high_volatility_threshold=0.03,
        current_forecast_label_selection=MarketRegimeCode.BREAKOUT,
    )
    values.update(overrides)
    return MandatoryBaselineEvidence(**values)


def _by_id(evidence: MandatoryBaselineEvidence):
    return {item.baseline_id: item for item in generate_mandatory_baselines(evidence)}


def test_generates_all_mandatory_baselines_in_canonical_order() -> None:
    predictions = generate_mandatory_baselines(_evidence())
    assert tuple(item.baseline_id for item in predictions) == MANDATORY_BASELINE_IDS
    assert all(item.prediction_available for item in predictions)


def test_baseline_decisions_are_deterministic_and_expected() -> None:
    rows = _by_id(_evidence())
    assert rows["always_range"].predicted_state is MarketRegimeCode.RANGE
    assert rows["last_state_persists"].predicted_state is MarketRegimeCode.RANGE
    assert rows["recent_return_sign"].predicted_state is MarketRegimeCode.UP_TREND
    assert rows["simple_ma_slope"].predicted_state is MarketRegimeCode.UP_TREND
    assert rows["simple_volatility_threshold"].predicted_state is MarketRegimeCode.RANGE
    assert rows["current_forecast_label_selection"].predicted_state is MarketRegimeCode.BREAKOUT


def test_negative_return_ma_and_high_volatility_map_to_down_and_chop() -> None:
    rows = _by_id(_evidence(recent_return=-0.01, fast_ma=99.0, slow_ma=100.0, realized_volatility=0.03))
    assert rows["recent_return_sign"].predicted_state is MarketRegimeCode.DOWN_TREND
    assert rows["simple_ma_slope"].predicted_state is MarketRegimeCode.DOWN_TREND
    assert rows["simple_volatility_threshold"].predicted_state is MarketRegimeCode.HIGH_VOL_CHOP


def test_missing_inputs_abstain_per_baseline_without_affecting_others() -> None:
    rows = _by_id(_evidence(recent_return=None, fast_ma=None, realized_volatility=None))
    assert rows["recent_return_sign"].prediction_available is False
    assert rows["simple_ma_slope"].prediction_available is False
    assert rows["simple_volatility_threshold"].prediction_available is False
    assert rows["always_range"].prediction_available is True
    assert rows["last_state_persists"].prediction_available is True


def test_last_state_uses_previous_only_when_current_unknown() -> None:
    rows = _by_id(_evidence(current_state=MarketRegimeCode.UNKNOWN))
    assert rows["last_state_persists"].predicted_state is MarketRegimeCode.DOWN_TREND
    rows = _by_id(_evidence(current_state=MarketRegimeCode.UNKNOWN, previous_state=MarketRegimeCode.UNKNOWN))
    assert rows["last_state_persists"].prediction_available is False


def test_lookahead_and_bad_thresholds_fail_closed() -> None:
    with pytest.raises(ValueError, match="lookahead_detected"):
        _evidence(source_timestamp_epoch_sec=1001.0)
    with pytest.raises(ValueError, match="threshold_order_invalid"):
        _evidence(low_volatility_threshold=0.04, high_volatility_threshold=0.03)


def test_probabilities_are_valid_and_selected_state_is_argmax() -> None:
    for row in generate_mandatory_baselines(_evidence()):
        assert sum(row.probability_by_state.values()) == pytest.approx(1.0)
        assert row.probability_by_state[row.predicted_state] == max(row.probability_by_state.values())
        assert MarketRegimeCode.UNKNOWN not in row.probability_by_state


def test_output_probability_mappings_are_immutable() -> None:
    row = generate_mandatory_baselines(_evidence())[0]
    with pytest.raises(TypeError):
        row.probability_by_state[MarketRegimeCode.RANGE] = 0.5
