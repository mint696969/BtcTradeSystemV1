# path: ./tools/test_prediction_system_ps_q9s_actual_observation_stdout_review_parser_guard.py
# desc: Focused guard for PS-Q9S actual observation stdout review parser.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_observation_stdout_review_parser import (
    ACTUAL_OBSERVATION_STDOUT_REVIEW_PARSER_VERSION,
    ACTUAL_OBSERVATION_STDOUT_REVIEW_SEQUENCE,
    build_prediction_warroom_actual_observation_stdout_review_parser,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_read_operator_runner_scaffold import ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_observation_stdout_review_parser.py"
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
    "build_prediction_warroom_actual_read_operator_runner_scaffold(",
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
    "observation_command_executed_by_this_parser: bool = True",
    "loader_execution_requested: bool = True",
    "actual_file_read_performed_by_this_parser: bool = True",
    "payload_decode_performed_by_this_parser: bool = True",
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
    "consume_supplied_stdout_text_only",
    "parse_key_value_stdout_lines_without_running_command",
    "verify_ps_q9q_runner_version_marker",
    "verify_expected_stdout_markers",
    "verify_safety_boundary_line_all_false",
    "verify_real_payload_review_handoff_ready_before_ui_consideration",
    "return_stdout_review_packet_only",
    "do_not_run_loader_or_observation_command",
    "do_not_read_runtime_file",
    "do_not_write_runtime_artifact",
    "do_not_mutate_warroom_page_or_panel",
    "do_not_trigger_autotrade_or_broker",
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


def _ready_stdout() -> str:
    return "\n".join(
        (
            "prediction_actual_read_runner=" + ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION,
            "state=actual_read_operator_runner_scaffold_ready",
            "boundary_state=operator_script_boundary_ready_for_ps_q9q_non_ui_runner_scaffold",
            "loader_state=loaded_read_only_payload_decode_succeeded_schema_validation_deferred",
            "loaded_payload_count=1",
            "composition_state=actual_read_review_composition_ready",
            "ready_for_real_payload_review_handoff=True",
            "ready_for_future_top_default_expanded_ux=False",
            "blockers=",
            "warnings=",
            "ui=false;warroom_page_mutation=false;runtime_write=false;approval=false;ledger=false;autotrade=false;broker=false",
        )
    )


def _blocked_stdout() -> str:
    return "\n".join(
        (
            "prediction_actual_read_runner=" + ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION,
            "state=actual_read_operator_runner_scaffold_blocked",
            "boundary_state=operator_script_boundary_ready_for_ps_q9q_non_ui_runner_scaffold",
            "loader_state=blocked_before_actual_read",
            "loaded_payload_count=0",
            "composition_state=actual_read_review_composition_blocked",
            "ready_for_real_payload_review_handoff=False",
            "ready_for_future_top_default_expanded_ux=False",
            "blockers=loaded_payload_count_not_positive",
            "warnings=",
            "ui=false;warroom_page_mutation=false;runtime_write=false;approval=false;ledger=false;autotrade=false;broker=false",
        )
    )


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["parser_only"] is True
    assert packet["supplied_text_only"] is True
    assert packet["stdout_review_only"] is True
    for key in (
        "ready_for_warroom_ui_mount",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "observation_command_executed_by_this_parser",
        "loader_execution_requested",
        "actual_file_read_performed_by_this_parser",
        "payload_decode_performed_by_this_parser",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "runtime_artifact_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
        "ready_for_future_top_default_expanded_ux",
    ):
        assert packet[key] is False, key


def test_ps_q9s_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_observation_stdout_review_parser.ps_q9s.v1" in text
    assert "build_prediction_warroom_actual_observation_stdout_review_parser" in text
    assert list(ACTUAL_OBSERVATION_STDOUT_REVIEW_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_OBSERVATION_STDOUT_REVIEW_PARSER_VERSION == "prediction_warroom_actual_observation_stdout_review_parser.ps_q9s.v1"


def test_ps_q9s_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_actual_observation_stdout_review_parser"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q9s_missing_stdout_fails_closed() -> None:
    packet = build_prediction_warroom_actual_observation_stdout_review_parser().to_dict()
    assert packet["parser_state"] == "actual_observation_stdout_review_blocked"
    assert packet["supplied_stdout_present"] is False
    assert "supplied_stdout_text_required" in packet["blocked_reasons"]
    assert packet["ready_for_real_payload_ui_handoff_consideration"] is False
    _assert_safe(packet)


def test_ps_q9s_ready_stdout_passes_for_ui_handoff_consideration_only() -> None:
    packet = build_prediction_warroom_actual_observation_stdout_review_parser(stdout_text=_ready_stdout()).to_dict()
    assert packet["parser_state"] == "actual_observation_stdout_review_ready_for_ui_handoff_consideration"
    assert packet["runner_version_marker_valid"] is True
    assert packet["runner_state"] == "actual_read_operator_runner_scaffold_ready"
    assert packet["loaded_payload_count"] == 1
    assert packet["composition_state"] == "actual_read_review_composition_ready"
    assert packet["ready_for_real_payload_review_handoff"] is True
    assert packet["ready_for_real_payload_ui_handoff_consideration"] is True
    assert packet["ready_for_warroom_ui_mount"] is False
    assert packet["blocked_reasons"] == []
    _assert_safe(packet)


def test_ps_q9s_blocked_stdout_remains_blocked() -> None:
    packet = build_prediction_warroom_actual_observation_stdout_review_parser(stdout_text=_blocked_stdout()).to_dict()
    assert packet["parser_state"] == "actual_observation_stdout_review_blocked"
    assert "runner_state_not_ready" in packet["blocked_reasons"]
    assert "loaded_payload_count_not_positive" in packet["blocked_reasons"]
    assert "composition_state_not_ready" in packet["blocked_reasons"]
    assert "real_payload_review_handoff_not_ready" in packet["blocked_reasons"]
    assert "stdout_reported_blockers_present" in packet["blocked_reasons"]
    assert packet["ready_for_real_payload_ui_handoff_consideration"] is False
    _assert_safe(packet)


def test_ps_q9s_missing_safety_line_blocks() -> None:
    stdout = _ready_stdout().replace("ui=false;warroom_page_mutation=false;runtime_write=false;approval=false;ledger=false;autotrade=false;broker=false", "ui=false")
    packet = build_prediction_warroom_actual_observation_stdout_review_parser(stdout_text=stdout).to_dict()
    assert packet["parser_state"] == "actual_observation_stdout_review_blocked"
    assert "expected_stdout_markers_missing" in packet["blocked_reasons"]
    assert "safety_boundary_line_missing_or_not_all_false" in packet["blocked_reasons"]
    assert packet["safety_flags_all_false"] is False
    _assert_safe(packet)


def test_ps_q9s_future_top_true_blocks() -> None:
    stdout = _ready_stdout().replace("ready_for_future_top_default_expanded_ux=False", "ready_for_future_top_default_expanded_ux=True")
    packet = build_prediction_warroom_actual_observation_stdout_review_parser(stdout_text=stdout).to_dict()
    assert packet["parser_state"] == "actual_observation_stdout_review_blocked"
    assert "expected_stdout_markers_missing" in packet["blocked_reasons"]
    assert "future_top_default_expanded_ux_should_remain_false" in packet["blocked_reasons"]
    assert packet["ready_for_future_top_default_expanded_ux"] is False
    _assert_safe(packet)


def main() -> int:
    test_ps_q9s_static_boundaries_and_markers()
    test_ps_q9s_does_not_mutate_warroom_page_or_panel()
    test_ps_q9s_missing_stdout_fails_closed()
    test_ps_q9s_ready_stdout_passes_for_ui_handoff_consideration_only()
    test_ps_q9s_blocked_stdout_remains_blocked()
    test_ps_q9s_missing_safety_line_blocks()
    test_ps_q9s_future_top_true_blocks()
    print("[OK] Prediction System PS-Q9S actual observation stdout review parser guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
