# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_parameter_set_comparison_status.py
# desc: Verifies WarRoom displays MarketRegime parameter-set comparison read-model status without inference, D-hot writes, broker, AutoTrade, or parameter mutation.

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
        "generated_at": "2026-07-08T12:00:00Z",
        "cards": [
            {
                "horizon": "現在",
                "horizon_key": "current",
                "regime_code": "RANGE",
                "regime_label": "レンジ",
                "confidence_percent": 70,
                "freshness_badge": "LIVE",
                "card_lines": ["レンジ", "70%", "方向感なし"],
            }
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_parameter_set_comparison_read_model(root: Path) -> None:
    path = root / "prediction/market_regime/parameter_set_comparison/latest_read_model.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "parameter_set_comparison_read_model",
        "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
        "comparison_ready": False,
        "comparison_blockers": ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"],
        "calibration_trust": {
            "trusted_row_count": 568,
            "reference_only_row_count": 804,
            "trusted_parameter_set_count": 1,
            "comparable_parameter_set_count": 1,
            "latest_cards_current_is_reference_only": True,
        },
        "promotion_candidates": [],
        "recommendations": [
            {
                "parameter_set_id": "market_regime_engine_parameter_set.v1",
                "recommendation": "keep_testing",
                "human_gate_required": True,
                "auto_apply_allowed": False,
                "auto_promotion_allowed": False,
            }
        ],
        "safety": {
            "display_read_model_only": True,
            "writes_dhot": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_parameter_set_comparison_status_caption_and_result_are_read_only(monkeypatch, tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_parameter_set_comparison_read_model(tmp_path)
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))

    shell_calls: list[dict[str, Any]] = []

    def fake_shell(**kwargs: object) -> dict[str, Any]:
        shell_calls.append(dict(kwargs))
        cards = kwargs.get("cards") if isinstance(kwargs.get("cards"), list) else []
        return {"cards": cards, "card_count": len(cards), "artifact_cards_used": bool(cards), "artifact_path": str(tmp_path / "prediction/market_regime/latest_cards.json"), "artifact_read_error": ""}

    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", fake_shell)
    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards({"generated_at": "2026-07-08T12:00:00Z", "cards": []}, fake_st)

    assert result["market_regime_parameter_set_comparison_read_model_used"] is True
    assert result["market_regime_parameter_set_comparison_ready"] is False
    assert result["market_regime_parameter_set_comparison_blockers"] == ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"]
    assert result["market_regime_parameter_set_comparison_trusted_row_count"] == 568
    assert result["market_regime_parameter_set_comparison_reference_only_row_count"] == 804
    assert result["market_regime_parameter_set_comparison_trusted_parameter_set_count"] == 1
    assert result["market_regime_parameter_set_comparison_comparable_parameter_set_count"] == 1
    assert result["market_regime_parameter_set_comparison_promotion_candidate_count"] == 0
    assert result["market_regime_parameter_set_comparison_recommendation_count"] == 1
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert result["broker_action_allowed"] is False
    assert shell_calls and isinstance(shell_calls[0].get("cards"), list)
    assert any("パラメータ比較" in caption and "比較未準備" in caption and "ready=False" in caption and "promotions=0" in caption for caption in fake_st.captions)
    assert fake_st.tables
    detail_rows = fake_st.tables[-1]
    assert {str(row.get("項目")) for row in detail_rows} >= {"状態", "信頼サンプル", "参考サンプル", "昇格候補", "blockers"}
    assert any(row.get("項目") == "昇格候補" and row.get("値") == "0" for row in detail_rows)
    assert any(row.get("項目") == "状態" and "比較未準備" in str(row.get("値")) for row in detail_rows)


def test_missing_parameter_set_comparison_read_model_is_safe(monkeypatch, tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", lambda **kwargs: {"cards": kwargs.get("cards") or [], "card_count": len(kwargs.get("cards") or []), "artifact_cards_used": bool(kwargs.get("cards")), "artifact_path": "", "artifact_read_error": ""})
    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards({"generated_at": "2026-07-08T12:00:00Z", "cards": []}, fake_st)
    assert result["market_regime_parameter_set_comparison_read_model_used"] is False
    assert result["market_regime_parameter_set_comparison_read_error"] == "parameter_set_comparison_read_model_missing"
    assert any("パラメータ比較: parameter_set_comparison_read_model_missing" in caption for caption in fake_st.captions)
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False


def test_parameter_set_comparison_status_source_has_no_execution_or_write_path() -> None:
    text = (Path(__file__).resolve().parents[1] / "prediction_warroom/v2/rt_ui/prediction_cards_view.py").read_text(encoding="utf-8")
    required = [
        "RT_MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_RELATIVE_PATH",
        "_read_market_regime_parameter_set_comparison_read_model_artifact",
        "_render_market_regime_parameter_set_comparison_status",
        "_render_parameter_set_comparison_detail_table",
        "_parameter_set_comparison_display_state",
        "market_regime_parameter_set_comparison_ready",
        "market_regime_parameter_set_comparison_promotion_candidate_count",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "write_market_regime_parameter_set_comparison_read_model(",
        "write_market_regime_latest_artifacts_once",
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
