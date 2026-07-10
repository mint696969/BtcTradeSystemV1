# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_currentness_gate.py
# desc: Focused MR-VS2 tests for pure MarketRegime currentness and source-quality gate reports.

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, SourceCoverage  # noqa: E402
from btcts.prediction.market_regime.currentness_gate import (  # noqa: E402
    MARKET_REGIME_CURRENTNESS_GATE_VERSION,
    build_market_regime_currentness_gate_report,
)


def _coverage(group: FeatureGroup, *, available: bool = True, freshness: FreshnessState = FreshnessState.LIVE) -> SourceCoverage:
    return SourceCoverage(
        feature_group=group,
        available=available,
        freshness_state=freshness,
        used_sources=(f"fixture:{group.value}",) if available else (),
        missing_sources=() if available else (group.value,),
    )


def _all_live() -> tuple[SourceCoverage, ...]:
    return tuple(_coverage(group) for group in FeatureGroup)


def test_all_live_sources_are_current_and_uncapped() -> None:
    report = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=_all_live())
    assert report.logic_version == MARKET_REGIME_CURRENTNESS_GATE_VERSION
    assert report.gate_state == "CURRENT"
    assert report.applied_confidence_cap_percent is None
    assert report.missing_source_ids == ()
    assert report.stale_source_ids == ()
    assert report.quality_failure_ids == ()
    assert report.blocking_source_ids == ()
    assert report.recovery_conditions == ()


def test_missing_non_required_primary_source_degrades_without_inventing_blocker() -> None:
    coverage = tuple(
        _coverage(group, available=False, freshness=FreshnessState.MISSING) if group == FeatureGroup.SOURCE_QUALITY else _coverage(group)
        for group in FeatureGroup
    )
    report = build_market_regime_currentness_gate_report(horizon_sec=0, coverage=coverage)
    assert report.required_source_ids == ()
    assert report.missing_required_source_ids == ()
    assert report.blocking_source_ids == ()
    assert report.gate_state == "DEGRADED"
    assert report.applied_confidence_cap_percent is None
    assert report.recovery_conditions == ("restore_available_source:market_regime.source_quality",)


def test_stale_sources_degrade_without_inventing_required_sources() -> None:
    current_coverage = tuple(
        _coverage(group, freshness=FreshnessState.STALE) if group == FeatureGroup.SOURCE_QUALITY else _coverage(group)
        for group in FeatureGroup
    )
    current = build_market_regime_currentness_gate_report(horizon_sec=0, coverage=current_coverage)
    assert current.gate_state == "DEGRADED"
    assert current.applied_confidence_cap_percent is None
    assert current.blocking_source_ids == ()

    short_coverage = tuple(
        _coverage(group, freshness=FreshnessState.STALE) if group == FeatureGroup.CROSS_VENUE else _coverage(group)
        for group in FeatureGroup
    )
    short = build_market_regime_currentness_gate_report(horizon_sec=300, coverage=short_coverage)
    assert short.gate_state == "DEGRADED"
    assert short.applied_confidence_cap_percent is None
    assert short.blocking_source_ids == ()
    assert short.stale_source_ids == ("market_regime.cross_venue",)


def test_quality_failure_is_explicit_without_inventing_required_source() -> None:
    report = build_market_regime_currentness_gate_report(
        horizon_sec=300,
        coverage=_all_live(),
        quality_percent_by_source_id={"market_regime.liquidity": 20},
    )
    assert report.quality_failure_ids == ("market_regime.liquidity",)
    assert report.blocking_source_ids == ()
    assert report.gate_state == "DEGRADED"
    assert report.applied_confidence_cap_percent is None
    assert report.recovery_conditions == ("restore_source_quality_at_or_above_40:market_regime.liquidity",)


def test_missing_non_profile_coverage_does_not_pollute_report() -> None:
    report = build_market_regime_currentness_gate_report(horizon_sec=0, coverage=_all_live())
    assert "market_regime.volatility" not in report.source_ids
    assert "market_regime.cross_venue" not in report.source_ids
    assert report.gate_state == "CURRENT"


def test_duplicate_coverage_fails_closed() -> None:
    duplicate = (_coverage(FeatureGroup.LIQUIDITY), _coverage(FeatureGroup.LIQUIDITY))
    with pytest.raises(ValueError, match="duplicate source coverage"):
        build_market_regime_currentness_gate_report(horizon_sec=300, coverage=duplicate)


def test_report_is_deterministic_and_contains_no_runtime_execution_path() -> None:
    first = build_market_regime_currentness_gate_report(horizon_sec=21600, coverage=_all_live())
    second = build_market_regime_currentness_gate_report(horizon_sec=21600, coverage=_all_live())
    assert first == second
    payload = json.dumps(first.to_dict(), ensure_ascii=False)
    for forbidden in ("raw_market_payload", "broker_order", "order_intent_payload", "runtime_write_path"):
        assert forbidden not in payload
    assert first.safety.runtime_source_read is False
    assert first.safety.runtime_artifact_write_allowed is False
    assert first.safety.producer_enabled is False
    assert first.safety.prediction_invoked is False
    assert first.safety.warroom_write_allowed is False
    assert first.safety.broker_private_api_allowed is False
    assert first.safety.autotrade_trigger_allowed is False
    assert first.safety.order_intent_submitted is False
    assert first.safety.parameter_auto_promotion_allowed is False
    assert first.safety.live_parameter_apply_allowed is False


def test_explicit_min_required_profile_source_can_block_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    from btcts.prediction.market_regime import currentness_gate as module

    original = module.build_market_regime_default_evidence_profile(horizon_sec=300)
    patched = dict(original)
    patched["sources"] = [dict(source) for source in original["sources"]]
    patched["sources"][0]["min_required"] = True
    required_source_id = patched["sources"][0]["source_id"]

    monkeypatch.setattr(module, "build_market_regime_default_evidence_profile", lambda **_: patched)
    coverage = tuple(
        _coverage(group, available=False, freshness=FreshnessState.MISSING)
        if f"market_regime.{group.value}" == required_source_id
        else _coverage(group)
        for group in FeatureGroup
    )
    report = module.build_market_regime_currentness_gate_report(horizon_sec=300, coverage=coverage)
    assert report.required_source_ids == (required_source_id,)
    assert report.missing_required_source_ids == (required_source_id,)
    assert report.blocking_source_ids == (required_source_id,)
    assert report.gate_state == "BLOCKED"
    assert report.applied_confidence_cap_percent == 0

def test_invalid_quality_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="unknown quality source ids"):
        build_market_regime_currentness_gate_report(
            horizon_sec=300,
            coverage=_all_live(),
            quality_percent_by_source_id={"market_regime.unknown": 50},
        )

    with pytest.raises(ValueError, match="source quality must be finite"):
        build_market_regime_currentness_gate_report(
            horizon_sec=300,
            coverage=_all_live(),
            quality_percent_by_source_id={"market_regime.liquidity": float("nan")},
        )
