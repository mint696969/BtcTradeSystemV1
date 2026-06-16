# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_runtime_control_snapshot_once.py
# desc: Tests for broker-free runtime_control one-shot snapshot writer.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_runtime_control_snapshot_once as app


def _command_row(command_id: str, command_type: str, *, accepted: bool = True, target: str | None = None) -> dict:
    return {
        "ledger_event": "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": [] if accepted else ["unit_blocked"],
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "unit",
            "requested_at": "2026-06-17T00:00:00Z",
            "current_mode": "ARMED_DRY_RUN",
            "target": target,
            "confirmation": True,
            "reason_codes": ["unit"],
            "note": "{}",
            "confirmation_required": False,
        },
    }


def test_snapshot_writer_creates_clear_runtime_control_snapshot(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_NOW", "2026-06-17T00:00:10Z")

    out = app.write_snapshot_from_environment(now="2026-06-17T00:00:10Z")
    path = Path(out["runtime_control_state_path"])
    data = json.loads(path.read_text(encoding="utf-8"))

    assert out["ok"] is True
    assert path.name == "runtime_control_state.json"
    assert path.parent.name == "diagnostics"
    assert data["ok"] is True
    assert data["heartbeat"]["fresh"] is True
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False
    assert data["mode_changed"] is False
    assert out["read_only"] is True
    assert out["would_send_to_broker"] is False
    assert out["mode_changed"] is False


def test_snapshot_writer_blocks_stale_heartbeat_and_open_incident(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_HEARTBEAT_OBSERVED_AT", "2026-06-17T00:00:00Z")
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_HEARTBEAT_MAX_AGE_SEC", "5")
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_INCIDENT_OPEN", "true")
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_INCIDENT_REASON", "unit_incident")

    out = app.write_snapshot_from_environment(now="2026-06-17T00:00:10Z")
    runtime = out["runtime_control"]

    assert out["ok"] is False
    assert "heartbeat_stale" in runtime["blocked_by"]
    assert "open_incident_present" in runtime["blocked_by"]
    assert runtime["incidents"][0]["reason"] == "unit_incident"
    assert runtime["read_only"] is True
    assert runtime["would_send_to_broker"] is False


def test_snapshot_writer_can_read_incidents_json(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    monkeypatch.setenv(
        "BTCTS_RUNTIME_CONTROL_INCIDENTS_JSON",
        json.dumps([
            {
                "incident_id": "inc_json_closed",
                "severity": "low",
                "status": "closed",
                "opened_at": "2026-06-17T00:00:00Z",
                "closed_at": "2026-06-17T00:00:01Z",
                "reason": "unit_closed",
            }
        ]),
    )

    out = app.write_snapshot_from_environment(now="2026-06-17T00:00:10Z")
    runtime = out["runtime_control"]

    assert out["ok"] is True
    assert runtime["incidents"][0]["open"] is False
    assert runtime["read_only"] is True
    assert runtime["would_send_to_broker"] is False


def test_snapshot_writer_uses_latest_accepted_halt_command_as_kill_switch(monkeypatch, tmp_path) -> None:
    hot = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(hot))
    ledger = hot / "autotrade" / "commands" / "command_requests.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        json.dumps(_command_row("cmd_unit_halt", "REQUEST_HALT_NEW", accepted=True, target="halt_new")) + "\n",
        encoding="utf-8",
    )

    out = app.write_snapshot_from_environment(now="2026-06-17T00:00:10Z")
    runtime = out["runtime_control"]

    assert out["ok"] is False
    assert runtime["kill_switch"]["active"] is True
    assert runtime["kill_switch"]["action"] == "HALT_NEW"
    assert runtime["kill_switch"]["command_id"] == "cmd_unit_halt"
    assert "kill_switch_active" in runtime["blocked_by"]
    assert "kill_switch_action:HALT_NEW" in runtime["blocked_by"]
    assert out["command_ledger_summary"]["latest_command_id"] == "cmd_unit_halt"
    assert out["would_send_to_broker"] is False


def test_snapshot_writer_explicit_env_overrides_command_ledger(monkeypatch, tmp_path) -> None:
    hot = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(hot))
    monkeypatch.setenv("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTIVE", "false")
    ledger = hot / "autotrade" / "commands" / "command_requests.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        json.dumps(_command_row("cmd_unit_halt", "REQUEST_HALT_AND_CANCEL", accepted=True, target="HALT_AND_CANCEL")) + "\n",
        encoding="utf-8",
    )

    out = app.write_snapshot_from_environment(now="2026-06-17T00:00:10Z")
    runtime = out["runtime_control"]

    assert out["ok"] is True
    assert runtime["kill_switch"]["active"] is False
    assert runtime["kill_switch"]["source"] == "env:BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTIVE"
    assert runtime["blocked_by"] == []
    assert runtime["would_send_to_broker"] is False
