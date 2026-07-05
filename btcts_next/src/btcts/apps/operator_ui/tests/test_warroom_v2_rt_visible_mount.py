# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_visible_mount.py
# desc: Verifies WarRoom v2 visible page mounts RT0-RT6 runtime and live push-widget packets instead of preview-only shell.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
RT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/rt_live_receiver_bridge.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_VISIBLE_MOUNT_2026-07-05.md"

from btcts.apps.operator_ui.views.warroom_v2_page import build_warroom_v2_page_mount_packet  # noqa: E402


def test_warroom_v2_page_is_rt_visible_mount_not_preview_shell() -> None:
    text = PAGE.read_text(encoding="utf-8-sig")
    assert "Preview shell only" not in text
    assert "render_warroom_v2_shell_preview_panel" not in text
    assert "ensure_warroom_push_widget_live_observation_runtime" in text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in text
    assert "render_wp9_push_widget_mount" in text
    assert "render_wp12_bottom_chart_layout" in text
    assert "render_wp13_prediction_card_connection" in text


def test_warroom_v2_page_mount_packet_reports_runtime_connected_when_started() -> None:
    packet = build_warroom_v2_page_mount_packet(
        runtime_status={"receiver_runtime_started": True, "socket_opened": True, "receive_loop_started": True},
        bridge_packet={"messages_applied": 4},
    )
    assert packet["thin_page_shell_only"] is False
    assert packet["rt_visible_mount_ready"] is True
    assert packet["runtime_connected"] is True
    assert packet["push_connected"] is True
    assert packet["websocket_enabled"] is True
    assert packet["messages_applied"] == 4
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_runtime_uses_env_runtime_config_defaults_and_doc_markers() -> None:
    rt = RT.read_text(encoding="utf-8-sig")
    assert "WARROOM_PUSH_WIDGET_SOURCE" in PAGE.read_text(encoding="utf-8-sig")
    assert "BTCTS_WS_CA_FILE" in PAGE.read_text(encoding="utf-8-sig")
    assert "BTCTS_WS_SSL_VERIFY" in PAGE.read_text(encoding="utf-8-sig")
    assert "bitflyer_collector_provider" in rt
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_visible_mount_ready=true" in doc
    assert "preview_shell_removed=true" in doc
    assert "warroom_page_uses_live_packet_when_present=true" in doc
