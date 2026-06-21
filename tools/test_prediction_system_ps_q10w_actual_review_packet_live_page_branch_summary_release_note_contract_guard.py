# path: ./tools/test_prediction_system_ps_q10w_actual_review_packet_live_page_branch_summary_release_note_contract_guard.py
# desc: Guard for PS-Q10W Q10R-Q10V branch summary/release note contract. Contract-only and no production UI mutation.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_BRANCH_SUMMARY_RELEASE_NOTE_CONTRACT_VERSION,
    BRANCH_SUMMARY_RELEASE_NOTE_COMPLETED_ITEMS,
    BRANCH_SUMMARY_RELEASE_NOTE_STATUS,
    BRANCH_SUMMARY_RELEASE_NOTE_TITLE,
    build_prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_readiness_exit_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION,
    MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE,
    MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS,
    MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract.py"
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


def test_ps_q10w_static_contract_only_and_no_ui_runtime_tokens() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    assert "build_prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract" not in page_text
    assert "build_prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract" not in panel_text
    assert "apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=st.session_state)" in page_text
    for token in FORBIDDEN_PAGE_RUNTIME_TOKENS:
        assert token not in page_text, token
    assert ACTUAL_REVIEW_PACKET_LIVE_PAGE_BRANCH_SUMMARY_RELEASE_NOTE_CONTRACT_VERSION == "prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract.ps_q10w.v1"


def test_ps_q10w_default_blocks_until_release_note_inputs() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract().to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_branch_summary_release_note_blocked"
    assert packet["ready_for_operator_review_handoff"] is False
    for reason in (
        "operator_acknowledgement_required",
        "ps_q10v_readiness_exit_ready_required",
        "all_lane_guards_green_required",
        "working_tree_clean_required",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def test_ps_q10w_ready_state_packages_branch_summary() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract(
        operator_acknowledged=True,
        q10v_readiness_exit_ready=True,
        all_lane_guards_green=True,
        working_tree_clean=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_branch_summary_release_note_ready"
    assert packet["ready_for_operator_review_handoff"] is True
    assert packet["release_note_title"] == BRANCH_SUMMARY_RELEASE_NOTE_TITLE
    assert packet["release_note_status"] == BRANCH_SUMMARY_RELEASE_NOTE_STATUS
    assert tuple(packet["completed_items"]) == BRANCH_SUMMARY_RELEASE_NOTE_COMPLETED_ITEMS
    assert tuple(packet["commit_lineage"]) == MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE
    assert tuple(packet["ready_capabilities"]) == MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES
    assert tuple(packet["not_done_items"]) == MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS
    assert packet["q10v_readiness_exit_contract_version"] == ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION
    assert packet["execution_path_enabled"] is False
    assert packet["production_ui_actual_read_trigger_added"] is False
    assert packet["browser_automation_artifact_added"] is False
    assert "release_note_ready_for_operator_review_handoff_not_execution" in packet["warning_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10w_rejects_unsafe_runtime_or_scope_requests() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract(
        operator_acknowledged=True,
        q10v_readiness_exit_ready=True,
        all_lane_guards_green=True,
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
    assert packet["contract_state"] == "actual_review_packet_live_page_branch_summary_release_note_blocked"
    for reason in (
        "warroom_page_patch_not_allowed_in_q10w",
        "warroom_panel_patch_not_allowed_in_q10w",
        "warroom_ui_actual_read_controls_not_allowed",
        "warroom_ui_loader_execution_not_allowed",
        "warroom_ui_file_read_or_payload_decode_not_allowed",
        "runtime_artifact_write_from_warroom_ui_not_allowed",
        "approval_ledger_autotrade_broker_not_allowed",
        "production_ui_actual_read_trigger_not_allowed_in_q10w",
        "browser_automation_artifact_not_allowed_in_q10w",
        "execution_path_not_allowed_in_q10w",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def test_ps_q10w_release_note_text_is_exact() -> None:
    assert BRANCH_SUMMARY_RELEASE_NOTE_TITLE == "Prediction WarRoom actual review-packet mounted observation lane Q10R-Q10V"
    assert BRANCH_SUMMARY_RELEASE_NOTE_STATUS == "ready_for_operator_review_handoff_not_execution"
    assert BRANCH_SUMMARY_RELEASE_NOTE_COMPLETED_ITEMS == (
        "Q10R mounted the local-only Q10P seed gate before the existing Q9G WarRoom panel.",
        "Q10S fixed passive and seeded live/local observation acceptance markers.",
        "Q10T validated passive and seeded local observation marker capture.",
        "Q10U packaged the operator passive/seeded/boundary handoff checklist.",
        "Q10V declared the mounted observation lane ready for human live/local confirmation and not an execution path.",
    )


def main() -> int:
    test_ps_q10w_static_contract_only_and_no_ui_runtime_tokens()
    test_ps_q10w_default_blocks_until_release_note_inputs()
    test_ps_q10w_ready_state_packages_branch_summary()
    test_ps_q10w_rejects_unsafe_runtime_or_scope_requests()
    test_ps_q10w_release_note_text_is_exact()
    print("[OK] Prediction System PS-Q10W actual review-packet live page branch summary release note contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
