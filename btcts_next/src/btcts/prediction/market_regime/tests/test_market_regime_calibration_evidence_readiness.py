# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_calibration_evidence_readiness.py
# desc: Validates MR-F7 calibration evidence readiness cohort separation and fail-closed semantics.

from __future__ import annotations

from btcts.prediction.market_regime.calibration_evidence_readiness import (
    build_market_regime_calibration_evidence_readiness,
)
from btcts.prediction.market_regime.trace_ledger import (
    MARKET_REGIME_SOURCE_FLAG_CONTRIBUTION_LEDGER_VERSION,
)


def _outcome(*, outcome_id: str, run_id: str, source: str = "candle_summary", label: str = "hit") -> dict:
    return {
        "outcome_id": outcome_id,
        "run_id": run_id,
        "horizon_key": "300s",
        "horizon_sec": 300,
        "outcome_label": label,
        "observation_source": source,
    }


def _trace(*, run_id: str, full: bool, detailed: bool = False) -> dict:
    contribution = {
        "source_id": "ticker",
        "flag_id": "ticker_spread_expansion",
        "supports_regime": "HIGH_VOLATILITY",
        "strength": 0.8,
        "weighted_strength": 0.6,
    }
    if detailed:
        contribution.update(
            {
                "parameter_id": "ticker_spread_expansion.weight",
                "parameter_version": "params.v1",
                "base_reliability": 0.7,
                "signed_contribution": 0.6,
                "interaction_adjustment": 0.0,
                "quality_adjustment": 0.0,
                "freshness_adjustment": 0.0,
                "final_contribution": 0.6,
            }
        )
    signal_summary = {
        "horizons": [
            {
                "horizon_key": "300s",
                "source_flag_contributions": [contribution] if full else None,
            }
        ]
    }
    if full:
        signal_summary["source_flag_contribution_ledger_version"] = MARKET_REGIME_SOURCE_FLAG_CONTRIBUTION_LEDGER_VERSION
    return {"run_id": run_id, "signal_summary": signal_summary}


def test_readiness_separates_legacy_coarse_and_full_but_incomplete_trace() -> None:
    result = build_market_regime_calibration_evidence_readiness(
        outcome_rows=[
            _outcome(outcome_id="o1", run_id="legacy"),
            _outcome(outcome_id="o2", run_id="full"),
            _outcome(outcome_id="o3", run_id="reference", source="latest_cards_current"),
        ],
        trace_rows=[
            _trace(run_id="legacy", full=False),
            _trace(run_id="full", full=True),
            _trace(run_id="reference", full=True),
        ],
    )
    assert result["ok"] is True
    assert result["coarse_calibration_ready"] is True
    assert result["detailed_source_flag_calibration_ready"] is False
    assert result["counts"]["coarse_calibration_eligible_count"] == 2
    assert result["counts"]["legacy_coarse_trace_count"] == 1
    assert result["counts"]["full_contribution_trace_count"] == 2
    assert result["counts"].get("detailed_calibration_eligible_count", 0) == 0
    assert "base_reliability" in result["missing_detailed_contribution_fields"]
    assert result["cohort_policy"]["missing_contribution_semantics_may_be_inferred"] is False


def test_readiness_accepts_detailed_only_when_trusted_evaluable_and_complete() -> None:
    result = build_market_regime_calibration_evidence_readiness(
        outcome_rows=[_outcome(outcome_id="o1", run_id="full")],
        trace_rows=[_trace(run_id="full", full=True, detailed=True)],
    )
    assert result["ok"] is True
    assert result["coarse_calibration_ready"] is True
    assert result["detailed_source_flag_calibration_ready"] is True
    assert result["counts"]["detailed_calibration_eligible_count"] == 1
    assert result["missing_detailed_contribution_fields"] == []
    assert result["invalid_detailed_contribution_fields"] == []
    assert result["next_required_actions"] == []


def test_readiness_fails_closed_on_duplicate_identity_and_reports_unmatched() -> None:
    result = build_market_regime_calibration_evidence_readiness(
        outcome_rows=[
            _outcome(outcome_id="same", run_id="missing"),
            _outcome(outcome_id="same", run_id="missing"),
        ],
        trace_rows=[_trace(run_id="dup", full=False), _trace(run_id="dup", full=False)],
    )
    assert result["ok"] is False
    assert "duplicate_trace_run_id:dup" in result["failures"]
    assert "duplicate_outcome_id:same" in result["failures"]
    assert result["counts"]["unmatched_trace_count"] == 1
    assert result["sample_unmatched_outcome_ids"] == ["same"]


def test_non_evaluable_or_reference_rows_never_enter_detailed_calibration() -> None:
    result = build_market_regime_calibration_evidence_readiness(
        outcome_rows=[
            _outcome(outcome_id="unknown", run_id="a", label="unknown"),
            _outcome(outcome_id="reference", run_id="b", source="latest_cards_current"),
        ],
        trace_rows=[_trace(run_id="a", full=True, detailed=True), _trace(run_id="b", full=True, detailed=True)],
    )
    assert result["counts"].get("coarse_calibration_eligible_count", 0) == 0
    assert result["counts"].get("detailed_calibration_eligible_count", 0) == 0
    assert result["detailed_source_flag_calibration_ready"] is False


def test_readiness_rejects_present_but_invalid_detailed_semantics() -> None:
    trace = _trace(run_id="full", full=True, detailed=True)
    contribution = trace["signal_summary"]["horizons"][0]["source_flag_contributions"][0]
    contribution["parameter_id"] = ""
    contribution["base_reliability"] = float("nan")
    contribution["final_contribution"] = None

    result = build_market_regime_calibration_evidence_readiness(
        outcome_rows=[_outcome(outcome_id="o1", run_id="full")],
        trace_rows=[trace],
    )

    assert result["ok"] is True
    assert result["coarse_calibration_ready"] is True
    assert result["detailed_source_flag_calibration_ready"] is False
    assert result["counts"].get("detailed_calibration_eligible_count", 0) == 0
    assert result["missing_detailed_contribution_fields"] == []
    assert result["invalid_detailed_contribution_fields"] == [
        "base_reliability",
        "final_contribution",
        "parameter_id",
    ]
