# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_q37e.py
# desc: PS-Q37E guards CP7 no-connect adapter instance; no runtime client and no socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp7_no_connect_adapter_instance import build_warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q37E_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP7_NO_CONNECT_ADAPTER_INSTANCE_NO_SEND_2026-07-05.md"


def test_q37e_instance_is_metadata_only_no_client() -> None:
    shape = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_packet", "adapter_interface_shape_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_packet(shape, allow_no_connect_instance=True)
    assert packet["no_connect_adapter_instance_ready"] is True
    assert packet["runtime_adapter_object_created"] is False
    assert packet["runtime_client_object_created"] is False
    assert packet["client_started"] is False
    assert packet["socket_opened"] is False
    assert "no_connect_adapter_instance_ready=true" in DOC.read_text(encoding="utf-8-sig")
