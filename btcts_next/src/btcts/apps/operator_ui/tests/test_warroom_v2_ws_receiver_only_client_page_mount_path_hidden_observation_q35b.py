# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_q35b.py
# desc: PS-Q35B guards for WarRoom page hidden receiver page-mount path observation. No visible UI, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_hidden_observation import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY,
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_hidden_observation.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35B_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_DEFAULT_OFF_NO_VISIBLE_UI_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _target_packet() -> dict[str, object]:
    return {"target_session_state_key": "warroom_v2_receiver_state", "readback_after_present": True, "readback_after_message_count": 3}


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def test_q35b_contract_is_hidden_observation_only() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_contract()
    assert packet["hidden_observation_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_VERSION
    assert packet["state_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY
    assert packet["hidden_session_state_observation"] is True
    assert packet["metadata_only"] is True
    assert packet["warroom_page_visible_ui_modified"] is False
    assert packet["visible_information_added"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["page_mount_invoked_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35b_default_packet_records_hidden_not_ready_without_rendering() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet(fragment_summary={"hybrid_refresh": True})
    assert packet["receiver_page_mount_path_status"] == "receiver_page_mount_path_hidden_default"
    assert packet["receiver_page_mount_path_ready_for_next_slice"] is False
    assert packet["fragment_summary"]["hybrid_refresh"] is True
    assert packet["visible_information_added"] is False
    assert packet["renders_warning_now"] is False
    assert packet["renders_help_text_now"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["target_session_state_mutated"] is False
    assert packet["state_mutated"] is False


def test_q35b_ready_packet_wraps_q35a_without_socket_or_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet(target_write_readback_reset_rollback_packet=_target_packet(), visible_mount_point_packet=_mount_packet(), receiver_page_mount_path_requested=True, operator_receiver_page_mount_path_ack=True)
    assert packet["receiver_page_mount_path_status"] == "receiver_page_mount_path_ready_no_socket_no_send"
    assert packet["receiver_page_mount_path_ready_for_next_slice"] is True
    assert packet["target_receiver_state_readback_ready"] is True
    assert packet["visible_mount_point_ready_for_page_mount_path"] is True
    assert packet["receiver_state_target_key"] == "warroom_v2_receiver_state"
    assert packet["receiver_state_message_count"] == 3
    assert packet["page_mount_path_readiness_packet"]["receiver_page_mount_path_ready_for_next_slice"] is True
    assert packet["page_mount_invoked_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35b_warroom_page_records_hidden_observation_without_visible_ui() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_page_mount_path_hidden_observation" in page
    assert "WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY" in page
    assert "build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet" in page
    assert "warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_q35b" in page
    assert "st.session_state[WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY]" in page
    assert "receiver_page_mount_path_ready_no_socket_no_send" not in page
    assert 'st.checkbox("receiver' not in page
    assert 'st.button("receiver' not in page
    assert 'st.caption("receiver' not in page
    assert 'st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))' in page
    assert page.count('st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))') == 1


def test_q35b_keeps_aggregator_inits_unchanged_and_module_small() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 180
    assert "PAGE_MOUNT_PATH_HIDDEN_OBSERVATION" not in transport_init
    assert "PAGE_MOUNT_PATH_HIDDEN_OBSERVATION" not in v2_init
    forbidden = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden:
        assert token not in module, f"forbidden token {token!r} found in Q35B module"


def test_q35b_doc_records_hidden_observation_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "hidden_session_state_observation=true" in doc
    assert "visible_information_added=false" in doc
    assert "not_modifying_visible_warroom_ui=true" in doc
    assert "not_opening_socket=true" in doc
