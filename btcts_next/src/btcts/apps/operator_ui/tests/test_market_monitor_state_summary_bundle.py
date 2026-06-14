# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_monitor_state_summary_bundle.py
# desc: Verify market_monitor_state keeps execution-market summary ui bundle and flat aliases together.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.market_monitor_state as state_mod  # noqa: E402


def main() -> int:
    original_execution_market_context = state_mod.execution_market_context
    original_latest_live_board_metrics = state_mod.latest_live_board_metrics
    original_load_execution_market_overview = state_mod.load_execution_market_overview
    original_load_execution_market_summary_ui_bundle = state_mod.load_execution_market_summary_ui_bundle
    original_market_monitor_metrics = state_mod.market_monitor_metrics
    original_market_state_diagnostics = state_mod.market_state_diagnostics

    summary_payload = {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "symbol_raw": "FX_BTC_JPY",
        "trust_state": "trusted",
        "continuity_state": "rest_baseline_snapshot",
        "interpretation_bucket": "allow_structural_use",
        "semantic_runtime_wiring_status": "wired",
    }
    summary_widget = {
        "widget_kind": "market_summary",
        "semantic_wiring_key": "wired",
    }
    summary_bundle = {
        "summary": {"summary_type": "market_summary"},
        "status_payload": summary_payload,
        "widget_model": summary_widget,
    }

    try:
        state_mod.execution_market_context = lambda: {
            "exchange": "bitflyer",
            "symbol_raw": "FX_BTC_JPY",
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
        }
        calls: list[tuple[str, str]] = []
        state_mod.latest_live_board_metrics = lambda **kwargs: calls.append((kwargs["exchange"], kwargs["symbol"])) or {}
        state_mod.load_execution_market_overview = lambda: {"market_uid": "bitflyer.fx.FX_BTC_JPY"}
        state_mod.load_execution_market_summary_ui_bundle = lambda: summary_bundle
        state_mod.market_monitor_metrics = lambda _state: {
            "best_bid": 100.0,
            "best_ask": 101.0,
            "spread": 1.0,
            "bid_depth": 2.0,
            "ask_depth": 3.0,
            "imbalance": -0.2,
            "event_ts": "2026-04-14T12:00:00Z",
            "trust_state": None,
            "boundary_reason": None,
            "continuity_state": None,
            "interpretation_bucket": None,
            "interpretation_reason": None,
        }
        state_mod.market_state_diagnostics = lambda **kwargs: {"preferred_row_freshness": "LIVE", "symbol_raw": kwargs["symbol_raw"]}

        state_bundle = state_mod.analyze_market_monitor_state()
        assert state_bundle is not None

        assert calls == [("bitflyer", "FX_BTC_JPY")]
        assert state_bundle["summary_bundle"] is summary_bundle
        assert state_bundle["summary"] is summary_payload
        assert state_bundle["summary_widget"] is summary_widget
        assert state_bundle["state_diag"]["preferred_row_freshness"] == "LIVE"
        assert state_bundle["state_diag"]["symbol_raw"] == "FX_BTC_JPY"
        assert state_bundle["source_label"] == "execution_market_state"
        assert state_bundle["board"]["spread"] == 1.0
    finally:
        state_mod.execution_market_context = original_execution_market_context
        state_mod.latest_live_board_metrics = original_latest_live_board_metrics
        state_mod.load_execution_market_overview = original_load_execution_market_overview
        state_mod.load_execution_market_summary_ui_bundle = original_load_execution_market_summary_ui_bundle
        state_mod.market_monitor_metrics = original_market_monitor_metrics
        state_mod.market_state_diagnostics = original_market_state_diagnostics

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
