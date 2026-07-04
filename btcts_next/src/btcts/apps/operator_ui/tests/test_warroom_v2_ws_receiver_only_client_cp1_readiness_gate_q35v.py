# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_q35v.py
# desc: PS-Q35V guards for receiver-only CP1 readiness gate. Metadata-only; no raw values, no page, no socket, no send.

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
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health import build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp1_readiness_gate import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP1_READINESS_GATE_VERSION,
    build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_contract,
    build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp1_readiness_gate.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35V_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP1_READINESS_GATE_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _health_packet() -> dict[str, Any]:
    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        return {"socket_opened": True}

    surface = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
        compact_status_badge_packet={"compact_status_badge_visible_now": True},
        runtime_config={"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35v", "allow_adapter_open": True, "auth_token": "secret-token", "connect_fn_registration_key": "paper"},
        connect_fn_registry={"paper": connect},
        allow_registration_surface=True,
        allow_connect_fn_source=True,
        allow_adapter_factory=True,
        operator_scope_ack=True,
    )
    readback = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet(surface, allow_registry_surface_readback=True)
    state: dict[str, Any] = {}
    apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record(state, registry_surface_readback_packet=readback, hidden_record_requested=True, operator_hidden_record_ack=True)
    hidden_readback = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet(state, allow_hidden_record_readback=True)
    return build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet(hidden_readback, allow_compact_hidden_health=True)


def test_q35v_contract_is_cp1_readiness_gate_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_contract()
    assert packet["cp1_readiness_gate_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP1_READINESS_GATE_VERSION
    assert packet["requires_compact_hidden_health_packet"] is True
    assert packet["raw_compact_hidden_health_packet_returned"] is False
    assert packet["connect_fn_called_at_cp1_gate"] is False
    assert packet["send_disabled"] is True


def test_q35v_blocks_without_allow_missing_invalid_or_unrecognized_health() -> None:
    health = _health_packet()
    assert build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet(health)["cp1_readiness_gate_status"] == "receiver_only_client_cp1_readiness_gate_blocked_allow_gate_required"
    assert build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet(None, allow_cp1_readiness_gate=True)["cp1_readiness_gate_status"] == "receiver_only_client_cp1_readiness_gate_missing_health"
    assert build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet("bad", allow_cp1_readiness_gate=True)["cp1_readiness_gate_status"] == "receiver_only_client_cp1_readiness_gate_invalid_health"
    assert build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet({"packet_kind": "other"}, allow_cp1_readiness_gate=True)["cp1_readiness_gate_status"] == "receiver_only_client_cp1_readiness_gate_unrecognized_health"


def test_q35v_accepts_compact_health_as_cp1_done_candidate() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet(_health_packet(), allow_cp1_readiness_gate=True)
    assert packet["cp1_readiness_gate_status"] == "receiver_only_client_cp1_readiness_gate_ready_no_send"
    assert packet["cp1_done_candidate"] is True
    assert packet["receiver_health_status"] == "waiting_socket_guards"
    assert packet["cp1_checkpoint_label"] == "safe_receiver_preparation_state_ready"
    assert "paper" not in str(packet)
    assert "secret-token" not in str(packet)


def test_q35v_doc_and_module_preserve_cp1_no_page_no_export_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "cp1_done_candidate" in module
    assert "cp1_done_candidate=true" in doc
    assert "raw_compact_hidden_health_packet_returned=false" in doc
    assert "not_sending_external_messages=true" in doc
    assert "ws_receiver_only_client_cp1_readiness_gate" not in page
    for token in ("import streamlit", "from streamlit", "import websockets", "from websockets", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92)):
        assert token not in module
