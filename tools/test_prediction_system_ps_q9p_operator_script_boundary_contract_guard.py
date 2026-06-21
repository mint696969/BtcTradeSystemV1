# path: ./tools/test_prediction_system_ps_q9p_operator_script_boundary_contract_guard.py
# desc: Focused guard for PS-Q9P non-UI operator-script boundary contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_read_operator_script_boundary_contract import (
    ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION,
    ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_SEQUENCE,
    REQUIRED_OPERATOR_STEPS,
    build_prediction_warroom_actual_read_operator_script_boundary_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_operator_script_boundary_contract.py"
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
    "load_prediction_warroom_latest_payload_read_only(",
    "allow_actual_read=True",
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
    "would_load_source_artifacts: bool = True",
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
EXPECTED_SEQUENCE = [
    "declare_non_ui_operator_script_boundary_contract_only",
    "require_explicit_operator_acknowledgement_before_future_runner_slice",
    "limit_future_runner_to_q9b_read_only_loader_and_q9o_composition_harness",
    "require_hot_latest_root_under_d_btc_ts_hot",
    "require_stdout_only_or_in_memory_result_observation",
    "forbid_warroom_ui_triggered_actual_read",
    "forbid_warroom_page_or_panel_mutation",
    "forbid_runtime_artifact_write_and_ledger_append",
    "forbid_autotrade_and_broker_controls",
    "return_operator_script_boundary_contract_only",
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
    assert packet["preflight_only"] is True
    assert packet["non_ui_operator_script_boundary_only"] is True
    assert packet["future_runner_must_stay_non_ui"] is True
    assert packet["future_runner_must_use_q9b_loader"] is True
    assert packet["future_runner_must_use_q9o_harness"] is True
    for key in (
        "ready_for_warroom_ui_mount",
        "actual_runner_included",
        "actual_observation_performed",
        "actual_file_read_performed_by_this_contract",
        "payload_decode_performed_by_this_contract",
        "loader_execution_performed_by_this_contract",
        "ui_triggered_loader_execution",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "runtime_artifact_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "streamlit_import_required",
        "ui_controls_added",
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


def test_ps_q9p_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_read_operator_script_boundary_contract.ps_q9p.v1" in text
    assert "build_prediction_warroom_actual_read_operator_script_boundary_contract" in text
    assert list(ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION == "prediction_warroom_actual_read_operator_script_boundary_contract.ps_q9p.v1"
    assert "run_non_ui_script_from_operator_shell_only" in REQUIRED_OPERATOR_STEPS


def test_ps_q9p_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_actual_read_operator_script_boundary_contract"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q9p_default_requires_operator_acknowledgement() -> None:
    packet = build_prediction_warroom_actual_read_operator_script_boundary_contract().to_dict()
    assert packet["contract_state"] == "operator_script_boundary_blocked"
    assert packet["ready_for_ps_q9q_non_ui_runner_scaffold"] is False
    assert packet["future_non_ui_runner_scaffold_allowed"] is False
    assert "operator_acknowledgement_required_before_non_ui_runner_scaffold" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9p_acknowledged_default_boundary_is_ready_for_next_scaffold_only() -> None:
    packet = build_prediction_warroom_actual_read_operator_script_boundary_contract(
        operator_acknowledged=True,
    ).to_dict()
    assert packet["contract_state"] == "operator_script_boundary_ready_for_ps_q9q_non_ui_runner_scaffold"
    assert packet["ready_for_ps_q9q_non_ui_runner_scaffold"] is True
    assert packet["future_non_ui_runner_scaffold_allowed"] is True
    assert packet["ready_for_warroom_ui_mount"] is False
    assert packet["actual_runner_included"] is False
    assert packet["actual_observation_performed"] is False
    assert packet["blocked_reasons"] == []
    _assert_safe(packet)


def test_ps_q9p_blocks_wrong_root_and_ui_requests() -> None:
    packet = build_prediction_warroom_actual_read_operator_script_boundary_contract(
        hot_latest_root_hint="E:\\btc_ts",
        operator_acknowledged=True,
        requested_ui_mount=True,
        requested_warroom_page_mutation=True,
        requested_warroom_panel_mutation=True,
    ).to_dict()
    assert packet["contract_state"] == "operator_script_boundary_blocked"
    assert "hot_latest_root_must_stay_under_D_btc_ts_hot" in packet["blocked_reasons"]
    assert "warroom_ui_mount_not_allowed_for_actual_read_runner" in packet["blocked_reasons"]
    assert "warroom_page_mutation_not_allowed" in packet["blocked_reasons"]
    assert "warroom_panel_mutation_not_allowed" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9p_blocks_runtime_execution_requests() -> None:
    packet = build_prediction_warroom_actual_read_operator_script_boundary_contract(
        operator_acknowledged=True,
        requested_runtime_artifact_write=True,
        requested_approval_or_authorization=True,
        requested_ledger_append=True,
        requested_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "operator_script_boundary_blocked"
    assert "runtime_artifact_write_not_allowed" in packet["blocked_reasons"]
    assert "approval_or_authorization_not_allowed" in packet["blocked_reasons"]
    assert "decision_or_command_ledger_append_not_allowed" in packet["blocked_reasons"]
    assert "autotrade_or_broker_not_allowed" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9p_non_default_roles_warn_only_when_boundary_is_otherwise_ready() -> None:
    packet = build_prediction_warroom_actual_read_operator_script_boundary_contract(
        operator_acknowledged=True,
        allowed_artifact_roles=("prediction_system_result_snapshot", "prediction_warroom_display_packet"),
    ).to_dict()
    assert packet["contract_state"] == "operator_script_boundary_ready_for_ps_q9q_non_ui_runner_scaffold"
    assert "non_default_artifact_roles_require_extra_review_before_runner_scaffold" in packet["warning_reasons"]
    assert packet["ready_for_warroom_ui_mount"] is False
    _assert_safe(packet)


def main() -> int:
    test_ps_q9p_static_boundaries_and_markers()
    test_ps_q9p_does_not_mutate_warroom_page_or_panel()
    test_ps_q9p_default_requires_operator_acknowledgement()
    test_ps_q9p_acknowledged_default_boundary_is_ready_for_next_scaffold_only()
    test_ps_q9p_blocks_wrong_root_and_ui_requests()
    test_ps_q9p_blocks_runtime_execution_requests()
    test_ps_q9p_non_default_roles_warn_only_when_boundary_is_otherwise_ready()
    print("[OK] Prediction System PS-Q9P operator-script boundary contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
