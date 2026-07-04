# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_readback_count_q35h.py
# desc: PS-Q35H guards for compact receiver status badge readback count. One line only, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_compact_status_badge import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_COUNT_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_compact_status_badge.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35H_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_COUNT_NO_SOCKET_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def _hidden_observation_packet(message_count: int = 9) -> dict[str, object]:
    return {"page_mount_path_readiness_packet": {"receiver_state_message_count": message_count, "receiver_page_mount_path_ready_for_next_slice": True}}


def test_q35h_contract_extends_q35g_badge_with_readback_count() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_contract()
    assert packet["compact_status_badge_readback_count_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_COUNT_VERSION
    assert packet["readback_count_display_enabled"] is True
    assert packet["selected_visible_surface"] == "compact_status_badge"
    assert packet["visible_controls_added"] is False
    assert packet["renders_badge_now"] is True
    assert packet["renders_card_now"] is False
    assert packet["renders_balloon_now"] is False
    assert packet["renders_warning_now"] is False
    assert packet["renders_help_text_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35h_badge_defaults_to_zero_count_without_hidden_observation() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet(visible_mount_point_packet=_mount_packet())
    assert packet["compact_status_badge_visible_now"] is True
    assert packet["receiver_state_message_count"] == 0
    assert packet["compact_badge_markdown"] == "`WS Receiver` mount ready · state=unknown · readback=unknown · msgs=0 · no socket/send"
    assert packet["socket_opened"] is False


def test_q35h_badge_displays_hidden_observation_readback_message_count() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet(
        visible_mount_point_packet=_mount_packet(),
        hidden_observation_packet=_hidden_observation_packet(12),
    )
    assert packet["receiver_state_message_count"] == 12
    assert packet["compact_badge_markdown"] == "`WS Receiver` mount ready · state=present · readback=ready · msgs=12 · no socket/send"
    assert packet["visible_surface_implemented_now"] is True
    assert packet["renders_badge_now"] is True
    assert packet["renders_warning_now"] is False
    assert packet["renders_help_text_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q35h_badge_still_blocks_without_mount_permission() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet(hidden_observation_packet=_hidden_observation_packet(12))
    assert packet["compact_status_badge_status"] == "receiver_page_mount_compact_status_badge_blocked_mount_point_required"
    assert packet["compact_status_badge_visible_now"] is False
    assert packet["receiver_state_message_count"] == 12
    assert packet["compact_badge_markdown"] == ""


def test_q35h_warroom_page_passes_q35b_hidden_observation_to_badge_builder() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "hidden_observation_packet = st.session_state.get(WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY)" in page
    assert "hidden_observation_packet=hidden_observation_packet if isinstance(hidden_observation_packet, dict) else None" in page
    assert page.count('st.markdown(str(badge_packet.get("compact_badge_markdown") or ""))') == 1
    assert "st.write(" not in page
    assert "st.metric(" not in page


def test_q35h_does_not_add_aggregator_exports_or_risky_paths() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "READBACK_COUNT" not in transport_init
    assert "READBACK_COUNT" not in v2_init
    forbidden = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden:
        assert token not in module, f"forbidden token {token!r} found in Q35H module"


def test_q35h_doc_records_readback_count_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "readback_count_display_enabled=true" in doc
    assert "rendered_line_template=`WS Receiver` page-mount ready · msgs={receiver_state_message_count} · no socket/send" in doc
    assert "visible_controls_added=false" in doc
    assert "not_opening_socket=true" in doc
    assert "not_sending_external_messages=true" in doc
