# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_source_scorecard_read_model.py
# desc: Focused MR-VS4 tests for the pure/read-only MarketRegime source scorecard read model and fail-closed input handling.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.source_scorecard_read_model import (  # noqa: E402
    build_market_regime_source_scorecard_read_model,
)


def _outcome(*, run_id: str = "run-1", horizon_key: str = "300s", parameter_set_id: str = "ps-1", label: str = "hit") -> dict:
    return {
        "outcome_id": f"{run_id}:{horizon_key}:{parameter_set_id}:outcome",
        "run_id": run_id,
        "horizon_key": horizon_key,
        "parameter_set_id": parameter_set_id,
        "predicted_regime_code": "RANGE",
        "outcome_label": label,
        "observation_source": "candle_summary",
    }


def _attribution(*, run_id: str = "run-1", horizon_key: str = "300s", parameter_set_id: str = "ps-1") -> dict:
    return {
        "run_id": run_id,
        "horizon_key": horizon_key,
        "parameter_set_id": parameter_set_id,
        "predicted_regime": "RANGE",
        "source_signals": {
            "market_regime.liquidity": {
                "direction": "RANGE",
                "signal_strength_percent": 80,
                "freshness_percent": 100,
                "quality_percent": 90,
            },
            "market_regime.orderflow": {
                "direction": "UP_TREND",
                "signal_strength_percent": 60,
                "freshness_percent": 75,
                "quality_percent": 80,
            },
        },
    }


def test_matching_trusted_outcome_builds_source_scorecards() -> None:
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[_outcome()],
        attribution_rows=[_attribution()],
        min_trusted_samples=1,
    )
    assert model["comparison_ready"] is True
    assert model["matched_outcome_count"] == 1
    assert model["source_scorecard_count"] == 2
    liquidity = next(row for row in model["source_scorecards"] if row["source_id"] == "market_regime.liquidity")
    assert liquidity["reliability_percent"] == 100
    assert liquidity["supporting_count"] == 1
    orderflow = next(row for row in model["source_scorecards"] if row["source_id"] == "market_regime.orderflow")
    assert orderflow["contradicting_count"] == 1


def test_unmatched_trusted_outcome_is_explicitly_blocked() -> None:
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[_outcome()], attribution_rows=[], min_trusted_samples=1
    )
    assert model["comparison_ready"] is False
    assert model["unmatched_trusted_outcome_count"] == 1
    assert "trusted_outcomes_missing_source_attribution" in model["comparison_blockers"]


def test_reference_only_outcomes_are_excluded() -> None:
    row = _outcome()
    row["observation_source"] = "latest_cards_current"
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[row], attribution_rows=[_attribution()], min_trusted_samples=1
    )
    assert model["trusted_outcome_count"] == 0
    assert model["comparison_ready"] is False
    assert "no_trusted_outcomes" in model["comparison_blockers"]


def test_minimum_sample_gate_prevents_reliability_update() -> None:
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[_outcome()], attribution_rows=[_attribution()], min_trusted_samples=20
    )
    assert model["comparison_ready"] is False
    assert "no_source_with_minimum_trusted_samples" in model["comparison_blockers"]
    assert all(row["reliability_percent"] is None for row in model["source_scorecards"])


def test_safety_and_no_auto_apply_are_fixed() -> None:
    model = build_market_regime_source_scorecard_read_model(outcome_rows=[], attribution_rows=[])
    assert model["auto_apply_allowed"] is False
    assert model["auto_promotion_allowed"] is False
    assert model["safety"]["writes_dhot"] is False
    assert model["safety"]["producer_enabled"] is False
    assert model["safety"]["broker_private_api_allowed"] is False
    assert model["safety"]["autotrade_trigger_allowed"] is False
    assert model["safety"]["live_parameter_apply_allowed"] is False
    assert model["safety"]["human_gate_required"] is True


def test_rejected_duplicate_rows_prevent_comparison_ready() -> None:
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[_outcome(), _outcome()],
        attribution_rows=[_attribution()],
        min_trusted_samples=1,
    )
    assert model["comparison_ready"] is False
    assert model["input_rejected_row_count"] == 1
    assert "input_rows_rejected" in model["comparison_blockers"]


def test_invalid_signal_percentages_fail_closed_into_rejected_input() -> None:
    attribution = _attribution()
    attribution["source_signals"]["market_regime.liquidity"]["quality_percent"] = float("nan")
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[_outcome()],
        attribution_rows=[attribution],
        min_trusted_samples=1,
    )
    assert model["comparison_ready"] is False
    assert model["input_rejected_row_count"] == 1
    assert any("quality_percent must be finite" in row for row in model["input_rejected_rows"])
    assert "input_rows_rejected" in model["comparison_blockers"]


def test_empty_source_id_and_non_mapping_signal_are_rejected() -> None:
    attribution = _attribution()
    attribution["source_signals"] = {"": {}, "market_regime.liquidity": "bad"}
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[_outcome()],
        attribution_rows=[attribution],
        min_trusted_samples=1,
    )
    assert model["comparison_ready"] is False
    assert model["input_rejected_row_count"] == 2
    assert "input_rows_rejected" in model["comparison_blockers"]


def test_minimum_trusted_samples_must_be_positive() -> None:
    import pytest

    with pytest.raises(ValueError, match="min_trusted_samples must be positive"):
        build_market_regime_source_scorecard_read_model(
            outcome_rows=[_outcome()],
            attribution_rows=[_attribution()],
            min_trusted_samples=0,
        )
