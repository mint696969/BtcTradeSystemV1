# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_guarded_socket_open_q35l.py
# desc: PS-Q35L guards for receiver-only client guarded socket open. Injected opener only; no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_guarded_socket_open import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_VERSION,
    build_warroom_v2_ws_receiver_only_client_guarded_socket_open_contract,
    build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_guarded_socket_open.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35L_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _preflight(*, ready: bool = True) -> dict[str, object]:
    return {"ready_for_guarded_socket_open_next_slice": ready, "socket_open_allowed_for_future_slice": ready, "client_start_allowed_for_future_slice": ready}


def test_q35l_contract_is_guarded_socket_open_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_guarded_socket_open_contract()
    assert packet["guarded_socket_open_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_VERSION
    assert packet["requires_q35k_preflight_ready"] is True
    assert packet["requires_socket_open_requested"] is True
    assert packet["requires_operator_socket_open_ack"] is True
    assert packet["requires_injected_socket_open_callable"] is True
    assert packet["no_hardcoded_endpoint"] is True
    assert packet["injected_opener_only"] is True
    assert packet["send_disabled"] is True
    assert packet["socket_open_attempted"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q35l_blocks_without_q35k_preflight_ready() -> None:
    calls: list[str] = []
    packet = build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(
        preflight_packet=_preflight(ready=False),
        endpoint_url="ws://example.invalid/receiver",
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
        socket_open_fn=lambda endpoint: calls.append(endpoint) or {"socket_opened": True},
    )
    assert packet["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_blocked_preflight_required"
    assert packet["socket_open_attempted"] is False
    assert packet["socket_opened"] is False
    assert calls == []


def test_q35l_blocks_until_request_ack_endpoint_allow_and_opener_are_present() -> None:
    base = {"preflight_packet": _preflight(), "endpoint_url": "ws://example.invalid/receiver"}
    assert build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(**base)["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_waiting_request"
    assert build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(**base, socket_open_requested=True)["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_blocked_operator_socket_open_ack_required"
    assert build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(preflight_packet=_preflight(), socket_open_requested=True, operator_socket_open_ack=True)["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_blocked_endpoint_required"
    assert build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(**base, socket_open_requested=True, operator_socket_open_ack=True)["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_blocked_allow_socket_open_flag_required"
    assert build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(**base, socket_open_requested=True, operator_socket_open_ack=True, allow_socket_open=True)["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_blocked_injected_opener_required"


def test_q35l_calls_injected_opener_once_when_all_guards_pass_and_never_sends() -> None:
    calls: list[str] = []

    def fake_open(endpoint: str) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True, "connection_id": "fake-q35l"}

    packet = build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(
        preflight_packet=_preflight(),
        endpoint_url="ws://example.invalid/receiver",
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
        socket_open_fn=fake_open,
    )
    assert calls == ["ws://example.invalid/receiver"]
    assert packet["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_opened_no_send"
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


def test_q35l_reports_injected_opener_failure_without_send() -> None:
    def fail_open(endpoint: str) -> dict[str, Any]:
        raise RuntimeError(f"failed {endpoint}")

    packet = build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(
        preflight_packet=_preflight(),
        endpoint_url="ws://example.invalid/receiver",
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
        socket_open_fn=fail_open,
    )
    assert packet["guarded_socket_open_status"] == "receiver_only_client_guarded_socket_open_attempt_failed_no_send"
    assert packet["socket_open_attempted"] is True
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["socket_open_error"]["error_type"] == "RuntimeError"


def test_q35l_does_not_modify_page_or_aggregator_exports_or_add_default_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "GUARDED_SOCKET_OPEN" not in transport_init
    assert "GUARDED_SOCKET_OPEN" not in v2_init
    assert "ws_receiver_only_client_guarded_socket_open" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35L module"


def test_q35l_doc_records_guarded_socket_open_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "injected_opener_only=true" in doc
    assert "no_hardcoded_endpoint=true" in doc
    assert "requires_q35k_preflight_ready=true" in doc
    assert "socket_opened=true_only_when_injected_opener_reports_open" in doc
    assert "client_sends_messages=false" in doc
    assert "not_sending_external_messages=true" in doc
