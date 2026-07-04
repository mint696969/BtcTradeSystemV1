# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_q37d.py
# desc: PS-Q37D guards CP7 adapter interface shape; metadata only, no runtime websocket import.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp7_adapter_interface_shape import build_warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q37D_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP7_ADAPTER_INTERFACE_SHAPE_NO_SEND_2026-07-05.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_adapter_interface_shape.py"


def test_q37d_shape_is_metadata_only_and_has_no_runtime_import() -> None:
    descriptor = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet", "redacted_endpoint_descriptor_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_packet(descriptor, allow_adapter_shape=True)
    assert packet["adapter_interface_shape_ready"] is True
    assert packet["connect_operation_defined"] is False
    assert packet["send_operation_defined"] is False
    assert packet["socket_opened"] is False
    text = MODULE.read_text(encoding="utf-8-sig")
    assert "import websockets" not in text
    assert "from websockets" not in text
    assert "adapter_interface_shape_ready=true" in DOC.read_text(encoding="utf-8-sig")
