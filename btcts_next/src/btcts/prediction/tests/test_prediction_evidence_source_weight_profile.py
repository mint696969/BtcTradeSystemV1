# path: ./btcts_next/src/btcts/prediction/tests/test_prediction_evidence_source_weight_profile.py
# desc: Tests common evidence-source weight profile contract. Pure/read-only; no raw market read, broker, AutoTrade, prediction invocation, or parameter apply.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.evidence_sources import (  # noqa: E402
    PREDICTION_EVIDENCE_SOURCE_WEIGHT_PROFILE_VERSION,
    build_prediction_evidence_source_descriptor,
    build_prediction_evidence_source_weight_profile,
    estimate_prediction_display_confidence_from_evidence_profile,
    validate_prediction_evidence_source_weight_profile,
)


def test_evidence_source_weight_profile_builds_parameter_set_tunable_contract() -> None:
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="trend_bias",
        family_part_role="directional_bias",
        horizon_key="current",
        horizon_group="nowcast",
        parameter_set_id="trend_bias.pset.shadow.v1",
        sources=[
            build_prediction_evidence_source_descriptor(
                source_id="multi_timeframe_trend_structure",
                role="primary",
                weight_percent=45,
                priority_rank=1,
                default_reliability_percent=72,
                default_signal_strength_percent=60,
                default_direction="bullish",
                rationale="directional trend structure dominates short-horizon bias",
            ),
            build_prediction_evidence_source_descriptor(
                source_id="volume_confirmation",
                role="supporting",
                weight_percent=25,
                priority_rank=2,
            ),
            build_prediction_evidence_source_descriptor(
                source_id="liquidity_spread_quality",
                role="confidence_cap",
                weight_percent=20,
                priority_rank=3,
                confidence_cap_percent=65,
            ),
            build_prediction_evidence_source_descriptor(
                source_id="latest_cards_current",
                role="reference_only",
                weight_percent=10,
                priority_rank=4,
            ),
        ],
        confidence_floor_percent=10,
        confidence_ceiling_percent=85,
        notes=["weights are candidates only; use outcome/calibration before live changes"],
    )

    assert profile["contract_version"] == PREDICTION_EVIDENCE_SOURCE_WEIGHT_PROFILE_VERSION
    assert profile["prediction_family_id"] == "trend_bias"
    assert profile["family_part_role"] == "directional_bias"
    assert profile["parameter_set_id"] == "trend_bias.pset.shadow.v1"
    assert profile["weight_total_percent"] == 100
    assert profile["source_count"] == 4
    assert profile["sources"][0]["source_id"] == "multi_timeframe_trend_structure"
    assert profile["sources"][0]["default_reliability_percent"] == 72
    assert profile["sources"][0]["default_signal_strength_percent"] == 60
    assert profile["sources"][0]["default_direction"] == "bullish"
    assert profile["sources"][2]["role"] == "confidence_cap"
    assert profile["sources"][2]["confidence_cap_percent"] == 65
    assert "sources[].weight_percent" in profile["tunable_fields"]
    assert "sources[].default_reliability_percent" in profile["tunable_fields"]
    assert profile["confidence_formula"]["formula_version"] == "display_confidence.weighted_reliability_signal_agreement.v1"
    assert "horizon_cap" in profile["confidence_formula"]["display_confidence_percent"]
    assert "correct historical calls" in profile["confidence_formula"]["source_reliability_percent"]
    assert profile["card_interval_calibration_policy"]["validity_scope"] == "until_next_same_family_same_horizon_card"
    assert profile["card_interval_calibration_policy"]["calibration_target_window"] == "current_card_to_next_same_family_same_horizon_card"
    assert profile["card_interval_calibration_policy"]["confidence_is_prophecy"] is False
    assert profile["card_interval_calibration_policy"]["prediction_may_change_before_next_card"] is True
    assert profile["confidence_model_owner"] == "parent_common_prediction_layer"
    assert "source_direction" in profile["family_vs_common_responsibility"]["family_specific_logic_owns"]
    assert "display_confidence_percent" in profile["family_vs_common_responsibility"]["common_parent_logic_owns"]
    assert "same meaning across all prediction families" in profile["family_vs_common_responsibility"]["reason"]
    assert profile["adjustment_loop"]["analysis_source"] == "outcome_and_calibration_read_models"
    assert profile["adjustment_loop"]["human_review_required"] is True
    assert profile["adjustment_loop"]["auto_apply_allowed"] is False
    assert profile["safety"]["parameter_set_tunable"] is True
    assert profile["safety"]["weights_apply_only_after_human_gate"] is True
    assert profile["safety"]["parameter_auto_promotion_allowed"] is False
    assert validate_prediction_evidence_source_weight_profile(profile)["ok"] is True


def test_market_regime_can_model_trusted_and_reference_sources_separately() -> None:
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="market_regime",
        horizon_key="300s",
        horizon_group="short_horizon",
        parameter_set_id="market_regime_engine_parameter_set.v1",
        sources=[
            build_prediction_evidence_source_descriptor(
                source_id="candle_summary",
                role="primary",
                source_kind="derived_observation_read_model",
                weight_percent=70,
                priority_rank=1,
                min_required=True,
                missing_policy="force_unknown",
            ),
            build_prediction_evidence_source_descriptor(
                source_id="source_quality_gate",
                role="blocker",
                weight_percent=20,
                priority_rank=2,
                confidence_cap_percent=50,
                missing_policy="block_signal",
            ),
            build_prediction_evidence_source_descriptor(
                source_id="latest_cards_current",
                role="reference_only",
                source_kind="display_read_model_reference",
                weight_percent=10,
                priority_rank=3,
            ),
        ],
    )

    assert profile["family_part_role"] == "primary_context"
    by_source = {source["source_id"]: source for source in profile["sources"]}
    assert by_source["candle_summary"]["role"] == "primary"
    assert by_source["candle_summary"]["missing_policy"] == "force_unknown"
    assert by_source["latest_cards_current"]["role"] == "reference_only"
    assert profile["validation"]["ok"] is True


def test_display_confidence_estimator_rewards_reliable_aligned_strong_sources() -> None:
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="trend_bias",
        family_part_role="directional_bias",
        horizon_key="900s",
        horizon_group="short_horizon",
        parameter_set_id="trend_bias.pset.shadow.v1",
        sources=[
            build_prediction_evidence_source_descriptor(
                source_id="trend_structure",
                role="primary",
                weight_percent=50,
                default_reliability_percent=99,
                default_signal_strength_percent=100,
                default_freshness_percent=100,
                default_quality_percent=100,
                default_direction="bullish",
                learned_from_outcomes=True,
            ),
            build_prediction_evidence_source_descriptor(
                source_id="volume_confirmation",
                role="supporting",
                weight_percent=30,
                default_reliability_percent=98,
                default_signal_strength_percent=100,
                default_freshness_percent=100,
                default_quality_percent=100,
                default_direction="bullish",
                learned_from_outcomes=True,
            ),
            build_prediction_evidence_source_descriptor(
                source_id="liquidity_quality",
                role="confidence_cap",
                weight_percent=20,
                default_reliability_percent=99,
                default_signal_strength_percent=100,
                default_freshness_percent=100,
                default_quality_percent=100,
                default_direction="bullish",
            ),
        ],
        confidence_ceiling_percent=99,
    )

    estimate = estimate_prediction_display_confidence_from_evidence_profile(profile, predicted_direction="bullish")

    assert estimate["ok"] is True
    assert estimate["display_confidence_percent"] == 92
    assert estimate["horizon_confidence_cap_percent"] == 92
    assert estimate["aligned_weighted_quality_ratio"] == 1.0
    assert all(row["aligned_with_prediction"] for row in estimate["source_rows"] if row["included_in_confidence"])


def test_display_confidence_estimator_caps_farther_horizons_by_default() -> None:
    nowcast = build_prediction_evidence_source_weight_profile(
        prediction_family_id="trend_bias",
        family_part_role="directional_bias",
        horizon_key="current",
        horizon_group="nowcast",
        parameter_set_id="trend_bias.pset.shadow.v1",
        sources=[
            build_prediction_evidence_source_descriptor(
                source_id="trend_structure",
                role="primary",
                weight_percent=100,
                default_reliability_percent=99,
                default_signal_strength_percent=100,
                default_direction="bullish",
            ),
        ],
        confidence_ceiling_percent=99,
    )
    long_horizon = build_prediction_evidence_source_weight_profile(
        prediction_family_id="trend_bias",
        family_part_role="directional_bias",
        horizon_key="86400s",
        horizon_group="long_horizon",
        parameter_set_id="trend_bias.pset.shadow.v1",
        sources=[
            build_prediction_evidence_source_descriptor(
                source_id="trend_structure",
                role="primary",
                weight_percent=100,
                default_reliability_percent=99,
                default_signal_strength_percent=100,
                default_direction="bullish",
            ),
        ],
        confidence_ceiling_percent=99,
    )

    near = estimate_prediction_display_confidence_from_evidence_profile(nowcast, predicted_direction="bullish")
    far = estimate_prediction_display_confidence_from_evidence_profile(long_horizon, predicted_direction="bullish")

    assert near["display_confidence_percent"] == 99
    assert far["horizon_confidence_cap_percent"] == 68
    assert far["display_confidence_percent"] == 68
    assert far["display_confidence_percent"] < near["display_confidence_percent"]
    assert long_horizon["card_interval_calibration_policy"]["confidence_is_prophecy"] is False


def test_display_confidence_estimator_penalizes_unreliable_or_conflicting_sources() -> None:
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="breakout_false_break",
        family_part_role="breakout_warning",
        horizon_key="300s",
        horizon_group="short_horizon",
        parameter_set_id="breakout.pset.shadow.v1",
        sources=[
            build_prediction_evidence_source_descriptor(
                source_id="breakout_structure",
                role="primary",
                weight_percent=55,
                default_reliability_percent=45,
                default_signal_strength_percent=70,
                default_direction="bullish",
            ),
            build_prediction_evidence_source_descriptor(
                source_id="failed_retest",
                role="supporting",
                weight_percent=30,
                default_reliability_percent=80,
                default_signal_strength_percent=75,
                default_direction="bearish",
            ),
            build_prediction_evidence_source_descriptor(
                source_id="spread_widening",
                role="confidence_cap",
                weight_percent=15,
                confidence_cap_percent=55,
                default_reliability_percent=75,
                default_signal_strength_percent=80,
                default_quality_percent=60,
                default_direction="risk_off",
            ),
        ],
    )

    estimate = estimate_prediction_display_confidence_from_evidence_profile(profile, predicted_direction="bullish")

    assert estimate["ok"] is True
    assert estimate["display_confidence_percent"] < 55
    assert estimate["aligned_weighted_quality_ratio"] < 0.5
    rows = {row["source_id"]: row for row in estimate["source_rows"]}
    assert rows["breakout_structure"]["aligned_with_prediction"] is True
    assert rows["failed_retest"]["aligned_with_prediction"] is False


def test_weight_profile_validator_rejects_weight_mismatch_and_unsafe_auto_apply() -> None:
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="volatility_risk",
        horizon_key="3600s",
        horizon_group="mid_horizon",
        parameter_set_id="volatility_risk.pset.test.v1",
        sources=[
            build_prediction_evidence_source_descriptor(source_id="realized_volatility", role="primary", weight_percent=60),
            build_prediction_evidence_source_descriptor(source_id="spread_widening", role="veto", weight_percent=20),
        ],
    )
    assert profile["validation"]["ok"] is False
    assert "weight_total_not_target" in profile["validation"]["failures"]

    bad = dict(profile)
    bad["weight_total_percent"] = 100
    bad["sources"] = [dict(source) for source in profile["sources"]]
    bad["sources"][0]["weight_percent"] = 80
    bad["adjustment_loop"] = dict(profile["adjustment_loop"])
    bad["adjustment_loop"]["auto_apply_allowed"] = True
    bad["safety"] = dict(profile["safety"])
    bad["safety"]["live_parameter_apply_allowed"] = True
    result = validate_prediction_evidence_source_weight_profile(bad)
    assert result["ok"] is False
    assert "adjustment_auto_apply_allowed_not_false" in result["failures"]
    assert "safety_live_parameter_apply_allowed_not_false" in result["failures"]


def test_weight_profile_rejects_raw_payload_keys() -> None:
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="liquidity_execution_quality",
        horizon_key="current",
        horizon_group="nowcast",
        parameter_set_id="liquidity.pset.test.v1",
        sources=[
            build_prediction_evidence_source_descriptor(source_id="orderbook_shape", role="primary", weight_percent=100),
        ],
    )
    bad = dict(profile)
    bad["sources"] = [dict(profile["sources"][0])]
    bad["sources"][0]["raw_orderbook"] = {"bids": []}
    result = validate_prediction_evidence_source_weight_profile(bad)
    assert result["ok"] is False
    assert "forbidden_raw_payload_key_present" in result["failures"]


def test_evidence_source_weight_profile_source_has_no_execution_or_prediction_path() -> None:
    text = (Path(__file__).resolve().parents[1] / "evidence_sources.py").read_text(encoding="utf-8")
    required = [
        "PREDICTION_EVIDENCE_SOURCE_WEIGHT_PROFILE_VERSION",
        "build_prediction_evidence_source_descriptor",
        "build_prediction_evidence_source_weight_profile",
        "validate_prediction_evidence_source_weight_profile",
        "estimate_prediction_display_confidence_from_evidence_profile",
        "parameter_set_tunable",
        "weights_apply_only_after_human_gate",
        "outcome_and_calibration_read_models",
        "display_confidence.weighted_reliability_signal_agreement.v1",
        "until_next_same_family_same_horizon_card",
        "confidence_is_prophecy",
        "horizon_confidence_cap_percent",
        "parent_common_prediction_layer",
        "family_vs_common_responsibility",
        "same meaning across all prediction families",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "import streamlit",
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "write_market_regime_latest_artifacts_once",
        "write_parent_scenario_guidance_latest_read_model(",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
    assert "raw_candles" in text  # forbidden-key guard only, not raw reading.
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="macro_cross_context",
        horizon_key="21600s",
        horizon_group="long_horizon",
        parameter_set_id="macro.pset.test.v1",
        sources=[build_prediction_evidence_source_descriptor(source_id="session_context", role="context_only", weight_percent=100)],
    )
    assert "raw_market_payload" not in json.dumps(profile, ensure_ascii=False)
