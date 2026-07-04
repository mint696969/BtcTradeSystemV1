# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_q35c.py
# desc: PS-Q35C guards for WarRoom receiver page-mount hidden observation readback diagnostics. No visible UI, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_hidden_observation import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_hidden_observation_readback import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_READBACK_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_hidden_observation_readback.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35C_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_READBACK_DEFAULT_OFF_NO_VISIBLE_UI_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _target_packet() -> dict[str, object]:
    return {"target_session_state_key": "warroom_v2_receiver_state", "readback_after_present": True, "readback_after_message_count": 4}


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def _hidden_packet() -> dict[str, object]:
    return build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet(
        target_write_readback_reset_rollback_packet=_target_packet(),
        visible_mount_point_packet=_mount_packet(),
        receiver_page_mount_path_requested=True,
        operator_receiver_page_mount_path_ack=True,
    )


def test_q35c_contract_is_hidden_readback_only() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_contract()
    assert packet["hidden_observation_readback_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_READBACK_VERSION
    assert packet["source_state_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY
    assert packet["read_only"] is True
    assert packet["metadata_only"] is True
    assert packet["hidden_readback_diagnostic"] is True
    assert packet["warroom_page_modified"] is False
    assert packet["visible_information_added"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["page_mount_invoked_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35c_missing_hidden_observation_is_safe_default() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet({})
    assert packet["hidden_observation_readback_status"] == "receiver_page_mount_hidden_observation_readback_missing"
    assert packet["hidden_observation_present"] is False
    assert packet["hidden_observation_readback_ready_for_next_slice"] is False
    assert packet["hidden_observation_packet"] == {}
    assert packet["page_mount_path_readiness_packet"] == {}
    assert packet["target_session_state_mutated"] is False
    assert packet["state_mutated"] is False
    assert packet["socket_opened"] is False


def test_q35c_invalid_hidden_observation_value_is_reported_without_mutation() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet({WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY: "bad"})
    assert packet["hidden_observation_readback_status"] == "receiver_page_mount_hidden_observation_readback_invalid_value"
    assert packet["hidden_observation_present"] is True
    assert packet["hidden_observation_value_is_mapping"] is False
    assert packet["hidden_observation_value_kind"] == "str"
    assert packet["hidden_observation_readback_ready_for_next_slice"] is False
    assert packet["state_mutated"] is False


def test_q35c_present_hidden_observation_without_readiness_packet_is_reported() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet({WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY: {"packet_kind": "manual"}})
    assert packet["hidden_observation_readback_status"] == "receiver_page_mount_hidden_observation_readback_present_without_readiness_packet"
    assert packet["hidden_observation_present"] is True
    assert packet["hidden_observation_value_is_mapping"] is True
    assert packet["page_mount_path_readiness_packet_present"] is False
    assert packet["hidden_observation_readback_ready_for_next_slice"] is False


def test_q35c_present_hidden_observation_extracts_q35b_readiness_summary() -> None:
    state = {WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY: _hidden_packet()}
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet(state)
    assert packet["hidden_observation_readback_status"] == "receiver_page_mount_hidden_observation_readback_present"
    assert packet["hidden_observation_readback_ready_for_next_slice"] is True
    assert packet["page_mount_path_readiness_packet_present"] is True
    assert packet["receiver_page_mount_path_status"] == "receiver_page_mount_path_ready_no_socket_no_send"
    assert packet["receiver_page_mount_path_ready_for_next_slice"] is True
    assert packet["target_receiver_state_readback_ready"] is True
    assert packet["visible_mount_point_ready_for_page_mount_path"] is True
    assert packet["receiver_state_target_key"] == "warroom_v2_receiver_state"
    assert packet["receiver_state_message_count"] == 4
    assert packet["mount_point_status"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed"
    assert packet["page_mount_invoked_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35c_does_not_modify_warroom_page_or_aggregator_exports() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "hidden_observation_readback_q35c" not in page
    assert "HIDDEN_OBSERVATION_READBACK" not in transport_init
    assert "HIDDEN_OBSERVATION_READBACK" not in v2_init
    assert page.count('st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))') == 1


def test_q35c_module_and_doc_preserve_no_visible_ui_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 180
    assert "hidden_readback_diagnostic=true" in doc
    assert "visible_information_added=false" in doc
    assert "warroom_page_modified=false" in doc
    assert "not_opening_socket=true" in doc
    forbidden = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden:
        assert token not in module, f"forbidden token {token!r} found in Q35C module"
