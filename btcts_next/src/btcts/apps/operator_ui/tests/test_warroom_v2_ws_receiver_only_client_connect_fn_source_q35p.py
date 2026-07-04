# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_connect_fn_source_q35p.py
# desc: PS-Q35P guards for receiver-only connect_fn source. Runtime-config callable source only; no default client and no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_source import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_VERSION,
    build_warroom_v2_ws_receiver_only_client_connect_fn_source_contract,
    build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_source.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35P_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_GUARDED_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge(*, visible: bool = True, state: str = "present", readback: str = "ready", messages: int = 11) -> dict[str, object]:
    return {"compact_status_badge_visible_now": visible, "receiver_state_presence_label": state, "receiver_readback_label": readback, "receiver_state_message_count": messages}


def _config(connect_fn: object) -> dict[str, object]:
    return {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35p", "allow_adapter_open": True, "auth_token": "secret-token", "low_level_connect_fn": connect_fn}


def test_q35p_contract_is_runtime_config_connect_fn_source_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_source_contract()
    assert packet["connect_fn_source_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_VERSION
    assert packet["composes_q35n_adapter_factory"] is True
    assert packet["composes_q35o_no_send_adapter"] is True
    assert packet["requires_low_level_connect_fn_from_runtime_config"] is True
    assert packet["requires_allow_connect_fn_source_flag"] is True
    assert packet["connect_fn_called_at_source_build"] is False
    assert packet["connect_fn_value_returned"] is False
    assert packet["callable_values_forwarded_to_adapter_runtime_config"] is False
    assert packet["no_default_network_client"] is True
    assert packet["send_disabled"] is True
    assert packet["warroom_page_modified"] is False
    assert packet["would_send_to_broker"] is False


def test_q35p_blocks_without_allow_source_or_callable_and_never_calls_connect() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    no_allow = build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(runtime_config=_config(connect), allow_connect_fn_source=False)
    assert no_allow["connect_fn_source_status"] == "receiver_only_client_connect_fn_source_blocked_allow_connect_fn_source_required"
    assert no_allow["adapter_factory_created"] is False

    no_fn = build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(runtime_config={"receiver_endpoint_url": "ws://example.invalid/receiver"}, allow_connect_fn_source=True)
    assert no_fn["connect_fn_source_status"] == "receiver_only_client_connect_fn_source_blocked_connect_fn_required"
    assert no_fn["adapter_factory_created"] is False

    non_callable = build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(runtime_config=_config("not-callable"), allow_connect_fn_source=True)
    assert non_callable["connect_fn_source_status"] == "receiver_only_client_connect_fn_source_blocked_connect_fn_not_callable"
    assert non_callable["adapter_factory_created"] is False
    assert calls == []


def test_q35p_creates_adapter_factory_but_q35n_socket_guards_block_before_connect() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(compact_status_badge_packet=_badge(), runtime_config=_config(connect), allow_connect_fn_source=True, allow_adapter_factory=True, operator_scope_ack=True)
    assert packet["connect_fn_source_status"] == "receiver_only_client_connect_fn_source_ready_to_build_q35o_adapter_factory_no_send"
    assert packet["adapter_factory_created"] is True
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_blocked_socket_open_request_required"
    assert packet["adapter_factory_called"] is False
    assert packet["socket_open_attempted"] is False
    assert calls == []


def test_q35p_calls_connect_once_only_after_q35n_q35m_q35l_and_q35o_allow_guards() -> None:
    calls: list[tuple[str, Mapping[str, Any]]] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append((endpoint, dict(config)))
        return {"socket_opened": True, "endpoint_url": endpoint, "auth_token": config.get("auth_token"), "connection_id": "fake-q35p"}

    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(
        compact_status_badge_packet=_badge(),
        runtime_config=_config(connect),
        allow_connect_fn_source=True,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert calls == [("ws://example.invalid/receiver", {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35p", "allow_adapter_open": True, "auth_token": "secret-token"})]
    assert packet["adapter_factory_called"] is True
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_opened_no_send"
    assert packet["socket_opened"] is True
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["send_disabled"] is True
    assert packet["runtime_config_keys"] == ["adapter_name", "allow_adapter_open", "auth_token", "low_level_connect_fn", "receiver_endpoint_url"]
    assert packet["adapter_runtime_config_keys"] == ["adapter_name", "allow_adapter_open", "auth_token", "receiver_endpoint_url"]
    assert "secret-token" not in str(packet)


def test_q35p_q35o_embedded_allow_adapter_open_still_blocks_connect() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    config = _config(connect)
    config["allow_adapter_open"] = False
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(compact_status_badge_packet=_badge(), runtime_config=config, allow_connect_fn_source=True, allow_adapter_factory=True, operator_scope_ack=True, socket_open_requested=True, operator_socket_open_ack=True, allow_socket_open=True)
    assert packet["adapter_factory_called"] is True
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_attempt_failed_no_send"
    assert packet["socket_opened"] is False
    assert calls == []


def test_q35p_does_not_modify_page_or_exports_or_import_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 220
    assert "CONNECT_FN_SOURCE" not in transport_init
    assert "CONNECT_FN_SOURCE" not in v2_init
    assert "ws_receiver_only_client_connect_fn_source" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35P module"


def test_q35p_doc_records_connect_fn_source_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "requires_low_level_connect_fn_from_runtime_config=true" in doc
    assert "connect_fn_called_at_source_build=false" in doc
    assert "callable_values_forwarded_to_adapter_runtime_config=false" in doc
    assert "no_default_network_client=true" in doc
    assert "not_sending_external_messages=true" in doc
