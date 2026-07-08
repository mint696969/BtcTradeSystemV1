# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_calibration_runtime_snapshot_cp24.py
# desc: CP24 tests for exposing calibration/latest_read_model.json through MarketRegime operator runtime snapshot. Read-only UI visibility; no classifier, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.calibration_read_model import CALIBRATION_LATEST_READ_MODEL_RELPATH  # noqa: E402
from btcts.prediction.market_regime.operator_ui_runtime import (  # noqa: E402
    market_regime_operator_ui_paths,
    market_regime_operator_ui_snapshot,
)


def _write_latest_cards(root: Path) -> None:
    path = root / "prediction/market_regime/latest_cards.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "latest_cards",
        "run_id": "market_regime_cp24_run",
        "generated_at": "2026-07-08T12:00:00Z",
        "horizon_count": 1,
        "cards": [
            {
                "horizon": "現在",
                "horizon_key": "current",
                "horizon_sec": 0,
                "regime_code": "RANGE",
                "regime_label": "レンジ",
                "confidence_percent": 70,
                "freshness_badge": "LIVE",
            }
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_calibration_read_model(root: Path) -> None:
    path = root / CALIBRATION_LATEST_READ_MODEL_RELPATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "calibration_read_model",
        "prediction_family_id": "market_regime",
        "date": "2026-07-08",
        "month": "2026-07",
        "primary_observation_source": "candle_summary",
        "primary": {
            "key": "candle_summary",
            "total": 568,
            "known_total": 568,
            "counts": {"hit": 306, "partial": 138, "miss": 124, "unknown": 0, "invalidated": 0},
            "hit_rate": 0.5387,
            "partial_rate": 0.243,
            "miss_rate": 0.2183,
            "calibration_score": 0.6602,
            "avg_confidence_percent": 68.75,
        },
        "latest_cards_current_reference": {
            "key": "latest_cards_current",
            "total": 804,
            "known_total": 804,
            "counts": {"hit": 804, "partial": 0, "miss": 0, "unknown": 0, "invalidated": 0},
            "hit_rate": 1.0,
            "partial_rate": 0.0,
            "miss_rate": 0.0,
            "calibration_score": 1.0,
            "avg_confidence_percent": 68.58,
        },
        "by_observation_source": [],
        "safety": {
            "read_only_calibration_inputs": True,
            "writes_read_model_artifact_only": True,
            "raw_market_data_read": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "would_send_to_broker": False,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_cp24_paths_include_calibration_latest_read_model(tmp_path: Path) -> None:
    paths = market_regime_operator_ui_paths(tmp_path)
    assert paths["calibration_latest_read_model"] == tmp_path / CALIBRATION_LATEST_READ_MODEL_RELPATH


def test_cp24_operator_snapshot_exposes_calibration_summary_read_only(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_calibration_read_model(tmp_path)
    snapshot = market_regime_operator_ui_snapshot(tmp_path)
    assert snapshot["latest_cards_available"] is True
    assert snapshot["calibration_read_model_available"] is True
    assert snapshot["calibration_primary_observation_source"] == "candle_summary"
    assert snapshot["calibration_primary_score"] == 0.6602
    assert snapshot["calibration_primary_known_total"] == 568
    assert snapshot["calibration_primary_counts"] == {"hit": 306, "partial": 138, "miss": 124, "unknown": 0, "invalidated": 0}
    assert snapshot["calibration_reference_score"] == 1.0
    assert snapshot["calibration_latest_read_model_path"].replace("\\", "/").endswith("prediction/market_regime/calibration/latest_read_model.json")
    assert snapshot["calibration_read_model"]["artifact_kind"] == "calibration_read_model"
    assert snapshot["scheduler_enabled"] is False
    assert snapshot["broker_private_api_allowed"] is False
    assert snapshot["autotrade_trigger_allowed"] is False
    assert snapshot["would_send_to_broker"] is False
    assert "raw_candles" not in json.dumps(snapshot, ensure_ascii=False)


def test_cp24_operator_snapshot_handles_missing_calibration_read_model(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    snapshot = market_regime_operator_ui_snapshot(tmp_path)
    assert snapshot["calibration_read_model_available"] is False
    assert snapshot["calibration_primary_observation_source"] == ""
    assert snapshot["calibration_primary_score"] is None
    assert snapshot["calibration_primary_known_total"] == 0


def test_cp24_runtime_source_has_no_ui_render_inference_or_execution_side_effects() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/operator_ui_runtime.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "calibration_latest_read_model",
        "calibration_read_model_available",
        "calibration_primary_observation_source",
        "calibration_primary_score",
        "calibration_primary_counts",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "import streamlit",
        "from btcts.apps.operator_ui",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "classify_market_regime_feature_bundle(",
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
