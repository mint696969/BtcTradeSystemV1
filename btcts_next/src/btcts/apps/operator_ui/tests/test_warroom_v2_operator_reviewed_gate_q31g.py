# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_reviewed_gate_q31g.py
# desc: PS-Q31G guards for WarRoom v2 operator-reviewed local transport enablement gate.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_operator_gate_evidence_snapshot,
    build_warroom_v2_operator_gate_review_packet,
    build_warroom_v2_operator_reviewed_gate_contract,
    evaluate_warroom_v2_operator_reviewed_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31G_WARROOM_V2_OPERATOR_REVIEWED_LOCAL_TRANSPORT_ENABLEMENT_GATE_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def _evidence() -> dict[str, str]:
    return {
        "q31f_focused_guard": "6_passed",
        "q31f_close_guard": "68_passed",
        "q31f_py_compile": "passed",
        "q31e_focused_guard": "5_passed",
        "q31d_focused_guard": "7_passed",
        "q31c_focused_guard": "7_passed",
        "q31b_focused_guard": "7_passed",
        "q31a_focused_guard": "8_passed",
    }


def test_q31g_contract_is_gate_only_and_disabled_effective() -> None:
    packet = build_warroom_v2_operator_reviewed_gate_contract()
    assert packet["gate_kind"] == "operator_reviewed_local_transport_enablement_decision_contract"
    assert packet["approval_token_required"] == WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN
    assert packet["candidate_transport_path_default"] == "local_only_in_process"
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["approval_required_before_enable"] is True
    assert packet["approval_recorded_default"] is False
    assert packet["transport_enabled_effective"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31g_missing_guard_evidence_blocks_gate() -> None:
    snapshot = build_warroom_v2_operator_gate_evidence_snapshot({"q31f_focused_guard": "6_passed"})
    evaluation = evaluate_warroom_v2_operator_reviewed_gate(evidence={"q31f_focused_guard": "6_passed"}, operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN)
    assert snapshot["ok"] is False
    assert "q31f_close_guard" in snapshot["missing_or_failed_guards"]
    assert evaluation["gate_status"] == "blocked_missing_guard_evidence"
    assert evaluation["ready_for_next_slice"] is False
    assert evaluation["transport_enabled_effective"] is False


def test_q31g_missing_operator_approval_blocks_gate_even_when_guards_pass() -> None:
    evaluation = evaluate_warroom_v2_operator_reviewed_gate(evidence=_evidence(), operator_approval_token="")
    assert evaluation["gate_status"] == "blocked_waiting_for_operator_approval"
    assert evaluation["operator_approval_recorded"] is False
    assert evaluation["ready_for_next_slice"] is False
    assert evaluation["local_loop_enabled_effective"] is False
    assert evaluation["message_emission_enabled"] is False


def test_q31g_unsupported_live_transport_paths_are_blocked() -> None:
    for path in ["websocket", "sse"]:
        evaluation = evaluate_warroom_v2_operator_reviewed_gate(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN, requested_transport_path=path)
        assert evaluation["gate_status"] == "blocked_unsupported_transport_path"
        assert evaluation["ready_for_next_slice"] is False
        assert evaluation["websocket_enabled"] is False
        assert evaluation["sse_enabled"] is False


def test_q31g_explicit_local_approval_only_marks_next_slice_ready_not_enabled_here() -> None:
    evaluation = evaluate_warroom_v2_operator_reviewed_gate(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN)
    assert evaluation["gate_status"] == "ready_for_next_slice_not_enabled_here"
    assert evaluation["ready_for_next_slice"] is True
    assert evaluation["next_slice_after_approval"] == "PS-Q31H_LOCAL_ONLY_TRUE_TRANSPORT_EXPERIMENT"
    assert evaluation["not_enabled_here"] is True
    assert evaluation["transport_enabled_effective"] is False
    assert evaluation["producer_enabled_effective"] is False
    assert evaluation["consumer_enabled_effective"] is False
    assert evaluation["message_emission_enabled"] is False


def test_q31g_review_packet_preserves_display_scope_and_disabled_boundary() -> None:
    packet = build_warroom_v2_operator_gate_review_packet(evidence=_evidence())
    assert packet["packet_kind"] == "operator_reviewed_local_transport_gate_review_packet"
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["visible_ui_decoration_added"] is False
    assert packet["fragment_refresh_replaced"] is False
    assert packet["transport_enabled_effective"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31g_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "gate_module=" in text
    assert "approval_required_before_enable=true" in text
    assert "transport_enabled_effective=false" in text
    assert "not_enabling_websocket=true" in text
    assert "not_invoking_prediction_inference=true" in text
    forbidden = (
        "import streamlit",
        "from streamlit",
        "websocket.",
        "sse.",
        "send_to_broker(",
        "append_ledger(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "run_prediction(",
        "invoke_classifier(",
        "st.write(",
        "st.metric(",
        "st.caption(",
        "D:" + chr(92),
        "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
