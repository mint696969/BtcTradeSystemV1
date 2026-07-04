# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_close_handoff_q36i.py
# desc: PS-Q36I guards for full Q35X-Q36I CP4 close handoff. Traceable CP4 completion before CP5.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness import build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness_implementation_gate import build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_minimal_visible_readiness_surface import build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness_readback import build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_close_handoff import build_warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_message_source import build_warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_state_write import STATE_KEY as WRITE_KEY, apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_readback import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_completion import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_close_handoff import build_warroom_v2_ws_receiver_only_client_cp4_close_handoff_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36I_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_CLOSE_COMMIT_HANDOFF_NO_SEND_2026-07-04.md"

def test_q36i_closes_full_q35x_to_q36i_pipeline_without_send() -> None:
    cp1 = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp1_completion_packet", "cp1_completed": True}
    q35x = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet(cp1_completion_packet=cp1, allow_visible_readiness_proposal=True)
    q35y = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet(q35x, allow_implementation_gate=True)
    q35z = build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet(compact_badge_packet={"compact_status_badge_visible_now": True, "compact_badge_markdown": "`WS Receiver` mount ready · no socket/send"}, implementation_gate_packet=q35y, allow_minimal_surface=True)
    q36a = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet(q35z, allow_visible_readiness_readback=True)
    q36b = build_warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet(q36a, allow_cp3_close_handoff=True)
    q36c = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet(q36b, allow_fake_receive_loop_contract=True)
    q36d = build_warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet(q36c, allow_fake_message_source=True)
    state: dict[str, object] = {}
    q36e = apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write(state, fake_message_source_packet=q36d, allow_state_write=True)
    q36f = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_packet(state, state_write_key=WRITE_KEY, allow_readback=True)
    q36g = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard_packet(q36f, allow_no_send_guard=True)
    q36h = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_packet(q36g, allow_cp4_completion=True)
    q36i = build_warroom_v2_ws_receiver_only_client_cp4_close_handoff_packet(q36h, allow_cp4_close=True)
    assert q36e["message_count"] == 3
    assert q36f["latest_message"]["topic"] == "fake.heartbeat"
    assert q36i["cp4_close_ready"] is True
    assert q36i["next_checkpoint"] == "CP5_message_normalizer_no_send"
    assert q36i["client_sends_messages"] is False
    assert "q35x_to_q36i_pipeline_closed=true" in DOC.read_text(encoding="utf-8-sig")
