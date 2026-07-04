# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_q35d.py
# desc: PS-Q35D guards for receiver page-mount next boundary. Metadata-only, no visible UI implementation, no socket, no send.

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
    build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_next_boundary import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_NEXT_BOUNDARY_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_next_boundary.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35D_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_NEXT_BOUNDARY_DEFAULT_OFF_NO_VISIBLE_UI_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _target_packet() -> dict[str, object]:
    return {"target_session_state_key": "warroom_v2_receiver_state", "readback_after_present": True, "readback_after_message_count": 5}


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def _readback_packet() -> dict[str, object]:
    hidden_packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet(
        target_write_readback_reset_rollback_packet=_target_packet(),
        visible_mount_point_packet=_mount_packet(),
        receiver_page_mount_path_requested=True,
        operator_receiver_page_mount_path_ack=True,
    )
    state = {WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY: hidden_packet}
    return build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet(state)


def test_q35d_contract_is_metadata_only_next_boundary_guard() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_contract()
    assert packet["next_boundary_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_NEXT_BOUNDARY_VERSION
    assert packet["metadata_only"] is True
    assert packet["read_only"] is True
    assert packet["visible_surface_requires_explicit_proposal"] is True
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["hidden_receiver_guard_can_continue"] is True
    assert packet["warroom_page_modified"] is False
    assert packet["visible_information_added"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35d_blocks_until_q35c_readback_ready() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet()
    assert packet["next_boundary_status"] == "receiver_page_mount_next_boundary_blocked_q35c_readback_required"
    assert packet["q35c_readback_ready"] is False
    assert packet["next_hidden_receiver_guard_allowed"] is False
    assert packet["next_visible_surface_proposal_ready"] is False
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["socket_opened"] is False


def test_q35d_allows_only_hidden_guard_by_default_after_readback() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet(hidden_observation_readback_packet=_readback_packet())
    assert packet["next_boundary_status"] == "receiver_page_mount_next_boundary_hidden_guard_allowed"
    assert packet["q35c_readback_ready"] is True
    assert packet["receiver_page_mount_path_status"] == "receiver_page_mount_path_ready_no_socket_no_send"
    assert packet["next_hidden_receiver_guard_allowed"] is True
    assert packet["next_visible_surface_proposal_ready"] is False
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["page_mount_invoked_now"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q35d_visible_surface_request_requires_explicit_proposal_ack_and_still_does_not_implement_ui() -> None:
    blocked = build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet(hidden_observation_readback_packet=_readback_packet(), visible_surface_requested=True)
    assert blocked["next_boundary_status"] == "receiver_page_mount_next_boundary_blocked_visible_surface_proposal_required"
    assert blocked["next_hidden_receiver_guard_allowed"] is False
    assert blocked["next_visible_surface_proposal_ready"] is False
    ready = build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet(hidden_observation_readback_packet=_readback_packet(), visible_surface_requested=True, operator_visible_surface_proposal_ack=True)
    assert ready["next_boundary_status"] == "receiver_page_mount_next_boundary_visible_surface_proposal_ready_no_implementation"
    assert ready["next_hidden_receiver_guard_allowed"] is False
    assert ready["next_visible_surface_proposal_ready"] is True
    assert ready["visible_surface_implementation_allowed_now"] is False
    assert ready["visible_information_added"] is False
    assert ready["renders_warning_now"] is False
    assert ready["renders_help_text_now"] is False


def test_q35d_waits_when_no_hidden_guard_and_no_visible_surface_requested() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet(hidden_observation_readback_packet=_readback_packet(), hidden_receiver_guard_requested=False)
    assert packet["next_boundary_status"] == "receiver_page_mount_next_boundary_waiting"
    assert packet["next_hidden_receiver_guard_allowed"] is False
    assert packet["next_visible_surface_proposal_ready"] is False
    assert packet["visible_surface_implementation_allowed_now"] is False


def test_q35d_does_not_modify_warroom_page_or_aggregator_exports() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "page_mount_path_next_boundary_q35d" not in page
    assert "NEXT_BOUNDARY" not in transport_init
    assert "NEXT_BOUNDARY" not in v2_init
    assert page.count('st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))') == 1


def test_q35d_module_and_doc_preserve_no_visible_ui_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 180
    assert "visible_surface_requires_explicit_proposal=true" in doc
    assert "visible_surface_implementation_allowed_now=false" in doc
    assert "warroom_page_modified=false" in doc
    assert "not_opening_socket=true" in doc
    forbidden = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden:
        assert token not in module, f"forbidden token {token!r} found in Q35D module"
