# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_sidebar_auto_refresh_q29w.py
# desc: PS-Q29W guards for WarRoom v2 sidebar-driven browser timer auto refresh.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.auto_refresh_control import (  # noqa: E402
    build_warroom_v2_auto_refresh_control_packet,
    sidebar_auto_refresh_settings,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CONTROL = RENDERER_DIR / "auto_refresh_control.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29W_WARROOM_V2_SIDEBAR_AUTO_REFRESH_2026-07-02.md"


def test_q29w_sidebar_settings_convert_ui_interval_seconds_to_ms() -> None:
    settings = sidebar_auto_refresh_settings(session_state={"ui_auto_refresh": True, "ui_refresh_interval": 3})
    assert settings == {"enabled": True, "interval_ms": 3000, "source": "operator_sidebar"}
    assert sidebar_auto_refresh_settings(session_state={"ui_auto_refresh": False, "ui_refresh_interval": 3})["enabled"] is False


def test_q29w_packet_marks_sidebar_source_without_push_transport() -> None:
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True, interval_ms=3000, source="operator_sidebar")
    assert packet["auto_refresh_enabled"] is True
    assert packet["auto_refresh_source"] == "operator_sidebar"
    assert packet["sidebar_auto_refresh_consumed"] is True
    assert packet["interval_ms"] == 3000
    assert packet["transport_kind"] == "browser_timer_polling"
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q29w_renderer_consumes_sidebar_state_and_injects_timer_when_enabled() -> None:
    text = CONTROL.read_text(encoding="utf-8-sig")
    assert 'state.get("ui_auto_refresh"' in text
    assert 'state.get("ui_refresh_interval"' in text
    assert "sidebar_auto_refresh_settings()" in text
    assert "window.setTimeout" in text
    assert "window.parent.location.reload" in text
    assert "push_connected=false" in text


def test_q29w_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29w_doc_records_sidebar_auto_refresh_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "sidebar_auto_refresh_consumed=true" in text
    assert "auto_refresh_source=operator_sidebar" in text
    assert "browser_timer_auto_refresh=true" in text
    assert "push_connected=false" in text
    assert "would_send_to_broker=false" in text
