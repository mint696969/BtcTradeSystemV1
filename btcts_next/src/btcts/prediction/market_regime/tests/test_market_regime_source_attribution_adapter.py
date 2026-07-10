# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_source_attribution_adapter.py
# desc: Focused MR-VS4 tests for pure expansion of trace source attribution into scorecard-ready horizon rows.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.source_attribution_adapter import (  # noqa: E402
    expand_market_regime_trace_source_attribution_rows,
)
from btcts.prediction.market_regime.source_scorecard_read_model import (  # noqa: E402
    build_market_regime_source_scorecard_read_model,
)


def _trace() -> dict:
    return {
        "trace_id": "run-1:trace",
        "run_id": "run-1",
        "generated_at": "2026-07-10T08:00:00Z",
        "active_parameter_set_id": "ps-1",
        "source_attribution_by_horizon": {
            "300s": {
                "horizon_key": "300s",
                "predicted_regime": "RANGE",
                "parameter_set_id": "ps-1",
                "logic_version": "logic-v1",
                "source_signals": {
                    "market_regime.liquidity": {
                        "direction": "RANGE",
                        "signal_strength_percent": 80,
                        "freshness_percent": 100,
                        "quality_percent": 90,
                        "blocked": False,
                    }
                },
            },
            "900s": {
                "horizon_key": "900s",
                "predicted_regime": "UP_TREND",
                "parameter_set_id": "ps-1",
                "logic_version": "logic-v1",
                "source_signals": {
                    "market_regime.orderflow": {
                        "direction": "UP_TREND",
                        "signal_strength_percent": 70,
                        "freshness_percent": 75,
                        "quality_percent": 80,
                        "blocked": False,
                    }
                },
            },
        },
    }


def test_trace_expands_to_one_row_per_horizon() -> None:
    result = expand_market_regime_trace_source_attribution_rows([_trace()])
    assert result["ok"] is True
    assert result["row_count"] == 2
    assert result["rejected_row_count"] == 0
    assert {(row["run_id"], row["horizon_key"], row["parameter_set_id"]) for row in result["rows"]} == {
        ("run-1", "300s", "ps-1"),
        ("run-1", "900s", "ps-1"),
    }


def test_expanded_rows_feed_source_scorecard_without_translation() -> None:
    result = expand_market_regime_trace_source_attribution_rows([_trace()])
    outcome = {
        "outcome_id": "run-1:300s:ps-1:outcome",
        "run_id": "run-1",
        "horizon_key": "300s",
        "parameter_set_id": "ps-1",
        "predicted_regime_code": "RANGE",
        "outcome_label": "hit",
        "observation_source": "candle_summary",
    }
    model = build_market_regime_source_scorecard_read_model(
        outcome_rows=[outcome],
        attribution_rows=result["rows"],
        min_trusted_samples=1,
    )
    assert model["comparison_ready"] is True
    assert model["matched_outcome_count"] == 1
    assert model["source_scorecards"][0]["source_id"] == "market_regime.liquidity"


def test_parameter_set_mismatch_is_rejected_fail_closed() -> None:
    trace = _trace()
    trace["source_attribution_by_horizon"]["300s"]["parameter_set_id"] = "ps-other"
    result = expand_market_regime_trace_source_attribution_rows([trace])
    assert result["ok"] is False
    assert result["rejected_row_count"] == 1
    assert any("parameter_set_id_mismatch" in row for row in result["rejected_rows"])


def test_duplicate_join_key_is_rejected() -> None:
    result = expand_market_regime_trace_source_attribution_rows([_trace(), _trace()])
    assert result["ok"] is False
    assert result["row_count"] == 2
    assert result["rejected_row_count"] == 2
    assert all("duplicate_join_key" in row for row in result["rejected_rows"])


def test_forbidden_raw_payload_is_rejected() -> None:
    trace = _trace()
    trace["raw_market_payload"] = {"secret": True}
    result = expand_market_regime_trace_source_attribution_rows([trace])
    assert result["ok"] is False
    assert result["row_count"] == 0
    assert result["rejected_rows"] == ["trace_0_forbidden_raw_payload"]


def test_safety_is_fixed_read_only() -> None:
    result = expand_market_regime_trace_source_attribution_rows([])
    assert result["safety"]["read_only"] is True
    assert result["safety"]["writes_dhot"] is False
    assert result["safety"]["producer_enabled"] is False
    assert result["safety"]["broker_private_api_allowed"] is False
    assert result["safety"]["autotrade_trigger_allowed"] is False
    assert result["safety"]["order_intent_submitted"] is False
    assert result["safety"]["parameter_auto_promotion_allowed"] is False
    assert result["safety"]["live_parameter_apply_allowed"] is False

def test_missing_active_parameter_set_id_is_rejected() -> None:
    trace = _trace()
    trace["active_parameter_set_id"] = ""
    result = expand_market_regime_trace_source_attribution_rows([trace])
    assert result["ok"] is False
    assert result["row_count"] == 0
    assert result["rejected_rows"] == ["trace_0_active_parameter_set_id_missing"]


def test_non_mapping_signal_is_rejected_without_partial_row() -> None:
    trace = _trace()
    trace["source_attribution_by_horizon"] = {
        "300s": {
            "horizon_key": "300s",
            "predicted_regime": "RANGE",
            "parameter_set_id": "ps-1",
            "source_signals": {
                "market_regime.liquidity": {
                    "direction": "RANGE",
                    "signal_strength_percent": 80,
                    "freshness_percent": 100,
                    "quality_percent": 90,
                    "blocked": False,
                },
                "market_regime.orderflow": "bad",
            },
        }
    }
    result = expand_market_regime_trace_source_attribution_rows([trace])
    assert result["ok"] is False
    assert result["row_count"] == 0
    assert any("signal_not_mapping:market_regime.orderflow" in row for row in result["rejected_rows"])


def test_empty_source_id_is_rejected_without_partial_row() -> None:
    trace = _trace()
    trace["source_attribution_by_horizon"]["300s"]["source_signals"] = {"": {}}
    result = expand_market_regime_trace_source_attribution_rows([trace])
    assert result["ok"] is False
    assert result["row_count"] == 1
    assert any("source_id_missing" in row for row in result["rejected_rows"])
