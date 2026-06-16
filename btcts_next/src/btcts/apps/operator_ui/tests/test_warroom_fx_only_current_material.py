# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_fx_only_current_material.py
# desc: G2 SR-FX Data/UI Integrity Gate: WarRoom current material is execution-market only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.market_monitor_state as monitor_state  # noqa: E402
import btcts.apps.operator_ui.components.liquidity_pressure_state as liquidity_state  # noqa: E402
import btcts.apps.operator_ui.components.market_signal_state as signal_state  # noqa: E402
import btcts.apps.operator_ui.components.trade_flow_state as flow_state  # noqa: E402
import btcts.apps.operator_ui.components.warroom_header_state as header_state  # noqa: E402


def _ctx() -> dict:
    return {
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "market_type": "fx",
        "market_role": "execution",
        "read_only": True,
        "would_send_to_broker": False,
    }


def test_market_monitor_uses_execution_market_state_and_does_not_replay_fallback(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(monitor_state, "execution_market_context", _ctx)
    monkeypatch.setattr(monitor_state, "latest_live_board_metrics", lambda **kwargs: calls.append((kwargs["exchange"], kwargs["symbol"])) or {})
    monkeypatch.setattr(monitor_state, "load_execution_market_overview", lambda: {"market_uid": "bitflyer.fx.FX_BTC_JPY", "spread": 1.0})
    monkeypatch.setattr(monitor_state, "load_execution_market_summary_ui_bundle", lambda: {"status_payload": {"market_uid": "bitflyer.fx.FX_BTC_JPY"}, "widget_model": object(), "summary": object()})
    monkeypatch.setattr(monitor_state, "market_state_diagnostics", lambda **kwargs: {"symbol_raw": kwargs["symbol_raw"]})
    monkeypatch.setattr(monitor_state, "market_monitor_metrics", lambda state: {"spread": 1.0, "event_ts": "2026-06-14T00:00:00Z"})
    monkeypatch.setattr(monitor_state, "load_latest_replay_payload", lambda: (_ for _ in ()).throw(AssertionError("replay fallback must not be used")))

    result = monitor_state.analyze_market_monitor_state()

    assert result is not None
    assert calls == [("bitflyer", "FX_BTC_JPY")]
    assert result["state"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert result["source_label"] == "execution_market_state"
    assert result["summary"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"


def test_liquidity_and_trade_flow_read_fx_live_only(monkeypatch) -> None:
    liq_calls: list[tuple[str, str]] = []
    flow_calls: list[tuple[str, str]] = []

    monkeypatch.setattr(liquidity_state, "execution_market_context", _ctx)
    monkeypatch.setattr(liquidity_state, "latest_live_board_metrics", lambda **kwargs: liq_calls.append((kwargs["exchange"], kwargs["symbol"])) or {"bid_depth": 2.0, "ask_depth": 1.0, "event_ts": "2026-06-14T00:00:00Z"})
    liq = liquidity_state.build_liquidity_pressure_state()
    assert liq is not None
    assert liq_calls == [("bitflyer", "FX_BTC_JPY")]
    assert liq["source_label"] == "execution_market_live_canonical"
    assert liq["market_uid"] == "bitflyer.fx.FX_BTC_JPY"

    monkeypatch.setattr(flow_state, "execution_market_context", _ctx)
    monkeypatch.setattr(flow_state, "recent_live_tradeflow_metrics", lambda **kwargs: flow_calls.append((kwargs["exchange"], kwargs["symbol"])) or {"buy_size": 1.0, "sell_size": 0.4, "delta": 0.6, "trade_count": 3, "event_ts": "2026-06-14T00:00:01Z"})
    flow = flow_state.build_trade_flow_state()
    assert flow is not None
    assert flow_calls == [("bitflyer", "FX_BTC_JPY")]
    assert flow["source_label"] == "execution_market_live_canonical"
    assert flow["market_uid"] == "bitflyer.fx.FX_BTC_JPY"


def test_current_signal_uses_execution_market_state_instead_of_replay(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(signal_state, "execution_market_context", _ctx)
    monkeypatch.setattr(signal_state, "latest_live_board_metrics", lambda **kwargs: calls.append((kwargs["exchange"], kwargs["symbol"])) or {})
    monkeypatch.setattr(signal_state, "recent_live_tradeflow_metrics", lambda **kwargs: {})
    monkeypatch.setattr(signal_state, "load_latest_experiment_payload", lambda: {})
    monkeypatch.setattr(signal_state, "latest_regime_name", lambda payload: "unknown")
    monkeypatch.setattr(signal_state, "latest_best_strategy_name", lambda payload: "baseline_none")
    monkeypatch.setattr(signal_state, "load_execution_market_overview", lambda: {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "symbol_raw": "FX_BTC_JPY",
        "spread": 1.0,
        "imbalance": 0.25,
        "trade_delta": -0.5,
        "near_zone_liquidity_summary": {"bid_size_total": 2.0, "ask_size_total": 1.0},
        "collector_ts": "2026-06-14T00:00:02Z",
    })
    assert not hasattr(signal_state, "load_latest_replay_payload")

    result = signal_state.load_market_signal_context()

    assert result is not None
    assert calls == [("bitflyer", "FX_BTC_JPY")]
    assert result["data_source"] == "execution_market_state"
    assert result["pressure_bias"] == "execution_market_state"
    assert result["spread"] == 1.0
    assert result["delta"] == -0.5


def test_warroom_header_prediction_uses_execution_market_widget(monkeypatch) -> None:
    monkeypatch.setattr(header_state, "load_market_signal_context", lambda: {
        "spread": 1.0,
        "imbalance": 0.25,
        "delta": -0.5,
        "wall_ratio": 0.1,
        "pressure_bias": "execution_market_state",
        "event_ts": "2026-06-14T00:00:00Z",
        "regime": "live_canonical",
        "best_strategy": "baseline_none",
        "data_source": "execution_market_state",
    })
    monkeypatch.setattr(header_state, "load_execution_market_prediction_summary_widget_model", lambda: type("Widget", (), {
        "short_horizon_bias_key": "neutral",
        "caution_level_key": "medium",
        "scenario_switch_hint_key": "watch",
        "trace_summary_key": "fx_trace",
    })())

    result = header_state.build_warroom_header_state()

    assert result is not None
    assert result["source_label"] == "execution_market_state + research_experiment"
    assert result["source"] == "execution_market_state + research_experiment"
    assert result["prediction_trace_summary"] == "fx_trace"
