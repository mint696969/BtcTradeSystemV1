# path: ./tools/test_prediction_system_ps_q8e_mount_review_ux_contract_guard.py
# desc: Guard for PS-Q8E Prediction WarRoom mount review UX contract. Manual visual verification contract only; no runtime loader, file reads, payload decode, Collector, AutoTrade, broker, approval, command, or WarRoom page mutation.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_mount_review_ux_contract import (
    build_prediction_warroom_mount_review_ux_contract,
    build_prediction_warroom_mount_review_ux_contract_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_mount_review_ux_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
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
    ".exists(",
    ".stat(",
    "st.",
    "build_prediction_system_result",
    "assess_source_quality",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "place_order(",
    "send_order(",
    "create_order(",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "ui_rendering_allowed: bool = True",
    "streamlit_render_allowed: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "page_mutation_allowed: bool = True",
    "actual_file_read_allowed_by_this_contract: bool = True",
    "actual_payload_decode_allowed_by_this_contract: bool = True",
    "actual_loader_execution_allowed: bool = True",
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
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


def _assert_safe(payload: dict) -> None:
    assert payload["read_only"] is True
    assert payload["non_executing"] is True
    assert payload["display_only"] is True
    assert payload["manual_visual_verification_only"] is True
    assert payload["ui_rendering_allowed"] is False
    assert payload["streamlit_render_allowed"] is False
    assert payload["warroom_page_mutation_allowed"] is False
    assert payload["page_mutation_allowed"] is False
    assert payload["app_routing_mutation_allowed"] is False
    assert payload["actual_loader_execution_allowed"] is False
    assert payload["actual_file_read_allowed_by_this_contract"] is False
    assert payload["actual_payload_decode_allowed_by_this_contract"] is False
    assert payload["would_load_hot_latest_artifacts"] is False
    assert payload["would_read_runtime_file"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["would_send_to_broker"] is False


def _function_source(module_text: str, function_name: str) -> str:
    tree = ast.parse(module_text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(module_text, node) or ""
    raise AssertionError(f"missing function: {function_name}")


def test_ps_q8e_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_mount_review_ux_contract.ps_q8e.v1" in text
    assert "PredictionWarRoomMountReviewUXContract" in text
    assert "build_prediction_warroom_mount_review_ux_contract" in text
    assert "build_prediction_warroom_mount_review_ux_contract_index" in text
    assert "manual_visual_verification_only" in text
    assert "human_visual_confirmation_required" in text


def test_ps_q8e_default_contract_is_ready_for_manual_visual_confirmation() -> None:
    contract = build_prediction_warroom_mount_review_ux_contract().to_dict()
    assert contract["contract_version"] == "prediction_warroom_mount_review_ux_contract.ps_q8e.v1"
    assert contract["source_presenter_version"] == "prediction_warroom_ui_mount_presenter.ps_q8b.v1"
    assert contract["source_insertion_contract_version"] == "prediction_warroom_page_insertion_contract.ps_q8c.v1"
    assert contract["ux_state"] == "ready_for_manual_visual_confirmation_runtime_disconnected"
    assert contract["section_label"] == "Prediction WarRoom mount review"
    assert contract["section_anchor"] == "after_operator_support_zone_before_slot_diagnostics"
    assert contract["expected_initial_expanded"] is False
    assert contract["expected_mount_entry_row_count"] == 12
    assert contract["expected_zone_section_count"] == 3
    assert contract["expected_blocked_entry_row_count"] == 0
    assert contract["manual_visual_check_count"] == 6
    assert contract["ux_metrics"]["runtime_disconnected"] is True
    assert contract["ux_metrics"]["ux_contract_ready"] is True
    for payload in (contract, contract["boundaries"], contract["integration_contract"], *contract["manual_visual_checks"]):
        _assert_safe(payload)


def test_ps_q8e_manual_checklist_is_explicit_and_non_automating() -> None:
    contract = build_prediction_warroom_mount_review_ux_contract().to_dict()
    check_ids = [item["check_id"] for item in contract["manual_visual_checks"]]
    assert check_ids == [
        "section_visible_in_warroom",
        "section_collapsed_by_default",
        "compact_line_visible_when_expanded",
        "zone_summary_rows_visible",
        "mount_entry_rows_visible",
        "runtime_remains_disconnected",
    ]
    assert all(item["status"] == "requires_human_visual_confirmation" for item in contract["manual_visual_checks"])
    assert all(item["completed_by_contract"] is False for item in contract["manual_visual_checks"])
    assert all(item["automated_runtime_check"] is False for item in contract["manual_visual_checks"])


def test_ps_q8e_index_is_compact_and_safe() -> None:
    index = build_prediction_warroom_mount_review_ux_contract_index()
    assert index["contract_index_version"] == "prediction_warroom_mount_review_ux_contract.ps_q8e.v1"
    assert index["ux_state"] == "ready_for_manual_visual_confirmation_runtime_disconnected"
    assert index["manual_visual_check_count"] == 6
    assert index["ux_metrics"]["loader_disconnected"] is True
    assert index["integration_contract"]["human_visual_confirmation_required"] is True
    assert index["integration_contract"]["does_not_mutate_warroom_page"] is True
    for payload in (index, index["boundaries"], index["integration_contract"], *index["manual_visual_checks"]):
        _assert_safe(payload)


def test_ps_q8e_warroom_page_section_still_matches_ux_contract() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    folded_section_marker = 'with live_shell.render_folded_section("Prediction WarRoom mount review", expanded=False):'
    assert page_text.count(folded_section_marker) == 1
    assert page_text.count("_render_prediction_warroom_ui_mount_review_section") == 2
    assert "build_prediction_warroom_ui_mount_presenter_packet().to_dict()" in page_text
    assert "Prediction WarRoom mount review is display-only" in page_text
    assert "mount rows={rows} / zones={zones} / blocked={blocked} / render=false" in page_text
    assert 'st.dataframe(zone_rows, width="stretch", hide_index=True)' in page_text
    assert 'st.dataframe(entry_rows, width="stretch", hide_index=True)' in page_text
    operator_support_pos = page_text.index("def _render_warroom_operator_support_review()")
    section_pos = page_text.index(folded_section_marker)
    diagnostics_pos = page_text.index("get_text(lang, \"ui_slot_diagnostics_title\")")
    assert operator_support_pos < section_pos < diagnostics_pos


def test_ps_q8e_warroom_page_helper_does_not_add_runtime_controls() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    helper_text = "\n".join(
        _function_source(page_text, function_name)
        for function_name in (
            "_prediction_warroom_mount_review_zone_rows",
            "_prediction_warroom_mount_review_entry_rows",
            "_render_prediction_warroom_ui_mount_review_section",
        )
    )
    forbidden = (
        "st.button",
        "st.form",
        "st.checkbox",
        "st.toggle",
        "st.file_uploader",
        "open(",
        "Path(",
        "read_text",
        "read_bytes",
        "json.load",
        "json.loads",
        "load_prediction",
        "latest_payload",
        "hot_latest",
        "append_command_ledger_record",
        "place_order(",
        "send_order(",
        "create_order(",
    )
    for token in forbidden:
        assert token not in helper_text, token


def main() -> int:
    test_ps_q8e_static_boundaries_and_markers()
    test_ps_q8e_default_contract_is_ready_for_manual_visual_confirmation()
    test_ps_q8e_manual_checklist_is_explicit_and_non_automating()
    test_ps_q8e_index_is_compact_and_safe()
    test_ps_q8e_warroom_page_section_still_matches_ux_contract()
    test_ps_q8e_warroom_page_helper_does_not_add_runtime_controls()
    print("[OK] Prediction System PS-Q8E mount review UX contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
