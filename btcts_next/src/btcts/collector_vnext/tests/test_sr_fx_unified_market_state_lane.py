# path: ./btcts_next/src/btcts/collector_vnext/tests/test_sr_fx_unified_market_state_lane.py
# desc: Pytest-free tests for optional SR-FX Unified daemon market_state lane and launcher identity.

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


def _set_env(root: Path, *, enabled: bool) -> None:
    os.environ["BTC_TS_DATA_DIR"] = str(root / "data")
    os.environ["BTC_TS_LOGS_DIR"] = str(root / "logs")
    os.environ["BTCTS_STATE_ROOT"] = str(root / "state")
    os.environ["BTCTS_DATA_ROOT"] = str(root / "data")
    os.environ["BTCTS_LOGS_ROOT"] = str(root / "logs")
    os.environ["BTCTS_MARKET"] = "fx"
    os.environ["BTCTS_SYMBOL"] = "FX_BTC_JPY"
    os.environ["BTCTS_INSTRUMENT_ID"] = "bitflyer.fx.FX_BTC_JPY"
    os.environ["BTCTS_EXECUTION_PRODUCT_CODE"] = "FX_BTC_JPY"
    os.environ["BTCTS_EXECUTION_MARKET_UID"] = "bitflyer.fx.FX_BTC_JPY"
    os.environ["BTCTS_EXECUTION_MARKET_TYPE"] = "fx"
    os.environ["BTCTS_MARKET_ENGINE_EXCHANGE"] = "bitflyer"
    os.environ["BTCTS_MARKET_ENGINE_SYMBOL"] = "FX_BTC_JPY"
    os.environ["BTCTS_MARKET_ENGINE_INSTRUMENT_ID"] = "bitflyer.fx.FX_BTC_JPY"
    os.environ["BTCTS_MARKET_ENGINE_MARKET_UID"] = "bitflyer.fx.FX_BTC_JPY"
    os.environ["BTCTS_MARKET_ENGINE_PROFILE"] = "bitflyer"
    os.environ["BTCTS_MARKET_ENGINE_WRITE_MARKET_STATE"] = "true"
    os.environ["BTCTS_UNIFIED_MARKET_STATE_ENABLED"] = "true" if enabled else "false"


def _snapshot_event() -> dict:
    return {
        "schema_version": "collector.vnext.canonical",
        "record_type": "market.orderbook.snapshot",
        "exchange": "bitflyer",
        "market": "fx",
        "symbol": "FX_BTC_JPY",
        "instrument_id": "bitflyer.fx.FX_BTC_JPY",
        "stream_session_id": "unit:fx_board_ws",
        "source_event_id": "snap-1",
        "sequence_id": 1,
        "collector_ts": "2026-06-14T00:00:00Z",
        "exchange_ts": "2026-06-14T00:00:00Z",
        "payload": {
            "event_type": "snapshot",
            "continuity_state": "continuous",
            "stream_event_no": 1,
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "bids": [{"price": 100.0, "size": 1.0}],
            "asks": [{"price": 101.0, "size": 2.0}],
        },
    }


def _delta_event() -> dict:
    event = _snapshot_event()
    event["record_type"] = "market.orderbook.diff"
    event["source_event_id"] = "delta-2"
    event["sequence_id"] = 2
    event["collector_ts"] = "2026-06-14T00:00:01Z"
    event["exchange_ts"] = "2026-06-14T00:00:01Z"
    event["payload"] = {
        "event_type": "delta",
        "continuity_state": "continuous",
        "stream_event_no": 2,
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "bids": [{"price": 100.5, "size": 0.7}],
        "asks": [],
    }
    return event


def _run_disabled_case(root: Path) -> None:
    from btcts.collector_vnext.unified_market_state_lane import UnifiedMarketStateLane

    _set_env(root, enabled=False)
    lane = UnifiedMarketStateLane()
    snap = lane.step(_snapshot_event())

    assert snap["enabled"] is False, snap
    assert snap["lane_state"] == "disabled", snap
    assert not (root / "data" / "market_state").exists()


def _run_enabled_case(root: Path) -> dict:
    from btcts.collector_vnext.config import load_config
    from btcts.collector_vnext.unified_market_state_lane import UnifiedMarketStateLane

    _set_env(root, enabled=True)
    cfg = load_config()
    assert str(cfg.data_root) == str(root / "data"), cfg.data_root
    assert str(cfg.logs_root) == str(root / "logs"), cfg.logs_root
    assert str(cfg.state_root) == str(root / "state"), cfg.state_root
    assert cfg.symbol == "FX_BTC_JPY", cfg.symbol
    assert cfg.instrument_id == "bitflyer.fx.FX_BTC_JPY", cfg.instrument_id
    assert cfg.execution_market.market_uid == "bitflyer.fx.FX_BTC_JPY", cfg.execution_market

    lane = UnifiedMarketStateLane()
    lane.step(_snapshot_event())
    snap = lane.step(_delta_event())

    assert snap["enabled"] is True, snap
    assert snap["lane_state"] == "live", snap
    assert snap["last_market_uid"] == "bitflyer.fx.FX_BTC_JPY", snap
    assert snap["last_symbol_raw"] == "FX_BTC_JPY", snap
    assert snap["last_best_bid"] == 100.5, snap
    assert snap["last_best_ask"] == 101.0, snap
    assert snap["last_output_path"] is not None, snap
    assert "symbol=FX_BTC_JPY" in snap["last_output_path"], snap
    assert "symbol=BTC_JPY" not in snap["last_output_path"], snap
    assert Path(snap["last_output_path"]).exists(), snap

    status_path = root / "state" / "collector_vnext" / "unified_market_state_status.json"
    assert status_path.exists(), status_path
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert status["read_only"] is True, status
    assert status["would_send_to_broker"] is False, status
    return snap


def _run_launcher_case() -> None:
    script = Path("tools/run_collector_vnext_sr_fx_unified_watchdog.ps1").read_text(encoding="utf-8")

    assert 'BTCTS_SYMBOL = "FX_BTC_JPY"' in script
    assert 'BTCTS_INSTRUMENT_ID = "bitflyer.fx.FX_BTC_JPY"' in script
    assert 'BTCTS_MARKET_ENGINE_SYMBOL = "FX_BTC_JPY"' in script
    assert 'BTCTS_MARKET_ENGINE_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"' in script
    assert 'BTCTS_UNIFIED_MARKET_STATE_ENABLED = "true"' in script
    assert 'BTC_TS_DATA_DIR = "D:\\btc_ts_hot\\data"' in script
    assert "btcts.collector_vnext.unified_watchdog" in script
    assert "run_g8_d_hot_fx_live_refresh_loop" not in script


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="btcts_g8_test_"))
    try:
        _run_disabled_case(root)
        snap = _run_enabled_case(root)
        _run_launcher_case()
        print(json.dumps({
            "ok": True,
            "latest_snapshot": snap,
            "read_only": True,
            "would_send_to_broker": False,
        }, ensure_ascii=False, indent=2))
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
