# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_q35q.py
# desc: PS-Q35Q guards for receiver-only connect_fn registry surface. Explicit in-memory mapping only; no default client and no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_VERSION,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_contract,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35Q_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge(*, visible: bool = True, state: str = "present", readback: str = "ready", messages: int = 12) -> dict[str, object]:
    return {"compact_status_badge_visible_now": visible, "receiver_state_presence_label": state, "receiver_readback_label": readback, "receiver_state_message_count": messages}


def _config() -> dict[str, object]:
    return {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35q", "allow_adapter_open": True, "auth_token": "secret-token", "connect_fn_registration_key": "paper"}


def test_q35q_contract_is_in_memory_registry_surface_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_contract()
    assert packet["connect_fn_registry_surface_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_VERSION
    assert packet["composes_q35p_connect_fn_source"] is True
    assert packet["requires_registry_mapping"] is True
    assert packet["requires_registration_key_from_runtime_config"] is True
    assert packet["requires_allow_registration_surface_flag"] is True
    assert packet["registry_values_returned"] is False
    assert packet["callable_values_returned"] is False
    assert packet["global_registry_mutated"] is False
    assert packet["direct_connect_fn_from_runtime_config_ignored"] is True
    assert packet["connect_fn_called_at_registration_surface"] is False
    assert packet["no_default_network_client"] is True
    assert packet["send_disabled"] is True
    assert packet["would_send_to_broker"] is False


def test_q35q_blocks_without_allow_key_registration_or_callable_and_never_calls_connect() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    no_allow = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(runtime_config=_config(), connect_fn_registry={"paper": connect})
    assert no_allow["registry_surface_status"] == "receiver_only_client_connect_fn_registry_surface_blocked_allow_registration_surface_required"

    no_key = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(runtime_config={"receiver_endpoint_url": "ws://example.invalid/receiver"}, connect_fn_registry={"paper": connect}, allow_registration_surface=True)
    assert no_key["registry_surface_status"] == "receiver_only_client_connect_fn_registry_surface_blocked_registration_key_required"

    missing = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(runtime_config=_config(), connect_fn_registry={}, allow_registration_surface=True)
    assert missing["registry_surface_status"] == "receiver_only_client_connect_fn_registry_surface_blocked_registration_missing"

    bad = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(runtime_config=_config(), connect_fn_registry={"paper": "not-callable"}, allow_registration_surface=True)
    assert bad["registry_surface_status"] == "receiver_only_client_connect_fn_registry_surface_blocked_registration_not_callable"
    assert calls == []


def test_q35q_ignores_direct_connect_fn_in_runtime_config_until_registry_guards_pass() -> None:
    calls: list[str] = []

    def direct_connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    config = _config()
    config["low_level_connect_fn"] = direct_connect
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
        runtime_config=config,
        connect_fn_registry={},
        allow_registration_surface=False,
        allow_connect_fn_source=True,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert packet["registry_surface_status"] == "receiver_only_client_connect_fn_registry_surface_blocked_allow_registration_surface_required"
    assert packet["connect_fn_source_status"] == "receiver_only_client_connect_fn_source_blocked_connect_fn_required"
    assert packet["adapter_factory_called"] is False
    assert "low_level_connect_fn" not in packet["adapter_runtime_config_keys"]
    assert calls == []


def test_q35q_resolves_registry_but_q35p_source_allow_still_blocks() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(runtime_config=_config(), connect_fn_registry={"paper": connect}, allow_registration_surface=True, allow_connect_fn_source=False)
    assert packet["registry_surface_status"] == "receiver_only_client_connect_fn_registry_surface_ready_to_call_q35p_source_no_send"
    assert packet["connect_fn_source_status"] == "receiver_only_client_connect_fn_source_blocked_allow_connect_fn_source_required"
    assert packet["adapter_factory_called"] is False
    assert calls == []


def test_q35q_resolves_registry_but_q35n_socket_guards_block_before_connect() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(compact_status_badge_packet=_badge(), runtime_config=_config(), connect_fn_registry={"paper": connect}, allow_registration_surface=True, allow_connect_fn_source=True, allow_adapter_factory=True, operator_scope_ack=True)
    assert packet["connect_fn_source_status"] == "receiver_only_client_connect_fn_source_ready_to_build_q35o_adapter_factory_no_send"
    assert packet["adapter_factory_status"] == "receiver_only_client_adapter_factory_blocked_socket_open_request_required"
    assert packet["adapter_factory_called"] is False
    assert packet["socket_open_attempted"] is False
    assert calls == []


def test_q35q_calls_registered_connect_once_only_after_all_source_socket_and_adapter_guards() -> None:
    calls: list[tuple[str, Mapping[str, Any]]] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append((endpoint, dict(config)))
        return {"socket_opened": True, "endpoint_url": endpoint, "auth_token": config.get("auth_token"), "connection_id": "fake-q35q"}

    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
        compact_status_badge_packet=_badge(),
        runtime_config=_config(),
        connect_fn_registry={"paper": connect},
        allow_registration_surface=True,
        allow_connect_fn_source=True,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=True,
        operator_socket_open_ack=True,
        allow_socket_open=True,
    )
    assert calls == [("ws://example.invalid/receiver", {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35q", "allow_adapter_open": True, "auth_token": "secret-token"})]
    assert packet["adapter_factory_called"] is True
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_opened_no_send"
    assert packet["socket_opened"] is True
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["runtime_config_keys"] == ["adapter_name", "allow_adapter_open", "auth_token", "connect_fn_registration_key", "receiver_endpoint_url"]
    assert packet["adapter_runtime_config_keys"] == ["adapter_name", "allow_adapter_open", "auth_token", "low_level_connect_fn", "receiver_endpoint_url"]
    assert "secret-token" not in str(packet)


def test_q35q_q35o_embedded_allow_adapter_open_still_blocks_registered_connect() -> None:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True}

    config = _config()
    config["allow_adapter_open"] = False
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(compact_status_badge_packet=_badge(), runtime_config=config, connect_fn_registry={"paper": connect}, allow_registration_surface=True, allow_connect_fn_source=True, allow_adapter_factory=True, operator_scope_ack=True, socket_open_requested=True, operator_socket_open_ack=True, allow_socket_open=True)
    assert packet["runtime_wiring_status"] == "receiver_only_client_guarded_socket_open_attempt_failed_no_send"
    assert packet["socket_opened"] is False
    assert calls == []


def test_q35q_does_not_modify_page_or_exports_or_import_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 220
    assert "CONNECT_FN_REGISTRY_SURFACE" not in transport_init
    assert "CONNECT_FN_REGISTRY_SURFACE" not in v2_init
    assert "ws_receiver_only_client_connect_fn_registry_surface" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35Q module"


def test_q35q_doc_records_registry_surface_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "requires_registry_mapping=true" in doc
    assert "global_registry_mutated=false" in doc
    assert "connect_fn_called_at_registration_surface=false" in doc
    assert "no_default_network_client=true" in doc
    assert "not_sending_external_messages=true" in doc
