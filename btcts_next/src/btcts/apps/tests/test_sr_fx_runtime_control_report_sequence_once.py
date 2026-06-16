# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_runtime_control_report_sequence_once.py
# desc: Tests for broker-free runtime_control refresh -> SR-FX report sequence.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_runtime_control_report_sequence_once as app


class DummyConfig:
    def __init__(self, root: Path) -> None:
        self.root = root

    def roots(self):
        return {"state": self.root / "state"}


class DummyAutoTradeReadiness:
    def to_dict(self) -> dict:
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


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _data_ui_ok() -> dict:
    return {
        "ok": True,
        "data_ui_integrity_ready_for_final_human_review": True,
        "autotrade_resume_authorized": False,
        "blocked_by": [],
        "summary": {"primary_lineage": "continuous_ws", "service_stale": False},
        "context": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"},
        "read_only": True,
        "would_send_to_broker": False,
    }


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
            "blocked_by": [],
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
            "blocked_by": ["order_sender_not_implemented"],
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def _seed_state(root: Path) -> None:
    state = root / "state"
    _write_json(state / "operator_ui" / "sr_fx_final_readiness_checkpoint.json", _data_ui_ok())
    _write_json(state / "public" / "bitflyer_fx_public_market_readiness.json", _public())
    _write_json(state / "private" / "bitflyer_fx_readiness.json", _private())
    _write_json(state / "private" / "bitflyer_fx_live_readiness_contract.json", _live())


def _patch_load_config(monkeypatch, cfg: DummyConfig) -> None:
    monkeypatch.setattr(app, "load_config", lambda: cfg)
    monkeypatch.setattr(app.safety_app, "load_config", lambda: cfg)
    monkeypatch.setattr(app.pre_live_app, "load_config", lambda: cfg)
    monkeypatch.setattr(app.final_review_app, "load_config", lambda: cfg)
    monkeypatch.setattr(app.handoff_app, "load_config", lambda: cfg)
    monkeypatch.setattr(app.safety_app, "evaluate_autotrade_live_readiness", lambda **kwargs: DummyAutoTradeReadiness())
    monkeypatch.setattr(app.pre_live_app, "evaluate_autotrade_live_readiness", lambda **kwargs: DummyAutoTradeReadiness())


def test_sequence_refreshes_runtime_control_before_reports(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    _seed_state(tmp_path)
    _patch_load_config(monkeypatch, cfg)
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_NOW", "2026-06-17T00:00:10Z")

    out = app.run_sr_fx_runtime_control_report_sequence()
    state = cfg.roots()["state"]
    safety = json.loads((state / "autotrade" / "sr_fx_execution_safety_harness.json").read_text(encoding="utf-8"))
    pre_live = json.loads((state / "autotrade" / "sr_fx_pre_live_blocker_report.json").read_text(encoding="utf-8"))
    final = json.loads((state / "operator_ui" / "sr_fx_final_review_package.json").read_text(encoding="utf-8"))
    handoff = json.loads((state / "operator_ui" / "sr_fx_data_ui_gate_handoff.json").read_text(encoding="utf-8"))

    assert out["ok"] is True
    assert out["sequence_complete"] is True
    assert [step["name"] for step in out["steps"]] == [
        "runtime_control_snapshot_refresh",
        "execution_safety_harness_report",
        "pre_live_blocker_report",
        "final_review_package",
        "data_ui_gate_handoff",
    ]
    assert out["summary"]["runtime_control_refreshed_first"] is True
    assert out["runtime_control"]["exists"] is True
    assert safety["runtime_control"]["exists"] is True
    assert pre_live["runtime_control"]["exists"] is True
    assert final["runtime_control"]["present"] is True
    assert handoff["execution_boundary"]["runtime_control"]["present"] is True
    assert "runtime_control_snapshot_missing" not in final["execution_boundary_blocked_by"]
    assert out["read_only"] is True
    assert out["would_send_to_broker"] is False
    assert out["mode_changed"] is False


def test_sequence_carries_stale_runtime_control_blockers_to_handoff(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    _seed_state(tmp_path)
    _patch_load_config(monkeypatch, cfg)
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_NOW", "2026-06-17T00:00:10Z")
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_HEARTBEAT_OBSERVED_AT", "2026-06-17T00:00:00Z")
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_HEARTBEAT_MAX_AGE_SEC", "5")

    out = app.run_sr_fx_runtime_control_report_sequence()
    state = cfg.roots()["state"]
    final = json.loads((state / "operator_ui" / "sr_fx_final_review_package.json").read_text(encoding="utf-8"))
    handoff = json.loads((state / "operator_ui" / "sr_fx_data_ui_gate_handoff.json").read_text(encoding="utf-8"))

    assert out["ok"] is True
    assert out["summary"]["runtime_control_snapshot_ok"] is False
    assert "heartbeat_stale" in out["runtime_control"]["blocked_by"]
    assert "runtime_control_not_clear" in final["execution_boundary_blocked_by"]
    assert "heartbeat_stale" in final["execution_boundary_blocked_by"]
    assert "heartbeat_stale" in handoff["execution_boundary"]["runtime_control"]["blocked_by"]
    assert "clear_runtime_control_heartbeat_kill_switch_incident_blockers" in handoff["execution_boundary"]["next_actions"]
    assert out["would_send_to_broker"] is False
