# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_execution_safety_harness_once.py
# desc: SR-FX execution safety harness app tests. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_execution_safety_harness_once as app


class DummyConfig:
    execution_market = type("ExecutionMarket", (), {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"})()

    def __init__(self, root: Path) -> None:
        self.root = root

    def roots(self):
        return {
            "state": self.root / "state",
        }


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _public() -> dict:
    return {
        "public_market_readiness": {
            "ok": True,
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "blocked_by": [],
            "warnings": [],
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def _private() -> dict:
    return {
        "readiness": {
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "private_state_known_and_fresh": True,
            "account_clear_for_new_auto_entry": True,
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def _live() -> dict:
    return {
        "live_readiness_contract": {
            "ready": False,
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "active_paper_order_count": 1,
            "paper_position_size": 0.001,
            "paper_position_side": "long",
            "order_sender_implemented": False,
            "bitflyer_order_send_enabled": False,
            "autotrade_live_order_enabled": False,
            "blocked_by": ["active_paper_orders_present", "paper_position_open", "order_sender_not_implemented"],
            "warnings": [],
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def test_sr_fx_execution_safety_harness_once_writes_read_only_json(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    state = cfg.roots()["state"]
    public_path = state / "public" / "bitflyer_fx_public_market_readiness.json"
    private_path = state / "private" / "bitflyer_fx_readiness.json"
    live_path = state / "private" / "bitflyer_fx_live_readiness_contract.json"
    safety_path = state / "autotrade" / "sr_fx_execution_safety_harness.json"
    _write_json(public_path, _public())
    _write_json(private_path, _private())
    _write_json(live_path, _live())

    class DummyAutoTradeReadiness:
        ready = False
        current_mode = type("Mode", (), {"value": "ARMED_DRY_RUN"})()
        target_mode = type("Mode", (), {"value": "LIVE_MIN_SIZE"})()

        def to_dict(self):
            return {
                "ready": False,
                "current_mode": "ARMED_DRY_RUN",
                "target_mode": "LIVE_MIN_SIZE",
                "blocked_by": ["sr_fx_live_readiness_not_ready"],
                "warnings": [],
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
            }

    monkeypatch.setattr(app, "load_config", lambda: cfg)
    monkeypatch.setattr(app, "evaluate_autotrade_live_readiness", lambda **kwargs: DummyAutoTradeReadiness())

    rc = app.main()
    data = json.loads(safety_path.read_text(encoding="utf-8"))

    assert rc == 0
    assert data["ok"] is False
    assert data["stage"] == "sr_fx_execution_safety_harness_once"
    assert data["paths"]["safety_harness_path"] == str(safety_path)
    harness = data["execution_safety_harness"]
    assert harness["ok"] is False
    assert "active_paper_orders_present" in harness["blocked_by"]
    assert "paper_position_open" in harness["blocked_by"]
    assert "sr_fx_live_readiness_not_ready" in harness["blocked_by"]
    assert harness["read_only"] is True
    assert harness["would_send_to_broker"] is False
    assert harness["mode_changed"] is False
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False


def test_sr_fx_execution_safety_harness_once_failsoft_writes_error_json(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    safety_path = cfg.roots()["state"] / "autotrade" / "sr_fx_execution_safety_harness.json"
    monkeypatch.setattr(app, "load_config", lambda: cfg)

    rc = app.main()
    data = json.loads(safety_path.read_text(encoding="utf-8"))

    assert rc == 0
    assert data["ok"] is False
    assert data["stage"] == "sr_fx_execution_safety_harness_once"
    assert "error" in data
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False
    assert data["mode_changed"] is False
