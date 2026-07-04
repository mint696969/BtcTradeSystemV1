# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_completion_q36q.py
# desc: PS-Q36Q guards for CP5 message normalizer completion. Full CP5 pipeline close before CP6.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_completion import build_warroom_v2_ws_receiver_only_client_cp5_completion_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_contract import build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_core import build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_fake_source_normalization import build_warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_live_shaped_fixture_normalization import build_warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_invalid_message_handling import build_warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_normalized_state_readback import apply_warroom_v2_ws_receiver_only_client_cp5_normalized_state_write, build_warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_no_send_traceability_guard import build_warroom_v2_ws_receiver_only_client_cp5_no_send_traceability_guard_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36Q_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_COMPLETION_NO_SEND_2026-07-04.md"


def test_q36q_closes_full_cp5_pipeline() -> None:
    q36j = build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_close_handoff_packet", "cp4_close_ready": True}, allow_cp5_contract=True)
    q36k = build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet(q36j, allow_core_normalization=True)
    fake_source = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet", "fake_message_source_ready": True, "fake_message_summaries": [{"topic": "fake.btc.tick", "symbol": "BTC", "sequence": 1}, {"topic": "fake.heartbeat", "symbol": "BTC", "sequence": 2}]}
    q36l = build_warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet(fake_source, normalizer_core_packet=q36k, allow_fake_source_normalization=True)
    q36m = build_warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_packet(q36k, allow_live_shaped_fixture_normalization=True)
    q36n = build_warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_packet(q36k, allow_invalid_message_handling=True)
    state: dict[str, object] = {}
    q36o_write = apply_warroom_v2_ws_receiver_only_client_cp5_normalized_state_write(state, fake_source_normalization_packet=q36l, live_shaped_fixture_normalization_packet=q36m, invalid_message_handling_packet=q36n, allow_normalized_state_write=True)
    q36o = build_warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet(state, state_key=q36o_write["state_key"], allow_normalized_state_readback=True)
    q36p = build_warroom_v2_ws_receiver_only_client_cp5_no_send_traceability_guard_packet(q36o, allow_cp5_no_send_guard=True)
    q36q = build_warroom_v2_ws_receiver_only_client_cp5_completion_packet(q36p, allow_cp5_completion=True)
    assert q36l["message_count"] == 2
    assert q36o["message_count"] == 7
    assert q36p["cp5_no_send_guard_ready"] is True
    assert q36q["cp5_completed"] is True
    assert q36q["next_checkpoint"] == "CP6_receiver_adapter_live_no_send_preparation"
    assert "cp5_completed=true" in DOC.read_text(encoding="utf-8-sig")
