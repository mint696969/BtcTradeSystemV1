# path: ./tools/test_prediction_system_ps_q10c_source_mapping_actual_observation_runbook_contract_guard.py
# desc: Focused guard for PS-Q10C source mapping actual observation runbook contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_source_mapping_actual_observation_runbook_contract import (
    EXPECTED_STDOUT_MARKERS,
    REQUIRED_OPERATOR_REVIEW_ITEMS,
    SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE,
    build_prediction_warroom_source_mapping_actual_observation_runbook_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_source_mapping_probe_runner import SOURCE_MAPPING_PROBE_RUNNER_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_mapping_actual_observation_runbook_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade",
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
    "build_prediction_system_result(",
    "aggregate_ohlcv_from_rows(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "build_prediction_warroom_display_packet(",
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
    "prediction_system_result_built_by_this_contract: bool = True",
    "latest_prediction_artifact_exported_by_this_contract: bool = True",
    "actual_runner_executed_by_this_contract: bool = True",
    "actual_observation_performed_by_this_contract: bool = True",
    "actual_file_read_performed_by_this_contract: bool = True",
    "payload_decode_performed_by_this_contract: bool = True",
    "runtime_artifact_write_allowed: bool = True",
    "approval_or_authorization_allowed: bool = True",
    "ledger_append_allowed: bool = True",
    "autotrade_trigger_allowed: bool = True",
    "broker_private_api_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_runner_execution: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_write_collector_state: bool = True",
    "would_send_to_broker: bool = True",
)
EXPECTED_SEQUENCE = [
    "declare_contract_only_non_ui_source_mapping_observation_runbook",
    "require_operator_acknowledgement_before_command_use",
    "generate_stdout_only_python_command_for_ps_q10b_runner",
    "include_pythonpath_for_btcts_next_src",
    "require_clean_working_tree_before_manual_observation",
    "require_hot_latest_root_under_d_btc_ts_hot",
    "require_operator_to_paste_stdout_back_for_review",
    "forbid_prediction_build_and_latest_payload_export",
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
        "actual_runner_executed_by_this_contract",
        "actual_observation_performed_by_this_contract",
        "actual_file_read_performed_by_this_contract",
        "payload_decode_performed_by_this_contract",
        "prediction_system_result_built_by_this_contract",
        "latest_prediction_artifact_exported_by_this_contract",
        "runtime_artifact_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_runner_execution",
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


def test_ps_q10c_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION == "prediction_warroom_source_mapping_actual_observation_runbook_contract.ps_q10c.v1"
    assert list(SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE) == EXPECTED_SEQUENCE
    assert "ready_for_future_prediction_system_result_builder=" in EXPECTED_STDOUT_MARKERS
    assert "safety_flags_all_false" in REQUIRED_OPERATOR_REVIEW_ITEMS


def test_ps_q10c_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_source_mapping_actual_observation_runbook_contract" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q10c_default_blocks_and_generates_no_command() -> None:
    packet = build_prediction_warroom_source_mapping_actual_observation_runbook_contract().to_dict()
    assert packet["contract_state"] == "source_mapping_actual_observation_runbook_blocked"
    assert packet["ready_for_manual_non_ui_observation"] is False
    assert packet["command_generated"] is False
    assert packet["generated_powershell_lines"] == []
    assert "operator_acknowledgement_required_before_generating_source_mapping_observation_command" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q10c_acknowledged_generates_stdout_only_manual_command_with_pythonpath() -> None:
    packet = build_prediction_warroom_source_mapping_actual_observation_runbook_contract(operator_acknowledged=True).to_dict()
    assert packet["contract_state"] == "source_mapping_actual_observation_runbook_ready_for_manual_non_ui_shell"
    assert packet["ready_for_manual_non_ui_observation"] is True
    assert packet["command_generated"] is True
    assert packet["command_allowed_for_manual_shell_use"] is True
    assert packet["blocked_reasons"] == []
    ps = "\n".join(packet["generated_powershell_lines"])
    assert "cd C:\\BtcTradeSystem" in ps
    assert "$env:PYTHONPATH = \"$PWD\\btcts_next\\src\"" in ps
    assert "build_prediction_warroom_source_mapping_probe_runner" in ps
    assert "format_prediction_warroom_source_mapping_probe_runner_stdout_summary" in ps
    assert "operator_acknowledged=True" in ps
    assert "allow_actual_read=True" in ps
    assert "D:\\btc_ts_hot" in ps
    assert SOURCE_MAPPING_PROBE_RUNNER_VERSION == "prediction_warroom_source_mapping_probe_runner.ps_q10b.v1"
    assert "build_prediction_system_result" not in ps
    assert "latest_payload_export" not in ps
    assert "write_text" not in ps
    assert "append" not in ps.lower()
    _assert_safe(packet)


def test_ps_q10c_blocks_wrong_root_and_forbidden_requests() -> None:
    packet = build_prediction_warroom_source_mapping_actual_observation_runbook_contract(
        hot_latest_root_hint="E:\\btc_ts",
        operator_acknowledged=True,
        requested_prediction_build=True,
        requested_latest_payload_export=True,
        requested_warroom_ui_mount=True,
        requested_runtime_artifact_write=True,
        requested_ledger_append=True,
        requested_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "source_mapping_actual_observation_runbook_blocked"
    assert "hot_latest_root_must_stay_under_D_btc_ts_hot" in packet["blocked_reasons"]
    assert "prediction_build_not_allowed_for_source_mapping_observation" in packet["blocked_reasons"]
    assert "latest_payload_export_not_allowed_for_source_mapping_observation" in packet["blocked_reasons"]
    assert "warroom_ui_mount_not_allowed_for_source_mapping_observation" in packet["blocked_reasons"]
    assert "runtime_artifact_write_not_allowed" in packet["blocked_reasons"]
    assert "decision_or_command_ledger_append_not_allowed" in packet["blocked_reasons"]
    assert "autotrade_or_broker_not_allowed" in packet["blocked_reasons"]
    assert packet["command_generated"] is False
    _assert_safe(packet)


def main() -> int:
    test_ps_q10c_static_boundaries_and_markers()
    test_ps_q10c_not_mounted_in_warroom_ui()
    test_ps_q10c_default_blocks_and_generates_no_command()
    test_ps_q10c_acknowledged_generates_stdout_only_manual_command_with_pythonpath()
    test_ps_q10c_blocks_wrong_root_and_forbidden_requests()
    print("[OK] Prediction System PS-Q10C source mapping actual observation runbook contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
