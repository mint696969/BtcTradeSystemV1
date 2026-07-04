# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_q35t.py
# desc: PS-Q35T guards for receiver-only registry surface hidden-record readback. Metadata-only; no raw record, no page, no socket, no send.

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
    apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record,
)
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_READBACK_VERSION,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_contract,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35T_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_READBACK_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge() -> dict[str, object]:
    return {"compact_status_badge_visible_now": True, "receiver_state_presence_label": "present", "receiver_readback_label": "ready", "receiver_state_message_count": 15}


def _state_with_record(*, all_guards: bool = False) -> tuple[dict[str, Any], list[str]]:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True, "endpoint_url": endpoint, "auth_token": config.get("auth_token")}

    surface = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
        compact_status_badge_packet=_badge(),
        runtime_config={"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35t", "allow_adapter_open": True, "auth_token": "secret-token", "connect_fn_registration_key": "paper"},
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
    state: dict[str, Any] = {}
    apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record(state, registry_surface_readback_packet=readback, hidden_record_requested=True, operator_hidden_record_ack=True)
    return state, calls


def test_q35t_contract_is_metadata_only_hidden_record_readback_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_contract()
    assert packet["hidden_record_readback_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_READBACK_VERSION
    assert packet["source_hidden_record_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY
    assert packet["requires_session_state_mapping"] is True
    assert packet["requires_allow_hidden_record_readback_flag"] is True
    assert packet["read_only"] is True
    assert packet["metadata_only"] is True
    assert packet["raw_hidden_record_value_returned"] is False
    assert packet["session_state_keys_returned"] is False
    assert packet["connect_fn_called_at_hidden_record_readback"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["send_disabled"] is True


def test_q35t_blocks_without_allow_missing_invalid_or_unrecognized_record() -> None:
    state, _ = _state_with_record()
    no_allow = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet(state)
    assert no_allow["hidden_record_readback_status"] == "receiver_only_client_registry_surface_hidden_record_readback_blocked_allow_readback_required"
    assert no_allow["hidden_record_readback_ready"] is False

    missing = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet({}, allow_hidden_record_readback=True)
    assert missing["hidden_record_readback_status"] == "receiver_only_client_registry_surface_hidden_record_readback_missing_record"

    invalid = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet({WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY: "not-mapping"}, allow_hidden_record_readback=True)
    assert invalid["hidden_record_readback_status"] == "receiver_only_client_registry_surface_hidden_record_readback_invalid_record"

    unrecognized = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet({WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY: {"packet_kind": "other"}}, allow_hidden_record_readback=True)
    assert unrecognized["hidden_record_readback_status"] == "receiver_only_client_registry_surface_hidden_record_readback_unrecognized_record"


def test_q35t_reads_ready_waiting_socket_metadata_without_mutation_or_connect() -> None:
    state, calls = _state_with_record(all_guards=False)
    before = dict(state)
    assert calls == []
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet(state, allow_hidden_record_readback=True)
    assert packet["hidden_record_readback_status"] == "receiver_only_client_registry_surface_hidden_record_readback_present_metadata_only_no_send"
    assert packet["hidden_record_readiness_label"] == "recorded_ready_waiting_socket_guards"
    assert packet["registry_surface_ready"] is True
    assert packet["connect_fn_source_ready"] is True
    assert packet["socket_opened"] is False
    assert packet["target_session_state_mutated"] is False
    assert state == before
    assert calls == []


def test_q35t_reads_opened_metadata_without_returning_raw_values() -> None:
    state, calls = _state_with_record(all_guards=True)
    assert calls == ["ws://example.invalid/receiver"]
    calls.clear()
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet(state, allow_hidden_record_readback=True)
    assert packet["hidden_record_readiness_label"] == "recorded_opened_no_send"
    assert packet["socket_opened"] is True
    assert packet["client_started"] is True
    assert packet["raw_hidden_record_value_returned"] is False
    assert packet["session_state_keys_returned"] is False
    assert "paper" not in str(packet)
    assert "secret-token" not in str(packet)
    assert "ws://example.invalid/receiver" not in str(packet)
    assert "hidden_record_value" not in packet
    assert calls == []


def test_q35t_does_not_modify_page_or_exports_or_import_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 220
    assert "HIDDEN_RECORD_READBACK" not in transport_init
    assert "HIDDEN_RECORD_READBACK" not in v2_init
    assert "ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35T module"


def test_q35t_doc_records_hidden_record_readback_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "raw_hidden_record_value_returned=false" in doc
    assert "session_state_keys_returned=false" in doc
    assert "connect_fn_called_at_hidden_record_readback=false" in doc
    assert "warroom_page_modified=false" in doc
    assert "not_sending_external_messages=true" in doc
