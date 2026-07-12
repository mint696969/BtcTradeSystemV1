# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_target_definition.py
# desc: Pure tests for MR-F5.2 horizon target definitions, identity, and lookahead guards.

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from btcts.prediction.market_regime.future_target_definition import (
    MARKET_REGIME_FUTURE_TARGET_POLICY_VERSION,
    MarketRegimeFutureTargetDefinition,
    TargetObservationRule,
    TargetPartialMatchRule,
    build_default_future_target_definitions,
    future_target_definitions_by_horizon,
    validate_source_timestamp_for_origin,
)


def test_default_target_policy_covers_exact_canonical_future_horizons() -> None:
    definitions = build_default_future_target_definitions()
    assert MARKET_REGIME_FUTURE_TARGET_POLICY_VERSION.endswith("mr_f5_2.v1")
    assert tuple(item.horizon_sec for item in definitions) == (300, 900, 1800, 3600, 21600, 43200, 86400)
    assert tuple(item.target_definition_version for item in definitions) == tuple(
        f"market_regime_target.{horizon}s.v1" for horizon in (300, 900, 1800, 3600, 21600, 43200, 86400)
    )


def test_target_definitions_are_immutable_and_point_in_time() -> None:
    definition = future_target_definitions_by_horizon()[900]
    assert definition.observation_rule is TargetObservationRule.POINT_IN_TIME_STATE
    assert definition.partial_match_rule is TargetPartialMatchRule.TRANSITION_ADJACENCY
    assert definition.target_timestamp_offset_sec == 900
    with pytest.raises(FrozenInstanceError):
        definition.horizon_sec = 300  # type: ignore[misc]


def test_short_label_projection_and_non_exact_identity_are_forbidden() -> None:
    base = future_target_definitions_by_horizon()[300]
    with pytest.raises(ValueError, match="short_horizon_label_projection_forbidden"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "allow_short_horizon_label_projection": True})
    with pytest.raises(ValueError, match="exact_horizon_identity_required"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "require_exact_horizon_identity": False})


def test_origin_cutoff_and_rule_types_fail_closed() -> None:
    base = future_target_definitions_by_horizon()[900]
    with pytest.raises(ValueError, match="origin_cutoff_must_be_inclusive"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "origin_cutoff_inclusive": False})
    with pytest.raises(ValueError, match="observation_rule_invalid"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "observation_rule": "POINT_IN_TIME_STATE"})
    with pytest.raises(ValueError, match="partial_match_rule_invalid"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "partial_match_rule": "TRANSITION_ADJACENCY"})


def test_feature_sets_and_outcome_values_fail_closed() -> None:
    base = future_target_definitions_by_horizon()[300]
    with pytest.raises(ValueError, match="required_optional_feature_families_overlap"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "optional_feature_families": base.optional_feature_families + ("price_structure",)})
    with pytest.raises(ValueError, match="missing_observation_outcome_must_be_unknown"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "missing_observation_outcome": "miss"})
    with pytest.raises(ValueError, match="invalid_observation_outcome_must_be_invalidated"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "invalid_observation_outcome": "unknown"})


def test_target_version_and_offset_must_match_horizon() -> None:
    base = future_target_definitions_by_horizon()[1800]
    with pytest.raises(ValueError, match="target_definition_version_horizon_mismatch"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "target_definition_version": "market_regime_target.900s.v1"})
    with pytest.raises(ValueError, match="target_timestamp_offset_must_equal_horizon"):
        MarketRegimeFutureTargetDefinition(**{**base.__dict__, "target_timestamp_offset_sec": 900})


def test_long_horizons_require_session_context_and_more_history() -> None:
    definitions = future_target_definitions_by_horizon()
    assert "session_context" not in definitions[3600].required_feature_families
    assert "session_context" in definitions[21600].required_feature_families
    assert "macro_context" in definitions[86400].optional_feature_families
    assert definitions[86400].minimum_required_history_sec > definitions[21600].minimum_required_history_sec


def test_missing_and_invalid_observations_fail_closed() -> None:
    for definition in build_default_future_target_definitions():
        assert definition.missing_observation_outcome == "unknown"
        assert definition.invalid_observation_outcome == "invalidated"
        assert definition.require_source_timestamp_lte_origin is True


def test_lookahead_guard_rejects_source_after_origin() -> None:
    validate_source_timestamp_for_origin(source_timestamp_epoch_sec=100.0, origin_timestamp_epoch_sec=100.0)
    with pytest.raises(ValueError, match="lookahead_source_timestamp_after_origin"):
        validate_source_timestamp_for_origin(source_timestamp_epoch_sec=100.1, origin_timestamp_epoch_sec=100.0)
