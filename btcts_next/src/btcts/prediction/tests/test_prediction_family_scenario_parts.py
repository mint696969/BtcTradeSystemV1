# path: ./btcts_next/src/btcts/prediction/tests/test_prediction_family_scenario_parts.py
# desc: PS_FAMILY_SCENARIO_PART_CONTRACT_V1 tests. Verifies common family scenario parts and parent scenario guidance are read-only and non-executing.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.scenario_parts import (  # noqa: E402
    PREDICTION_FAMILY_SCENARIO_PART_CONTRACT_VERSION,
    PREDICTION_PARENT_SCENARIO_GUIDANCE_CONTRACT_VERSION,
    build_parent_scenario_guidance_read_model,
    build_prediction_family_scenario_part,
    validate_parent_scenario_guidance_read_model,
    validate_prediction_family_scenario_part,
)


def test_family_scenario_part_contract_is_read_only_and_parent_mergeable() -> None:
    part = build_prediction_family_scenario_part(
        prediction_family_id="market_regime",
        horizon_key="15m",
        horizon_group="short_horizon",
        scenario_state="bullish",
        scenario_label="上昇地合い",
        scenario_summary="MarketRegime sees upward regime context.",
        confidence_percent=65,
        estimated_signal_strength_percent=65,
        part_role="primary_context",
        drivers=["candle_summary_upward_bias"],
        blockers=[],
        warnings=["comparison_not_ready"],
        evidence_refs=[{"artifact_ref": "prediction/market_regime/latest_read_model.json"}],
        parameter_set_id="market_regime_engine_parameter_set.v1",
        generated_at="2026-07-10T00:00:00Z",
    )

    assert part["contract_version"] == PREDICTION_FAMILY_SCENARIO_PART_CONTRACT_VERSION
    assert part["artifact_kind"] == "family_scenario_part"
    assert part["prediction_family_id"] == "market_regime"
    assert part["parent_merge"]["eligible_for_parent_guidance"] is True
    assert part["parent_merge"]["family_decides_overall_scenario"] is False
    assert part["parent_merge"]["same_run_recursive_dependency_allowed"] is False
    assert part["safety"]["family_part_only"] is True
    assert part["safety"]["writes_dhot"] is False
    assert part["safety"]["broker_private_api_allowed"] is False
    assert part["safety"]["autotrade_trigger_allowed"] is False
    assert validate_prediction_family_scenario_part(part)["ok"] is True


def test_parent_scenario_guidance_combines_parts_without_execution() -> None:
    market_regime = build_prediction_family_scenario_part(
        prediction_family_id="market_regime",
        horizon_key="15m",
        horizon_group="short_horizon",
        scenario_state="range",
        scenario_label="レンジ地合い",
        scenario_summary="Range context dominates.",
        confidence_percent=60,
        estimated_signal_strength_percent=60,
        part_role="primary_context",
    )
    volatility = build_prediction_family_scenario_part(
        prediction_family_id="volatility_risk",
        horizon_key="15m",
        horizon_group="short_horizon",
        scenario_state="risk_off",
        scenario_label="ボラ警戒",
        scenario_summary="Volatility risk caps confidence.",
        confidence_percent=55,
        estimated_signal_strength_percent=55,
        part_role="risk_cap",
        warnings=["volatility_expansion_watch"],
    )

    guidance = build_parent_scenario_guidance_read_model(
        [market_regime, volatility],
        horizon_key="15m",
        horizon_group="short_horizon",
        generated_at="2026-07-10T00:00:00Z",
    )

    assert guidance["contract_version"] == PREDICTION_PARENT_SCENARIO_GUIDANCE_CONTRACT_VERSION
    assert guidance["artifact_kind"] == "parent_scenario_guidance_read_model"
    assert guidance["dominant_family_id"] == "market_regime"
    assert guidance["family_part_count"] == 2
    assert guidance["operator_guidance"]["guidance_mode"] == "observational_scenario_only"
    assert guidance["operator_guidance"]["prediction_invoked"] is False
    assert guidance["operator_guidance"]["broker_action_allowed"] is False
    assert guidance["safety"]["parent_guidance_only"] is True
    assert guidance["safety"]["writes_dhot"] is False
    assert guidance["safety"]["ui_render_invokes_classifier"] is False
    assert validate_parent_scenario_guidance_read_model(guidance)["ok"] is True


def test_scenario_part_and_parent_validator_reject_raw_payload_and_mutation_flags() -> None:
    part = build_prediction_family_scenario_part(
        prediction_family_id="trend_bias",
        horizon_key="5m",
        horizon_group="short_horizon",
        scenario_state="bullish",
        scenario_label="上方向優勢",
        scenario_summary="Trend bias part only.",
        part_role="directional_bias",
    )
    part["evidence_refs"].append({"raw_trades": []})
    part["safety"]["broker_private_api_allowed"] = True
    validation = validate_prediction_family_scenario_part(part)
    assert validation["ok"] is False
    assert "forbidden_raw_payload_key_present" in validation["failures"]
    assert "safety_broker_private_api_allowed_not_false" in validation["failures"]

    parent = build_parent_scenario_guidance_read_model([], horizon_key="5m", horizon_group="short_horizon")
    parent["raw_candles"] = []
    parent["safety"]["prediction_invoked"] = True
    parent_validation = validate_parent_scenario_guidance_read_model(parent)
    assert parent_validation["ok"] is False
    assert "forbidden_raw_payload_key_present" in parent_validation["failures"]
    assert "safety_prediction_invoked_not_false" in parent_validation["failures"]


def test_scenario_parts_source_has_no_writer_or_runtime_paths() -> None:
    text = (Path(__file__).resolve().parents[1] / "scenario_parts.py").read_text(encoding="utf-8")
    required = [
        "build_prediction_family_scenario_part",
        "build_parent_scenario_guidance_read_model",
        "family_decides_overall_scenario",
        "same_run_recursive_dependency_allowed",
        "observational_scenario_only",
        "parent_guidance_only",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "write_text(",
        "open(\"a",
        "subprocess.Popen",
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
