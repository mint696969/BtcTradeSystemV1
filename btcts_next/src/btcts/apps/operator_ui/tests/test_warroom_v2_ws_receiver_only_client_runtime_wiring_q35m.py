# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_runtime_wiring_q35m.py
# desc: PS-Q35M guards for receiver-only client runtime wiring. Composes Q35K/Q35L; injected opener only; no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_runtime_wiring import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_VERSION,
    build_warroom_v2_ws_receiver_only_client_runtime_wiring_contract,
    build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_runtime_wiring.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35M_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge(*, visible: bool = True, state: str = "present", readback: str = "ready", messages: int = 5) -> dict[str, object]:
    return {"compact_status_badge_visible_now": visible, "receiver_state_presence_label": state, "receiver_readback_label": readback, "receiver_state_message_count": messages}


def test_q35m_contract_composes_preflight_and_guarded_open_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_runtime_wiring_contract()
    assert packet["runtime_wiring_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_VERSION
    assert packet["composes_q35k_preflight"] is True
    assert packet["composes_q35l_guarded_socket_open"] is True
    assert packet["requires_injected_socket_open_callable"] is True
    assert packet["injected_opener_only"] is True
    assert packet["no_hardcoded_endpoint"] is True
    assert packet["send_disabled"] is True
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["visible_controls_added"] is False
    assert packet["would_send_to_broker"] is False


def test_q35m_blocks_when_badge_preflight_not_ready_and_does_not_call_opener() -> None:
    calls: list[str] = []
    packet = build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet(
        compact_status_badge_packet=_badge(state="missing", readback="blocked", messages=0),
        operator_scope_ack=True,
        endpoint_url="ws://example.invalid/receiver",
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
        socket_open_fn=lambda endpoint: calls.append(endpoint) or {"socket_opened": True},
    )
    assert packet["preflight_ready_for_guarded_socket_open"] is False
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_blocked_preflight_required"
    assert packet["socket_open_attempted"] is False
    assert packet["socket_opened"] is False
    assert calls == []


def test_q35m_waits_for_operator_scope_ack_before_socket_boundary() -> None:
    calls: list[str] = []
    packet = build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet(
        compact_status_badge_packet=_badge(),
        operator_scope_ack=False,
        endpoint_url="ws://example.invalid/receiver",
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
        socket_open_fn=lambda endpoint: calls.append(endpoint) or {"socket_opened": True},
    )
    assert packet["preflight_packet"]["receiver_only_client_start_preflight_status"] == "receiver_only_client_start_preflight_waiting_operator_scope_ack"
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_blocked_preflight_required"
    assert packet["socket_open_attempted"] is False
    assert calls == []


def test_q35m_calls_injected_opener_once_when_composed_guards_pass() -> None:
    calls: list[str] = []

    def fake_open(endpoint: str) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True, "connection_id": "fake-q35m"}

    packet = build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet(
        compact_status_badge_packet=_badge(messages=8),
        operator_scope_ack=True,
        endpoint_url="ws://example.invalid/receiver",
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
        socket_open_fn=fake_open,
    )
    assert calls == ["ws://example.invalid/receiver"]
    assert packet["preflight_ready_for_guarded_socket_open"] is True
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_opened_no_send"
    assert packet["socket_open_attempted"] is True
    assert packet["socket_opened"] is True
    assert packet["client_started"] is True
    assert packet["websocket_enabled"] is True
    assert packet["runtime_connected"] is True
    assert packet["push_connected"] is True
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["send_disabled"] is True
    assert packet["would_send_to_broker"] is False


def test_q35m_preserves_guarded_open_failure_as_data_without_send() -> None:
    def fail_open(endpoint: str) -> dict[str, Any]:
        raise RuntimeError(f"failed {endpoint}")

    packet = build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet(
        compact_status_badge_packet=_badge(),
        operator_scope_ack=True,
        endpoint_url="ws://example.invalid/receiver",
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
        socket_open_fn=fail_open,
    )
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_attempt_failed_no_send"
    assert packet["socket_open_attempted"] is True
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["guarded_socket_open_packet"]["socket_open_error"]["error_type"] == "RuntimeError"
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False


def test_q35m_does_not_modify_page_or_aggregator_exports_or_add_default_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "RUNTIME_WIRING" not in transport_init
    assert "RUNTIME_WIRING" not in v2_init
    assert "ws_receiver_only_client_runtime_wiring" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35M module"


def test_q35m_doc_records_runtime_wiring_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "composes_q35k_preflight=true" in doc
    assert "composes_q35l_guarded_socket_open=true" in doc
    assert "injected_opener_only=true" in doc
    assert "client_sends_messages=false" in doc
    assert "not_sending_external_messages=true" in doc
