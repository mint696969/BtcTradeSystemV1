# path: ./tools/test_prediction_system_ps_q10p_actual_review_packet_live_session_seed_gate_guard.py
# desc: Focused guard for PS-Q10P live-session seed gate. It is unmounted and delegates to PS-Q10N only under local-only explicit gates.

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_session_seed_gate import (
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION,
    build_prediction_warroom_actual_review_packet_live_session_seed_gate,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import resolve_prediction_warroom_lowered_display_packet_visibility_review_source
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_session_seed_gate.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
FORBIDDEN_IMPORT_PREFIXES = ("streamlit", "pathlib", "json", "subprocess", "requests", "httpx", "ccxt", "pybitflyer", "websocket", "btcts.collector_vnext", "btcts.autotrade")
FORBIDDEN_MODULE_TOKENS = (
    "import streamlit", "open(", "Path(", "read_text", "read_bytes", "json.load", "json.loads", "write_text", "write_bytes",
    "json.dump", "json.dumps", "subprocess", "st.button", "st.form", "st.checkbox", "st.toggle",
    "build_prediction_warroom_actual_read_operator_runner_scaffold(", "build_prediction_warroom_latest_payload_actual_export_runner(",
    "load_prediction_warroom_latest_payload_read_only(", "allow_actual_read=True", "execute_actual_read=True",
    "place_order(", "send_order(", "create_order(", "append_decision_jsonl", "append_command_ledger_record",
)
FORBIDDEN_PAGE_TOKENS = (
    "prediction_warroom_actual_review_packet_live_session_seed_gate",
    "build_prediction_warroom_actual_review_packet_live_session_seed_gate",
    "warroom_prediction_actual_review_packet_live_session_seed",
    "allow_actual_read=True",
    "execute_actual_read=True",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _actual_display_packet() -> dict[str, Any]:
    payload = build_prediction_warroom_sample_display_packet()
    payload["prediction_run_id"] = "actual_live_session_seed_gate_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:actual_live_session_seed_gate_run_20260621T000000Z"
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["primary_signal_summary"].pop("synthetic_only", None)
    payload["primary_signal_summary"].pop("fixture_only", None)
    payload["boundaries"] = dict(payload["boundaries"])
    payload["boundaries"].pop("synthetic_only", None)
    payload["boundaries"].pop("fixture_only", None)
    payload.pop("synthetic_only", None)
    payload.pop("fixture_only", None)
    return payload


def _review_packet() -> dict[str, Any]:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=_actual_display_packet()).to_dict()
    review = build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=lowering).to_dict()
    assert review["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert review["widget_group_count"] == 6
    return review


def _assert_no_side_effect_flags(packet: dict[str, Any]) -> None:
    for key in (
        "streamlit_import_required", "ui_controls_added", "ui_triggered_loader_execution", "would_load_source_artifacts",
        "would_read_runtime_file", "would_decode_payload", "would_write_runtime_artifact", "would_write_collector_state",
        "would_send_to_broker", "broker_execution_requested", "mode_apply_requested", "command_ledger_append_requested",
        "approval_append_requested", "authorization_grant_requested", "autotrade_trigger_enabled",
    ):
        assert packet[key] is False, key


def test_ps_q10p_static_unmounted_and_no_runtime_boundaries() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    for token in FORBIDDEN_PAGE_TOKENS:
        assert token not in page_text, token
    assert "render_prediction_warroom_lowered_display_packet_visibility_review_panel()" in page_text
    assert "build_prediction_warroom_actual_review_packet_live_session_seed_gate" not in panel_text
    assert ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION == "prediction_warroom_actual_review_packet_live_session_seed_gate.ps_q10p.v1"
    assert "do_not_mount_warroom_page_in_this_slice" in text


def test_ps_q10p_default_is_passive_and_preserves_fallback() -> None:
    state: dict[str, Any] = {}
    packet = build_prediction_warroom_actual_review_packet_live_session_seed_gate(session_state=state).to_dict()
    assert packet["gate_state"] == "actual_review_packet_live_session_seed_gate_blocked"
    assert packet["seed_attempted"] is False
    assert packet["seed_hook_delegated"] is False
    assert packet["session_state_updated"] is False
    assert packet["source_handoff_ready"] is False
    assert packet["fallback_used"] is True
    assert packet["ready_for_existing_q9g_panel_render"] is False
    assert packet["ready_for_live_warroom_mount"] is False
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY not in state
    assert "live_session_seed_gate_passive_no_seed_attempted" in packet["warning_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10p_blocks_until_all_local_only_gates_are_explicit() -> None:
    state: dict[str, Any] = {}
    packet = build_prediction_warroom_actual_review_packet_live_session_seed_gate(
        review_packet=_review_packet(),
        session_state=state,
        operator_acknowledged=True,
        local_only_observation_enabled=True,
        allow_live_session_seed=False,
        gate_mode=ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE,
    ).to_dict()
    assert packet["gate_state"] == "actual_review_packet_live_session_seed_gate_blocked"
    assert "live_session_seed_not_allowed" in packet["blocked_reasons"]
    assert packet["seed_hook_delegated"] is False
    assert packet["session_state_updated"] is False
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY not in state
    _assert_no_side_effect_flags(packet)


def test_ps_q10p_delegates_to_q10n_and_verifies_q9h_when_all_gates_pass() -> None:
    state: dict[str, Any] = {}
    packet = build_prediction_warroom_actual_review_packet_live_session_seed_gate(
        review_packet=_review_packet(),
        session_state=state,
        operator_acknowledged=True,
        local_only_observation_enabled=True,
        allow_live_session_seed=True,
        gate_mode=ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE,
    ).to_dict()
    resolved = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(session_state=state).to_dict()
    assert packet["gate_state"] == "actual_review_packet_live_session_seed_gate_seeded_for_existing_q9g_panel"
    assert packet["seed_attempted"] is True
    assert packet["seed_hook_delegated"] is True
    assert packet["session_state_updated"] is True
    assert packet["source_handoff_ready"] is True
    assert packet["fallback_used"] is False
    assert packet["ready_for_existing_q9g_panel_render"] is True
    assert packet["ready_for_live_warroom_mount"] is False
    assert packet["blocker_count"] == 0
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in state
    assert resolved["source_kind"] == "session_state_in_memory_mapping"
    assert resolved["fallback_used"] is False
    assert resolved["review_packet_ready"] is True
    assert packet["seed_hook_packet"]["hook_state"] == "actual_review_packet_local_observation_seed_hook_actual_packet_installed"
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q10p_static_unmounted_and_no_runtime_boundaries()
    test_ps_q10p_default_is_passive_and_preserves_fallback()
    test_ps_q10p_blocks_until_all_local_only_gates_are_explicit()
    test_ps_q10p_delegates_to_q10n_and_verifies_q9h_when_all_gates_pass()
    print("[OK] Prediction System PS-Q10P actual review-packet live-session seed gate guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
