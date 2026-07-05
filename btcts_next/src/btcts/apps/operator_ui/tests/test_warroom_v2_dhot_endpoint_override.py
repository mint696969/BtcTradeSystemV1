# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_dhot_endpoint_override.py
# desc: Verifies WarRoom v2 D-hot source wins over stale bitFlyer env/session_state during default realtime observation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
LAUNCH = REPO_ROOT / "tools/run_operator_ui_sr_fx_dhot.ps1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_DHOT_ENDPOINT_OVERRIDE_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import runtime_env  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.rt_live_receiver_bridge import WARROOM_RT_LIVE_ENDPOINT_STATE_KEY  # noqa: E402
from btcts.apps.operator_ui.views.warroom_v2_page import _apply_runtime_endpoint_to_session_state  # noqa: E402


def test_default_realtime_observation_prefers_dhot_over_stale_bitflyer_env(monkeypatch) -> None:
    monkeypatch.setenv("WARROOM_PUSH_WIDGET_REALTIME_OBSERVATION_DEFAULT", "true")
    monkeypatch.setenv("WARROOM_PUSH_WIDGET_WS_URL", "bitflyer://FX_BTC_JPY")
    monkeypatch.setenv("WARROOM_PUSH_WIDGET_SOURCE", "bitflyer_collector_provider")
    monkeypatch.setenv("BTCTS_STATE_ROOT", "D:/btc_ts_hot/state")
    assert runtime_env.endpoint_from_env() == "dhot://unified_market_state"
    assert runtime_env.runtime_config_from_env()["source"] == "dhot_unified_market_state_provider"


def test_page_endpoint_apply_overwrites_stale_session_state() -> None:
    state = {WARROOM_RT_LIVE_ENDPOINT_STATE_KEY: "bitflyer://FX_BTC_JPY", "warroom_v2_rt_display_packet_source": "waiting"}
    changed = _apply_runtime_endpoint_to_session_state(state, "dhot://unified_market_state")
    assert changed is True
    assert state[WARROOM_RT_LIVE_ENDPOINT_STATE_KEY] == "dhot://unified_market_state"
    assert "warroom_v2_rt_display_packet_source" not in state


def test_launch_script_forces_dhot_defaults_and_doc_markers() -> None:
    launch = LAUNCH.read_text(encoding="utf-8-sig")
    assert '$env:WARROOM_PUSH_WIDGET_WS_URL = "dhot://unified_market_state"' in launch
    assert '$env:WARROOM_PUSH_WIDGET_SOURCE = "dhot_unified_market_state_provider"' in launch
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "_apply_runtime_endpoint_to_session_state" in page
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "stale_bitflyer_endpoint_overridden=true" in doc
    assert "dhot_endpoint_forced_by_default_launch=true" in doc
