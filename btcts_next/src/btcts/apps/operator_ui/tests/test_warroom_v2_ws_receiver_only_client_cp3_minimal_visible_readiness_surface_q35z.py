# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_q35z.py
# desc: PS-Q35Z guards for CP3 minimal visible readiness surface on existing compact badge. No controls, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_minimal_visible_readiness_surface import build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet  # noqa: E402

MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_minimal_visible_readiness_surface.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35Z_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP3_MINIMAL_VISIBLE_READINESS_SURFACE_NO_SEND_2026-07-04.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _gate() -> dict[str, object]:
    return {"packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet", "cp3_visible_readiness_implementation_gate_ready": True, "receiver_visible_readiness_label": "cp1_ready"}


def _badge() -> dict[str, object]:
    return {"compact_status_badge_visible_now": True, "compact_badge_markdown": "`WS Receiver` mount ready · no socket/send"}


def test_q35z_builds_minimal_surface_on_existing_badge() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet(compact_badge_packet=_badge(), implementation_gate_packet=_gate(), allow_minimal_surface=True)
    assert packet["cp3_minimal_visible_readiness_surface_visible_now"] is True
    assert packet["visible_readiness_markdown"].endswith("readiness=cp1_ready · live=off")
    assert packet["visible_controls_added"] is False


def test_q35z_page_uses_existing_badge_markdown_call_only() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_cp3_minimal_visible_readiness_surface" in page
    assert "build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet" in page
    assert "build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet" in page
    assert page.count('st.markdown(str(badge_packet.get("compact_badge_markdown") or ""))') == 1


def test_q35z_doc_and_module_no_send() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "existing_compact_status_badge=true" in doc
    assert "additional_markdown_calls_added=false" in doc
    assert "not_sending_external_messages=true" in doc
    for token in ("import streamlit", "from streamlit", "import websockets", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier("):
        assert token not in module
