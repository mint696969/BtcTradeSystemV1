# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_q35s.py
# desc: PS-Q35S guards for receiver-only registry surface readback hidden session-state record. Default-off metadata-only; no page, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface import build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback import build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY,
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_VERSION,
    apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35S_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge() -> dict[str, object]:
    return {"compact_status_badge_visible_now": True, "receiver_state_presence_label": "present", "receiver_readback_label": "ready", "receiver_state_message_count": 14}


def _config() -> dict[str, object]:
    return {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35s", "allow_adapter_open": True, "auth_token": "secret-token", "connect_fn_registration_key": "paper"}


def _readback_packet(*, all_guards: bool = False) -> tuple[dict[str, Any], list[str]]:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True, "endpoint_url": endpoint, "auth_token": config.get("auth_token")}

    surface = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
        compact_status_badge_packet=_badge(),
        runtime_config=_config(),
        connect_fn_registry={"paper": connect},
        allow_registration_surface=True,
        allow_connect_fn_source=True,
        allow_adapter_factory=True,
        operator_scope_ack=True,
        socket_open_requested=all_guards,
        operator_socket_open_ack=all_guards,
        allow_socket_open=all_guards,
    )
    readback = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet(surface, allow_registry_surface_readback=True)
    return readback, calls


def test_q35s_contract_is_default_off_hidden_session_state_record_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_contract()
    assert packet["registry_surface_readback_hidden_record_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_VERSION
    assert packet["hidden_record_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY
    assert packet["requires_hidden_record_request"] is True
    assert packet["requires_operator_hidden_record_ack"] is True
    assert packet["requires_mutable_session_state_mapping"] is True
    assert packet["record_metadata_only"] is True
    assert packet["raw_readback_packet_recorded"] is False
    assert packet["connect_fn_called_at_hidden_record"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["aggregator_exports_added"] is False
    assert packet["send_disabled"] is True


def test_q35s_default_off_does_not_mutate_session_state() -> None:
    state: dict[str, Any] = {}
    readback, calls = _readback_packet()
    packet = apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record(state, registry_surface_readback_packet=readback)
    assert packet["hidden_record_status"] == "receiver_only_client_registry_surface_readback_hidden_record_default_off"
    assert packet["hidden_record_applied"] is False
    assert packet["target_session_state_mutated"] is False
    assert state == {}
    assert calls == []


def test_q35s_requires_ack_ready_and_session_state_before_recording() -> None:
    readback, _ = _readback_packet()
    no_ack = apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record({}, registry_surface_readback_packet=readback, hidden_record_requested=True)
    assert no_ack["hidden_record_status"] == "receiver_only_client_registry_surface_readback_hidden_record_blocked_operator_ack_required"

    not_ready = apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record({}, registry_surface_readback_packet={}, hidden_record_requested=True, operator_hidden_record_ack=True)
    assert not_ready["hidden_record_status"] == "receiver_only_client_registry_surface_readback_hidden_record_blocked_readback_ready_required"

    no_state = apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record(None, registry_surface_readback_packet=readback, hidden_record_requested=True, operator_hidden_record_ack=True)
    assert no_state["hidden_record_status"] == "receiver_only_client_registry_surface_readback_hidden_record_blocked_session_state_required"


def test_q35s_records_metadata_only_value_without_raw_packet_or_sensitive_values() -> None:
    state: dict[str, Any] = {}
    readback, calls = _readback_packet(all_guards=True)
    assert calls == ["ws://example.invalid/receiver"]
    calls.clear()
    packet = apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record(state, registry_surface_readback_packet=readback, hidden_record_requested=True, operator_hidden_record_ack=True)
    assert packet["hidden_record_status"] == "receiver_only_client_registry_surface_readback_hidden_record_applied_no_send"
    assert packet["hidden_record_applied"] is True
    assert packet["target_session_state_mutated"] is True
    assert WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY in state
    value = state[WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY]
    assert value == packet["hidden_record_value"]
    assert value["readback_readiness_label"] == "opened_no_send"
    assert value["socket_opened"] is True
    assert value["metadata_only"] is True
    assert value["raw_registry_surface_packet_returned"] is False
    assert "paper" not in str(packet)
    assert "secret-token" not in str(packet)
    assert "ws://example.invalid/receiver" not in str(packet)
    assert calls == []


def test_q35s_does_not_modify_page_or_exports_or_import_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 220
    assert "REGISTRY_SURFACE_READBACK_HIDDEN_RECORD" not in transport_init
    assert "REGISTRY_SURFACE_READBACK_HIDDEN_RECORD" not in v2_init
    assert "ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35S module"


def test_q35s_doc_records_hidden_record_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "record_metadata_only=true" in doc
    assert "raw_readback_packet_recorded=false" in doc
    assert "connect_fn_called_at_hidden_record=false" in doc
    assert "warroom_page_modified=false" in doc
    assert "not_sending_external_messages=true" in doc
