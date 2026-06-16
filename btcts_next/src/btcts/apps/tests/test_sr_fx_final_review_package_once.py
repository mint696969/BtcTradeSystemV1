# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_final_review_package_once.py
# desc: SR-FX final review package tests. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_final_review_package_once as app


class DummyConfig:
    def __init__(self, root: Path) -> None:
        self.root = root

    def roots(self):
        return {"state": self.root / "state"}


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


def _public(ok: bool = True) -> dict:
    return {
        "public_market_readiness": {
            "ok": ok,
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "blocked_by": [] if ok else ["fx_public_ws_preflight_not_ok"],
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def _private(clear: bool = True) -> dict:
    return {
        "readiness": {
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "private_state_known_and_fresh": True,
            "account_clear_for_new_auto_entry": clear,
            "blocked_by": [] if clear else ["account_not_clear_for_new_auto_entry"],
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def _live(ready: bool = False) -> dict:
    return {
        "live_readiness_contract": {
            "ready": ready,
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "blocked_by": [] if ready else ["order_sender_not_implemented"],
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def _safety(ok: bool = False) -> dict:
    return {
        "execution_safety_harness": {
            "ok": ok,
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "blocked_by": [] if ok else ["sr_fx_live_readiness_not_ready"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
    }


def _report(ok: bool = False, *, runtime_ok: bool | None = None) -> dict:
    runtime = _runtime_control(ok=bool(runtime_ok if runtime_ok is not None else ok))["runtime_control"]
    return {
        "runtime_control": runtime,
        "report": {
            "ok": ok,
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "primary_blockers": [] if ok else ["pre_live_blockers_present"],
            "blocked_by": [] if ok else ["pre_live_blockers_present"],
            "sections": {
                "runtime_control": {
                    "ok": runtime["ok"],
                    "blocked_by": runtime["blocked_by"],
                    "warnings": runtime["warnings"],
                    "summary": {"heartbeat_fresh": runtime["heartbeat"]["fresh"], "incident_count": len(runtime["incidents"])},
                    "read_only": True,
                    "would_send_to_broker": False,
                }
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
    }



def _runtime_control(ok: bool = False) -> dict:
    return {
        "runtime_control": {
            "exists": True,
            "path": "D:/btc_ts_hot/state/autotrade/diagnostics/runtime_control_state.json",
            "ok": ok,
            "blocked_by": [] if ok else ["heartbeat_stale", "open_incident_present"],
            "warnings": ["runtime_control_scaffold_read_only"],
            "kill_switch": {"active": False, "action": "HALT_NEW"},
            "heartbeat": {"fresh": ok, "component": "autotrade.runtime"},
            "incidents": [] if ok else [{"incident_id": "inc_unit", "open": True}],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
    }

def test_package_can_be_ok_for_data_ui_while_execution_boundary_is_blocked() -> None:
    payload = app.build_sr_fx_final_review_package_payload(
        data_ui_checkpoint=_data_ui_ok(),
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=False),
        execution_safety_harness=_safety(ok=False),
        pre_live_blocker_report=_report(ok=False),
        generated_at="2026-06-14T00:00:00Z",
    )

    assert payload["ok"] is True
    assert payload["data_ui_integrity_ready_for_final_human_review"] is True
    assert payload["execution_boundary_clear"] is False
    assert "live_readiness_contract_not_ready" in payload["execution_boundary_blocked_by"]
    assert "execution_safety_harness_not_ready" in payload["execution_boundary_blocked_by"]
    assert payload["autotrade_resume_authorized"] is False
    assert payload["final_human_review_required"] is True
    assert payload["mode_changed"] is False
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_package_blocks_when_data_ui_checkpoint_not_ready() -> None:
    data_ui = _data_ui_ok()
    data_ui["ok"] = False
    data_ui["data_ui_integrity_ready_for_final_human_review"] = False
    data_ui["blocked_by"] = ["service_not_stale"]

    payload = app.build_sr_fx_final_review_package_payload(
        data_ui_checkpoint=data_ui,
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=True),
        execution_safety_harness=_safety(ok=True),
        pre_live_blocker_report=_report(ok=True),
        generated_at="2026-06-14T00:00:00Z",
    )

    assert payload["ok"] is False
    assert "data_ui_integrity_checkpoint_not_ready" in payload["blocked_by"]
    assert "service_not_stale" in payload["blocked_by"]
    assert payload["autotrade_resume_authorized"] is False
    assert payload["would_send_to_broker"] is False


def test_package_detects_missing_optional_execution_artifacts() -> None:
    payload = app.build_sr_fx_final_review_package_payload(
        data_ui_checkpoint=_data_ui_ok(),
        public_market_readiness=None,
        private_readiness=None,
        live_readiness_contract=None,
        execution_safety_harness=None,
        pre_live_blocker_report=None,
        generated_at="2026-06-14T00:00:00Z",
    )

    assert payload["ok"] is True
    assert payload["execution_boundary_clear"] is False
    assert "public_market_readiness_not_confirmed" in payload["execution_boundary_blocked_by"]
    assert "private_readiness_not_confirmed" in payload["execution_boundary_blocked_by"]
    assert "live_readiness_contract_not_ready" in payload["execution_boundary_blocked_by"]
    assert "execution_safety_harness_missing" in payload["execution_boundary_blocked_by"]
    assert "pre_live_blocker_report_missing" in payload["execution_boundary_blocked_by"]
    assert "runtime_control_not_confirmed" in payload["execution_boundary_blocked_by"]
    assert "runtime_control_snapshot_missing" in payload["execution_boundary_blocked_by"]
    assert payload["autotrade_resume_authorized"] is False


def test_main_writes_final_review_package(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    state = cfg.roots()["state"]
    paths = {
        "data_ui_checkpoint": state / "operator_ui" / "sr_fx_final_readiness_checkpoint.json",
        "public_market_readiness": state / "public" / "bitflyer_fx_public_market_readiness.json",
        "private_readiness": state / "private" / "bitflyer_fx_readiness.json",
        "live_readiness_contract": state / "private" / "bitflyer_fx_live_readiness_contract.json",
        "execution_safety_harness": state / "autotrade" / "sr_fx_execution_safety_harness.json",
        "pre_live_blocker_report": state / "autotrade" / "sr_fx_pre_live_blocker_report.json",
    }
    for path, payload in [
        (paths["data_ui_checkpoint"], _data_ui_ok()),
        (paths["public_market_readiness"], _public(ok=True)),
        (paths["private_readiness"], _private(clear=True)),
        (paths["live_readiness_contract"], _live(ready=False)),
        (paths["execution_safety_harness"], _safety(ok=False)),
        (paths["pre_live_blocker_report"], _report(ok=False)),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(app, "load_config", lambda: cfg)

    rc = app.main()
    out = state / "operator_ui" / "sr_fx_final_review_package.json"
    data = json.loads(out.read_text(encoding="utf-8"))

    assert rc == 0
    assert data["ok"] is True
    assert data["execution_boundary_clear"] is False
    assert data["paths"]["final_review_package"] == str(out)
    assert data["autotrade_resume_authorized"] is False
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False

def test_package_surfaces_runtime_control_visibility_and_blockers() -> None:
    payload = app.build_sr_fx_final_review_package_payload(
        data_ui_checkpoint=_data_ui_ok(),
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=True),
        execution_safety_harness=_safety(ok=True),
        pre_live_blocker_report=_report(ok=False, runtime_ok=False),
        generated_at="2026-06-14T00:00:00Z",
    )

    assert payload["execution_boundary_clear"] is False
    assert payload["checks"]["runtime_control_present"] is True
    assert payload["checks"]["runtime_control_clear"] is False
    assert payload["runtime_control"]["present"] is True
    assert payload["runtime_control"]["clear"] is False
    assert payload["runtime_control"]["heartbeat_fresh"] is False
    assert "runtime_control_not_clear" in payload["execution_boundary_blocked_by"]
    assert "heartbeat_stale" in payload["execution_boundary_blocked_by"]
    assert "open_incident_present" in payload["execution_boundary_blocked_by"]
    assert payload["autotrade_resume_authorized"] is False
    assert payload["would_send_to_broker"] is False


def test_package_can_show_runtime_control_clear_when_pre_live_report_clear() -> None:
    payload = app.build_sr_fx_final_review_package_payload(
        data_ui_checkpoint=_data_ui_ok(),
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=True),
        execution_safety_harness=_safety(ok=True),
        pre_live_blocker_report=_report(ok=True, runtime_ok=True),
        generated_at="2026-06-14T00:00:00Z",
    )

    assert payload["checks"]["runtime_control_present"] is True
    assert payload["checks"]["runtime_control_clear"] is True
    assert payload["runtime_control"]["clear"] is True
    assert "runtime_control_not_clear" not in payload["execution_boundary_blocked_by"]
    assert payload["would_send_to_broker"] is False

