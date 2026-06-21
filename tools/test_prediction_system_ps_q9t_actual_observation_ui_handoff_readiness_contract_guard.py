# path: ./tools/test_prediction_system_ps_q9t_actual_observation_ui_handoff_readiness_contract_guard.py
# desc: Focused guard for PS-Q9T actual observation UI handoff readiness contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_observation_stdout_review_parser import (
    build_prediction_warroom_actual_observation_stdout_review_parser,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_observation_ui_handoff_readiness_contract import (
    ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_CONTRACT_VERSION,
    ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_SEQUENCE,
    build_prediction_warroom_actual_observation_ui_handoff_readiness_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_read_operator_runner_scaffold import ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_observation_ui_handoff_readiness_contract.py"
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
    "build_prediction_warroom_actual_observation_stdout_review_parser(",
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
    "ready_for_warroom_ui_mount: bool = True",
    "top_default_expanded_application_allowed: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "page_patch_included: bool = True",
    "panel_patch_included: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_loader_execution: bool = True",
    "observation_command_executed_by_this_contract: bool = True",
    "stdout_parser_executed_by_this_contract: bool = True",
    "loader_execution_requested: bool = True",
    "actual_file_read_performed_by_this_contract: bool = True",
    "payload_decode_performed_by_this_contract: bool = True",
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
    "consume_supplied_ps_q9s_parser_packet_only",
    "verify_ps_q9s_parser_version",
    "verify_real_payload_stdout_review_ready",
    "verify_parser_safety_flags_all_false",
    "allow_future_layout_review_consideration_only",
    "keep_warroom_ui_mount_false",
    "keep_warroom_page_and_panel_mutation_false",
    "keep_top_default_expanded_application_false",
    "return_ui_handoff_readiness_contract_only",
    "do_not_parse_stdout_or_run_loader",
    "do_not_render_streamlit",
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


def _ready_parser_packet() -> dict:
    return build_prediction_warroom_actual_observation_stdout_review_parser(stdout_text=_ready_stdout()).to_dict()


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["contract_only"] is True
    assert packet["supplied_parser_packet_only"] is True
    assert packet["ui_handoff_readiness_only"] is True
    for key in (
        "ready_for_warroom_ui_mount",
        "top_default_expanded_application_allowed",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "page_patch_included",
        "panel_patch_included",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "observation_command_executed_by_this_contract",
        "stdout_parser_executed_by_this_contract",
        "loader_execution_requested",
        "actual_file_read_performed_by_this_contract",
        "payload_decode_performed_by_this_contract",
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
    ):
        assert packet[key] is False, key


def test_ps_q9t_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_observation_ui_handoff_readiness_contract.ps_q9t.v1" in text
    assert "build_prediction_warroom_actual_observation_ui_handoff_readiness_contract" in text
    assert list(ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_CONTRACT_VERSION == "prediction_warroom_actual_observation_ui_handoff_readiness_contract.ps_q9t.v1"


def test_ps_q9t_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_actual_observation_ui_handoff_readiness_contract"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q9t_missing_parser_fails_closed() -> None:
    packet = build_prediction_warroom_actual_observation_ui_handoff_readiness_contract().to_dict()
    assert packet["contract_state"] == "actual_observation_ui_handoff_readiness_blocked"
    assert "ps_q9s_parser_packet_required" in packet["blocked_reasons"]
    assert packet["ready_for_future_warroom_layout_review"] is False
    assert packet["ready_for_future_top_default_expanded_review"] is False
    _assert_safe(packet)


def test_ps_q9t_ready_parser_allows_layout_review_only() -> None:
    packet = build_prediction_warroom_actual_observation_ui_handoff_readiness_contract(
        parser_packet=_ready_parser_packet(),
    ).to_dict()
    assert packet["contract_state"] == "actual_observation_ui_handoff_ready_for_layout_review"
    assert packet["parser_packet_version_valid"] is True
    assert packet["parser_ready_for_real_payload_ui_handoff_consideration"] is True
    assert packet["parser_ready_for_real_payload_review_handoff"] is True
    assert packet["parser_safety_flags_all_false"] is True
    assert packet["parser_loaded_payload_count"] == 1
    assert packet["ready_for_future_warroom_layout_review"] is True
    assert packet["ready_for_future_top_default_expanded_review"] is True
    assert packet["ready_for_warroom_ui_mount"] is False
    assert packet["top_default_expanded_application_allowed"] is False
    assert packet["blocked_reasons"] == []
    _assert_safe(packet)


def test_ps_q9t_blocked_parser_blocks() -> None:
    parser = _ready_parser_packet()
    parser["parser_state"] = "actual_observation_stdout_review_blocked"
    parser["ready_for_real_payload_ui_handoff_consideration"] = False
    parser["blocked_reasons"] = ["synthetic_blocker"]
    packet = build_prediction_warroom_actual_observation_ui_handoff_readiness_contract(parser_packet=parser).to_dict()
    assert packet["contract_state"] == "actual_observation_ui_handoff_readiness_blocked"
    assert "ps_q9s_parser_blockers_present" in packet["blocked_reasons"]
    assert "ps_q9s_parser_state_not_ready" in packet["blocked_reasons"]
    assert "ps_q9s_parser_not_ready_for_ui_handoff_consideration" in packet["blocked_reasons"]
    assert packet["ready_for_future_warroom_layout_review"] is False
    _assert_safe(packet)


def test_ps_q9t_rejects_unsafe_parser_true_flag() -> None:
    parser = _ready_parser_packet()
    parser["would_send_to_broker"] = True
    packet = build_prediction_warroom_actual_observation_ui_handoff_readiness_contract(parser_packet=parser).to_dict()
    assert packet["contract_state"] == "actual_observation_ui_handoff_readiness_blocked"
    assert "ps_q9s_parser_unsafe_true_flag:would_send_to_broker" in packet["blocked_reasons"]
    assert packet["ready_for_future_warroom_layout_review"] is False
    _assert_safe(packet)


def test_ps_q9t_rejects_invalid_parser_version() -> None:
    parser = _ready_parser_packet()
    parser["parser_version"] = "invalid"
    packet = build_prediction_warroom_actual_observation_ui_handoff_readiness_contract(parser_packet=parser).to_dict()
    assert packet["contract_state"] == "actual_observation_ui_handoff_readiness_blocked"
    assert "ps_q9s_parser_version_invalid" in packet["blocked_reasons"]
    assert packet["parser_packet_version_valid"] is False
    _assert_safe(packet)


def main() -> int:
    test_ps_q9t_static_boundaries_and_markers()
    test_ps_q9t_does_not_mutate_warroom_page_or_panel()
    test_ps_q9t_missing_parser_fails_closed()
    test_ps_q9t_ready_parser_allows_layout_review_only()
    test_ps_q9t_blocked_parser_blocks()
    test_ps_q9t_rejects_unsafe_parser_true_flag()
    test_ps_q9t_rejects_invalid_parser_version()
    print("[OK] Prediction System PS-Q9T actual observation UI handoff readiness contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
