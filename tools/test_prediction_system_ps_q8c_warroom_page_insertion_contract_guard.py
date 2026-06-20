# path: ./tools/test_prediction_system_ps_q8c_warroom_page_insertion_contract_guard.py
# desc: Guard for PS-Q8C Prediction WarRoom page insertion contract. Contract metadata only; no rendering, page mutation, runtime reads, payload decode, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_page_insertion_contract import (
    build_prediction_warroom_page_insertion_contract,
    build_prediction_warroom_page_insertion_contract_index,
)
from btcts.apps.operator_ui.components.prediction_warroom_ui_mount_presenter import build_prediction_warroom_ui_mount_presenter_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_page_insertion_contract.py"
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
    "build_prediction_system_result",
    "assess_source_quality",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "st.button",
    "st.form",
    "persist=True",
    "ui_rendering_allowed: bool = True",
    "streamlit_render_allowed: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "page_mutation_allowed: bool = True",
    "app_routing_mutation_allowed: bool = True",
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
    assert payload["render_intent_only"] is True
    assert payload["not_loaded_as_runtime_display_source"] is True
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


def test_ps_q8c_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_page_insertion_contract.ps_q8c.v1" in text
    assert "PredictionWarRoomPageInsertionContract" in text
    assert "build_prediction_warroom_page_insertion_contract" in text
    assert "build_prediction_warroom_page_insertion_contract_index" in text
    assert "does_not_call_streamlit" in text
    assert "does_not_mutate_warroom_page" in text
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    assert "prediction_warroom_page_insertion_contract" not in page_text
    # Q8D may insert the folded review section after this contract slice.
    if "prediction_warroom_ui_mount_review_section" in page_text:
        assert 'render_folded_section("Prediction WarRoom mount review", expanded=False)' in page_text
        assert "_render_prediction_warroom_ui_mount_review_section" in page_text


def test_ps_q8c_default_contract_is_ready_but_does_not_insert() -> None:
    contract = build_prediction_warroom_page_insertion_contract().to_dict()
    assert contract["contract_version"] == "prediction_warroom_page_insertion_contract.ps_q8c.v1"
    assert contract["source_presenter_version"] == "prediction_warroom_ui_mount_presenter.ps_q8b.v1"
    assert contract["insertion_state"] == "ready_for_future_guarded_warroom_page_insertion"
    assert contract["target_view_module"] == "btcts.apps.operator_ui.views.warroom_page"
    assert contract["proposed_section_anchor"] == "after_operator_support_zone_before_slot_diagnostics"
    assert contract["proposed_section_id"] == "prediction_warroom_ui_mount_review_section"
    assert contract["presenter_display_state"] == "ready_for_operator_review_render_disabled"
    assert contract["zone_section_count"] == 3
    assert contract["mount_entry_row_count"] == 12
    assert contract["blocked_entry_row_count"] == 0
    assert contract["insertion_blockers"] == []
    metrics = contract["insertion_metrics"]
    assert metrics["future_insertion_allowed_by_contract"] is True
    assert metrics["insertion_allowed_in_this_slice"] is False
    assert metrics["completed_in_this_slice_count"] == 0
    assert metrics["required_step_count"] == 5
    for payload in (contract, contract["boundaries"], contract["integration_contract"], *contract["insertion_steps"]):
        _assert_safe(payload)


def test_ps_q8c_insertion_steps_are_explicit_and_folded() -> None:
    contract = build_prediction_warroom_page_insertion_contract().to_dict()
    step_ids = [item["step_id"] for item in contract["insertion_steps"]]
    assert step_ids == [
        "add_presenter_import",
        "add_folded_render_helper",
        "insert_after_operator_support_before_slot_diagnostics",
        "keep_section_collapsed_by_default",
        "render_compact_line_and_zone_rows_only",
    ]
    assert all(item["completed_in_this_slice"] is False for item in contract["insertion_steps"])
    assert all(item["allowed_in_future_guarded_slice"] is True for item in contract["insertion_steps"])
    assert contract["integration_contract"]["future_slice_must_keep_section_folded_by_default"] is True
    assert contract["integration_contract"]["future_slice_must_use_existing_live_shell_folded_section"] is True
    assert contract["integration_contract"]["future_slice_must_not_decode_payload_or_read_hot_latest"] is True


def test_ps_q8c_index_is_compact_and_safe() -> None:
    index = build_prediction_warroom_page_insertion_contract_index()
    assert index["contract_index_version"] == "prediction_warroom_page_insertion_contract.ps_q8c.v1"
    assert index["insertion_state"] == "ready_for_future_guarded_warroom_page_insertion"
    assert index["zone_section_count"] == 3
    assert index["mount_entry_row_count"] == 12
    assert index["blocked_entry_row_count"] == 0
    assert index["insertion_metrics"]["future_insertion_allowed_by_contract"] is True
    assert index["integration_contract"]["requires_streamlit_rendering"] is False
    for payload in (index, index["boundaries"], index["integration_contract"], *index["insertion_steps"]):
        _assert_safe(payload)


def test_ps_q8c_blocked_presenter_blocks_future_insertion_without_mutation() -> None:
    presenter = build_prediction_warroom_ui_mount_presenter_packet().to_dict()
    presenter["display_state"] = "blocked_for_operator_review_render_disabled"
    contract = build_prediction_warroom_page_insertion_contract(presenter_packet=presenter).to_dict()
    assert contract["insertion_state"] == "blocked_before_future_guarded_warroom_page_insertion"
    assert contract["insertion_metrics"]["future_insertion_allowed_by_contract"] is False
    assert any(item["issue_code"] == "presenter_not_ready_for_operator_review" for item in contract["insertion_blockers"])
    assert contract["warroom_page_mutation_allowed"] is False
    _assert_safe(contract)


def test_ps_q8c_blocked_rows_block_future_insertion_without_runtime_access() -> None:
    presenter = build_prediction_warroom_ui_mount_presenter_packet().to_dict()
    presenter["blocked_entry_row_count"] = 1
    contract = build_prediction_warroom_page_insertion_contract(presenter_packet=presenter).to_dict()
    assert contract["insertion_state"] == "blocked_before_future_guarded_warroom_page_insertion"
    issue_codes = {item["issue_code"] for item in contract["insertion_blockers"]}
    assert "presenter_has_blocked_entry_rows" in issue_codes
    assert contract["actual_file_read_allowed_by_this_contract"] is False
    assert contract["actual_payload_decode_allowed_by_this_contract"] is False
    _assert_safe(contract)


def main() -> int:
    test_ps_q8c_static_boundaries_and_markers()
    test_ps_q8c_default_contract_is_ready_but_does_not_insert()
    test_ps_q8c_insertion_steps_are_explicit_and_folded()
    test_ps_q8c_index_is_compact_and_safe()
    test_ps_q8c_blocked_presenter_blocks_future_insertion_without_mutation()
    test_ps_q8c_blocked_rows_block_future_insertion_without_runtime_access()
    print("[OK] Prediction System PS-Q8C WarRoom page insertion contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
