# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_warroom_visual_binding_diagnostic_once.py
# desc: SR-FX WarRoom visual binding diagnostic tests. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_warroom_visual_binding_diagnostic_once as app


class DummyConfig:
    def __init__(self, root: Path) -> None:
        self.root = root

    def roots(self):
        return {"state": self.root / "state"}


def test_source_status_extracts_fx_identity() -> None:
    call = {"ok": True, "value": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"}}
    status = app._source_status("unit", call)

    assert status["present"] is True
    assert status["identity_ok"] is True
    assert status["identity"]["product_code"] == "FX_BTC_JPY"
    assert status["identity"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"


def test_identity_blocker_detects_nested_spot_market_uid() -> None:
    assert app._identity_blocker(
        "unit_widget",
        {"market_uid": "bitflyer.spot.BTC_JPY"},
    ) == "unit_widget_not_execution_market"
    assert app._identity_blocker(
        "unit_widget",
        {"symbol_raw": "BTC_JPY"},
    ) == "unit_widget_not_execution_product"
    assert app._identity_blocker(
        "unit_widget",
        {"execution_product_code": "FX_BTC_JPY", "execution_market_uid": "bitflyer.fx.FX_BTC_JPY"},
    ) is None


def test_next_diagnostic_blocks_missing_required_panels(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(app, "load_config", lambda: DummyConfig(tmp_path))
    monkeypatch.setattr(app, "execution_market_context", lambda: {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_overview", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_summary_status_payload", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_summary_widget_model", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_prediction_summary_status_payload", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_prediction_summary_widget_model", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_market_summary_status_payload", lambda: {"symbol_raw": "BTC_JPY", "market_uid": "bitflyer.spot.BTC_JPY"})
    monkeypatch.setattr(app, "load_market_signal_context", lambda: None)
    monkeypatch.setattr(app, "build_warroom_header_state", lambda: None)
    monkeypatch.setattr(app, "build_market_regime_state", lambda: None)
    monkeypatch.setattr(app, "analyze_market_monitor_state", lambda: {"state": {"symbol_raw": "FX_BTC_JPY"}})
    monkeypatch.setattr(app, "build_liquidity_pressure_state", lambda: {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "build_trade_flow_state", lambda: None)
    monkeypatch.setattr(app, "analyze_operator_state", lambda: None)
    monkeypatch.setattr(app, "load_operator_display_sources", lambda: {"summary_widget": {"symbol_raw": "BTC_JPY"}})

    payload = app.build_sr_fx_warroom_visual_binding_diagnostic_payload()

    assert payload["ok"] is False
    assert "warroom_header_state_missing" in payload["blocked_by"]
    assert "market_regime_state_missing" in payload["blocked_by"]
    assert "trade_flow_state_missing" in payload["blocked_by"]
    assert "ai_operator_state_missing" in payload["blocked_by"]
    assert "legacy_default_market_summary_still_btc_jpy_visible_to_warroom" not in payload["blocked_by"]
    assert "legacy_default_market_summary_is_btc_jpy_informational_only" in payload["warnings"]
    assert "ai_operator_summary_widget_not_execution_product" in payload["blocked_by"]
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_main_writes_diagnostic_json(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    monkeypatch.setattr(app, "load_config", lambda: cfg)
    monkeypatch.setattr(app, "build_sr_fx_warroom_visual_binding_diagnostic_payload", lambda: {
        "stage": app.STAGE,
        "ok": True,
        "blocked_by": [],
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
    })

    rc = app.main()
    out = cfg.roots()["state"] / "operator_ui" / "sr_fx_warroom_visual_binding_diagnostic.json"
    data = json.loads(out.read_text(encoding="utf-8"))

    assert rc == 0
    assert data["ok"] is True
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False

def test_diagnostic_allows_legacy_default_when_actual_warroom_sources_are_execution_market(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(app, "load_config", lambda: DummyConfig(tmp_path))
    monkeypatch.setattr(app, "execution_market_context", lambda: {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_overview", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_summary_status_payload", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_summary_widget_model", lambda: {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_prediction_summary_status_payload", lambda: {"execution_product_code": "FX_BTC_JPY", "execution_market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_execution_market_prediction_summary_widget_model", lambda: {"market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "load_market_summary_status_payload", lambda: {"symbol_raw": "BTC_JPY", "market_uid": "bitflyer.spot.BTC_JPY"})
    monkeypatch.setattr(app, "load_market_signal_context", lambda: {"data_source": "execution_market_live_canonical"})
    monkeypatch.setattr(app, "build_warroom_header_state", lambda: {"data_source": "execution_market_live_canonical"})
    monkeypatch.setattr(app, "build_market_regime_state", lambda: {"data_source": "execution_market_live_canonical"})
    monkeypatch.setattr(app, "analyze_market_monitor_state", lambda: {"state": {"symbol_raw": "FX_BTC_JPY"}})
    monkeypatch.setattr(app, "build_liquidity_pressure_state", lambda: {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "build_trade_flow_state", lambda: {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})
    monkeypatch.setattr(app, "analyze_operator_state", lambda: {"data_source": "execution_market_live_canonical"})
    monkeypatch.setattr(app, "load_operator_display_sources", lambda: {
        "summary_widget": {"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"},
        "prediction_widget": {"market_uid": "bitflyer.fx.FX_BTC_JPY"},
        "tactic_context": {"execution_product_code": "FX_BTC_JPY", "execution_market_uid": "bitflyer.fx.FX_BTC_JPY"},
    })

    payload = app.build_sr_fx_warroom_visual_binding_diagnostic_payload()

    assert payload["ok"] is True
    assert payload["blocked_by"] == []
    assert payload["decision"] == "warroom_visual_binding_ok"
    assert "legacy_default_market_summary_is_btc_jpy_informational_only" in payload["warnings"]
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False

