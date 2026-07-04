# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_q35e.py
# desc: PS-Q35E guards for receiver page-mount visible surface proposal only. No UI implementation, no socket, no send.

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
    build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_visible_surface_proposal import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES,
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_visible_surface_proposal.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35E_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ONLY_NO_IMPLEMENTATION_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _target_packet() -> dict[str, object]:
    return {"target_session_state_key": "warroom_v2_receiver_state", "readback_after_present": True, "readback_after_message_count": 6}


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def _next_boundary_packet() -> dict[str, object]:
    hidden_packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet(
        target_write_readback_reset_rollback_packet=_target_packet(),
        visible_mount_point_packet=_mount_packet(),
        receiver_page_mount_path_requested=True,
        operator_receiver_page_mount_path_ack=True,
    )
    state = {WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY: hidden_packet}
    readback = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet(state)
    return build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet(hidden_observation_readback_packet=readback, visible_surface_requested=True, operator_visible_surface_proposal_ack=True)


def test_q35e_contract_is_proposal_only_no_implementation() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_contract()
    assert packet["visible_surface_proposal_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_VERSION
    assert packet["allowed_visible_surfaces"] == list(WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES)
    assert packet["proposal_only"] is True
    assert packet["metadata_only"] is True
    assert packet["visible_surface_requires_explicit_proposal"] is True
    assert packet["visible_surface_requires_operator_ack"] is True
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["visible_surface_implemented_now"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["visible_information_added"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35e_blocks_without_q35c_readback_ready_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet(proposed_visible_surface="compact_status_badge", operator_proposal_ack=True)
    assert packet["visible_surface_proposal_status"] == "receiver_page_mount_visible_surface_proposal_blocked_q35c_readback_required"
    assert packet["q35c_readback_ready"] is False
    assert packet["visible_surface_proposal_ready_for_future_slice"] is False
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["socket_opened"] is False


def test_q35e_reports_no_surface_selected() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet(next_boundary_packet=_next_boundary_packet())
    assert packet["visible_surface_proposal_status"] == "receiver_page_mount_visible_surface_proposal_no_surface_selected"
    assert packet["proposed_visible_surface"] == ""
    assert packet["visible_surface_proposal_ready_for_future_slice"] is False
    assert packet["visible_surface_implemented_now"] is False


def test_q35e_rejects_unapproved_surface_names() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet(next_boundary_packet=_next_boundary_packet(), proposed_visible_surface="warning_panel", operator_proposal_ack=True)
    assert packet["visible_surface_proposal_status"] == "receiver_page_mount_visible_surface_proposal_invalid_surface"
    assert packet["proposed_visible_surface_valid"] is False
    assert packet["visible_surface_proposal_ready_for_future_slice"] is False
    assert packet["renders_warning_now"] is False
    assert packet["renders_help_text_now"] is False


def test_q35e_valid_surface_waits_for_operator_ack() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet(next_boundary_packet=_next_boundary_packet(), proposed_visible_surface="compact_status_card")
    assert packet["visible_surface_proposal_status"] == "receiver_page_mount_visible_surface_proposal_waiting_operator_ack"
    assert packet["proposed_visible_surface_valid"] is True
    assert packet["operator_proposal_ack"] is False
    assert packet["visible_surface_proposal_ready_for_future_slice"] is False
    assert packet["visible_surface_implementation_allowed_now"] is False


def test_q35e_operator_ack_accepts_future_slice_only_and_still_does_not_render() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet(next_boundary_packet=_next_boundary_packet(), proposed_visible_surface="compact_status_badge", operator_readability_reason="single compact status at existing receiver area", operator_proposal_ack=True)
    assert packet["visible_surface_proposal_status"] == "receiver_page_mount_visible_surface_proposal_accepted_for_future_slice_no_implementation"
    assert packet["visible_surface_proposal_ready_for_future_slice"] is True
    assert packet["operator_readability_reason"] == "single compact status at existing receiver area"
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["visible_surface_implemented_now"] is False
    assert packet["renders_badge_now"] is False
    assert packet["renders_card_now"] is False
    assert packet["renders_balloon_now"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["page_mount_invoked_now"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q35e_does_not_modify_warroom_page_or_aggregator_exports() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "visible_surface_proposal_q35e" not in page
    assert "VISIBLE_SURFACE_PROPOSAL" not in transport_init
    assert "VISIBLE_SURFACE_PROPOSAL" not in v2_init
    assert page.count('st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))') == 1


def test_q35e_module_and_doc_preserve_no_ui_implementation_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 180
    assert "proposal_only=true" in doc
    assert "visible_surface_implementation_allowed_now=false" in doc
    assert "visible_surface_implemented_now=false" in doc
    assert "warroom_page_modified=false" in doc
    forbidden = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden:
        assert token not in module, f"forbidden token {token!r} found in Q35E module"
