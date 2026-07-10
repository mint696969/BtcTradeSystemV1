# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_source_scorecard_pipeline.py
# desc: Focused MR-VS4 tests for fail-closed orchestration from trace attribution and trusted outcomes to source scorecard readiness.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.source_scorecard_pipeline import (  # noqa: E402
    build_market_regime_source_scorecard_pipeline,
)


def _trace(run_id: str = "run-1") -> dict:
    return {
        "trace_id": f"{run_id}:trace",
        "run_id": run_id,
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
            }
        },
    }


def _outcome(run_id: str = "run-1", label: str = "hit") -> dict:
    return {
        "outcome_id": f"{run_id}:300s:ps-1:outcome",
        "run_id": run_id,
        "horizon_key": "300s",
        "parameter_set_id": "ps-1",
        "predicted_regime_code": "RANGE",
        "outcome_label": label,
        "observation_source": "candle_summary",
    }


def test_pipeline_ready_when_adapter_and_scorecard_are_ready() -> None:
    result = build_market_regime_source_scorecard_pipeline(
        trace_rows=[_trace()],
        outcome_rows=[_outcome()],
        min_trusted_samples=1,
    )
    assert result["pipeline_ready"] is True
    assert result["pipeline_blockers"] == []
    assert result["ready_source_count"] == 1
    assert result["source_progress"] == [{
        "source_id": "market_regime.liquidity",
        "trusted_sample_count": 1,
        "minimum_trusted_sample_count": 1,
        "remaining_trusted_samples": 0,
        "ready": True,
    }]


def test_pipeline_exposes_remaining_sample_count() -> None:
    result = build_market_regime_source_scorecard_pipeline(
        trace_rows=[_trace()],
        outcome_rows=[_outcome()],
        min_trusted_samples=20,
    )
    assert result["pipeline_ready"] is False
    assert result["source_progress"][0]["remaining_trusted_samples"] == 19
    assert "no_source_with_minimum_trusted_samples" in result["pipeline_blockers"]


def test_adapter_rejection_forces_pipeline_not_ready() -> None:
    bad = _trace()
    bad["active_parameter_set_id"] = ""
    result = build_market_regime_source_scorecard_pipeline(
        trace_rows=[bad],
        outcome_rows=[_outcome()],
        min_trusted_samples=1,
    )
    assert result["pipeline_ready"] is False
    assert result["adapter"]["ok"] is False
    assert "source_attribution_adapter_rejected_rows" in result["pipeline_blockers"]


def test_unmatched_outcome_is_explicit() -> None:
    result = build_market_regime_source_scorecard_pipeline(
        trace_rows=[_trace("run-1")],
        outcome_rows=[_outcome("run-2")],
        min_trusted_samples=1,
    )
    assert result["pipeline_ready"] is False
    assert "trusted_outcomes_missing_source_attribution" in result["pipeline_blockers"]


def test_safety_is_fixed_read_only() -> None:
    result = build_market_regime_source_scorecard_pipeline(
        trace_rows=[], outcome_rows=[], min_trusted_samples=20
    )
    assert result["safety"]["read_only"] is True
    assert result["safety"]["writes_dhot"] is False
    assert result["safety"]["producer_enabled"] is False
    assert result["safety"]["broker_private_api_allowed"] is False
    assert result["safety"]["autotrade_trigger_allowed"] is False
    assert result["safety"]["parameter_auto_promotion_allowed"] is False
    assert result["safety"]["live_parameter_apply_allowed"] is False
    assert result["safety"]["human_gate_required"] is True

def test_trace_without_outcome_exposes_zero_progress_for_observed_sources() -> None:
    result = build_market_regime_source_scorecard_pipeline(
        trace_rows=[_trace()],
        outcome_rows=[],
        min_trusted_samples=20,
    )
    assert result["pipeline_ready"] is False
    assert result["source_count"] == 1
    assert result["ready_source_count"] == 0
    assert result["source_progress"] == [{
        "source_id": "market_regime.liquidity",
        "trusted_sample_count": 0,
        "minimum_trusted_sample_count": 20,
        "remaining_trusted_samples": 20,
        "ready": False,
    }]
    assert "no_trusted_outcomes" in result["pipeline_blockers"]


def test_multiple_observed_sources_are_reported_deterministically_before_outcomes() -> None:
    trace = _trace()
    trace["source_attribution_by_horizon"]["300s"]["source_signals"][
        "market_regime.orderflow"
    ] = {
        "direction": "RANGE",
        "signal_strength_percent": 60,
        "freshness_percent": 100,
        "quality_percent": 80,
        "blocked": False,
    }
    result = build_market_regime_source_scorecard_pipeline(
        trace_rows=[trace],
        outcome_rows=[],
        min_trusted_samples=3,
    )
    assert [row["source_id"] for row in result["source_progress"]] == [
        "market_regime.liquidity",
        "market_regime.orderflow",
    ]
    assert all(row["trusted_sample_count"] == 0 for row in result["source_progress"])
    assert all(row["remaining_trusted_samples"] == 3 for row in result["source_progress"])
