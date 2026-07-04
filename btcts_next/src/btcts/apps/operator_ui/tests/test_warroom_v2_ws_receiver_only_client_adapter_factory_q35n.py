# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_adapter_factory_q35n.py
# desc: PS-Q35N guards for receiver-only client adapter factory. Explicit runtime config and injected factory only; no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_adapter_factory import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_VERSION,
    build_warroom_v2_ws_receiver_only_client_adapter_factory_contract,
    build_warroom_v2_ws_receiver_only_client_adapter_factory_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_adapter_factory.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35N_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge(*, visible: bool = True, state: str = "present", readback: str = "ready", messages: int = 6) -> dict[str, object]:
    return {"compact_status_badge_visible_now": visible, "receiver_state_presence_label": state, "receiver_readback_label": readback, "receiver_state_message_count": messages}


def _config() -> dict[str, object]:
    return {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "fake"}


def test_q35n_contract_is_configured_adapter_factory_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_contract()
    assert packet["adapter_factory_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_VERSION
    assert packet["composes_q35k_preflight"] is True
    assert packet["composes_q35m_runtime_wiring"] is True
    assert packet["requires_runtime_config"] is True
    assert packet["runtime_config_values_returned"] is False
    assert packet["runtime_config_keys_returned"] is True
    assert packet["requires_endpoint_url_from_runtime_config"] is True
    assert packet["requires_allow_adapter_factory_flag"] is True
    assert packet["requires_injected_adapter_factory"] is True
    assert packet["injected_adapter_factory_only"] is True
    assert packet["no_hardcoded_endpoint"] is True
    assert packet["no_default_network_client"] is True
    assert packet["send_disabled"] is True
    assert packet["client_sends_messages"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["visible_controls_added"] is False
    assert packet["would_send_to_broker"] is False


def test_q35n_does_not_call_factory_when_preflight_not_ready() -> None:
    factory_calls: list[Mapping[str, Any]] = []

    def factory(config: Mapping[str, Any]):
        factory_calls.append(config)
        return lambda endpoint: {"socket_opened": True, "endpoint": endpoint}

    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(state="missing", readback="blocked", messages=0),
        runtime_config=_config(),
        adapter_factory=factory,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_blocked_preflight_required"
    assert packet["adapter_factory_called"] is False
    assert packet["socket_open_attempted"] is False
    assert factory_calls == []


def test_q35n_blocks_without_endpoint_or_allow_flag_before_factory_call() -> None:
    factory_calls: list[Mapping[str, Any]] = []

    def factory(config: Mapping[str, Any]):
        factory_calls.append(config)
        return lambda endpoint: {"socket_opened": True, "endpoint": endpoint}

    no_endpoint = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(),
        runtime_config={"adapter_name": "fake"},
        adapter_factory=factory,
        allow_adapter_factory=True,
        operator_scope_ack=True,
    )
    assert no_endpoint["adapter_factory_status"] == "receiver_only_client_adapter_factory_blocked_endpoint_config_required"
    assert no_endpoint["adapter_factory_called"] is False

    no_allow = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(),
        runtime_config=_config(),
        adapter_factory=factory,
        allow_adapter_factory=False,
        operator_scope_ack=True,
    )
    assert no_allow["adapter_factory_status"] == "receiver_only_client_adapter_factory_blocked_allow_adapter_factory_flag_required"
    assert no_allow["adapter_factory_called"] is False
    assert factory_calls == []


def test_q35n_builds_opener_and_runtime_wiring_calls_it_once_when_all_guards_pass() -> None:
    factory_calls: list[Mapping[str, Any]] = []
    opener_calls: list[str] = []

    def factory(config: Mapping[str, Any]):
        factory_calls.append(config)

        def opener(endpoint: str) -> dict[str, Any]:
            opener_calls.append(endpoint)
            return {"socket_opened": True, "connection_id": "fake-q35n"}

        return opener

    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(messages=9),
        runtime_config=_config(),
        adapter_factory=factory,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_ready_to_build_injected_opener_no_send"
    assert "runtime_config" not in packet
    assert packet["runtime_config_keys"] == ["adapter_name", "receiver_endpoint_url"]
    assert packet["runtime_config_redacted"] == {"present": True, "keys": ["adapter_name", "receiver_endpoint_url"]}
    assert "ws://example.invalid/receiver" not in str({key: value for key, value in packet.items() if key != "runtime_wiring_packet"})
    assert packet["adapter_factory_called"] is True
    assert factory_calls == [_config()]
    assert opener_calls == ["ws://example.invalid/receiver"]
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_opened_no_send"
    assert packet["socket_open_attempted"] is True
    assert packet["socket_opened"] is True
    assert packet["client_started"] is True
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["send_disabled"] is True


def test_q35n_reports_factory_error_without_socket_open_or_send() -> None:
    def factory(config: Mapping[str, Any]):
        raise RuntimeError("factory failed")

    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(),
        runtime_config=_config(),
        adapter_factory=factory,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_failed_exception_no_send"
    assert packet["adapter_factory_called"] is True
    assert packet["adapter_factory_error"]["error_type"] == "RuntimeError"
    assert packet["socket_open_attempted"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False


def test_q35n_reports_non_callable_factory_result_without_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=_badge(),
        runtime_config=_config(),
        adapter_factory=lambda config: {"not": "callable"},
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_failed_non_callable_opener_no_send"
    assert packet["socket_open_attempted"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False


def test_q35n_does_not_modify_page_or_exports_or_import_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "ADAPTER_FACTORY" not in transport_init
    assert "ADAPTER_FACTORY" not in v2_init
    assert "ws_receiver_only_client_adapter_factory" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35N module"


def test_q35n_doc_records_adapter_factory_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "requires_endpoint_url_from_runtime_config=true" in doc
    assert "requires_injected_adapter_factory=true" in doc
    assert "no_default_network_client=true" in doc
    assert "client_sends_messages=false" in doc
    assert "not_sending_external_messages=true" in doc
