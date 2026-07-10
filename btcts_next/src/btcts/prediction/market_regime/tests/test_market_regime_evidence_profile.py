# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_evidence_profile.py
# desc: Focused MR-VS1 tests for MarketRegime default evidence profiles. Pure/read-only.

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.contracts import FeatureGroup  # noqa: E402
from btcts.prediction.market_regime.evidence_profile import (  # noqa: E402
    MARKET_REGIME_EVIDENCE_PROFILE_VERSION,
    build_all_market_regime_default_evidence_profiles,
    build_market_regime_default_evidence_profile,
    market_regime_common_horizon_group,
    market_regime_evidence_source_id,
)
from btcts.prediction.market_regime.horizon_policy import (  # noqa: E402
    MarketRegimeHorizonGroup,
    build_default_horizon_policy,
)
from btcts.prediction.market_regime.parameter_set_registry import (  # noqa: E402
    MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
)
from btcts.prediction.market_regime.source_priority_policy import (  # noqa: E402
    build_default_source_priority_policy,
)


def test_all_default_profiles_cover_configured_horizons_and_validate() -> None:
    horizon_policy = build_default_horizon_policy()
    profiles = build_all_market_regime_default_evidence_profiles()

    assert len(profiles) == len(horizon_policy.horizons) == 8
    assert [profile["horizon_key"] for profile in profiles] == [horizon.horizon_key for horizon in horizon_policy.horizons]
    assert all(profile["validation"]["ok"] is True for profile in profiles)
    assert all(profile["weight_total_percent"] == 100 for profile in profiles)
    assert all(profile["target_weight_total_percent"] == 100 for profile in profiles)
    assert all(profile["parameter_set_id"] == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID for profile in profiles)
    assert all(profile["market_regime_evidence_profile_version"] == MARKET_REGIME_EVIDENCE_PROFILE_VERSION for profile in profiles)


def test_default_profiles_are_thin_adapters_over_source_priority_policy() -> None:
    horizon_policy = build_default_horizon_policy()
    source_policy = build_default_source_priority_policy()

    for horizon in horizon_policy.horizons:
        profile = build_market_regime_default_evidence_profile(horizon_sec=horizon.horizon_sec)
        priority = source_policy.priority_for_group(horizon.group)
        assert [source["source_id"] for source in profile["sources"]] == [
            market_regime_evidence_source_id(group) for group in priority.ordered_feature_groups
        ]
        assert [source["weight_percent"] for source in profile["sources"]] == [
            int(round(priority.weight_for(group) * 100)) for group in priority.ordered_feature_groups
        ]
        assert [source["priority_rank"] for source in profile["sources"]] == list(range(1, len(priority.ordered_feature_groups) + 1))
        assert profile["sources"][0]["role"] == "primary"
        assert all(source["role"] == "supporting" for source in profile["sources"][1:])


def test_horizon_mapping_is_explicit_and_market_regime_owned() -> None:
    assert market_regime_common_horizon_group(MarketRegimeHorizonGroup.CURRENT) == "nowcast"
    assert market_regime_common_horizon_group(MarketRegimeHorizonGroup.SHORT) == "short_horizon"
    assert market_regime_common_horizon_group(MarketRegimeHorizonGroup.MID) == "mid_horizon"
    assert market_regime_common_horizon_group(MarketRegimeHorizonGroup.MEDIUM_LONG) == "long_horizon"
    assert market_regime_common_horizon_group(MarketRegimeHorizonGroup.LONG) == "long_horizon"


def test_source_identity_is_stable_and_neutral_until_later_vertical_slices() -> None:
    assert market_regime_evidence_source_id(FeatureGroup.SOURCE_QUALITY) == "market_regime.source_quality"
    profile = build_market_regime_default_evidence_profile(horizon_sec=300)
    source_ids = [source["source_id"] for source in profile["sources"]]
    assert len(source_ids) == len(set(source_ids))
    assert all(source["source_kind"] == "derived_feature_group" for source in profile["sources"])
    assert all(source["default_reliability_percent"] == 50 for source in profile["sources"])
    assert all(source["default_signal_strength_percent"] == 50 for source in profile["sources"])
    assert all(source["default_direction"] == "unknown" for source in profile["sources"])
    assert all(source["learned_from_outcomes"] is False for source in profile["sources"])
    assert all(source["min_required"] is False for source in profile["sources"])
    assert all(source["missing_policy"] == "degrade_confidence" for source in profile["sources"])


def test_profiles_are_deterministic_and_contain_no_raw_payload_or_execution_path() -> None:
    first = build_market_regime_default_evidence_profile(horizon_sec=21600, parameter_set_id="market_regime.shadow.test.v1")
    second = build_market_regime_default_evidence_profile(horizon_sec=21600, parameter_set_id="market_regime.shadow.test.v1")
    assert first == second

    payload = json.dumps(first, ensure_ascii=False)
    for forbidden in ("raw_candles", "raw_orderbook", "raw_trades", "raw_executions", "raw_market_payload"):
        assert forbidden not in payload
    assert first["safety"]["raw_market_data_read"] is False
    assert first["safety"]["prediction_invoked"] is False
    assert first["safety"]["producer_enabled"] is False
    assert first["safety"]["broker_private_api_allowed"] is False
    assert first["safety"]["autotrade_trigger_allowed"] is False
    assert first["safety"]["parameter_auto_promotion_allowed"] is False
    assert first["safety"]["live_parameter_apply_allowed"] is False


def test_unknown_horizon_fails_closed() -> None:
    with pytest.raises(KeyError):
        build_market_regime_default_evidence_profile(horizon_sec=12345)

def test_invalid_source_priority_fails_closed() -> None:
    from btcts.prediction.market_regime.evidence_profile import _integer_weight_percentages
    from btcts.prediction.market_regime.source_priority_policy import HorizonSourcePriority

    duplicate = HorizonSourcePriority(
        group=MarketRegimeHorizonGroup.CURRENT,
        ordered_feature_groups=(FeatureGroup.LIQUIDITY, FeatureGroup.LIQUIDITY),
        weights={FeatureGroup.LIQUIDITY: 1.0},
    )
    with pytest.raises(ValueError, match="duplicate feature groups"):
        _integer_weight_percentages(duplicate)

    missing = HorizonSourcePriority(
        group=MarketRegimeHorizonGroup.CURRENT,
        ordered_feature_groups=(FeatureGroup.LIQUIDITY,),
        weights={},
    )
    with pytest.raises(ValueError, match="weight missing"):
        _integer_weight_percentages(missing)

    non_positive = HorizonSourcePriority(
        group=MarketRegimeHorizonGroup.CURRENT,
        ordered_feature_groups=(FeatureGroup.LIQUIDITY,),
        weights={FeatureGroup.LIQUIDITY: 0.0},
    )
    with pytest.raises(ValueError, match="must be positive"):
        _integer_weight_percentages(non_positive)
