# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_fragment_refresh_q29y.py
# desc: PS-Q29Y guards for WarRoom v2 fragment refresh without page reload.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.auto_refresh_control import build_warroom_v2_auto_refresh_control_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.fragment_refresh import build_warroom_v2_fragment_refresh_packet, fragment_interval_sec_from_ms  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CONTROL = RENDERER_DIR / "auto_refresh_control.py"
FRAGMENT = RENDERER_DIR / "fragment_refresh.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29Y_WARROOM_V2_FRAGMENT_REFRESH_2026-07-02.md"


def test_q29y_auto_refresh_packet_disables_page_reload_and_declares_fragment_transport() -> None:
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True, interval_ms=3000, source="operator_sidebar")
    assert packet["effective_transport_kind"] == "streamlit_fragment_polling"
    assert packet["page_reload_enabled"] is False
    assert packet["browser_timer_reload_enabled"] is False
    assert packet["fragment_refresh_target"] is True
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q29y_fragment_packet_maps_interval_and_keeps_transport_disconnected() -> None:
    refresh = build_warroom_v2_auto_refresh_control_packet(enabled=True, interval_ms=3000, source="operator_sidebar")
    packet = build_warroom_v2_fragment_refresh_packet(refresh_packet=refresh)
    assert fragment_interval_sec_from_ms(3000) == 3
    assert packet["effective_transport_kind"] == "streamlit_fragment_polling"
    assert packet["page_reload_enabled"] is False
    assert packet["browser_timer_reload_enabled"] is False
    assert packet["interval_sec"] == 3
    assert packet["push_connected"] is False


def test_q29y_shell_refreshes_snapshot_and_chart_with_fragment_blocks() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    assert "render_warroom_v2_fragment_refresh_block" in text
    assert 'label="market_snapshot_strip"' in text
    assert 'label="chart_review_panel"' in text
    assert "Streamlit fragment refresh / no page reload" in text
    assert "window.parent.location.reload" not in text


def test_q29y_browser_timer_is_not_called_by_render_control() -> None:
    text = CONTROL.read_text(encoding="utf-8-sig")
    body = text.split("def render_warroom_v2_auto_refresh_control", 1)[1]
    assert "_inject_browser_timer" not in body
    assert "page_reload=false" in text
    assert "effective_transport_kind" in text


def test_q29y_fragment_helper_uses_streamlit_fragment_not_websocket_or_sse() -> None:
    text = FRAGMENT.read_text(encoding="utf-8-sig")
    assert "getattr(st, \"fragment\"" in text
    assert "run_every" in text
    assert "websocket." not in text
    assert "sse." not in text


def test_q29y_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29y_doc_records_fragment_refresh_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "streamlit_fragment_refresh=true" in text
    assert "page_reload_enabled=false" in text
    assert "browser_timer_reload_enabled=false" in text
    assert "push_connected=false" in text
    assert "would_send_to_broker=false" in text
