# path: ./btcts_next/src/btcts/autotrade/tests/test_runtime_control_scaffold.py
# desc: Tests for broker-free runtime control snapshot scaffold: kill switch / incident / heartbeat.

from __future__ import annotations

import json

from btcts.autotrade.execution.runtime_control import (
    build_runtime_control_snapshot,
    build_runtime_heartbeat_state,
    build_runtime_incident_record,
    build_runtime_kill_switch_state,
    read_runtime_control_snapshot,
    runtime_control_state_path,
    write_runtime_control_snapshot,
)


def test_runtime_control_snapshot_is_ok_when_heartbeat_fresh_and_no_incident() -> None:
    heartbeat = build_runtime_heartbeat_state(
        observed_at="2026-06-17T00:00:05Z",
        now="2026-06-17T00:00:10Z",
        max_age_sec=10,
    )

    snapshot = build_runtime_control_snapshot(heartbeat=heartbeat)
    data = snapshot.to_dict()

    assert snapshot.ok is True
    assert snapshot.blocked_by == ()
    assert data["heartbeat"]["fresh"] is True
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False
    assert data["mode_changed"] is False


def test_runtime_control_snapshot_blocks_stale_heartbeat_and_kill_switch() -> None:
    heartbeat = build_runtime_heartbeat_state(
        observed_at="2026-06-17T00:00:00Z",
        now="2026-06-17T00:00:30Z",
        max_age_sec=10,
    )
    kill = build_runtime_kill_switch_state(active=True, action="HALT_AND_CANCEL", reason="unit")

    snapshot = build_runtime_control_snapshot(kill_switch=kill, heartbeat=heartbeat)

    assert snapshot.ok is False
    assert "heartbeat_stale" in snapshot.blocked_by
    assert "kill_switch_active" in snapshot.blocked_by
    assert "kill_switch_action:HALT_AND_CANCEL" in snapshot.blocked_by
    assert snapshot.read_only is True
    assert snapshot.would_send_to_broker is False


def test_emergency_flatten_is_blocked_as_separate_human_protocol() -> None:
    kill = build_runtime_kill_switch_state(active=True, action="REQUEST_EMERGENCY_FLATTEN")
    heartbeat = build_runtime_heartbeat_state(
        observed_at="2026-06-17T00:00:09Z",
        now="2026-06-17T00:00:10Z",
    )

    snapshot = build_runtime_control_snapshot(kill_switch=kill, heartbeat=heartbeat)

    assert snapshot.kill_switch.action == "EMERGENCY_FLATTEN"
    assert "kill_switch_active" in snapshot.blocked_by
    assert "emergency_flatten_requires_separate_human_protocol" in snapshot.blocked_by
    assert snapshot.would_send_to_broker is False


def test_open_incident_blocks_runtime_control_snapshot() -> None:
    incident = build_runtime_incident_record(
        incident_id="inc_unit_001",
        severity="high",
        status="open",
        opened_at="2026-06-17T00:00:00Z",
        reason="unit_open_incident",
    )
    heartbeat = build_runtime_heartbeat_state(
        observed_at="2026-06-17T00:00:09Z",
        now="2026-06-17T00:00:10Z",
    )

    snapshot = build_runtime_control_snapshot(heartbeat=heartbeat, incidents=(incident,))

    assert snapshot.ok is False
    assert "open_incident_present" in snapshot.blocked_by
    assert snapshot.incidents[0].open is True
    assert snapshot.incidents[0].to_dict()["open"] is True


def test_runtime_control_snapshot_persists_to_hot_runtime_diagnostics(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    heartbeat = build_runtime_heartbeat_state(
        observed_at="2026-06-17T00:00:09Z",
        now="2026-06-17T00:00:10Z",
    )
    snapshot = build_runtime_control_snapshot(heartbeat=heartbeat)

    path = write_runtime_control_snapshot(snapshot)
    loaded = read_runtime_control_snapshot()
    explicit_path = runtime_control_state_path(ensure=False)

    assert path == explicit_path
    assert str(tmp_path / "btc_ts_hot") in str(path)
    assert path.name == "runtime_control_state.json"
    assert path.parent.name == "diagnostics"
    assert loaded["exists"] is True
    assert loaded["ok"] is True
    assert loaded["read_only"] is True
    assert loaded["would_send_to_broker"] is False
    assert loaded["mode_changed"] is False
    assert json.loads(path.read_text(encoding="utf-8"))["contract_version"] == "autotrade_runtime_control_snapshot.v1"


def test_missing_runtime_control_snapshot_is_fail_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))

    loaded = read_runtime_control_snapshot()

    assert loaded["exists"] is False
    assert "runtime_control_snapshot_missing" in loaded["blocked_by"]
    assert loaded["read_only"] is True
    assert loaded["would_send_to_broker"] is False
    assert loaded["mode_changed"] is False
