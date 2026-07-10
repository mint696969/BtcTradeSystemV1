# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_parent_scenario_guidance_status.py
# desc: Verifies WarRoom displays parent scenario-guidance latest read-model status without inference, D-hot writes, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import prediction_cards_view as view  # noqa: E402


class FakeExpander:
    def __enter__(self) -> "FakeExpander":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.tables: list[list[dict[str, object]]] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def expander(self, *_args: object, **_kwargs: object) -> FakeExpander:
        return FakeExpander()

    def dataframe(self, rows: list[dict[str, object]], **_kwargs: object) -> None:
        self.tables.append(rows)


def _write_latest_cards(root: Path) -> None:
    path = root / "prediction/market_regime/latest_cards.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "latest_cards",
        "generated_at": "2026-07-10T00:00:00Z",
        "cards": [
            {
                "horizon": "現在",
                "horizon_key": "current",
                "regime_code": "UNKNOWN",
                "regime_label": "不明",
                "confidence_percent": 15,
                "freshness_badge": "STALE",
                "card_lines": ["不明", "15%", "データ不足"],
            }
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_parent_scenario_guidance(root: Path) -> None:
    path = root / "prediction/scenario_guidance/latest_read_model.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_family": "prediction/scenario_guidance",
        "artifact_kind": "parent_scenario_guidance_latest_read_model",
        "contract_version": "prediction.parent_scenario_guidance_artifact.2026_07_10.v1",
        "relpath": "prediction/scenario_guidance/latest_read_model.json",
        "generated_at": "2026-07-10T00:00:00Z",
        "source_run_id": "market_regime_test_run",
        "horizon_count": 2,
        "family_part_count": 2,
        "rejected_part_count": 0,
        "prediction_family_ids": ["market_regime"],
        "horizons": [
            {
                "artifact_family": "prediction/scenario_guidance",
                "artifact_kind": "parent_scenario_guidance_read_model",
                "schema_version": "prediction_parent_scenario_guidance.2026_07_10.v1",
                "contract_version": "prediction.parent_scenario_guidance.2026_07_10.v1",
                "generated_at": "2026-07-10T00:00:00Z",
                "horizon_key": "current",
                "horizon_group": "nowcast",
                "scenario_state": "unknown",
                "scenario_label": "不明",
                "scenario_summary": "dominant_family=market_regime / scenario=不明 / parts=1 / read_only=true",
                "dominant_family_id": "market_regime",
                "family_part_count": 1,
                "supporting_parts": [],
                "conflicting_parts": [
                    {
                        "prediction_family_id": "market_regime",
                        "part_role": "primary_context",
                        "horizon_key": "current",
                        "horizon_group": "nowcast",
                        "scenario_state": "unknown",
                        "scenario_label": "不明",
                        "confidence_percent": 15,
                        "estimated_signal_strength_percent": 15,
                        "blockers": ["market_regime_unknown"],
                        "warnings": ["forecast_records_stale", "current_l4_candle_window_stale"],
                    }
                ],
                "rejected_parts": [],
                "operator_guidance": {
                    "guidance_mode": "observational_scenario_only",
                    "operator_action": "read_context_only",
                    "scenario_state": "unknown",
                    "blockers": ["market_regime_unknown"],
                    "warnings": ["forecast_records_stale", "current_l4_candle_window_stale"],
                    "prediction_invoked": False,
                    "classifier_invoked": False,
                    "broker_action_allowed": False,
                    "autotrade_trigger_allowed": False,
                    "rejected_part_count": 0,
                },
                "read_only": True,
                "safety": {
                    "read_only_inputs": True,
                    "display_read_model_only": True,
                    "parent_guidance_only": True,
                    "writes_dhot": False,
                    "raw_market_data_read": False,
                    "raw_market_data_duplicated": False,
                    "ui_render_invokes_classifier": False,
                    "classifier_invoked": False,
                    "prediction_invoked": False,
                    "producer_enabled": False,
                    "scheduler_enabled": False,
                    "broker_private_api_allowed": False,
                    "autotrade_trigger_allowed": False,
                    "order_intent_submitted": False,
                    "parameter_auto_promotion_allowed": False,
                    "live_parameter_apply_allowed": False,
                    "would_send_to_broker": False,
                },
            },
            {
                "artifact_family": "prediction/scenario_guidance",
                "artifact_kind": "parent_scenario_guidance_read_model",
                "schema_version": "prediction_parent_scenario_guidance.2026_07_10.v1",
                "contract_version": "prediction.parent_scenario_guidance.2026_07_10.v1",
                "generated_at": "2026-07-10T00:00:00Z",
                "horizon_key": "300s",
                "horizon_group": "short_horizon",
                "scenario_state": "bullish",
                "scenario_label": "上昇地合い",
                "scenario_summary": "dominant_family=market_regime / scenario=上昇地合い / parts=1 / read_only=true",
                "dominant_family_id": "market_regime",
                "family_part_count": 1,
                "supporting_parts": [
                    {
                        "prediction_family_id": "market_regime",
                        "part_role": "primary_context",
                        "horizon_key": "300s",
                        "horizon_group": "short_horizon",
                        "scenario_state": "bullish",
                        "scenario_label": "上昇地合い",
                        "confidence_percent": 65,
                        "estimated_signal_strength_percent": 65,
                        "blockers": [],
                        "warnings": [],
                    }
                ],
                "conflicting_parts": [],
                "rejected_parts": [],
                "operator_guidance": {
                    "guidance_mode": "observational_scenario_only",
                    "operator_action": "read_context_only",
                    "scenario_state": "bullish",
                    "blockers": [],
                    "warnings": [],
                    "prediction_invoked": False,
                    "classifier_invoked": False,
                    "broker_action_allowed": False,
                    "autotrade_trigger_allowed": False,
                    "rejected_part_count": 0,
                },
                "read_only": True,
                "safety": {
                    "read_only_inputs": True,
                    "display_read_model_only": True,
                    "parent_guidance_only": True,
                    "writes_dhot": False,
                    "raw_market_data_read": False,
                    "raw_market_data_duplicated": False,
                    "ui_render_invokes_classifier": False,
                    "classifier_invoked": False,
                    "prediction_invoked": False,
                    "producer_enabled": False,
                    "scheduler_enabled": False,
                    "broker_private_api_allowed": False,
                    "autotrade_trigger_allowed": False,
                    "order_intent_submitted": False,
                    "parameter_auto_promotion_allowed": False,
                    "live_parameter_apply_allowed": False,
                    "would_send_to_broker": False,
                },
            },
        ],
        "rejected_parts": [],
        "summary": {
            "scenario_states": ["bullish", "unknown"],
            "dominant_family_ids": ["market_regime"],
            "read_only": True,
            "display_only": True,
            "parent_guidance_artifact_only": True,
        },
        "safety": {
            "read_only_inputs": True,
            "display_read_model_only": True,
            "parent_guidance_artifact_only": True,
            "writes_dhot": False,
            "raw_market_data_read": False,
            "raw_market_data_duplicated": False,
            "ui_render_invokes_classifier": False,
            "classifier_invoked": False,
            "prediction_invoked": False,
            "producer_enabled": False,
            "scheduler_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_parent_scenario_guidance_status_caption_table_and_result_are_read_only(monkeypatch, tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_parent_scenario_guidance(tmp_path)
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", lambda **kwargs: {"cards": kwargs.get("cards") or [], "card_count": len(kwargs.get("cards") or []), "artifact_cards_used": bool(kwargs.get("cards")), "artifact_path": str(tmp_path / "prediction/market_regime/latest_cards.json"), "artifact_read_error": ""})

    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards({"generated_at": "2026-07-10T00:00:00Z", "cards": []}, fake_st)

    assert result["parent_scenario_guidance_read_model_used"] is True
    assert result["parent_scenario_guidance_horizon_count"] == 2
    assert result["parent_scenario_guidance_family_part_count"] == 2
    assert result["parent_scenario_guidance_rejected_part_count"] == 0
    assert result["parent_scenario_guidance_prediction_family_ids"] == ["market_regime"]
    assert result["parent_scenario_guidance_scenario_states"] == ["bullish", "unknown"]
    assert result["parent_scenario_guidance_broker_private_api_allowed"] is False
    assert result["parent_scenario_guidance_autotrade_trigger_allowed"] is False
    assert result["parent_scenario_guidance_would_send_to_broker"] is False
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert result["broker_action_allowed"] is False
    assert any("親シナリオ" in caption and "horizons=2" in caption and "states=bullish,unknown" in caption for caption in fake_st.captions)
    assert fake_st.tables
    detail_rows = fake_st.tables[0]
    assert {str(row.get("horizon")) for row in detail_rows} == {"current", "300s"}
    assert any(row.get("state") == "unknown" and "market_regime_unknown" in str(row.get("blockers")) for row in detail_rows)
    assert any(row.get("state") == "bullish" and row.get("dominant") == "market_regime" for row in detail_rows)


def test_missing_parent_scenario_guidance_read_model_is_safe(monkeypatch, tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", lambda **kwargs: {"cards": kwargs.get("cards") or [], "card_count": len(kwargs.get("cards") or []), "artifact_cards_used": bool(kwargs.get("cards")), "artifact_path": "", "artifact_read_error": ""})

    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards({"generated_at": "2026-07-10T00:00:00Z", "cards": []}, fake_st)

    assert result["parent_scenario_guidance_read_model_used"] is False
    assert result["parent_scenario_guidance_read_error"] == "parent_scenario_guidance_read_model_missing"
    assert any("親シナリオ: parent_scenario_guidance_read_model_missing" in caption for caption in fake_st.captions)
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False


def test_parent_scenario_guidance_status_source_has_no_execution_write_or_producer_path() -> None:
    text = (Path(__file__).resolve().parents[1] / "prediction_warroom/v2/rt_ui/prediction_cards_view.py").read_text(encoding="utf-8")
    required = [
        "RT_PARENT_SCENARIO_GUIDANCE_READ_MODEL_RELATIVE_PATH",
        "_read_parent_scenario_guidance_read_model_artifact",
        "_render_parent_scenario_guidance_status",
        "_render_parent_scenario_guidance_detail_table",
        "parent_scenario_guidance_horizon_count",
        "parent_scenario_guidance_prediction_family_ids",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "write_parent_scenario_guidance_latest_read_model(",
        "write_market_regime_latest_artifacts_once",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
        "raw_candles",
        "raw_orderbook",
        "raw_trades",
        "raw_executions",
    ]
    assert [token for token in forbidden if token in text] == []
