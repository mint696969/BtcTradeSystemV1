# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_market_regime_latest_cards_hot_root_cp11.py
# desc: Verifies WarRoom market-regime latest_cards artifact resolves from D-hot root, not D-hot/data root.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
LAUNCH = REPO_ROOT / "tools/run_operator_ui_sr_fx_dhot.ps1"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import prediction_cards_view as view  # noqa: E402


def test_cp11_launch_sets_btcts_hot_root_for_prediction_artifacts() -> None:
    text = LAUNCH.read_text(encoding="utf-8-sig")
    assert '$env:BTCTS_HOT_ROOT = "D:\\btc_ts_hot"' in text
    assert '$env:BTCTS_DATA_ROOT = "D:\\btc_ts_hot\\data"' in text


def test_cp11_latest_cards_path_prefers_btcts_hot_root(monkeypatch, tmp_path: Path) -> None:
    hot = tmp_path / "hot"
    data = hot / "data"
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(hot))
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(data))
    path = view._market_regime_cards_artifact_path()
    assert path == hot / "prediction/market_regime/latest_cards.json"


def test_cp11_latest_cards_path_repairs_data_root_when_hot_root_missing(monkeypatch, tmp_path: Path) -> None:
    hot = tmp_path / "hot"
    data = hot / "data"
    monkeypatch.delenv("BTCTS_HOT_ROOT", raising=False)
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(data))
    path = view._market_regime_cards_artifact_path()
    assert path == hot / "prediction/market_regime/latest_cards.json"


def test_cp11_latest_cards_path_does_not_use_data_prediction_child(monkeypatch, tmp_path: Path) -> None:
    hot = tmp_path / "hot"
    data = hot / "data"
    monkeypatch.delenv("BTCTS_HOT_ROOT", raising=False)
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(data))
    path = view._market_regime_cards_artifact_path()
    assert "data/prediction" not in path.as_posix()
    assert "data\\prediction" not in str(path)
