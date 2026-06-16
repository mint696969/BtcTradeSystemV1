# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_readiness_cli.py
# desc: Guards CLI controls for parameter bundle runtime readiness enforcement.

from __future__ import annotations

import json
import sys

from btcts.apps import autotrade_readiness_once


class _FakeReadinessResult:
    def __init__(self, *, ready: bool = True) -> None:
        self.ready = ready

    def to_dict(self):
        return {
            "ready": self.ready,
            "would_send_to_broker": False,
            "parameter_bundle_runtime": {
                "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
            },
        }


def _stdout_json(capsys):
    return json.loads(capsys.readouterr().out)


def test_readiness_cli_enforces_live_parameter_bundle_runtime_by_default(monkeypatch, capsys) -> None:
    calls = {}

    def fake_evaluate_autotrade_live_readiness(**kwargs):
        calls.update(kwargs)
        return _FakeReadinessResult(ready=True)

    monkeypatch.setattr(
        autotrade_readiness_once,
        "evaluate_autotrade_live_readiness",
        fake_evaluate_autotrade_live_readiness,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "autotrade_readiness_once.py",
            "--current-mode",
            "ARMED_DRY_RUN",
            "--target-mode",
            "LIVE_MIN_SIZE",
            "--human-confirmed",
            "--allow-warnings",
        ],
    )

    exit_code = autotrade_readiness_once.main()
    data = _stdout_json(capsys)

    assert exit_code == 0
    assert calls["enforce_parameter_bundle_runtime"] is True
    assert calls["required_parameter_bundle_stage"] == "live"
    assert calls["human_confirmed"] is True
    assert calls["allow_warnings"] is True
    assert data["would_send_to_broker"] is False


def test_readiness_cli_can_disable_parameter_bundle_runtime_guard_explicitly(monkeypatch, capsys) -> None:
    calls = {}

    def fake_evaluate_autotrade_live_readiness(**kwargs):
        calls.update(kwargs)
        return _FakeReadinessResult(ready=True)

    monkeypatch.setattr(
        autotrade_readiness_once,
        "evaluate_autotrade_live_readiness",
        fake_evaluate_autotrade_live_readiness,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "autotrade_readiness_once.py",
            "--current-mode",
            "SHADOW",
            "--target-mode",
            "PAPER_OR_REPLAY",
            "--disable-parameter-bundle-runtime-check",
            "--required-parameter-bundle-stage",
            "shadow",
        ],
    )

    exit_code = autotrade_readiness_once.main()
    data = _stdout_json(capsys)

    assert exit_code == 0
    assert calls["enforce_parameter_bundle_runtime"] is False
    assert calls["required_parameter_bundle_stage"] == "shadow"
    assert calls["current_mode"] == "SHADOW"
    assert calls["target_mode"] == "PAPER_OR_REPLAY"
    assert data["parameter_bundle_runtime"]["schema_version"] == "autotrade_parameter_bundle_runtime_status.v1"
