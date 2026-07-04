# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_start_preflight_q35k.py
# desc: PS-Q35K guards for receiver-only client start preflight. Metadata-only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_start_preflight import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_START_PREFLIGHT_VERSION,
    build_warroom_v2_ws_receiver_only_client_start_preflight_contract,
    build_warroom_v2_ws_receiver_only_client_start_preflight_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_start_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35K_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_START_PREFLIGHT_NO_SOCKET_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge(*, visible: bool = True, state: str = "present", readback: str = "ready", messages: int = 3) -> dict[str, object]:
    return {"compact_status_badge_visible_now": visible, "receiver_state_presence_label": state, "receiver_readback_label": readback, "receiver_state_message_count": messages}


def test_q35k_contract_is_preflight_only_no_socket_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_start_preflight_contract()
    assert packet["receiver_only_client_start_preflight_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_START_PREFLIGHT_VERSION
    assert packet["preflight_only"] is True
    assert packet["metadata_only"] is True
    assert packet["requires_operator_scope_ack"] is True
    assert packet["warroom_page_modified"] is False
    assert packet["visible_controls_added"] is False
    assert packet["socket_open_allowed_now"] is False
    assert packet["client_start_allowed_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35k_blocks_when_badge_missing_or_not_ready() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_start_preflight_packet(compact_status_badge_packet={})
    assert packet["receiver_only_client_start_preflight_status"] == "receiver_only_client_start_preflight_blocked_badge_readback_ready_required"
    assert packet["ready_for_guarded_socket_open_next_slice"] is False
    assert packet["socket_open_allowed_for_future_slice"] is False
    assert packet["socket_opened"] is False


def test_q35k_blocks_when_badge_state_missing() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_start_preflight_packet(compact_status_badge_packet=_badge(state="missing", readback="blocked", messages=0), operator_scope_ack=True)
    assert packet["badge_ready_for_receiver_client_preflight"] is False
    assert packet["receiver_only_client_start_preflight_status"] == "receiver_only_client_start_preflight_blocked_badge_readback_ready_required"
    assert packet["client_start_allowed_for_future_slice"] is False


def test_q35k_waits_for_operator_scope_ack_after_badge_ready() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_start_preflight_packet(compact_status_badge_packet=_badge(), operator_scope_ack=False)
    assert packet["badge_ready_for_receiver_client_preflight"] is True
    assert packet["receiver_only_client_start_preflight_status"] == "receiver_only_client_start_preflight_waiting_operator_scope_ack"
    assert packet["ready_for_guarded_socket_open_next_slice"] is False
    assert packet["socket_open_allowed_now"] is False
    assert packet["client_start_allowed_now"] is False


def test_q35k_ready_for_next_slice_but_still_does_not_open_socket() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_start_preflight_packet(compact_status_badge_packet=_badge(messages=7), operator_scope_ack=True)
    assert packet["receiver_only_client_start_preflight_status"] == "receiver_only_client_start_preflight_ready_for_guarded_socket_open_next_slice"
    assert packet["ready_for_guarded_socket_open_next_slice"] is True
    assert packet["socket_open_allowed_for_future_slice"] is True
    assert packet["client_start_allowed_for_future_slice"] is True
    assert packet["socket_open_allowed_now"] is False
    assert packet["client_start_allowed_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["websocket_enabled"] is False
    assert packet["external_message_send_enabled"] is False


def test_q35k_does_not_modify_page_or_aggregator_exports_or_risky_paths() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "START_PREFLIGHT" not in transport_init
    assert "START_PREFLIGHT" not in v2_init
    assert "ws_receiver_only_client_start_preflight" not in page
    forbidden_module = ("import streamlit", "from streamlit", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35K module"


def test_q35k_doc_records_preflight_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "preflight_only=true" in doc
    assert "socket_open_allowed_now=false" in doc
    assert "client_start_allowed_now=false" in doc
    assert "ready_for_guarded_socket_open_next_slice=true_only_after_operator_scope_ack" in doc
    assert "not_opening_socket=true" in doc
    assert "not_sending_external_messages=true" in doc
