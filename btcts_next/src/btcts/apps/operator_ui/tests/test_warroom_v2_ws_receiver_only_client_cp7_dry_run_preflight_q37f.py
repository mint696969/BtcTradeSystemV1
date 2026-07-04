# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_q37f.py
# desc: PS-Q37F guards CP7 dry-run preflight; descriptor plus no-connect instance, no network/send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp7_dry_run_preflight import build_warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q37F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP7_DRY_RUN_PREFLIGHT_NO_SEND_2026-07-05.md"


def test_q37f_preflight_combines_descriptor_and_instance_without_connect() -> None:
    descriptor = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet", "redacted_endpoint_descriptor_ready": True}
    instance = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_packet", "no_connect_adapter_instance_ready": True, "adapter_interface_shape_kind_recognized": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_packet(cp7_redacted_endpoint_descriptor_packet=descriptor, cp7_no_connect_adapter_instance_packet=instance, allow_preflight=True)
    assert packet["dry_run_preflight_ready"] is True
    assert packet["real_adapter_shape_defined"] is True
    assert packet["external_network_used"] is False
    assert packet["client_sends_messages"] is False
    assert "dry_run_preflight_ready=true" in DOC.read_text(encoding="utf-8-sig")
