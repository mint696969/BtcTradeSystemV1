# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_operator_ui_loop_control_cp15b.py
# desc: Tests Operator UI wiring for MarketRegime controlled producer loop start/stop/restart. No real subprocess required; no broker, AutoTrade, or Collector button linkage.

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
COLLECTOR_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py"

from btcts.prediction.market_regime import operator_ui_runtime as runtime  # noqa: E402


class _FakePopen:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pid = 424242


def test_cp15b_loop_runtime_paths_and_snapshot_are_safe(tmp_path: Path) -> None:
    snapshot = runtime.market_regime_producer_loop_runtime_snapshot(tmp_path)
    assert snapshot["active"] is False
    assert snapshot["mode"] == "STOPPED"
    assert snapshot["producer_loop_enabled"] is False
    assert snapshot["broker_private_api_allowed"] is False
    assert snapshot["autotrade_trigger_allowed"] is False
    assert snapshot["loop_control_path"].endswith("state\\market_regime_inference\\control.json") or snapshot["loop_control_path"].endswith("state/market_regime_inference/control.json")


def test_cp15b_start_detached_writes_lock_and_uses_explicit_loop_ack(monkeypatch, tmp_path: Path) -> None:
    calls = []

    def fake_popen(*args, **kwargs):
        calls.append((args, kwargs))
        return _FakePopen(*args, **kwargs)

    monkeypatch.setattr(runtime.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(runtime, "_pid_active", lambda _pid: False)
    ok, msg, already = runtime.start_market_regime_producer_loop_detached(tmp_path, interval_sec=1)
    assert ok is True
    assert already is False
    assert "pid=424242" in msg
    paths = runtime.market_regime_producer_loop_runtime_paths(tmp_path)
    lock = json.loads(paths["loop_lock"].read_text(encoding="utf-8"))
    status = json.loads(paths["loop_status"].read_text(encoding="utf-8"))
    assert lock["pid"] == 424242
    assert "--once-loop" in lock["command_args"]
    assert "btcts.prediction.market_regime.producer_loop" in lock["command_args"]
    assert status["mode"] == "STARTING"
    assert status["broker_private_api_allowed"] is False
    assert status["autotrade_trigger_allowed"] is False
    assert calls


def test_cp15b_start_detached_prevents_multi_start(monkeypatch, tmp_path: Path) -> None:
    paths = runtime.market_regime_producer_loop_runtime_paths(tmp_path)
    runtime._write_json(paths["loop_lock"], {"pid": 12345})
    monkeypatch.setattr(runtime, "_pid_active", lambda _pid: True)
    ok, msg, already = runtime.start_market_regime_producer_loop_detached(tmp_path)
    assert ok is True
    assert already is True
    assert "already running" in msg


def test_cp15b_safe_stop_and_restart_request_write_control(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runtime, "_pid_active", lambda _pid: True)
    paths = runtime.market_regime_producer_loop_runtime_paths(tmp_path)
    runtime._write_json(paths["loop_lock"], {"pid": 12345})
    ok, msg = runtime.request_market_regime_producer_loop_safe_stop(tmp_path)
    assert ok is True
    assert "safe_stop" in msg
    control = json.loads(paths["loop_control"].read_text(encoding="utf-8"))
    assert control["action"] == "safe_stop"
    assert control["safety"]["broker_private_api_allowed"] is False
    ok, msg = runtime.request_market_regime_producer_loop_restart(tmp_path)
    assert ok is True
    assert "restart" in msg
    control = json.loads(paths["loop_control"].read_text(encoding="utf-8"))
    assert control["action"] == "restart"


def test_cp15b_collector_page_contains_loop_control_buttons() -> None:
    text = COLLECTOR_PAGE.read_text(encoding="utf-8")
    required = [
        "Start Loop",
        "Safe Stop",
        "Restart Request",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "request_market_regime_producer_loop_restart",
        "market_regime_producer_loop_runtime_snapshot",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "Collector Start button linked to MarketRegime",
    ]
    assert [token for token in forbidden if token in text] == []
