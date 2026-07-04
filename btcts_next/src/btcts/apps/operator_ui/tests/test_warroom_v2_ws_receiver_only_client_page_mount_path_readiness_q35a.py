# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_q35a.py
# desc: PS-Q35A guards for receiver-only client page-mount path readiness. Metadata-only/default-off/no socket/no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_readiness import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_READINESS_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35A_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_READINESS_DEFAULT_OFF_OPERATOR_GATED_NO_SEND_2026-07-04.md"
TRANSPORT_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_readiness.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _target_packet() -> dict[str, object]:
    return {"target_session_state_key": "warroom_v2_receiver_state", "readback_after_present": True, "readback_after_message_count": 2}


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def test_q35a_contract_is_metadata_only_page_mount_path_readiness() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_contract()
    assert packet["page_mount_path_readiness_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_READINESS_VERSION
    assert packet["page_mount_path_readiness_kind"] == "warroom_v2_ws_receiver_only_client_page_mount_path_readiness_default_off_operator_gated_no_send"
    assert packet["receiver_page_mount_path_requested_default"] is False
    assert packet["operator_receiver_page_mount_path_ack_default"] is False
    assert packet["metadata_only"] is True
    assert packet["warroom_page_modified"] is False
    assert packet["visible_information_added"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35a_default_packet_keeps_path_hidden_and_does_not_mutate_or_render() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet()
    assert packet["receiver_page_mount_path_status"] == "receiver_page_mount_path_hidden_default"
    assert packet["receiver_page_mount_path_ready_for_next_slice"] is False
    assert packet["target_receiver_state_readback_ready"] is False
    assert packet["visible_mount_point_ready_for_page_mount_path"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["page_mount_invoked_now"] is False
    assert packet["target_session_state_mutated"] is False
    assert packet["state_mutated"] is False


def test_q35a_ready_requires_request_ack_readback_and_mount_point_readiness() -> None:
    blocked_ack = build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet(target_write_readback_reset_rollback_packet=_target_packet(), visible_mount_point_packet=_mount_packet(), receiver_page_mount_path_requested=True)
    assert blocked_ack["receiver_page_mount_path_status"] == "receiver_page_mount_path_blocked_operator_ack_required"
    blocked_target = build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet(visible_mount_point_packet=_mount_packet(), receiver_page_mount_path_requested=True, operator_receiver_page_mount_path_ack=True)
    assert blocked_target["receiver_page_mount_path_status"] == "receiver_page_mount_path_blocked_receiver_state_readback_required"
    blocked_mount = build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet(target_write_readback_reset_rollback_packet=_target_packet(), receiver_page_mount_path_requested=True, operator_receiver_page_mount_path_ack=True)
    assert blocked_mount["receiver_page_mount_path_status"] == "receiver_page_mount_path_blocked_visible_mount_point_readiness_required"
    ready = build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet(target_write_readback_reset_rollback_packet=_target_packet(), visible_mount_point_packet=_mount_packet(), receiver_page_mount_path_requested=True, operator_receiver_page_mount_path_ack=True)
    assert ready["receiver_page_mount_path_status"] == "receiver_page_mount_path_ready_no_socket_no_send"
    assert ready["receiver_page_mount_path_ready_for_next_slice"] is True
    assert ready["receiver_state_target_key"] == "warroom_v2_receiver_state"
    assert ready["receiver_state_message_count"] == 2
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q35a_doc_and_warroom_page_preserve_no_visible_info_addition() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "metadata_only=true" in doc
    assert "visible_information_added=false" in doc
    assert "not_modifying_warroom_page=true" in doc
    assert "not_opening_socket=true" in doc
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "receiver_page_mount_path_readiness_q35a" not in page
    assert "receiver_page_mount_path_ready_no_socket_no_send" not in page
    assert "data_quality_badge_policy" not in page
    assert "板品質" not in page


def test_q35a_transport_module_preserves_no_socket_order_prediction_boundary() -> None:
    forbidden = (
        "import streamlit", "from streamlit", "websocket.", "sse.", "polling_loop(", "browser_timer_reload(",
        "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(",
        "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92),
    )
    body = TRANSPORT_MODULE.read_text(encoding="utf-8-sig")
    assert len(body.splitlines()) <= 180, "Q35A transport module should remain small"
    for token in forbidden:
        assert token not in body, f"forbidden token {token!r} found in Q35A module"


def test_q35a_uses_direct_module_import_without_aggregator_init_bloat() -> None:
    body = TRANSPORT_MODULE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_READINESS_VERSION" in body
    assert "build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet" in body
