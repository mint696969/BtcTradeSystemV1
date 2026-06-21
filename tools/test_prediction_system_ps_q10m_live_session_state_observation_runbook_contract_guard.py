# path: ./tools/test_prediction_system_ps_q10m_live_session_state_observation_runbook_contract_guard.py
# desc: Focused guard for PS-Q10M live session-state observation runbook contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_live_session_state_observation_runbook_contract import (
    FUTURE_SEED_SLICE_REQUIREMENTS,
    LIVE_BROWSER_ACCEPTANCE_MARKERS,
    LIVE_SESSION_STATE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    LIVE_SESSION_STATE_OBSERVATION_SEQUENCE,
    build_prediction_warroom_live_session_state_observation_runbook_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_live_session_state_observation_runbook_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
LOCAL_HOOK = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_local_observation_hook.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit",
    "pathlib",
    "json",
    "subprocess",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "btcts.collector_vnext",
    "btcts.autotrade",
)
FORBIDDEN_MODULE_TOKENS = (
    "import streamlit",
    "open(",
    "Path(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    "subprocess",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "build_prediction_warroom_actual_read_operator_runner_scaffold(",
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "load_prediction_warroom_latest_payload_read_only(",
    "allow_actual_read=True",
    "execute_actual_read=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_loader_execution: bool = True",
    "would_read_runtime_file: bool = True",
    "would_decode_payload: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)
FORBIDDEN_PRODUCTION_MUTATION_MARKERS = (
    "prediction_warroom_live_session_state_observation_runbook_contract",
    "build_prediction_warroom_live_session_state_observation_runbook_contract",
)
EXPECTED_SEQUENCE = [
    "declare_contract_only_live_browser_observation_runbook",
    "require_ps_q10k_actual_review_packet_session_handoff_ready",
    "require_ps_q10l_existing_q9g_panel_session_handoff_guard_green",
    "require_actual_review_packet_to_be_built_outside_warroom_ui",
    "declare_live_streamlit_session_state_seed_requires_future_reviewed_slice",
    "forbid_warroom_ui_actual_read_controls",
    "forbid_warroom_ui_loader_execution",
    "forbid_warroom_ui_file_read_or_payload_decode",
    "forbid_warroom_ui_runtime_artifact_write",
    "forbid_warroom_page_or_panel_mutation_in_this_slice",
    "forbid_approval_ledger_autotrade_broker",
    "return_runbook_contract_only",
]


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _assert_no_execution_boundaries(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["contract_only"] is True
    assert packet["runbook_only"] is True
    assert packet["ready_for_live_browser_observation_now"] is False
    assert packet["live_session_state_seed_implemented_this_slice"] is False
    assert packet["live_session_state_seed_performed_by_this_contract"] is False
    assert packet["browser_observation_performed_by_this_contract"] is False
    assert packet["warroom_page_patch_included"] is False
    assert packet["warroom_panel_patch_included"] is False
    assert packet["warroom_local_observation_hook_patch_included"] is False
    for key in (
        "ui_actual_read_controls_allowed",
        "ui_loader_execution_allowed",
        "ui_file_read_allowed",
        "ui_payload_decode_allowed",
        "runtime_artifact_write_allowed_from_ui",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "streamlit_import_required",
        "streamlit_render_performed_by_this_contract",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "would_load_source_artifacts",
        "would_read_runtime_file",
        "would_decode_payload",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    ):
        assert packet[key] is False, key


def test_ps_q10m_static_contract_boundaries() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    assert LIVE_SESSION_STATE_OBSERVATION_RUNBOOK_CONTRACT_VERSION == "prediction_warroom_live_session_state_observation_runbook_contract.ps_q10m.v1"
    assert list(LIVE_SESSION_STATE_OBSERVATION_SEQUENCE) == EXPECTED_SEQUENCE
    assert "fallback=False" in LIVE_BROWSER_ACCEPTANCE_MARKERS
    assert "widgets=6" in LIVE_BROWSER_ACCEPTANCE_MARKERS
    assert "must_not_run_q9b_q9q_q10h_from_warroom_ui" in FUTURE_SEED_SLICE_REQUIREMENTS
    assert "must_not_read_files_from_warroom_ui" in FUTURE_SEED_SLICE_REQUIREMENTS


def test_ps_q10m_does_not_mount_or_mutate_production_ui_files() -> None:
    for path in (WARROOM_PAGE, PANEL, LOCAL_HOOK):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_PRODUCTION_MUTATION_MARKERS:
            assert marker not in text, f"{marker} in {path}"
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    assert "Prediction WarRoom real payload review" in page_text
    assert "render_prediction_warroom_lowered_display_packet_visibility_review_panel()" in page_text


def test_ps_q10m_default_blocks_before_operator_acknowledgement() -> None:
    packet = build_prediction_warroom_live_session_state_observation_runbook_contract().to_dict()
    assert packet["contract_state"] == "live_session_state_observation_runbook_blocked"
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "ps_q10k_actual_session_handoff_guard_required" in packet["blocked_reasons"]
    assert "ps_q10l_panel_session_handoff_guard_required" in packet["blocked_reasons"]
    assert "actual_review_packet_must_be_available_outside_warroom_ui" in packet["blocked_reasons"]
    assert packet["ready_for_future_live_session_seed_slice"] is False
    _assert_no_execution_boundaries(packet)


def test_ps_q10m_ready_state_is_future_seed_slice_not_live_observation_now() -> None:
    packet = build_prediction_warroom_live_session_state_observation_runbook_contract(
        operator_acknowledged=True,
        q10k_guard_passed=True,
        q10l_guard_passed=True,
        actual_review_packet_available_outside_ui=True,
    ).to_dict()
    assert packet["contract_state"] == "live_session_state_observation_runbook_ready_for_future_seed_slice"
    assert packet["ready_for_future_live_session_seed_slice"] is True
    assert packet["ready_for_live_browser_observation_now"] is False
    assert packet["blocker_count"] == 0
    assert "live_browser_observation_still_requires_future_session_state_seed_slice" in packet["warning_reasons"]
    assert packet["runbook_summary"]["target_session_key"] == "warroom_prediction_lowered_display_packet_visibility_review_packet"
    assert packet["runbook_summary"]["ready_for_future_live_session_seed_slice"] is True
    assert packet["runbook_summary"]["ready_for_live_browser_observation_now"] is False
    assert "fallback=False" in packet["runbook_summary"]["acceptance_markers"]
    assert "must_not_run_q9b_q9q_q10h_from_warroom_ui" in packet["runbook_summary"]["future_seed_slice_requirements"]
    _assert_no_execution_boundaries(packet)


def test_ps_q10m_rejects_unsafe_live_seed_and_ui_runtime_requests() -> None:
    packet = build_prediction_warroom_live_session_state_observation_runbook_contract(
        operator_acknowledged=True,
        q10k_guard_passed=True,
        q10l_guard_passed=True,
        actual_review_packet_available_outside_ui=True,
        requested_page_or_panel_mutation=True,
        requested_live_session_state_seed_this_slice=True,
        requested_warroom_ui_actual_read_control=True,
        requested_warroom_ui_loader_execution=True,
        requested_warroom_ui_file_read_or_decode=True,
        requested_runtime_artifact_write_from_ui=True,
        requested_approval_ledger_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "live_session_state_observation_runbook_blocked"
    for reason in (
        "warroom_page_or_panel_mutation_not_allowed_in_q10m",
        "live_session_state_seed_requires_future_reviewed_slice",
        "warroom_ui_actual_read_control_not_allowed",
        "warroom_ui_loader_execution_not_allowed",
        "warroom_ui_file_read_or_payload_decode_not_allowed",
        "runtime_artifact_write_from_warroom_ui_not_allowed",
        "approval_ledger_autotrade_broker_not_allowed",
    ):
        assert reason in packet["blocked_reasons"]
    assert packet["ready_for_future_live_session_seed_slice"] is False
    _assert_no_execution_boundaries(packet)


def main() -> int:
    test_ps_q10m_static_contract_boundaries()
    test_ps_q10m_does_not_mount_or_mutate_production_ui_files()
    test_ps_q10m_default_blocks_before_operator_acknowledgement()
    test_ps_q10m_ready_state_is_future_seed_slice_not_live_observation_now()
    test_ps_q10m_rejects_unsafe_live_seed_and_ui_runtime_requests()
    print("[OK] Prediction System PS-Q10M live session-state observation runbook contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
