# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_q35f.py
# desc: PS-Q35F guards for receiver page-mount visible surface implementation gate. No UI implementation, no socket, no send.

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
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_hidden_observation_readback import build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_next_boundary import build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_visible_surface_proposal import build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_IMPLEMENTATION_GATE_VERSION,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_contract,
    build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35F_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_VISIBLE_SURFACE_IMPLEMENTATION_GATE_NO_UI_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _target_packet() -> dict[str, object]:
    return {"target_session_state_key": "warroom_v2_receiver_state", "readback_after_present": True, "readback_after_message_count": 7}


def _mount_packet() -> dict[str, object]:
    return {"mount_point_status": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed", "streamlit_markdown_allowed": True, "status_line_visible_now": True, "status_line_mounted_now": True}


def _accepted_proposal(*, surface: str = "compact_status_badge", reason: str = "single compact removable receiver status") -> dict[str, object]:
    hidden_packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet(
        target_write_readback_reset_rollback_packet=_target_packet(),
        visible_mount_point_packet=_mount_packet(),
        receiver_page_mount_path_requested=True,
        operator_receiver_page_mount_path_ack=True,
    )
    state = {WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY: hidden_packet}
    readback = build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet(state)
    boundary = build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet(hidden_observation_readback_packet=readback, visible_surface_requested=True, operator_visible_surface_proposal_ack=True)
    return build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet(next_boundary_packet=boundary, proposed_visible_surface=surface, operator_readability_reason=reason, operator_proposal_ack=True)


def test_q35f_contract_is_implementation_gate_only_no_ui() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_contract()
    assert packet["implementation_gate_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_IMPLEMENTATION_GATE_VERSION
    assert packet["implementation_gate_only"] is True
    assert packet["metadata_only"] is True
    assert packet["requires_accepted_q35e_proposal"] is True
    assert packet["requires_operator_readability_reason"] is True
    assert packet["requires_operator_scope_ack"] is True
    assert packet["implementation_allowed_for_future_slice"] is False
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["visible_surface_implemented_now"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False


def test_q35f_blocks_without_accepted_q35e_proposal() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet()
    assert packet["implementation_gate_status"] == "receiver_page_mount_visible_surface_implementation_gate_blocked_proposal_required"
    assert packet["q35e_proposal_ready_for_future_slice"] is False
    assert packet["implementation_allowed_for_future_slice"] is False
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["socket_opened"] is False


def test_q35f_blocks_invalid_surface_even_with_forged_proposal_ready() -> None:
    proposal = {"visible_surface_proposal_ready_for_future_slice": True, "proposed_visible_surface": "warning_panel", "operator_readability_reason": "too broad", "visible_surface_proposal_status": "forged"}
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet(visible_surface_proposal_packet=proposal, operator_scope_ack=True)
    assert packet["implementation_gate_status"] == "receiver_page_mount_visible_surface_implementation_gate_blocked_invalid_surface"
    assert packet["proposed_visible_surface_valid"] is False
    assert packet["implementation_allowed_for_future_slice"] is False
    assert packet["renders_warning_now"] is False


def test_q35f_requires_readability_reason() -> None:
    proposal = _accepted_proposal(reason="")
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet(visible_surface_proposal_packet=proposal, operator_scope_ack=True)
    assert packet["implementation_gate_status"] == "receiver_page_mount_visible_surface_implementation_gate_blocked_readability_reason_required"
    assert packet["operator_readability_reason_present"] is False
    assert packet["implementation_allowed_for_future_slice"] is False


def test_q35f_waits_for_operator_scope_ack_after_valid_proposal() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet(visible_surface_proposal_packet=_accepted_proposal())
    assert packet["implementation_gate_status"] == "receiver_page_mount_visible_surface_implementation_gate_waiting_operator_scope_ack"
    assert packet["operator_scope_ack"] is False
    assert packet["implementation_allowed_for_future_slice"] is False
    assert packet["visible_surface_implemented_now"] is False


def test_q35f_marks_future_slice_ready_but_still_does_not_implement_ui() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet(visible_surface_proposal_packet=_accepted_proposal(), operator_scope_ack=True)
    assert packet["implementation_gate_status"] == "receiver_page_mount_visible_surface_implementation_gate_ready_for_future_slice_no_implementation"
    assert packet["implementation_allowed_for_future_slice"] is True
    assert packet["visible_surface_implementation_allowed_now"] is False
    assert packet["visible_surface_implemented_now"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["renders_badge_now"] is False
    assert packet["renders_card_now"] is False
    assert packet["renders_balloon_now"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["page_mount_invoked_now"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q35f_does_not_modify_warroom_page_or_aggregator_exports() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "visible_surface_implementation_gate_q35f" not in page
    assert "VISIBLE_SURFACE_IMPLEMENTATION_GATE" not in transport_init
    assert "VISIBLE_SURFACE_IMPLEMENTATION_GATE" not in v2_init
    assert page.count('st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))') == 1


def test_q35f_module_and_doc_preserve_no_ui_implementation_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 180
    assert "implementation_gate_only=true" in doc
    assert "implementation_allowed_for_future_slice=true only after accepted proposal plus scope ack" in doc
    assert "visible_surface_implementation_allowed_now=false" in doc
    assert "visible_surface_implemented_now=false" in doc
    assert "warroom_page_modified=false" in doc
    forbidden = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden:
        assert token not in module, f"forbidden token {token!r} found in Q35F module"
