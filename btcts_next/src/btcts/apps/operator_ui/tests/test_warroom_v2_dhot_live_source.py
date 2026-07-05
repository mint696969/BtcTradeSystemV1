# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_dhot_live_source.py
# desc: Verifies WarRoom v2 default realtime source reads D-hot unified market state instead of opening an extra bitFlyer provider connection.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
LAUNCH = REPO_ROOT / "tools/run_operator_ui_sr_fx_dhot.ps1"
RT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/rt_live_receiver_bridge.py"
ENV = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/runtime_env.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_DHOT_LIVE_SOURCE_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.rt_live_receiver_bridge import _DhotUnifiedMarketStateConnection  # noqa: E402


def test_dhot_unified_market_state_connection_maps_status_file_to_push_messages(tmp_path: Path) -> None:
    status_dir = tmp_path / "collector_vnext"
    status_dir.mkdir(parents=True)
    (status_dir / "unified_market_state_status.json").write_text(
        json.dumps(
            {
                "lane_state": "live",
                "last_event_ts": "2026-07-05T03:44:18Z",
                "last_best_bid": 10104241.0,
                "last_best_ask": 10105078.0,
                "last_spread": 837.0,
                "last_symbol_raw": "FX_BTC_JPY",
                "last_market_uid": "bitflyer.fx.FX_BTC_JPY",
                "step_count": 2396080,
                "last_error": None,
            }
        ),
        encoding="utf-8",
    )
    conn = _DhotUnifiedMarketStateConnection("unified_market_state", {"state_root": str(tmp_path), "poll_interval_sec": 0})
    payload = conn.recv()
    messages = payload["messages"]
    assert {msg["topic_key"] for msg in messages} >= {"market.depth", "market.spread", "market.liquidity", "receiver.lifecycle", "warroom.summary", "warroom.alerts"}
    depth = next(msg for msg in messages if msg["topic_key"] == "market.depth")
    assert depth["value"]["best_bid"] == 10104241.0
    assert depth["value"]["best_ask"] == 10105078.0
    spread = next(msg for msg in messages if msg["topic_key"] == "market.spread")
    assert spread["value"]["spread"] == 837.0
    assert spread["value"]["spread_bps"] > 0


def test_launch_defaults_to_dhot_source() -> None:
    launch = LAUNCH.read_text(encoding="utf-8-sig")
    assert "dhot://unified_market_state" in launch
    assert "dhot_unified_market_state_provider" in launch
    assert "WARROOM_PUSH_WIDGET_WS_URL" in launch
    assert "WARROOM_PUSH_WIDGET_SOURCE" in launch
    rt_text = RT.read_text(encoding="utf-8-sig")
    assert "class _DhotUnifiedMarketStateConnection" in rt_text
    assert "dhot://" in rt_text
    env_text = ENV.read_text(encoding="utf-8-sig")
    assert "state_root" in env_text
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_dhot_live_source_default=true" in doc
