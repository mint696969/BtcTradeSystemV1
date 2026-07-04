# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_q35r.py
# desc: PS-Q35R guards for receiver-only registry surface hidden readback. Metadata-only; no values, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface import build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_VERSION,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_contract,
    build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35R_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/__init__.py"
V2_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py"


def _badge() -> dict[str, object]:
    return {"compact_status_badge_visible_now": True, "receiver_state_presence_label": "present", "receiver_readback_label": "ready", "receiver_state_message_count": 13}


def _config() -> dict[str, object]:
    return {"receiver_endpoint_url": "ws://example.invalid/receiver", "adapter_name": "q35r", "allow_adapter_open": True, "auth_token": "secret-token", "connect_fn_registration_key": "paper"}


def _surface_packet(*, all_guards: bool = False) -> tuple[dict[str, Any], list[str]]:
    calls: list[str] = []

    def connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
        calls.append(endpoint)
        return {"socket_opened": True, "endpoint_url": endpoint, "auth_token": config.get("auth_token")}

    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
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
    return packet, calls


def test_q35r_contract_is_hidden_metadata_only_readback_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_contract()
    assert packet["registry_surface_readback_version"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_VERSION
    assert packet["requires_registry_surface_packet"] is True
    assert packet["requires_allow_registry_surface_readback_flag"] is True
    assert packet["read_only"] is True
    assert packet["metadata_only"] is True
    assert packet["hidden_readback_diagnostic"] is True
    assert packet["raw_registry_surface_packet_returned"] is False
    assert packet["registry_keys_returned"] is False
    assert packet["runtime_config_keys_returned"] is False
    assert packet["callable_values_returned"] is False
    assert packet["connect_fn_called_at_readback"] is False
    assert packet["no_default_network_client"] is True
    assert packet["send_disabled"] is True


def test_q35r_blocks_without_allow_or_valid_packet() -> None:
    valid_packet, _ = _surface_packet()
    no_allow = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet(valid_packet)
    assert no_allow["registry_surface_readback_status"] == "receiver_only_client_connect_fn_registry_surface_readback_blocked_allow_readback_required"
    assert no_allow["registry_surface_readback_ready"] is False

    missing = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet(None, allow_registry_surface_readback=True)
    assert missing["registry_surface_readback_status"] == "receiver_only_client_connect_fn_registry_surface_readback_missing_packet"

    invalid = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet("not-a-packet", allow_registry_surface_readback=True)
    assert invalid["registry_surface_readback_status"] == "receiver_only_client_connect_fn_registry_surface_readback_invalid_packet"

    unrecognized = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet({"packet_kind": "other"}, allow_registry_surface_readback=True)
    assert unrecognized["registry_surface_readback_status"] == "receiver_only_client_connect_fn_registry_surface_readback_unrecognized_packet"


def test_q35r_reads_registry_ready_waiting_socket_guards_without_calling_connect() -> None:
    surface_packet, calls = _surface_packet(all_guards=False)
    assert calls == []
    readback = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet(surface_packet, allow_registry_surface_readback=True)
    assert readback["registry_surface_readback_status"] == "receiver_only_client_connect_fn_registry_surface_readback_present_hidden_no_send"
    assert readback["registry_surface_ready"] is True
    assert readback["connect_fn_source_ready"] is True
    assert readback["adapter_factory_called"] is False
    assert readback["socket_open_attempted"] is False
    assert readback["socket_opened"] is False
    assert readback["readback_readiness_label"] == "ready_waiting_socket_guards"
    assert calls == []


def test_q35r_reads_opened_packet_without_returning_raw_values_or_callables() -> None:
    surface_packet, calls = _surface_packet(all_guards=True)
    assert calls == ["ws://example.invalid/receiver"]
    calls.clear()
    readback = build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet(surface_packet, allow_registry_surface_readback=True)
    assert readback["socket_opened"] is True
    assert readback["client_started"] is True
    assert readback["adapter_factory_called"] is True
    assert readback["readback_readiness_label"] == "opened_no_send"
    assert readback["raw_registry_surface_packet_returned"] is False
    assert readback["registry_keys_returned"] is False
    assert readback["runtime_config_keys_returned"] is False
    assert readback["callable_values_returned"] is False
    assert "paper" not in str(readback)
    assert "secret-token" not in str(readback)
    assert "ws://example.invalid/receiver" not in str(readback)
    assert calls == []


def test_q35r_does_not_modify_page_or_exports_or_import_network_client() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    transport_init = TRANSPORT_INIT.read_text(encoding="utf-8-sig")
    v2_init = V2_INIT.read_text(encoding="utf-8-sig")
    assert len(module.splitlines()) <= 220
    assert "REGISTRY_SURFACE_READBACK" not in transport_init
    assert "REGISTRY_SURFACE_READBACK" not in v2_init
    assert "ws_receiver_only_client_connect_fn_registry_surface_readback" not in page
    forbidden_module = ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "sse.", "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92))
    for token in forbidden_module:
        assert token not in module, f"forbidden token {token!r} found in Q35R module"


def test_q35r_doc_records_hidden_readback_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "raw_registry_surface_packet_returned=false" in doc
    assert "registry_keys_returned=false" in doc
    assert "runtime_config_keys_returned=false" in doc
    assert "connect_fn_called_at_readback=false" in doc
    assert "not_sending_external_messages=true" in doc
