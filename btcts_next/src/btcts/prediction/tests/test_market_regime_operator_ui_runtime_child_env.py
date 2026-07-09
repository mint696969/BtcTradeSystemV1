# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_operator_ui_runtime_child_env.py
# desc: Verifies detached MarketRegime producer child env imports current repo source before any inherited PYTHONPATH entries.

from __future__ import annotations

import os
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import operator_ui_runtime as runtime  # noqa: E402


def test_market_regime_child_env_prepends_repo_src_to_inherited_pythonpath(monkeypatch, tmp_path: Path) -> None:
    inherited = "C:/some/old/site-packages"
    monkeypatch.setenv("PYTHONPATH", inherited)
    env = runtime._child_env(tmp_path)
    parts = [part for part in env["PYTHONPATH"].split(os.pathsep) if part]
    expected_src = str(runtime._repo_root() / "btcts_next" / "src")
    assert parts[0] == expected_src
    assert inherited in parts
    assert env["BTCTS_HOT_ROOT"] == str(tmp_path)
    assert env["BTCTS_DATA_ROOT"] == str(tmp_path / "data")
    assert env["BTC_TS_DATA_DIR"] == str(tmp_path / "data")


def test_market_regime_child_env_does_not_duplicate_repo_src(monkeypatch, tmp_path: Path) -> None:
    expected_src = str(runtime._repo_root() / "btcts_next" / "src")
    inherited = os.pathsep.join(["C:/old", expected_src])
    monkeypatch.setenv("PYTHONPATH", inherited)
    env = runtime._child_env(tmp_path)
    parts = [part for part in env["PYTHONPATH"].split(os.pathsep) if part]
    assert parts[0] == expected_src
    assert parts.count(expected_src) == 1
