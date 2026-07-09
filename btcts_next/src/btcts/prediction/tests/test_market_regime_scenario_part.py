# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_scenario_part.py
# desc: PS_MARKET_REGIME_SCENARIO_PART_V1 tests. Verifies MarketRegime latest read models/cards adapt to parent scenario-part contract without writes, UI inference, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.scenario_part import (  # noqa: E402
    MARKET_REGIME_SCENARIO_PART_VERSION,
    build_market_regime_scenario_part_from_latest_cards,
    build_market_regime_scenario_part_from_latest_read_model,
    validate_market_regime_scenario_part,
)
from btcts.prediction.scenario_parts import validate_prediction_family_scenario_part  # noqa: E402


def _latest_read_model() -> dict[str, object]:
    return {
        "artifact_kind": "latest_read_model",
        "prediction_family_id": "market_regime",
        "generated_at": "2026-07-10T00:00:00Z",
        "run_id": "market_regime_20260710T000000Z_test",
        "horizons": [
            {
                "horizon": "15分後",
                "horizon_key": "900s",
                "horizon_sec": 900,
                "primary_regime": "RANGE",
                "primary_regime_label": "レンジ",
                "confidence_percent": 70,
                "drivers": ["price_in_range", "mean_reversion_to_vwap"],
                "conflicts": ["sell_pressure_conflict"],
                "invalidation": ["range_low_break_with_volume"],
                "parameter_set_id": "market_regime.pset.test.v1",
            }
        ],
    }


def _latest_cards() -> dict[str, object]:
    return {
        "artifact_kind": "latest_cards",
        "prediction_family_id": "market_regime",
        "generated_at": "2026-07-10T00:00:00Z",
        "run_id": "market_regime_20260710T000000Z_test",
        "parameter_set_id": "market_regime.pset.cards.v1",
        "cards": [
            {
                "horizon": "現在",
                "horizon_key": "current",
                "horizon_sec": 0,
                "regime_code": "UP_TREND",
                "regime_label": "上昇地合い",
                "confidence_percent": 66,
                "freshness_badge": "LIVE",
                "detail": {
                    "reason_lines": ["upward_candle_structure"],
                    "warning_lines": ["liquidity_thin"],
                    "invalidation_lines": ["vwap_break_down"],
                    "source_lines": ["market_regime_inference_artifact"],
                    "parameter_set_id": "market_regime.pset.cards.v1",
                },
            }
        ],
    }


def test_market_regime_scenario_part_from_latest_read_model_is_parent_mergeable() -> None:
    part = build_market_regime_scenario_part_from_latest_read_model(_latest_read_model(), horizon_key="900s")

    assert part["prediction_family_id"] == "market_regime"
    assert part["part_role"] == "primary_context"
    assert part["horizon_key"] == "900s"
    assert part["horizon_group"] == "short_horizon"
    assert part["scenario_state"] == "range"
    assert part["scenario_label"] == "レンジ"
    assert part["confidence_percent"] == 70
    assert part["estimated_signal_strength_percent"] == 70
    assert part["drivers"] == ["price_in_range", "mean_reversion_to_vwap"]
    assert part["warnings"] == ["sell_pressure_conflict", "range_low_break_with_volume"]
    assert part["blockers"] == []
    assert part["evidence_refs"][0]["scenario_part_builder_version"] == MARKET_REGIME_SCENARIO_PART_VERSION
    assert part["parent_merge"]["family_decides_overall_scenario"] is False
    assert part["parent_merge"]["same_run_recursive_dependency_allowed"] is False
    assert part["safety"]["writes_dhot"] is False
    assert part["safety"]["ui_render_invokes_classifier"] is False
    assert validate_prediction_family_scenario_part(part)["ok"] is True
    assert validate_market_regime_scenario_part(part)["ok"] is True


def test_market_regime_scenario_part_from_latest_cards_maps_current_uptrend() -> None:
    part = build_market_regime_scenario_part_from_latest_cards(_latest_cards(), horizon_key="current")

    assert part["scenario_state"] == "bullish"
    assert part["scenario_label"] == "上昇地合い"
    assert part["horizon_group"] == "nowcast"
    assert part["parameter_set_id"] == "market_regime.pset.cards.v1"
    assert part["drivers"] == ["upward_candle_structure"]
    assert part["warnings"] == ["liquidity_thin", "vwap_break_down"]
    assert part["source_quality_notes"] == ["market_regime_inference_artifact"]
    assert validate_market_regime_scenario_part(part)["ok"] is True


def test_market_regime_scenario_part_missing_horizon_stays_safe_unknown() -> None:
    part = build_market_regime_scenario_part_from_latest_read_model(_latest_read_model(), horizon_key="3600s")

    assert part["scenario_state"] == "unknown"
    assert part["horizon_key"] == "3600s"
    assert "market_regime_horizon_not_found" in part["blockers"]
    assert "market_regime_unknown" in part["blockers"]
    assert "market_regime_confidence_unavailable" in part["blockers"]
    assert part["safety"]["broker_private_api_allowed"] is False
    assert part["safety"]["autotrade_trigger_allowed"] is False
    assert validate_market_regime_scenario_part(part)["ok"] is True


def test_market_regime_scenario_part_source_has_no_writer_or_execution_path() -> None:
    text = (Path(__file__).resolve().parents[1] / "market_regime/scenario_part.py").read_text(encoding="utf-8")
    required = [
        "build_market_regime_scenario_part_from_latest_read_model",
        "build_market_regime_scenario_part_from_latest_cards",
        "validate_market_regime_scenario_part",
        "family_decides_overall_scenario",
        "same_run_recursive_dependency_allowed",
        "primary_context",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "write_text(",
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
