# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_confidence_integration.py
# desc: Focused MR-VS3 shadow confidence integration tests. No classifier output replacement or runtime I/O.

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.confidence_integration import (  # noqa: E402
    MARKET_REGIME_CONFIDENCE_INTEGRATION_VERSION,
    build_market_regime_shadow_confidence_report,
)
from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage  # noqa: E402
from btcts.prediction.market_regime.currentness_gate import build_market_regime_currentness_gate_report  # noqa: E402


def _coverage(group: FeatureGroup, freshness: FreshnessState = FreshnessState.LIVE) -> SourceCoverage:
    return SourceCoverage(feature_group=group, available=freshness != FreshnessState.MISSING, freshness_state=freshness)


def _all_live() -> tuple[SourceCoverage, ...]:
    return tuple(_coverage(group) for group in FeatureGroup)


def _signal_report(*, horizon_key: str = "300s", strength: float = 0.9, supports: str = "RANGE") -> dict:
    return {
        "horizons": [
            {
                "horizon_key": horizon_key,
                "signal_votes_top_n": [
                    {"source_family": group.value, "supports_regime": supports, "strength": strength}
                    for group in FeatureGroup
                ],
            }
        ]
    }


def test_aligned_live_sources_build_shadow_report_without_replacing_classifier() -> None:
    coverage = _all_live()
    gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=coverage)
    report = build_market_regime_shadow_confidence_report(
        horizon_sec=300,
        predicted_regime=MarketRegimeCode.RANGE,
        signal_score_report=_signal_report(),
        coverage=coverage,
        currentness_gate=gate,
        legacy_confidence_percent=70,
    )
    assert report.logic_version == MARKET_REGIME_CONFIDENCE_INTEGRATION_VERSION
    assert report.horizon_key == "300s"
    assert report.shadow_display_confidence_percent > 0
    assert report.confidence_delta_percent == report.shadow_display_confidence_percent - 70
    assert report.safety.shadow_only is True
    assert report.safety.classifier_output_replaced is False
    assert report.estimator["horizon_confidence_cap_percent"] == 92


def test_conflicting_votes_reduce_shadow_confidence() -> None:
    coverage = _all_live()
    gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=coverage)
    aligned = build_market_regime_shadow_confidence_report(
        horizon_sec=300,
        predicted_regime="RANGE",
        signal_score_report=_signal_report(supports="RANGE"),
        coverage=coverage,
        currentness_gate=gate,
    )
    conflicting = build_market_regime_shadow_confidence_report(
        horizon_sec=300,
        predicted_regime="RANGE",
        signal_score_report=_signal_report(supports="UP_TREND"),
        coverage=coverage,
        currentness_gate=gate,
    )
    assert conflicting.shadow_display_confidence_percent < aligned.shadow_display_confidence_percent


def test_stale_coverage_reduces_shadow_confidence() -> None:
    live = _all_live()
    stale = tuple(_coverage(group, FreshnessState.STALE) for group in FeatureGroup)
    live_gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=live)
    stale_gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=stale)
    live_report = build_market_regime_shadow_confidence_report(
        horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=live, currentness_gate=live_gate
    )
    stale_report = build_market_regime_shadow_confidence_report(
        horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=stale, currentness_gate=stale_gate
    )
    assert stale_report.shadow_display_confidence_percent < live_report.shadow_display_confidence_percent
    assert stale_report.currentness_gate_state == "DEGRADED"


def test_horizon_mismatch_and_duplicate_coverage_fail_closed() -> None:
    coverage = _all_live()
    wrong_gate = build_market_regime_currentness_gate_report(horizon_sec=900, coverage=coverage)
    with pytest.raises(ValueError, match="horizon mismatch"):
        build_market_regime_shadow_confidence_report(
            horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=coverage, currentness_gate=wrong_gate
        )

    duplicate = coverage + (_coverage(FeatureGroup.LIQUIDITY),)
    gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=coverage)
    with pytest.raises(ValueError, match="duplicate source coverage"):
        build_market_regime_shadow_confidence_report(
            horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=duplicate, currentness_gate=gate
        )


def test_report_is_deterministic_and_has_no_runtime_execution_path() -> None:
    coverage = _all_live()
    gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=coverage)
    first = build_market_regime_shadow_confidence_report(
        horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=coverage, currentness_gate=gate
    )
    second = build_market_regime_shadow_confidence_report(
        horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=coverage, currentness_gate=gate
    )
    assert first == second
    payload = json.dumps(first.to_dict(), ensure_ascii=False)
    assert "raw_market_payload" not in payload
    assert first.safety.runtime_source_read is False
    assert first.safety.runtime_artifact_write_allowed is False
    assert first.safety.producer_enabled is False
    assert first.safety.broker_private_api_allowed is False
    assert first.safety.autotrade_trigger_allowed is False
    assert first.safety.order_intent_submitted is False
    assert first.safety.parameter_auto_promotion_allowed is False
    assert first.safety.live_parameter_apply_allowed is False

def test_quality_failure_reduces_shadow_confidence() -> None:
    coverage = _all_live()
    normal_gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=coverage)
    failed_gate = build_market_regime_currentness_gate_report(
        horizon_sec=300,
        coverage=coverage,
        quality_percent_by_source_id={"market_regime.liquidity": 0},
    )
    normal = build_market_regime_shadow_confidence_report(
        horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=coverage, currentness_gate=normal_gate
    )
    failed = build_market_regime_shadow_confidence_report(
        horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=coverage, currentness_gate=failed_gate
    )
    assert failed.shadow_display_confidence_percent < normal.shadow_display_confidence_percent
    assert failed.source_signals["market_regime.liquidity"]["quality_percent"] == 0


def test_explicit_blocker_applies_zero_confidence_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    from dataclasses import replace

    coverage = _all_live()
    gate = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=coverage)
    blocked_gate = replace(
        gate,
        blocking_source_ids=("market_regime.liquidity",),
        applied_confidence_cap_percent=0,
        gate_state="BLOCKED",
    )
    report = build_market_regime_shadow_confidence_report(
        horizon_sec=300, predicted_regime="RANGE", signal_score_report=_signal_report(), coverage=coverage, currentness_gate=blocked_gate
    )
    assert report.shadow_display_confidence_percent == 0
    assert report.source_signals["market_regime.liquidity"]["confidence_cap_percent"] == 0


def test_parameter_set_mismatch_fails_closed() -> None:
    coverage = _all_live()
    gate = build_market_regime_currentness_gate_report(
        horizon_sec=300, coverage=coverage, parameter_set_id="market_regime.shadow.other.v1"
    )
    with pytest.raises(ValueError, match="parameter_set mismatch"):
        build_market_regime_shadow_confidence_report(
            horizon_sec=300,
            predicted_regime="RANGE",
            signal_score_report=_signal_report(),
            coverage=coverage,
            currentness_gate=gate,
        )
