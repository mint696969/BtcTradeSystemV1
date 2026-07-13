# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_current_l4_origin_feature_shadow_registry.py
# desc: MR-F6.10 tests for the analysis-backed shadow-only origin feature parameter registry.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.features.current_l4_origin_feature_shadow_registry import (
    ANALYSIS_ROLLING_VOLATILITY_SAMPLE_COUNT,
    ANALYSIS_SOURCE_ROW_COUNT,
    ANALYSIS_USABLE_SEGMENT_COUNT,
    build_default_current_l4_origin_feature_shadow_registry,
    get_current_l4_origin_feature_shadow_candidate,
    validate_current_l4_origin_feature_shadow_registry,
)


def test_default_registry_contains_all_eight_explicit_shadow_combinations() -> None:
    registry = build_default_current_l4_origin_feature_shadow_registry()
    validation = validate_current_l4_origin_feature_shadow_registry(registry)
    assert validation["ok"] is True
    assert validation["candidate_count"] == 8
    assert validation["active_candidate_count"] == 0
    assert validation["runtime_selected_candidate_count"] == 0
    assert {item.parameters.fast_ma_window_rows for item in registry} == {3, 5, 10, 15}
    assert {item.parameters.slow_ma_window_rows for item in registry} == {10, 20, 30, 60}
    assert {item.volatility_band_id for item in registry} == {"interquartile", "central_80_percent"}


def test_interquartile_and_central_80_thresholds_match_analysis() -> None:
    registry = build_default_current_l4_origin_feature_shadow_registry()
    bands = {
        item.volatility_band_id: (
            item.parameters.low_volatility_threshold_bps,
            item.parameters.high_volatility_threshold_bps,
        )
        for item in registry
    }
    assert bands["interquartile"] == (4.47257112, 7.35462997)
    assert bands["central_80_percent"] == (3.79525581, 10.04311125)


def test_ma_sample_counts_and_sign_change_rates_match_analysis() -> None:
    registry = build_default_current_l4_origin_feature_shadow_registry()
    by_pair = {
        (item.parameters.fast_ma_window_rows, item.parameters.slow_ma_window_rows): (
            item.ma_analysis_sample_count,
            item.ma_sign_change_rate,
        )
        for item in registry
    }
    assert by_pair[(3, 10)] == (17161, 0.12575758)
    assert by_pair[(5, 20)] == (14951, 0.06334448)
    assert by_pair[(10, 30)] == (13341, 0.03770615)
    assert by_pair[(15, 60)] == (10516, 0.02063718)


def test_candidate_lookup_requires_explicit_exact_id() -> None:
    with pytest.raises(ValueError, match="explicit_candidate_id_required"):
        get_current_l4_origin_feature_shadow_candidate("")
    with pytest.raises(KeyError, match="candidate_not_found"):
        get_current_l4_origin_feature_shadow_candidate("unknown")
    candidate = get_current_l4_origin_feature_shadow_candidate(
        "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"
    )
    assert candidate.parameters.fast_ma_window_rows == 5
    assert candidate.parameters.slow_ma_window_rows == 20


def test_registry_is_shadow_only_and_cannot_apply_or_promote() -> None:
    registry = build_default_current_l4_origin_feature_shadow_registry()
    assert all(item.registry_state == "shadow" for item in registry)
    assert all(item.selected_for_runtime is False for item in registry)
    assert all(item.live_parameter_apply_allowed is False for item in registry)
    assert all(item.auto_promotion_allowed is False for item in registry)
    assert all(item.canonical_replacement_allowed is False for item in registry)


def test_analysis_evidence_counts_are_preserved() -> None:
    from btcts.prediction.market_regime.features.current_l4_origin_feature_shadow_registry import ANALYSIS_EVIDENCE_REF

    assert ANALYSIS_SOURCE_ROW_COUNT == 20160
    assert ANALYSIS_ROLLING_VOLATILITY_SAMPLE_COUNT == 10516
    assert ANALYSIS_USABLE_SEGMENT_COUNT == 71
    assert ANALYSIS_EVIDENCE_REF.startswith("docs/strategy/")
    assert not ANALYSIS_EVIDENCE_REF.startswith("tmp/")
