# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_calibration_status_cp26.py
# desc: CP26 verifies WarRoom prediction cards display MarketRegime calibration read-model status without prediction/classifier/raw/broker side effects.

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
        "schema_version": "market_regime_latest_cards.2026_07_08.v1",
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


def _write_calibration_read_model(root: Path) -> None:
    path = root / "prediction/market_regime/calibration/latest_read_model.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "calibration_read_model",
        "date": "2026-07-08",
        "month": "2026-07",
        "primary_observation_source": "candle_summary",
        "primary": {
            "key": "candle_summary",
            "known_total": 568,
            "counts": {"hit": 306, "partial": 138, "miss": 124, "unknown": 0, "invalidated": 0},
            "calibration_score": 0.6602,
        },
        "latest_cards_current_reference": {"key": "latest_cards_current", "calibration_score": 1.0},
        "safety": {
            "raw_market_data_read": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "would_send_to_broker": False,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_cp26_warroom_prediction_cards_render_calibration_status_caption(monkeypatch, tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_calibration_read_model(tmp_path)
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))

    shell_calls: list[dict[str, Any]] = []

    def fake_shell(**kwargs: object) -> dict[str, Any]:
        shell_calls.append(dict(kwargs))
        cards = kwargs.get("cards") if isinstance(kwargs.get("cards"), list) else []
        return {
            "cards": cards,
            "card_count": len(cards),
            "artifact_cards_used": bool(cards),
            "artifact_path": str(tmp_path / "prediction/market_regime/latest_cards.json"),
            "artifact_read_error": "",
        }

    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", fake_shell)
    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards({"generated_at": "2026-07-08T12:00:00Z", "cards": []}, fake_st)

    assert shell_calls and isinstance(shell_calls[0].get("cards"), list)
    assert result["market_regime_calibration_read_model_used"] is True
    assert result["market_regime_calibration_primary_observation_source"] == "candle_summary"
    assert result["market_regime_calibration_primary_score"] == 0.6602
    assert result["market_regime_calibration_primary_known_total"] == 568
    assert result["market_regime_calibration_primary_counts"] == {"hit": 306, "partial": 138, "miss": 124, "unknown": 0, "invalidated": 0}
    assert result["market_regime_calibration_reference_score"] == 1.0
    assert any("地合い評価" in caption and "source=candle_summary" in caption and "score=0.6602" in caption for caption in fake_st.captions)
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert result["broker_action_allowed"] is False


def test_cp26_missing_calibration_read_model_is_safe(monkeypatch, tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", lambda **kwargs: {"cards": kwargs.get("cards") or [], "card_count": len(kwargs.get("cards") or []), "artifact_cards_used": bool(kwargs.get("cards")), "artifact_path": "", "artifact_read_error": ""})
    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards({"generated_at": "2026-07-08T12:00:00Z", "cards": []}, fake_st)
    assert result["market_regime_calibration_read_model_used"] is False
    assert result["market_regime_calibration_read_error"] == "calibration_read_model_missing"
    assert any("地合い評価: calibration_read_model_missing" in caption for caption in fake_st.captions)
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False


def test_cp26_prediction_cards_source_is_read_only_calibration_display() -> None:
    text = (Path(__file__).resolve().parents[1] / "prediction_warroom/v2/rt_ui/prediction_cards_view.py").read_text(encoding="utf-8")
    required = [
        "RT_MARKET_REGIME_CALIBRATION_READ_MODEL_RELATIVE_PATH",
        "_read_market_regime_calibration_read_model_artifact",
        "_render_market_regime_calibration_status",
        "market_regime_calibration_primary_observation_source",
        "market_regime_calibration_primary_score",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "write_market_regime_latest_artifacts_once",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "raw_candles",
        "raw_orderbook",
        "raw_trades",
        "raw_executions",
    ]
    assert [token for token in forbidden if token in text] == []
