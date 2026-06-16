# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_bounded_observer_wiring.py
# desc: Guards runtime parameter bundle pass-through for bounded shadow and observer cycle entrypoints.

from __future__ import annotations

import sys
from pathlib import Path

from btcts.apps import autotrade_observer_bounded, autotrade_shadow_bounded
from btcts.autotrade import observer_cycle


class _FakeBoundedResult:
    def __init__(self, completed_cycles: int) -> None:
        self.completed_cycles = completed_cycles

    def to_dict(self):
        return {
            "completed_cycles": self.completed_cycles,
            "would_send_to_broker": False,
            "blocked_by": [],
        }


class _FakeGate:
    allow_shadow_decision_append = True
    allow_forecast_outcome_resolution = True
    blocked_by = ()

    def to_dict(self):
        return {
            "allow_shadow_decision_append": True,
            "allow_forecast_outcome_resolution": True,
            "blocked_by": [],
        }


class _FakeShadow:
    appended = False
    blocked_by = ()
    would_send_to_broker = False

    class _Result:
        snapshot_id = "snap_obs"

    result = _Result()

    def to_dict(self):
        return {
            "appended": False,
            "blocked_by": [],
            "would_send_to_broker": False,
            "result": {"snapshot_id": "snap_obs"},
        }


class _FakeForecastResolution:
    appended_count = 0
    blocked_by = ()

    def to_dict(self):
        return {
            "appended_count": 0,
            "blocked_by": [],
            "would_send_to_broker": False,
        }


def test_shadow_bounded_cli_passes_runtime_bundle_args(monkeypatch, tmp_path, capsys) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    calls = {}

    def fake_run_shadow_cycle_bounded(**kwargs):
        calls.update(kwargs)
        return _FakeBoundedResult(completed_cycles=2)

    monkeypatch.setattr(autotrade_shadow_bounded, "run_shadow_cycle_bounded", fake_run_shadow_cycle_bounded)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "autotrade_shadow_bounded.py",
            "--max-cycles",
            "2",
            "--no-persist",
            "--use-runtime-parameter-bundle",
            "--parameter-bundle-stage",
            "paper",
            "--parameter-bundle-id",
            "pb_shadow_bounded",
            "--parameter-bundle-registry-path",
            str(registry_path),
        ],
    )

    exit_code = autotrade_shadow_bounded.main()

    assert exit_code == 0
    assert calls["load_runtime_parameter_bundle"] is True
    assert calls["parameter_bundle_stage"] == "paper"
    assert calls["parameter_bundle_id"] == "pb_shadow_bounded"
    assert calls["parameter_bundle_registry_path"] == registry_path
    assert calls["persist"] is False
    assert calls["max_cycles"] == 2
    assert "would_send_to_broker" in capsys.readouterr().out


def test_observer_cycle_passes_runtime_bundle_args_to_shadow_cycle(monkeypatch, tmp_path) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    calls = {}

    def fake_run_shadow_cycle_once(**kwargs):
        calls.update(kwargs)
        return _FakeShadow()

    monkeypatch.setattr(observer_cycle, "build_mode_runtime_gate", lambda: _FakeGate())
    monkeypatch.setattr(observer_cycle, "run_shadow_cycle_once", fake_run_shadow_cycle_once)
    monkeypatch.setattr(observer_cycle, "resolve_due_shadow_forecast_outcomes", lambda **kwargs: _FakeForecastResolution())

    result = observer_cycle.run_observer_cycle_once(
        load_runtime_parameter_bundle=True,
        parameter_bundle_stage="live",
        parameter_bundle_id="pb_observer_once",
        parameter_bundle_registry_path=registry_path,
        persist=False,
    )

    assert result.snapshot_id == "snap_obs"
    assert calls["load_runtime_parameter_bundle"] is True
    assert calls["parameter_bundle_stage"] == "live"
    assert calls["parameter_bundle_id"] == "pb_observer_once"
    assert calls["parameter_bundle_registry_path"] == registry_path
    assert calls["persist"] is False
    assert result.would_send_to_broker is False


def test_observer_bounded_cli_passes_runtime_bundle_args(monkeypatch, tmp_path, capsys) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    calls = {}

    def fake_run_observer_cycle_bounded(**kwargs):
        calls.update(kwargs)
        return _FakeBoundedResult(completed_cycles=3)

    monkeypatch.setattr(autotrade_observer_bounded, "run_observer_cycle_bounded", fake_run_observer_cycle_bounded)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "autotrade_observer_bounded.py",
            "--max-cycles",
            "3",
            "--no-persist",
            "--no-run-record",
            "--use-runtime-parameter-bundle",
            "--parameter-bundle-stage",
            "last_known_good",
            "--parameter-bundle-id",
            "pb_observer_bounded",
            "--parameter-bundle-registry-path",
            str(registry_path),
        ],
    )

    exit_code = autotrade_observer_bounded.main()

    assert exit_code == 0
    assert calls["load_runtime_parameter_bundle"] is True
    assert calls["parameter_bundle_stage"] == "last_known_good"
    assert calls["parameter_bundle_id"] == "pb_observer_bounded"
    assert calls["parameter_bundle_registry_path"] == registry_path
    assert calls["persist"] is False
    assert calls["persist_run_record"] is False
    assert calls["max_cycles"] == 3
    assert "would_send_to_broker" in capsys.readouterr().out
