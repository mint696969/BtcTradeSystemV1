# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_pure_contract_and_policy.py
# desc: PS-Q27G tests for pure market-regime contract and policy skeleton. No UI/D-hot/runtime behavior.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import (  # noqa: E402
    EvidenceQuality,
    FeatureGroup,
    FreshnessState,
    MarketRegimeCode,
    MarketRegimePrediction,
    TacticalHint,
    build_default_freshness_policy,
    build_default_horizon_policy,
    build_default_market_regime_parameter_set,
    build_default_source_priority_policy,
    build_empty_market_regime_packet,
)
from btcts.prediction.market_regime.horizon_policy import MarketRegimeHorizonGroup  # noqa: E402

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "market_regime"


def test_q27g_horizon_policy_matches_warroom_goal_and_cadence() -> None:
    policy = build_default_horizon_policy()
    assert [h.label for h in policy.horizons] == ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]
    assert [h.horizon_sec for h in policy.horizons] == [0, 300, 900, 1800, 3600, 21600, 43200, 86400]
    assert policy.horizon_by_label("現在").normal_refresh_sec == 3
    assert policy.horizon_by_label("5分後").event_refresh_allowed is True
    assert policy.horizon_by_label("24時間後").normal_refresh_sec == 3600
    assert policy.scheduler_enabled is False
    assert policy.producer_enabled is False


def test_q27g_freshness_policy_is_horizon_appropriate() -> None:
    freshness = build_default_freshness_policy()
    assert freshness.state_for_age(horizon_sec=0, age_sec=3) == FreshnessState.LIVE
    assert freshness.state_for_age(horizon_sec=0, age_sec=20) == FreshnessState.STALE
    assert freshness.state_for_age(horizon_sec=300, age_sec=45) == FreshnessState.WARM
    assert freshness.state_for_age(horizon_sec=86400, age_sec=3600) == FreshnessState.LIVE
    assert freshness.state_for_age(horizon_sec=86400, age_sec=None) == FreshnessState.MISSING
    assert freshness.scheduler_enabled is False
    assert freshness.producer_enabled is False


def test_q27g_source_priority_differs_by_horizon_group() -> None:
    policy = build_default_source_priority_policy()
    short = policy.priority_for_group(MarketRegimeHorizonGroup.SHORT)
    long = policy.priority_for_group(MarketRegimeHorizonGroup.LONG)
    assert short.ordered_feature_groups[:2] == (FeatureGroup.LIQUIDITY, FeatureGroup.ORDERFLOW)
    assert long.ordered_feature_groups[:2] == (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY)
    assert short.weight_for(FeatureGroup.ORDERFLOW) > long.weight_for(FeatureGroup.ORDERFLOW)
    assert policy.live_parameter_apply_allowed is False
    assert policy.human_review_required_before_apply is True


def test_q27g_parameter_set_is_proposal_ready_but_not_live_mutating() -> None:
    params = build_default_market_regime_parameter_set()
    data = params.to_dict()
    assert data["supported_horizons_sec"] == [0, 300, 900, 1800, 3600, 21600, 43200, 86400]
    assert data["gpt_parameter_proposal_allowed"] is True
    assert data["live_parameter_apply_allowed"] is False
    assert data["human_review_required_before_apply"] is True
    assert data["broker_private_api_allowed"] is False
    assert data["autotrade_trigger_allowed"] is False
    assert data["ledger_append_allowed"] is False
    assert data["runtime_artifact_write_allowed"] is False
    shadow = params.with_status("shadow", change_reason="proposal_review_copy")
    assert shadow.status == "shadow"
    assert params.status == "draft"


def test_q27g_prediction_packet_clamps_confidence_and_preserves_safety() -> None:
    prediction = MarketRegimePrediction(
        horizon_label="5分後",
        horizon_sec=300,
        regime_code=MarketRegimeCode.RANGE,
        confidence_percent=150,
        evidence_quality=EvidenceQuality.PARTIAL,
        freshness_state=FreshnessState.LIVE,
        tactical_hint=TacticalHint.RANGE_TACTIC,
        drivers=("range_boundary_visible",),
    )
    data = prediction.to_dict()
    assert data["confidence_percent"] == 99
    assert data["regime_code"] == "RANGE"
    assert data["safety"]["read_only"] is True
    assert data["safety"]["ui_display_only"] is True
    for key in (
        "runtime_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert data["safety"][key] is False

    packet = build_empty_market_regime_packet(generated_at="2026-07-01T00:00:00Z").to_dict()
    assert packet["missing_sources"] == ["market_regime_predictions_not_built_yet"]
    assert packet["safety"]["would_send_to_broker"] is False


def test_q27g_core_package_has_no_ui_or_runtime_reader_imports() -> None:
    forbidden = ("import streamlit", "from streamlit", "D:\\btc_ts_hot", "runtime_root(", "send_to_broker(", "append_ledger(", "ledger.append(")
    for path in PACKAGE_ROOT.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"
