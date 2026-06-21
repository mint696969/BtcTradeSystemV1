# path: ./tools/test_prediction_system_ps_q9r_actual_observation_runbook_contract_guard.py
# desc: Focused guard for PS-Q9R actual observation runbook contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_observation_runbook_contract import (
    ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE,
    EXPECTED_STDOUT_MARKERS,
    REQUIRED_OPERATOR_REVIEW_ITEMS,
    build_prediction_warroom_actual_observation_runbook_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_observation_runbook_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.processing.l4_consumer_models.shared",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "json",
    "pathlib",
)
FORBIDDEN_TOKENS = (
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
    ".exists(",
    ".stat(",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "persist=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_loader_execution: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "runtime_artifact_write_allowed: bool = True",
    "approval_or_authorization_allowed: bool = True",
    "ledger_append_allowed: bool = True",
    "autotrade_trigger_allowed: bool = True",
    "broker_private_api_allowed: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)
EXPECTED_SEQUENCE = [
    "declare_contract_only_non_ui_actual_observation_runbook",
    "require_operator_acknowledgement_before_command_use",
    "generate_stdout_only_python_command_for_ps_q9q_runner",
    "require_clean_working_tree_before_manual_observation",
    "require_hot_latest_root_under_d_btc_ts_hot",
    "require_operator_to_paste_stdout_back_for_review",
    "forbid_warroom_ui_mount_or_page_panel_mutation",
    "forbid_runtime_artifact_write_and_ledger_append",
    "forbid_autotrade_and_broker_controls",
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


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["contract_only"] is True
    assert packet["runbook_only"] is True
    assert packet["stdout_capture_contract_only"] is True
    assert packet["command_must_be_run_from_operator_shell"] is True
    assert packet["command_must_not_be_run_from_warroom_ui"] is True
    assert packet["command_must_remain_stdout_only"] is True
    assert packet["command_must_not_write_files"] is True
    assert packet["command_must_not_append_ledgers"] is True
    assert packet["command_must_not_trigger_trade"] is True
    for key in (
        "ready_for_warroom_ui_mount",
        "actual_runner_executed_by_this_contract",
        "actual_observation_performed_by_this_contract",
        "actual_file_read_performed_by_this_contract",
        "payload_decode_performed_by_this_contract",
        "runtime_artifact_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
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


def test_ps_q9r_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_observation_runbook_contract.ps_q9r.v1" in text
    assert "build_prediction_warroom_actual_observation_runbook_contract" in text
    assert list(ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION == "prediction_warroom_actual_observation_runbook_contract.ps_q9r.v1"
    assert "ready_for_real_payload_review_handoff=" in EXPECTED_STDOUT_MARKERS
    assert "safety_flags_all_false" in REQUIRED_OPERATOR_REVIEW_ITEMS


def test_ps_q9r_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_actual_observation_runbook_contract"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q9r_default_is_blocked_and_generates_no_command() -> None:
    packet = build_prediction_warroom_actual_observation_runbook_contract().to_dict()
    assert packet["contract_state"] == "actual_observation_runbook_blocked"
    assert packet["ready_for_manual_non_ui_observation"] is False
    assert packet["command_generated"] is False
    assert packet["generated_powershell_lines"] == []
    assert "operator_acknowledgement_required_before_generating_manual_observation_command" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9r_acknowledged_generates_stdout_only_manual_command() -> None:
    packet = build_prediction_warroom_actual_observation_runbook_contract(
        operator_acknowledged=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_observation_runbook_ready_for_manual_non_ui_shell"
    assert packet["ready_for_manual_non_ui_observation"] is True
    assert packet["command_generated"] is True
    assert packet["command_allowed_for_manual_shell_use"] is True
    assert packet["blocked_reasons"] == []
    ps = "\n".join(packet["generated_powershell_lines"])
    assert "cd C:\\BtcTradeSystem" in ps
    assert "build_prediction_warroom_actual_read_operator_runner_scaffold" in ps
    assert "format_prediction_warroom_actual_read_operator_runner_stdout_summary" in ps
    assert "operator_acknowledged=True" in ps
    assert "execute_actual_read=True" in ps
    assert "D:\\btc_ts_hot" in ps
    assert "write_text" not in ps
    assert "append" not in ps.lower()
    _assert_safe(packet)


def test_ps_q9r_blocks_wrong_root_and_runtime_requests() -> None:
    packet = build_prediction_warroom_actual_observation_runbook_contract(
        hot_latest_root_hint="E:\\btc_ts",
        operator_acknowledged=True,
        requested_warroom_ui_mount=True,
        requested_runtime_artifact_write=True,
        requested_ledger_append=True,
        requested_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_observation_runbook_blocked"
    assert "hot_latest_root_must_stay_under_D_btc_ts_hot" in packet["blocked_reasons"]
    assert "warroom_ui_mount_not_allowed_for_actual_observation" in packet["blocked_reasons"]
    assert "runtime_artifact_write_not_allowed" in packet["blocked_reasons"]
    assert "decision_or_command_ledger_append_not_allowed" in packet["blocked_reasons"]
    assert "autotrade_or_broker_not_allowed" in packet["blocked_reasons"]
    assert packet["command_generated"] is False
    _assert_safe(packet)


def test_ps_q9r_non_default_roles_warn_only_when_ready() -> None:
    packet = build_prediction_warroom_actual_observation_runbook_contract(
        operator_acknowledged=True,
        allowed_artifact_roles=("prediction_system_result_snapshot", "prediction_warroom_display_packet"),
    ).to_dict()
    assert packet["contract_state"] == "actual_observation_runbook_ready_for_manual_non_ui_shell"
    assert "non_default_artifact_roles_require_extra_review_before_manual_observation" in packet["warning_reasons"]
    assert packet["command_generated"] is True
    _assert_safe(packet)


def main() -> int:
    test_ps_q9r_static_boundaries_and_markers()
    test_ps_q9r_does_not_mutate_warroom_page_or_panel()
    test_ps_q9r_default_is_blocked_and_generates_no_command()
    test_ps_q9r_acknowledged_generates_stdout_only_manual_command()
    test_ps_q9r_blocks_wrong_root_and_runtime_requests()
    test_ps_q9r_non_default_roles_warn_only_when_ready()
    print("[OK] Prediction System PS-Q9R actual observation runbook contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
