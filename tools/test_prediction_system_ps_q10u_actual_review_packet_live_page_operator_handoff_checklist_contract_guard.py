# path: ./tools/test_prediction_system_ps_q10u_actual_review_packet_live_page_operator_handoff_checklist_contract_guard.py
# desc: Guard for PS-Q10U operator-facing live/local observation handoff/checklist contract. Contract-only and no production UI mutation.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_observation_capture_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS,
    SEEDED_LIVE_PAGE_OBSERVATION_MARKERS,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION,
    BOUNDARY_OPERATOR_CONFIRMATION_CHECKLIST,
    PASSIVE_OPERATOR_CONFIRMATION_CHECKLIST,
    SEEDED_OPERATOR_CONFIRMATION_CHECKLIST,
    build_prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_session_seed_page_mount import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract.py"
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


def test_ps_q10u_static_contract_only_and_no_ui_runtime_tokens() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    assert "build_prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract" not in page_text
    assert "build_prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract" not in panel_text
    assert "apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=st.session_state)" in page_text
    assert page_text.index("apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(") < page_text.index("render_prediction_warroom_lowered_display_packet_visibility_review_panel()")
    for token in FORBIDDEN_PAGE_RUNTIME_TOKENS:
        assert token not in page_text, token
    assert ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION == "prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract.ps_q10u.v1"


def test_ps_q10u_default_blocks_until_prerequisites_and_confirmations() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract().to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_operator_handoff_checklist_blocked"
    assert packet["ready_for_operator_live_local_handoff"] is False
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "ps_q10r_live_page_mount_guard_required" in packet["blocked_reasons"]
    assert "ps_q10s_runbook_ready_required" in packet["blocked_reasons"]
    assert "ps_q10t_capture_acceptance_required" in packet["blocked_reasons"]
    assert "passive_operator_checklist_confirmation_required" in packet["blocked_reasons"]
    assert "seeded_operator_checklist_confirmation_required" in packet["blocked_reasons"]
    assert "boundary_operator_checklist_confirmation_required" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10u_ready_state_packages_operator_checklists_and_versions() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract(
        operator_acknowledged=True,
        q10r_guard_passed=True,
        q10s_runbook_ready=True,
        q10t_capture_accepted=True,
        passive_checklist_confirmed=True,
        seeded_checklist_confirmed=True,
        boundary_checklist_confirmed=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_operator_handoff_checklist_ready"
    assert packet["ready_for_operator_live_local_handoff"] is True
    assert packet["q10r_page_mount_version"] == ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    assert packet["q10s_runbook_contract_version"] == ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
    assert packet["q10t_capture_contract_version"] == ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
    assert tuple(packet["expected_passive_markers"]) == PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS
    assert tuple(packet["expected_seeded_markers"]) == SEEDED_LIVE_PAGE_OBSERVATION_MARKERS
    assert tuple(packet["passive_operator_confirmation_checklist"]) == PASSIVE_OPERATOR_CONFIRMATION_CHECKLIST
    assert tuple(packet["seeded_operator_confirmation_checklist"]) == SEEDED_OPERATOR_CONFIRMATION_CHECKLIST
    assert tuple(packet["boundary_operator_confirmation_checklist"]) == BOUNDARY_OPERATOR_CONFIRMATION_CHECKLIST
    assert "operator_handoff_checklist_ready_contract_only" in packet["warning_reasons"]
    assert packet["live_browser_observation_performed_by_this_contract"] is False
    assert packet["session_state_seed_performed_by_this_contract"] is False
    _assert_no_side_effect_flags(packet)


def test_ps_q10u_rejects_unsafe_runtime_or_ui_requests() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract(
        operator_acknowledged=True,
        q10r_guard_passed=True,
        q10s_runbook_ready=True,
        q10t_capture_accepted=True,
        passive_checklist_confirmed=True,
        seeded_checklist_confirmed=True,
        boundary_checklist_confirmed=True,
        requested_warroom_page_patch_this_slice=True,
        requested_warroom_panel_patch_this_slice=True,
        requested_ui_actual_read_controls=True,
        requested_ui_loader_execution=True,
        requested_ui_file_read_or_decode=True,
        requested_runtime_artifact_write_from_ui=True,
        requested_approval_ledger_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_operator_handoff_checklist_blocked"
    for reason in (
        "warroom_page_patch_not_allowed_in_q10u",
        "warroom_panel_patch_not_allowed_in_q10u",
        "warroom_ui_actual_read_controls_not_allowed",
        "warroom_ui_loader_execution_not_allowed",
        "warroom_ui_file_read_or_payload_decode_not_allowed",
        "runtime_artifact_write_from_warroom_ui_not_allowed",
        "approval_ledger_autotrade_broker_not_allowed",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def test_ps_q10u_checklist_text_is_exact_and_operator_facing() -> None:
    assert PASSIVE_OPERATOR_CONFIRMATION_CHECKLIST == (
        "Open WarRoom page without supplying actual review packet or local-only seed gates.",
        "Confirm Prediction WarRoom real payload review remains top/default-expanded.",
        "Confirm source_handoff=review_source_handoff_fallback_blocked.",
        "Confirm source_kind=blocked_fallback_contract.",
        "Confirm fallback=True.",
        "Confirm No lowered display-packet widget candidates are available for review yet.",
    )
    assert SEEDED_OPERATOR_CONFIRMATION_CHECKLIST == (
        "Use only a pre-built actual Q9F review packet supplied in memory/session_state.",
        "Set explicit local-only seed gates before WarRoom panel render.",
        "Do not call Q9B/Q9Q/Q10H from WarRoom UI.",
        "Confirm source_handoff=review_source_handoff_ready.",
        "Confirm source_kind=session_state_in_memory_mapping.",
        "Confirm fallback=False.",
        "Confirm ready_for_ui_mount=True.",
        "Confirm widgets=6.",
        "Confirm fallback info message is absent.",
    )
    assert BOUNDARY_OPERATOR_CONFIRMATION_CHECKLIST == (
        "Confirm no UI actual-read button/form/toggle was added.",
        "Confirm no UI loader execution occurred.",
        "Confirm no file read from WarRoom UI occurred.",
        "Confirm no payload decode from WarRoom UI occurred.",
        "Confirm no runtime artifact write from WarRoom UI occurred.",
        "Confirm no approval or authorization grant occurred.",
        "Confirm no decision or command ledger append occurred.",
        "Confirm no AutoTrade trigger occurred.",
        "Confirm no broker/private API call occurred.",
    )


def main() -> int:
    test_ps_q10u_static_contract_only_and_no_ui_runtime_tokens()
    test_ps_q10u_default_blocks_until_prerequisites_and_confirmations()
    test_ps_q10u_ready_state_packages_operator_checklists_and_versions()
    test_ps_q10u_rejects_unsafe_runtime_or_ui_requests()
    test_ps_q10u_checklist_text_is_exact_and_operator_facing()
    print("[OK] Prediction System PS-Q10U actual review-packet live page operator handoff checklist contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
