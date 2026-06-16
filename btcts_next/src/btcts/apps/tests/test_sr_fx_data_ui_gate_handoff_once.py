# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_data_ui_gate_handoff_once.py
# desc: SR-FX Data/UI Integrity Gate handoff tests. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_data_ui_gate_handoff_once as app


class DummyConfig:
    def __init__(self, root: Path) -> None:
        self.root = root

    def roots(self):
        return {"state": self.root / "state"}


def _package_ok_blocked() -> dict:
    return {
        "ok": True,
        "data_ui_integrity_ready_for_final_human_review": True,
        "execution_boundary_clear": False,
        "execution_boundary_blocked_by": [
            "private_readiness_not_confirmed",
            "account_not_clear_for_new_auto_entry",
            "reconciliation_not_clean",
            "order_sender_not_implemented",
            "observer_run_missing",
            "pre_live_blocker_report_not_clear",
            "runtime_control_not_clear",
            "heartbeat_stale",
            "open_incident_present",
        ],
        "decision": "data_ui_ready_but_execution_safety_boundaries_remain_separate",
        "package_version": "sr_fx_final_review_package.v1",
        "generated_at": "2026-06-14T00:00:00Z",
        "checks": {
            "identity_ok": True,
            "public_market_ready": True,
            "private_readiness_clear": False,
            "live_readiness_contract_ready": False,
            "execution_safety_harness_ready": False,
            "pre_live_blocker_report_clear": False,
            "runtime_control_clear": False,
        },
        "runtime_control": {
            "present": True,
            "clear": False,
            "source": "pre_live_blocker_report.runtime_control",
            "path": "D:/btc_ts_hot/state/autotrade/diagnostics/runtime_control_state.json",
            "blocked_by": ["heartbeat_stale", "open_incident_present"],
            "kill_switch_active": False,
            "heartbeat_fresh": False,
            "incident_count": 1,
        },
        "summary": {
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "data_ui_primary_lineage": "continuous_ws",
            "data_ui_service_stale": False,
            "public_market_ready": True,
        },
        "autotrade_resume_authorized": False,
        "final_human_review_required": True,
        "mode_changed": False,
        "read_only": True,
        "would_send_to_broker": False,
    }


def test_handoff_marks_data_ui_complete_but_keeps_execution_blocked() -> None:
    payload = app.build_sr_fx_data_ui_gate_handoff_payload(
        final_review_package=_package_ok_blocked(),
        generated_at="2026-06-14T00:01:00Z",
    )

    assert payload["ok"] is True
    assert payload["handoff_complete"] is True
    assert payload["decision"] == "data_ui_integrity_gate_complete_execution_boundary_blocked"
    assert payload["completed_scope"]["primary_lineage"] == "continuous_ws"
    assert payload["execution_boundary"]["clear"] is False
    assert "account_not_clear_for_new_auto_entry" in payload["execution_boundary"]["blocked_by"]
    assert payload["execution_boundary"]["runtime_control"]["present"] is True
    assert payload["execution_boundary"]["runtime_control"]["clear"] is False
    assert "heartbeat_stale" in payload["execution_boundary"]["runtime_control"]["blocked_by"]
    assert "resolve_or_explicitly_accept_existing_fx_positions_and_open_orders" in payload["execution_boundary"]["next_actions"]
    assert "clear_runtime_control_heartbeat_kill_switch_incident_blockers" in payload["execution_boundary"]["next_actions"]
    assert "resolve_or_explicitly_close_runtime_incident_before_live_review" in payload["execution_boundary"]["next_actions"]
    assert "require_final_human_review_before_any_mode_change" in payload["execution_boundary"]["next_actions"]
    assert payload["autotrade_resume_authorized"] is False
    assert payload["final_human_review_required"] is True
    assert payload["mode_changed"] is False
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_handoff_blocks_when_final_package_not_data_ui_ready() -> None:
    package = _package_ok_blocked()
    package["ok"] = False
    package["data_ui_integrity_ready_for_final_human_review"] = False
    package["blocked_by"] = ["data_ui_integrity_checkpoint_not_ready"]

    payload = app.build_sr_fx_data_ui_gate_handoff_payload(
        final_review_package=package,
        generated_at="2026-06-14T00:01:00Z",
    )

    assert payload["ok"] is False
    assert payload["handoff_complete"] is False
    assert "final_review_package_not_data_ui_ready" in payload["blocked_by"]
    assert "data_ui_integrity_checkpoint_not_ready" in payload["blocked_by"]
    assert payload["autotrade_resume_authorized"] is False
    assert payload["would_send_to_broker"] is False


def test_main_writes_handoff_json(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    state = cfg.roots()["state"]
    package_path = state / "operator_ui" / "sr_fx_final_review_package.json"
    handoff_path = state / "operator_ui" / "sr_fx_data_ui_gate_handoff.json"
    package_path.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(json.dumps(_package_ok_blocked()), encoding="utf-8")
    monkeypatch.setattr(app, "load_config", lambda: cfg)

    rc = app.main()
    data = json.loads(handoff_path.read_text(encoding="utf-8"))

    assert rc == 0
    assert data["ok"] is True
    assert data["paths"]["final_review_package"] == str(package_path)
    assert data["paths"]["handoff"] == str(handoff_path)
    assert data["safety_lock"]["autotrade_resume_authorized"] is False
    assert data["autotrade_resume_authorized"] is False
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False
