# path: ./tools/test_prediction_system_ps_q10q_actual_review_packet_live_mount_plan_contract_guard.py
# desc: Focused guard for PS-Q10Q future WarRoom mount plan contract. Contract-only; verifies page is not patched yet and plan boundaries remain safe.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_mount_plan_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_MOUNT_PLAN_CONTRACT_VERSION,
    FUTURE_PAGE_PATCH_REQUIREMENTS,
    LIVE_MOUNT_PLAN_EXISTING_PANEL_CALL,
    LIVE_MOUNT_PLAN_TARGET_SECTION_LABEL,
    build_prediction_warroom_actual_review_packet_live_mount_plan_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_mount_plan_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
Q10P_GATE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_session_seed_gate.py"
FORBIDDEN_IMPORT_PREFIXES = ("streamlit", "pathlib", "json", "subprocess", "requests", "httpx", "ccxt", "pybitflyer", "websocket", "btcts.collector_vnext", "btcts.autotrade")
FORBIDDEN_MODULE_TOKENS = (
    "import streamlit", "open(", "Path(", "read_text", "read_bytes", "json.load", "json.loads", "write_text", "write_bytes", "json.dump", "json.dumps",
    "subprocess", "st.button", "st.form", "st.checkbox", "st.toggle", "build_prediction_warroom_actual_read_operator_runner_scaffold(",
    "build_prediction_warroom_latest_payload_actual_export_runner(", "load_prediction_warroom_latest_payload_read_only(", "allow_actual_read=True", "execute_actual_read=True",
    "place_order(", "send_order(", "create_order(", "append_decision_jsonl", "append_command_ledger_record",
    "streamlit_import_required: bool = True", "ui_controls_added: bool = True", "ui_triggered_loader_execution: bool = True",
    "would_read_runtime_file: bool = True", "would_decode_payload: bool = True", "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True", "broker_execution_requested: bool = True", "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True", "authorization_grant_requested: bool = True", "autotrade_trigger_enabled: bool = True",
)
FORBIDDEN_PAGE_TOKENS = (
    "prediction_warroom_actual_review_packet_live_mount_plan_contract",
    "build_prediction_warroom_actual_review_packet_live_mount_plan_contract",
    "prediction_warroom_actual_review_packet_live_session_seed_gate",
    "build_prediction_warroom_actual_review_packet_live_session_seed_gate",
    "warroom_prediction_actual_review_packet_live_session_seed",
    "st.button(\"Actual",
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


def _assert_no_side_effect_flags(packet: dict) -> None:
    for key in (
        "streamlit_import_required", "ui_controls_added", "ui_triggered_loader_execution", "would_load_source_artifacts",
        "would_read_runtime_file", "would_decode_payload", "would_write_runtime_artifact", "would_write_collector_state",
        "would_send_to_broker", "broker_execution_requested", "mode_apply_requested", "command_ledger_append_requested",
        "approval_append_requested", "authorization_grant_requested", "autotrade_trigger_enabled",
    ):
        assert packet[key] is False, key


def test_ps_q10q_static_contract_only_and_page_not_patched() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    q10p_text = Q10P_GATE.read_text(encoding="utf-8")
    for token in FORBIDDEN_PAGE_TOKENS:
        assert token not in page_text, token
    assert LIVE_MOUNT_PLAN_TARGET_SECTION_LABEL in page_text
    assert LIVE_MOUNT_PLAN_EXISTING_PANEL_CALL in page_text
    assert "build_prediction_warroom_actual_review_packet_live_mount_plan_contract" not in panel_text
    assert "ready_for_live_warroom_mount=False" in q10p_text
    assert ACTUAL_REVIEW_PACKET_LIVE_MOUNT_PLAN_CONTRACT_VERSION == "prediction_warroom_actual_review_packet_live_mount_plan_contract.ps_q10q.v1"
    assert "do_not_mount_warroom_page_in_this_slice" in text


def test_ps_q10q_default_blocks_before_ack_and_prerequisites() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_mount_plan_contract().to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_mount_plan_blocked"
    assert packet["ready_for_future_page_patch_slice"] is False
    assert packet["ready_for_live_warroom_mount_now"] is False
    assert packet["page_patch_included_this_slice"] is False
    assert packet["panel_patch_included_this_slice"] is False
    assert packet["gate_mount_performed_this_slice"] is False
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "ps_q10p_live_session_seed_gate_guard_required" in packet["blocked_reasons"]
    assert "ps_q10o_seed_to_panel_integration_guard_required" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10q_ready_state_is_future_page_patch_not_live_mount_now() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_mount_plan_contract(
        operator_acknowledged=True,
        q10p_guard_passed=True,
        q10o_guard_passed=True,
        top_real_payload_review_section_present=True,
        existing_q9g_panel_call_present=True,
        actual_review_packet_available_in_process_memory=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_mount_plan_ready_for_future_page_patch"
    assert packet["ready_for_future_page_patch_slice"] is True
    assert packet["ready_for_live_warroom_mount_now"] is False
    assert packet["page_patch_included_this_slice"] is False
    assert packet["panel_patch_included_this_slice"] is False
    assert packet["gate_mount_performed_this_slice"] is False
    assert "future_page_patch_slice_still_required_before_live_browser_mount" in packet["warning_reasons"]
    assert packet["plan_summary"]["insertion_anchor"] == "before_existing_q9g_panel_render_call"
    assert packet["plan_summary"]["existing_panel_call"] == LIVE_MOUNT_PLAN_EXISTING_PANEL_CALL
    _assert_no_side_effect_flags(packet)


def test_ps_q10q_rejects_unsafe_mount_or_runtime_requests() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_mount_plan_contract(
        operator_acknowledged=True,
        q10p_guard_passed=True,
        q10o_guard_passed=True,
        top_real_payload_review_section_present=True,
        existing_q9g_panel_call_present=True,
        actual_review_packet_available_in_process_memory=True,
        requested_page_patch_this_slice=True,
        requested_panel_patch_this_slice=True,
        requested_gate_mount_this_slice=True,
        requested_ui_actual_read_controls=True,
        requested_ui_loader_execution=True,
        requested_ui_file_read_or_decode=True,
        requested_runtime_artifact_write_from_ui=True,
        requested_approval_ledger_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_mount_plan_blocked"
    for reason in (
        "warroom_page_patch_not_allowed_in_q10q",
        "warroom_panel_patch_not_allowed_in_q10q",
        "gate_mount_not_allowed_in_q10q",
        "warroom_ui_actual_read_controls_not_allowed",
        "warroom_ui_loader_execution_not_allowed",
        "warroom_ui_file_read_or_payload_decode_not_allowed",
        "runtime_artifact_write_from_warroom_ui_not_allowed",
        "approval_ledger_autotrade_broker_not_allowed",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def test_ps_q10q_future_patch_requirements_are_exact_safety_contract() -> None:
    assert FUTURE_PAGE_PATCH_REQUIREMENTS == (
        "must_mount_inside_prediction_warroom_real_payload_review_section",
        "must_call_gate_before_existing_q9g_panel_render_only",
        "must_leave_existing_q9g_panel_call_in_place",
        "must_be_passive_by_default_without_packet_or_gates",
        "must_preserve_fallback_message_without_packet",
        "must_not_add_button_toggle_form_for_actual_read",
        "must_not_call_q9b_q9q_q10h_from_warroom_ui",
        "must_not_read_files_from_warroom_ui",
        "must_not_decode_payloads_from_warroom_ui",
        "must_not_write_runtime_artifacts_from_warroom_ui",
        "must_not_append_approval_or_ledgers",
        "must_not_trigger_autotrade_or_broker",
    )


def main() -> int:
    test_ps_q10q_static_contract_only_and_page_not_patched()
    test_ps_q10q_default_blocks_before_ack_and_prerequisites()
    test_ps_q10q_ready_state_is_future_page_patch_not_live_mount_now()
    test_ps_q10q_rejects_unsafe_mount_or_runtime_requests()
    test_ps_q10q_future_patch_requirements_are_exact_safety_contract()
    print("[OK] Prediction System PS-Q10Q actual review-packet live mount plan contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
