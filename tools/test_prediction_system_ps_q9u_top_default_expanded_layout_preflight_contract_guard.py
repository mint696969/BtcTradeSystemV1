# path: ./tools/test_prediction_system_ps_q9u_top_default_expanded_layout_preflight_contract_guard.py
# desc: Focused guard for PS-Q9U top/default-expanded layout preflight contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_observation_stdout_review_parser import (
    build_prediction_warroom_actual_observation_stdout_review_parser,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_observation_ui_handoff_readiness_contract import (
    build_prediction_warroom_actual_observation_ui_handoff_readiness_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_read_operator_runner_scaffold import ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_top_default_expanded_layout_preflight_contract import (
    TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_CONTRACT_VERSION,
    TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_SEQUENCE,
    build_prediction_warroom_top_default_expanded_layout_preflight_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_top_default_expanded_layout_preflight_contract.py"
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
    "build_prediction_warroom_actual_observation_ui_handoff_readiness_contract(",
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
    "default_expanded_applied: bool = True",
    "page_patch_included: bool = True",
    "panel_patch_included: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_loader_execution: bool = True",
    "stdout_parser_executed_by_this_contract: bool = True",
    "observation_command_executed_by_this_contract: bool = True",
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
    "consume_supplied_ps_q9t_readiness_packet_only",
    "verify_ps_q9t_contract_version",
    "verify_future_layout_review_ready",
    "verify_future_top_default_expanded_review_ready",
    "declare_target_warroom_top_section_plan",
    "declare_default_expanded_plan_without_applying_it",
    "require_next_slice_explicit_page_patch",
    "keep_warroom_page_and_panel_mutation_false",
    "keep_ui_controls_and_loader_execution_false",
    "return_layout_preflight_contract_only",
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


def _ready_q9t_packet() -> dict:
    parser = build_prediction_warroom_actual_observation_stdout_review_parser(stdout_text=_ready_stdout()).to_dict()
    return build_prediction_warroom_actual_observation_ui_handoff_readiness_contract(parser_packet=parser).to_dict()


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["contract_only"] is True
    assert packet["supplied_q9t_packet_only"] is True
    assert packet["layout_preflight_only"] is True
    for key in (
        "ready_for_warroom_ui_mount",
        "top_default_expanded_application_allowed",
        "default_expanded_applied",
        "page_patch_included",
        "panel_patch_included",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "stdout_parser_executed_by_this_contract",
        "observation_command_executed_by_this_contract",
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


def test_ps_q9u_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_top_default_expanded_layout_preflight_contract.ps_q9u.v1" in text
    assert "build_prediction_warroom_top_default_expanded_layout_preflight_contract" in text
    assert list(TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_SEQUENCE) == EXPECTED_SEQUENCE
    assert TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_CONTRACT_VERSION == "prediction_warroom_top_default_expanded_layout_preflight_contract.ps_q9u.v1"


def test_ps_q9u_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_top_default_expanded_layout_preflight_contract"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q9u_missing_q9t_packet_fails_closed() -> None:
    packet = build_prediction_warroom_top_default_expanded_layout_preflight_contract().to_dict()
    assert packet["contract_state"] == "top_default_expanded_layout_preflight_blocked"
    assert "ps_q9t_ui_handoff_readiness_packet_required" in packet["blocked_reasons"]
    assert packet["ready_for_next_ui_patch_slice"] is False
    _assert_safe(packet)


def test_ps_q9u_ready_q9t_packet_allows_next_ui_patch_slice_only() -> None:
    packet = build_prediction_warroom_top_default_expanded_layout_preflight_contract(
        ui_handoff_readiness_packet=_ready_q9t_packet(),
    ).to_dict()
    assert packet["contract_state"] == "top_default_expanded_layout_preflight_ready_for_next_ui_patch_slice"
    assert packet["q9t_packet_version_valid"] is True
    assert packet["q9t_ready_for_future_warroom_layout_review"] is True
    assert packet["q9t_ready_for_future_top_default_expanded_review"] is True
    assert packet["ready_for_next_ui_patch_slice"] is True
    assert packet["ready_for_warroom_ui_mount"] is False
    assert packet["top_default_expanded_application_allowed"] is False
    assert packet["default_expanded_applied"] is False
    assert packet["page_patch_included"] is False
    assert packet["panel_patch_included"] is False
    rows = packet["target_layout_plan_rows"]
    assert rows[0]["target_location"] == "warroom_top_before_overview_zone"
    assert rows[0]["expanded_by_default_plan"] == "true_after_next_ui_patch_only"
    assert rows[0]["applied_this_slice"] == "false"
    assert packet["blocked_reasons"] == []
    _assert_safe(packet)


def test_ps_q9u_blocked_q9t_packet_blocks() -> None:
    q9t = _ready_q9t_packet()
    q9t["contract_state"] = "actual_observation_ui_handoff_readiness_blocked"
    q9t["ready_for_future_warroom_layout_review"] = False
    q9t["blocked_reasons"] = ["synthetic_blocker"]
    packet = build_prediction_warroom_top_default_expanded_layout_preflight_contract(
        ui_handoff_readiness_packet=q9t,
    ).to_dict()
    assert packet["contract_state"] == "top_default_expanded_layout_preflight_blocked"
    assert "ps_q9t_blockers_present" in packet["blocked_reasons"]
    assert "ps_q9t_contract_state_not_ready" in packet["blocked_reasons"]
    assert "ps_q9t_future_layout_review_not_ready" in packet["blocked_reasons"]
    assert packet["ready_for_next_ui_patch_slice"] is False
    _assert_safe(packet)


def test_ps_q9u_rejects_unsafe_q9t_true_flags() -> None:
    q9t = _ready_q9t_packet()
    q9t["page_patch_included"] = True
    q9t["warroom_page_mutation_allowed"] = True
    packet = build_prediction_warroom_top_default_expanded_layout_preflight_contract(
        ui_handoff_readiness_packet=q9t,
    ).to_dict()
    assert packet["contract_state"] == "top_default_expanded_layout_preflight_blocked"
    assert "ps_q9t_unsafe_true_flag:page_patch_included" in packet["blocked_reasons"]
    assert "ps_q9t_unsafe_true_flag:warroom_page_mutation_allowed" in packet["blocked_reasons"]
    assert "ps_q9t_page_patch_must_not_already_be_included" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9u_rejects_invalid_q9t_version() -> None:
    q9t = _ready_q9t_packet()
    q9t["contract_version"] = "invalid"
    packet = build_prediction_warroom_top_default_expanded_layout_preflight_contract(
        ui_handoff_readiness_packet=q9t,
    ).to_dict()
    assert packet["contract_state"] == "top_default_expanded_layout_preflight_blocked"
    assert "ps_q9t_contract_version_invalid" in packet["blocked_reasons"]
    assert packet["q9t_packet_version_valid"] is False
    _assert_safe(packet)


def main() -> int:
    test_ps_q9u_static_boundaries_and_markers()
    test_ps_q9u_does_not_mutate_warroom_page_or_panel()
    test_ps_q9u_missing_q9t_packet_fails_closed()
    test_ps_q9u_ready_q9t_packet_allows_next_ui_patch_slice_only()
    test_ps_q9u_blocked_q9t_packet_blocks()
    test_ps_q9u_rejects_unsafe_q9t_true_flags()
    test_ps_q9u_rejects_invalid_q9t_version()
    print("[OK] Prediction System PS-Q9U top/default-expanded layout preflight contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
