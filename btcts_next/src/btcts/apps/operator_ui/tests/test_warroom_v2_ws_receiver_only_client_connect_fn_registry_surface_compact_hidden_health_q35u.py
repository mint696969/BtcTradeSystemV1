# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_q35u.py
# desc: PS-Q35U guards for receiver-only compact hidden health summary. Metadata-only; no raw values, no page, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface import build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback import build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record import apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback import build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_COMPACT_HIDDEN_HEALTH_VERSION,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_contract,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35U_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_REGISTRY_SURFACE_COMPACT_HIDDEN_HEALTH_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _hidden_record_readback(*, all_guards: bool = False) -> tuple[dict[str, Any], list[str]]:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True, "endpoint_url": endpoint, "auth_token": config.get("auth_token")}

    surface = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
        compact_status_badge_packet={"compact_status_badge_visible_now": True, "receiver_state_message_count": 16},
        runtime_config={"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35u", "allow_adapter_open": True, "auth_token": "secret-token", "connect_fn_registration_key": "paper"},
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
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet(state, allow_hidden_record_readback=True)
    return packet, calls


def test_q35u_contract_is_compact_hidden_health_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_contract()
    assert packet["compact_hidden_health_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_COMPACT_HIDDEN_HEALTH_VERSION
    assert packet["hidden_health_summary"] is True
    assert packet["receiver_safe_to_remain_idle"] is True
    assert packet["raw_hidden_record_readback_returned"] is False
    assert packet["session_state_keys_returned"] is False
    assert packet["connect_fn_called_at_compact_health"] is False
    assert packet["send_disabled"] is True


def test_q35u_blocks_without_allow_missing_invalid_or_unrecognized_readback() -> None:
    valid, _ = _hidden_record_readback()
    assert build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet(valid)["compact_hidden_health_status"] == "receiver_only_client_registry_surface_compact_hidden_health_blocked_allow_health_required"
    assert build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet(None, allow_compact_hidden_health=True)["compact_hidden_health_status"] == "receiver_only_client_registry_surface_compact_hidden_health_missing_readback"
    assert build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet("bad", allow_compact_hidden_health=True)["compact_hidden_health_status"] == "receiver_only_client_registry_surface_compact_hidden_health_invalid_readback"
    assert build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet({"packet_kind": "other"}, allow_compact_hidden_health=True)["compact_hidden_health_status"] == "receiver_only_client_registry_surface_compact_hidden_health_unrecognized_readback"


def test_q35u_summarizes_waiting_socket_guards_without_raw_values_or_connect() -> None:
    readback, calls = _hidden_record_readback(all_guards=False)
    assert calls == []
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet(readback, allow_compact_hidden_health=True)
    assert packet["compact_hidden_health_ready"] is True
    assert packet["receiver_health_status"] == "waiting_socket_guards"
    assert packet["cp1_health_summary_ready"] is True
    assert packet["receiver_safe_to_remain_idle"] is True
    assert "paper" not in str(packet)
    assert "secret-token" not in str(packet)
    assert "ws://example.invalid/receiver" not in str(packet)
    assert calls == []


def test_q35u_doc_and_module_preserve_hidden_no_page_no_export_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert "receiver_health_status" in module
    assert "raw_hidden_record_readback_returned=false" in doc
    assert "receiver_safe_to_remain_idle=true" in doc
    assert "not_sending_external_messages=true" in doc
    assert "COMPACT_HIDDEN_HEALTH" not in transport_init
    assert "COMPACT_HIDDEN_HEALTH" not in v2_init
    assert "ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health" not in page
    for token in ("import streamlit", "from streamlit", "import websockets", "from websockets", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92)):
        assert token not in module
