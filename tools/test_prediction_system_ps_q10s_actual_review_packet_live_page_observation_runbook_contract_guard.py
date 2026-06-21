# path: ./tools/test_prediction_system_ps_q10s_actual_review_packet_live_page_observation_runbook_contract_guard.py
# desc: Guard for PS-Q10S live page observation runbook contract. Contract-only and no WarRoom UI mutation.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS,
    SEEDED_LIVE_PAGE_OBSERVATION_MARKERS,
    build_prediction_warroom_actual_review_packet_live_page_observation_runbook_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_observation_runbook_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
MOUNT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_session_seed_page_mount.py"
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


def test_ps_q10s_static_contract_only_and_q10r_mount_present() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    mount_text = MOUNT.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    assert "apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=st.session_state)" in page_text
    assert page_text.index("apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(") < page_text.index("render_prediction_warroom_lowered_display_packet_visibility_review_panel()")
    assert "Prediction WarRoom real payload review" in page_text
    assert "passive_by_default_without_packet_or_gates" in mount_text
    assert "build_prediction_warroom_actual_review_packet_live_page_observation_runbook_contract" not in page_text
    assert "build_prediction_warroom_actual_review_packet_live_page_observation_runbook_contract" not in panel_text
    for token in FORBIDDEN_PAGE_RUNTIME_TOKENS:
        assert token not in page_text, token
    assert ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION == "prediction_warroom_actual_review_packet_live_page_observation_runbook_contract.ps_q10s.v1"


def test_ps_q10s_default_blocks_before_observation_prerequisites() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_observation_runbook_contract().to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_observation_runbook_blocked"
    assert packet["ready_for_live_local_observation_runbook"] is False
    assert packet["live_observation_performed_by_this_contract"] is False
    assert packet["warroom_page_patch_included_this_slice"] is False
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "ps_q10r_live_page_mount_guard_required" in packet["blocked_reasons"]
    assert "passive_browser_observation_must_be_planned_first" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10s_ready_state_is_runbook_ready_not_observation_performed() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_observation_runbook_contract(
        operator_acknowledged=True,
        q10r_guard_passed=True,
        warroom_page_mounted_by_q10r=True,
        passive_browser_observation_planned=True,
        seeded_browser_observation_planned=True,
        supplied_actual_q9f_review_packet_available=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_observation_runbook_ready"
    assert packet["ready_for_live_local_observation_runbook"] is True
    assert packet["live_observation_performed_by_this_contract"] is False
    assert packet["session_state_seed_performed_by_this_contract"] is False
    assert packet["warroom_page_patch_included_this_slice"] is False
    assert "runbook_ready_observation_not_performed_by_contract" in packet["warning_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10s_rejects_unsafe_runtime_or_ui_requests() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_observation_runbook_contract(
        operator_acknowledged=True,
        q10r_guard_passed=True,
        warroom_page_mounted_by_q10r=True,
        passive_browser_observation_planned=True,
        seeded_browser_observation_planned=True,
        supplied_actual_q9f_review_packet_available=True,
        requested_warroom_page_patch_this_slice=True,
        requested_warroom_panel_patch_this_slice=True,
        requested_ui_actual_read_controls=True,
        requested_ui_loader_execution=True,
        requested_ui_file_read_or_decode=True,
        requested_runtime_artifact_write_from_ui=True,
        requested_approval_ledger_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_observation_runbook_blocked"
    for reason in (
        "warroom_page_patch_not_allowed_in_q10s",
        "warroom_panel_patch_not_allowed_in_q10s",
        "warroom_ui_actual_read_controls_not_allowed",
        "warroom_ui_loader_execution_not_allowed",
        "warroom_ui_file_read_or_payload_decode_not_allowed",
        "runtime_artifact_write_from_warroom_ui_not_allowed",
        "approval_ledger_autotrade_broker_not_allowed",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def test_ps_q10s_acceptance_markers_are_exact() -> None:
    assert PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS == (
        "Prediction WarRoom real payload review",
        "top/default-expanded",
        "source_handoff=review_source_handoff_fallback_blocked",
        "source_kind=blocked_fallback_contract",
        "fallback=True",
        "No lowered display-packet widget candidates are available for review yet.",
        "ui_triggered_loader_execution:false",
        "runtime_file_read:false",
        "payload_decode:false",
        "runtime_artifact_write:false",
        "approval_or_authorization_grant:false",
        "decision_or_command_ledger_append:false",
        "autotrade_trigger:false",
        "broker_private_api:false",
    )
    assert SEEDED_LIVE_PAGE_OBSERVATION_MARKERS == (
        "Prediction WarRoom real payload review",
        "source_handoff=review_source_handoff_ready",
        "source_kind=session_state_in_memory_mapping",
        "fallback=False",
        "ready_for_ui_mount=True",
        "widgets=6",
        "No lowered display-packet widget candidates are available for review yet:absent",
        "ui_triggered_loader_execution:false",
        "runtime_file_read:false",
        "payload_decode:false",
        "runtime_artifact_write:false",
        "approval_or_authorization_grant:false",
        "decision_or_command_ledger_append:false",
        "autotrade_trigger:false",
        "broker_private_api:false",
    )


def main() -> int:
    test_ps_q10s_static_contract_only_and_q10r_mount_present()
    test_ps_q10s_default_blocks_before_observation_prerequisites()
    test_ps_q10s_ready_state_is_runbook_ready_not_observation_performed()
    test_ps_q10s_rejects_unsafe_runtime_or_ui_requests()
    test_ps_q10s_acceptance_markers_are_exact()
    print("[OK] Prediction System PS-Q10S actual review-packet live page observation runbook contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
