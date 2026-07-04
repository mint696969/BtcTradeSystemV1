# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_no_send_adapter_q35o.py
# desc: PS-Q35O guards for receiver-only no-send adapter implementation. Explicit low-level connect injection only; no live network tests and no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_adapter_factory import build_warroom_v2_ws_receiver_only_client_adapter_factory_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_no_send_adapter import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_VERSION,
    WarRoomV2ReceiverOnlyClientNoSendAdapter,
    build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract,
    build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory,
    build_warroom_v2_ws_receiver_only_client_no_send_adapter_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_no_send_adapter.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35O_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_IMPLEMENTATION_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge(*, visible: bool = True, state: str = "present", readback: str = "ready", messages: int = 10) -> dict[str, object]:
    return {"compact_status_badge_visible_now": visible, "receiver_state_presence_label": state, "receiver_readback_label": readback, "receiver_state_message_count": messages}


def _config() -> dict[str, object]:
    return {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35o", "auth_token": "secret-token"}


def test_q35o_contract_is_no_send_adapter_implementation() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract()
    assert packet["no_send_adapter_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_VERSION
    assert packet["requires_low_level_connect_fn"] is True
    assert packet["low_level_connect_fn_injected_only"] is True
    assert packet["factory_creation_connects"] is False
    assert packet["adapter_open_allowed_only_after_allow_flag"] is True
    assert packet["factory_embeds_allow_adapter_open_from_runtime_config"] is True
    assert packet["injected_adapter_factory_compatible"] is True
    assert packet["runtime_config_values_returned"] is False
    assert packet["connect_result_sanitized"] is True
    assert packet["no_hardcoded_endpoint"] is True
    assert packet["no_default_network_client"] is True
    assert packet["send_disabled"] is True
    assert packet["client_sends_messages"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["visible_controls_added"] is False
    assert packet["would_send_to_broker"] is False


def test_q35o_packet_blocks_without_connect_fn_or_allow_flag() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    no_connect = build_warroom_v2_ws_receiver_only_client_no_send_adapter_packet(endpoint_url="ws://example.invalid/receiver", runtime_config=_config(), connect_fn=None, allow_adapter_open=True)
    assert no_connect["adapter_open_status"] == "receiver_only_client_no_send_adapter_blocked_injected_connect_fn_required"
    assert no_connect["connect_called"] is False

    no_allow = build_warroom_v2_ws_receiver_only_client_no_send_adapter_packet(endpoint_url="ws://example.invalid/receiver", runtime_config=_config(), connect_fn=connect, allow_adapter_open=False)
    assert no_allow["adapter_open_status"] == "receiver_only_client_no_send_adapter_blocked_allow_adapter_open_flag_required"
    assert no_allow["connect_called"] is False
    assert calls == []


def test_q35o_adapter_open_calls_injected_connect_once_and_sanitizes_values() -> None:
    calls: list[tuple[str, Mapping[str, Any]]] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append((endpoint, dict(config)))
        return {"socket_opened": True, "endpoint_url": endpoint, "auth_token": config.get("auth_token"), "connection_id": "fake-q35o"}

    packet = build_warroom_v2_ws_receiver_only_client_no_send_adapter_packet(endpoint_url="ws://example.invalid/receiver", runtime_config=_config(), connect_fn=connect, allow_adapter_open=True)
    assert calls == [("ws://example.invalid/receiver", _config())]
    assert packet["adapter_open_status"] == "receiver_only_client_no_send_adapter_opened_no_send"
    assert packet["connect_called"] is True
    assert packet["socket_opened"] is True
    assert packet["client_started"] is True
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["send_disabled"] is True
    assert packet["runtime_config_keys"] == ["adapter_name", "auth_token", "receiver_endpoint_url"]
    assert packet["runtime_config_redacted"] == {"present": True, "keys": ["adapter_name", "auth_token", "receiver_endpoint_url"]}
    assert packet["connect_result"]["endpoint_url"] == "<redacted>"
    assert packet["connect_result"]["auth_token"] == "<redacted>"
    assert "secret-token" not in str(packet)


def test_q35o_adapter_open_reports_connect_failure_as_data_without_send() -> None:
    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        raise RuntimeError("connect failed")

    adapter = WarRoomV2ReceiverOnlyClientNoSendAdapter(connect_fn=connect, runtime_config=_config(), allow_adapter_open=True)
    packet = adapter.open("ws://example.invalid/receiver")
    assert packet["adapter_open_status"] == "receiver_only_client_no_send_adapter_attempt_failed_no_send"
    assert packet["connect_called"] is True
    assert packet["connect_error"]["error_type"] == "RuntimeError"
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False


def test_q35o_direct_adapter_open_blocks_without_allow_flag() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    adapter = WarRoomV2ReceiverOnlyClientNoSendAdapter(connect_fn=connect, runtime_config=_config())
    packet = adapter.open("ws://example.invalid/receiver")
    assert packet["adapter_open_status"] == "receiver_only_client_no_send_adapter_blocked_allow_adapter_open_flag_required"
    assert packet["connect_called"] is False
    assert packet["socket_opened"] is False
    assert calls == []


def test_q35o_factory_creation_does_not_connect_and_q35n_calls_opener_once_after_guards() -> None:
    connect_calls: list[tuple[str, Mapping[str, Any]]] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        connect_calls.append((endpoint, dict(config)))
        return {"socket_opened": True, "connection_id": "fake-q35o-q35n"}

    adapter_factory = build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory(connect_fn=connect, base_runtime_config={"base_name": "q35o"})
    assert connect_calls == []

    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(),
        runtime_config={**_config(), "allow_adapter_open": True},
        adapter_factory=adapter_factory,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_ready_to_build_injected_opener_no_send"
    assert packet["adapter_factory_called"] is True
    assert connect_calls == [("ws://example.invalid/receiver", {"base_name": "q35o", **_config(), "allow_adapter_open": True})]
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_opened_no_send"
    assert packet["socket_opened"] is True
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False


def test_q35o_factory_with_q35n_blocks_without_embedded_allow_adapter_open() -> None:
    connect_calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        connect_calls.append(endpoint)
        return {"socket_opened": True}

    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(),
        runtime_config=_config(),
        adapter_factory=build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory(connect_fn=connect),
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_ready_to_build_injected_opener_no_send"
    assert packet["adapter_factory_called"] is True
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_attempt_failed_no_send"
    assert packet["socket_open_attempted"] is True
    assert packet["socket_opened"] is False
    assert connect_calls == []


def test_q35o_factory_with_q35n_does_not_connect_when_preflight_blocks() -> None:
    connect_calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        connect_calls.append(endpoint)
        return {"socket_opened": True}

    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(state="missing", readback="blocked", messages=0),
        runtime_config=_config(),
        adapter_factory=build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory(connect_fn=connect),
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_blocked_preflight_required"
    assert packet["adapter_factory_called"] is False
    assert packet["socket_open_attempted"] is False
    assert connect_calls == []


def test_q35o_does_not_modify_page_or_exports_or_import_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "NO_SEND_ADAPTER" not in transport_init
    assert "NO_SEND_ADAPTER" not in v2_init
    assert "ws_receiver_only_client_no_send_adapter" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35O module"


def test_q35o_doc_records_no_send_adapter_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "low_level_connect_fn_injected_only=true" in doc
    assert "factory_creation_connects=false" in doc
    assert "connect_result_sanitized=true" in doc
    assert "no_default_network_client=true" in doc
    assert "client_sends_messages=false" in doc
    assert "not_sending_external_messages=true" in doc
