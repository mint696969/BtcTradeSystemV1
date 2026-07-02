# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_auto_refresh_staging_q29t.py
# desc: PS-Q29T guards for WarRoom v2 browser-timer auto refresh staging.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.auto_refresh_control import build_warroom_v2_auto_refresh_control_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import build_warroom_v2_shell_preview_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CONTROL = RENDERER_DIR / "auto_refresh_control.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29T_WARROOM_V2_AUTO_REFRESH_STAGING_2026-07-02.md"


def test_q29t_auto_refresh_packet_is_controlled_and_non_push_transport() -> None:
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True, interval_ms=250)
    assert packet["transport_kind"] == "browser_timer_polling"
    assert packet["auto_refresh_available"] is True
    assert packet["auto_refresh_enabled"] is True
    assert packet["auto_refresh_enabled_default"] is False
    assert packet["interval_ms"] == 1000
    assert packet["refresh_targets"] == ["market_snapshot_strip", "prediction_cards", "chart_review_panel"]
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q29t_shell_packet_mounts_auto_refresh_without_changing_default_data_contract() -> None:
    packet = build_warroom_v2_shell_preview_panel_packet()
    assert packet["auto_refresh_control_below_top_bar"] is True
    assert packet["auto_refresh_control"]["auto_refresh_available"] is True
    assert packet["auto_refresh_control"]["auto_refresh_enabled"] is False
    assert packet["data_connected"] is False
    assert packet["push_connected"] is False
    assert packet["runtime_connected"] is False


def test_q29t_render_order_is_top_refresh_snapshot_cards_chart() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    calls = {
        "top": text.index("    render_warroom_v2_top_bar("),
        "refresh": text.index("    packet[\"auto_refresh_control\"] = render_warroom_v2_auto_refresh_control()"),
        "snapshot": text.index("    render_warroom_v2_market_snapshot_strip("),
        "cards": text.index("    render_warroom_v2_prediction_cards("),
        "chart": text.index("    render_warroom_v2_chart_review_panel("),
    }
    assert calls["top"] < calls["refresh"] < calls["snapshot"] < calls["cards"] < calls["chart"]


def test_q29t_control_uses_browser_timer_not_websocket_or_sse() -> None:
    text = CONTROL.read_text(encoding="utf-8-sig")
    assert "components.html" in text
    assert "window.setTimeout" in text
    assert "window.parent.location.reload" in text
    assert "push_connected" in text
    assert "websocket." not in text
    assert "sse." not in text


def test_q29t_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29t_doc_records_auto_refresh_staging_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "browser_timer_auto_refresh=true" in text
    assert "auto_refresh_enabled_default=false" in text
    assert "push_connected=false" in text
    assert "not_enabling_websocket=true" in text
    assert "not_enabling_sse=true" in text
    assert "would_send_to_broker=false" in text
