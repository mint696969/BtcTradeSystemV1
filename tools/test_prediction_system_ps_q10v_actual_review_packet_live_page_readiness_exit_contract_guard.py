# path: ./tools/test_prediction_system_ps_q10v_actual_review_packet_live_page_readiness_exit_contract_guard.py
# desc: Guard for PS-Q10V consolidated mounted observation lane readiness/exit contract. Contract-only and no production UI mutation.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_observation_capture_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_readiness_exit_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION,
    MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE,
    MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS,
    MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES,
    build_prediction_warroom_actual_review_packet_live_page_readiness_exit_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_session_seed_page_mount import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_readiness_exit_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
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
FORBIDDEN_PAGE_RUNTIME_TOKENS = (
    "build_prediction_warroom_actual_read_operator_runner_scaffold",
    "build_prediction_warroom_latest_payload_actual_export_runner",
    "load_prediction_warroom_latest_payload_read_only",
    "allow_actual_read=True",
    "execute_actual_read=True",
    "st.button(\"Actual",
    "st.form(\"Actual",
    "st.toggle(\"Actual",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "place_order(", "send_order(", "create_order(",
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
        "would_send_to_broker", "broker_execution_requested", "command_ledger_append_requested", "approval_append_requested",
        "authorization_grant_requested", "autotrade_trigger_enabled",
    ):
        assert packet[key] is False, key


def test_ps_q10v_static_contract_only_and_no_ui_runtime_tokens() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    assert "build_prediction_warroom_actual_review_packet_live_page_readiness_exit_contract" not in page_text
    assert "build_prediction_warroom_actual_review_packet_live_page_readiness_exit_contract" not in panel_text
    assert "apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=st.session_state)" in page_text
    assert page_text.index("apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(") < page_text.index("render_prediction_warroom_lowered_display_packet_visibility_review_panel()")
    for token in FORBIDDEN_PAGE_RUNTIME_TOKENS:
        assert token not in page_text, token
    assert ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION == "prediction_warroom_actual_review_packet_live_page_readiness_exit_contract.ps_q10v.v1"


def test_ps_q10v_default_blocks_until_all_readiness_inputs() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_readiness_exit_contract().to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_readiness_exit_blocked"
    assert packet["ready_for_human_live_local_confirmation"] is False
    for reason in (
        "operator_acknowledgement_required",
        "ps_q10r_page_mount_guard_required",
        "ps_q10s_runbook_guard_required",
        "ps_q10t_capture_guard_required",
        "ps_q10u_operator_handoff_guard_required",
        "all_close_guards_green_required",
        "working_tree_clean_required",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def test_ps_q10v_ready_state_is_human_confirmation_not_execution() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_readiness_exit_contract(
        operator_acknowledged=True,
        q10r_guard_passed=True,
        q10s_guard_passed=True,
        q10t_guard_passed=True,
        q10u_guard_passed=True,
        all_close_guards_passed=True,
        working_tree_clean=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_readiness_exit_ready"
    assert packet["ready_for_human_live_local_confirmation"] is True
    assert packet["execution_path_enabled"] is False
    assert packet["production_ui_actual_read_trigger_added"] is False
    assert packet["browser_automation_artifact_added"] is False
    assert packet["live_browser_observation_performed_by_this_contract"] is False
    assert packet["session_state_seed_performed_by_this_contract"] is False
    assert tuple(packet["commit_lineage"]) == MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE
    assert tuple(packet["ready_capabilities"]) == MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES
    assert tuple(packet["not_done_items"]) == MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS
    assert packet["q10r_page_mount_version"] == ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    assert packet["q10s_runbook_contract_version"] == ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
    assert packet["q10t_capture_contract_version"] == ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
    assert packet["q10u_operator_handoff_contract_version"] == ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION
    assert "mounted_observation_lane_ready_for_human_confirmation_not_execution" in packet["warning_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10v_rejects_unsafe_runtime_or_scope_requests() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_readiness_exit_contract(
        operator_acknowledged=True,
        q10r_guard_passed=True,
        q10s_guard_passed=True,
        q10t_guard_passed=True,
        q10u_guard_passed=True,
        all_close_guards_passed=True,
        working_tree_clean=True,
        requested_warroom_page_patch_this_slice=True,
        requested_warroom_panel_patch_this_slice=True,
        requested_ui_actual_read_controls=True,
        requested_ui_loader_execution=True,
        requested_ui_file_read_or_decode=True,
        requested_runtime_artifact_write_from_ui=True,
        requested_approval_ledger_autotrade_or_broker=True,
        requested_production_ui_actual_read_trigger=True,
        requested_browser_automation_artifact=True,
        requested_execution_path=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_readiness_exit_blocked"
    for reason in (
        "warroom_page_patch_not_allowed_in_q10v",
        "warroom_panel_patch_not_allowed_in_q10v",
        "warroom_ui_actual_read_controls_not_allowed",
        "warroom_ui_loader_execution_not_allowed",
        "warroom_ui_file_read_or_payload_decode_not_allowed",
        "runtime_artifact_write_from_warroom_ui_not_allowed",
        "approval_ledger_autotrade_broker_not_allowed",
        "production_ui_actual_read_trigger_not_allowed_in_q10v",
        "browser_automation_artifact_not_allowed_in_q10v",
        "execution_path_not_allowed_in_q10v",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def test_ps_q10v_lineage_and_exit_items_are_exact() -> None:
    assert MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE == (
        "3043f12e feat: mount actual review packet live session seed gate",
        "60bd0d43 docs: add actual review packet live page observation runbook",
        "21c60169 test: capture actual review packet live page observation",
        "52db4fd7 docs: add actual review packet live page operator handoff checklist",
    )
    assert MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES == (
        "q10r_minimal_warroom_page_mount_q10p_gate_before_existing_q9g_panel",
        "q10s_passive_and_seeded_acceptance_markers_fixed",
        "q10t_passive_and_seeded_marker_capture_validated",
        "q10u_operator_handoff_checklist_packaged",
        "ready_for_human_live_local_confirmation",
    )
    assert MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS == (
        "production_ui_actual_read_trigger_not_added",
        "browser_automation_artifact_not_added",
        "broker_or_autotrade_execution_path_not_added",
        "q9b_q9q_q10h_not_called_from_warroom_ui",
        "runtime_file_read_not_enabled_from_warroom_ui",
        "payload_decode_not_enabled_from_warroom_ui",
        "runtime_artifact_write_not_enabled_from_warroom_ui",
        "approval_ledger_not_enabled_from_warroom_ui",
    )


def main() -> int:
    test_ps_q10v_static_contract_only_and_no_ui_runtime_tokens()
    test_ps_q10v_default_blocks_until_all_readiness_inputs()
    test_ps_q10v_ready_state_is_human_confirmation_not_execution()
    test_ps_q10v_rejects_unsafe_runtime_or_scope_requests()
    test_ps_q10v_lineage_and_exit_items_are_exact()
    print("[OK] Prediction System PS-Q10V actual review-packet live page readiness exit contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
