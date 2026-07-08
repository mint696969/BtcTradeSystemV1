# path: ./btcts_next/src/btcts/apps/tests/test_market_regime_calibration_ui_panel_cp25.py
# desc: CP25 source-level tests for displaying MarketRegime calibration read-model in Operator UI without invoking prediction/classifier/raw reads from render path.

from __future__ import annotations

from pathlib import Path


def _collector_page_text() -> str:
    return (Path(__file__).resolve().parents[1] / "operator_ui" / "views" / "collector_page.py").read_text(encoding="utf-8")


def test_cp25_collector_page_renders_market_regime_calibration_metrics() -> None:
    text = _collector_page_text()
    required = [
        "Calibration",
        "Cal Source",
        "Cal Score",
        "Known",
        "Hit / Partial / Miss",
        "Reference",
        "calibration_primary_observation_source",
        "calibration_primary_score",
        "calibration_primary_known_total",
        "calibration_primary_counts",
        "calibration_reference_score",
        "calibration_latest_read_model_path",
    ]
    assert [token for token in required if token not in text] == []


def test_cp25_collector_page_calibration_panel_is_read_only_display() -> None:
    text = _collector_page_text()
    calibration_block = text.split('st.caption("Calibration read-model")', 1)[1].split('b1, b2, b3, b4, b5 = st.columns(5)', 1)[0]
    forbidden = [
        "request_market_regime_preflight(",
        "request_market_regime_run_once(",
        "start_market_regime_producer_loop_detached(",
        "request_market_regime_producer_loop_safe_stop(",
        "request_market_regime_producer_loop_restart(",
        "write_market_regime_latest_artifacts_once",
        "classify_market_regime_feature_bundle",
        "build_market_regime_source_snapshot",
        "build_market_regime_feature_bundle",
        "raw_candles",
        "raw_orderbook",
        "raw_trades",
        "raw_executions",
    ]
    assert [token for token in forbidden if token in calibration_block] == []
    assert "st.button" not in calibration_block
    assert ".metric(" in calibration_block
