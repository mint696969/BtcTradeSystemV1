# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_q35g.py
# desc: PS-Q35G guards for actual one-line compact receiver status badge. No socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_compact_status_badge import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_STATE_KEY,
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_compact_status_badge.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35G_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_IMPLEMENTATION_NO_SOCKET_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def test_q35g_contract_is_actual_compact_badge_only_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_contract()
    assert packet["compact_status_badge_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_VERSION
    assert packet["state_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_STATE_KEY
    assert packet["selected_visible_surface"] == "compact_status_badge"
    assert packet["visible_surface_implemented_now"] is True
    assert packet["visible_controls_added"] is False
    assert packet["renders_badge_now"] is True
    assert packet["renders_card_now"] is False
    assert packet["renders_balloon_now"] is False
    assert packet["renders_warning_now"] is False
    assert packet["renders_help_text_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35g_blocks_until_existing_q32y_mount_point_allows_markdown() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet(visible_mount_point_packet={})
    assert packet["compact_status_badge_status"] == "receiver_page_mount_compact_status_badge_blocked_mount_point_required"
    assert packet["compact_status_badge_visible_now"] is False
    assert packet["compact_badge_markdown"] == ""
    assert packet["streamlit_markdown_allowed"] is False
    assert packet["socket_opened"] is False


def test_q35g_builds_one_line_compact_badge_when_mount_ready() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet(visible_mount_point_packet=_mount_packet())
    assert packet["compact_status_badge_status"] == "receiver_page_mount_compact_status_badge_visible_one_line_no_socket_no_send"
    assert packet["compact_status_badge_visible_now"] is True
    assert packet["visible_surface_implemented_now"] is True
    assert packet["compact_badge_markdown"] == "`WS Receiver` page-mount ready · msgs=0 · no socket/send"
    assert packet["renders_badge_now"] is True
    assert packet["renders_warning_now"] is False
    assert packet["renders_help_text_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q35g_warroom_page_mounts_badge_after_existing_top_minimal_line() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_page_mount_path_compact_status_badge" in page
    assert "WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_STATE_KEY" in page
    assert "def _render_warroom_v2_receiver_page_mount_compact_status_badge_q35g()" in page
    assert "_render_warroom_v2_receiver_page_mount_compact_status_badge_q35g()" in page
    top_call = page.index("_render_warroom_v2_top_minimal_status_line_mount_q32y()", page.index("def render()"))
    badge_call = page.index("_render_warroom_v2_receiver_page_mount_compact_status_badge_q35g()", page.index("def render()"))
    assert top_call < badge_call
    assert page.count('st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))') == 1
    assert page.count('st.markdown(str(badge_packet.get("compact_badge_markdown") or ""))') == 1


def test_q35g_does_not_add_aggregator_exports_or_risky_paths() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "COMPACT_STATUS_BADGE" not in transport_init
    assert "COMPACT_STATUS_BADGE" not in v2_init
    forbidden_module = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35G module"
    forbidden_page = ("websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier(")
    for token in forbidden_page:
        assert token not in page, f"forbidden token {token!r} found in WarRoom page"


def test_q35g_doc_records_actual_implementation_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "selected_visible_surface=compact_status_badge" in doc
    assert "visible_surface_implemented_now=true" in doc
    assert "visible_controls_added=false" in doc
    assert "not_opening_socket=true" in doc
    assert "not_sending_external_messages=true" in doc
