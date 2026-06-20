# path: ./tools/test_prediction_system_ps_q8d_guarded_warroom_page_insertion_guard.py
# desc: Guard for PS-Q8D guarded folded WarRoom page insertion. UI rendering only in an initial-collapsed review section; no loader, file read, payload decode, Collector, AutoTrade, broker, approval, or command behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_page_insertion_contract import build_prediction_warroom_page_insertion_contract
from btcts.apps.operator_ui.components.prediction_warroom_ui_mount_presenter import build_prediction_warroom_ui_mount_presenter_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
Q8C_GUARD = REPO_ROOT / "tools/test_prediction_system_ps_q8c_warroom_page_insertion_contract_guard.py"
FORBIDDEN_NEW_HELPER_TOKENS = (
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "st.file_uploader",
    "st.text_input",
    "st.number_input",
    "open(",
    "Path(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    ".exists(",
    ".stat(",
    "load_prediction",
    "latest_payload",
    "hot_latest",
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
)
REQUIRED_HELPER_MARKERS = (
    "def _prediction_warroom_mount_review_zone_rows(packet: dict) -> list[dict]:",
    "def _prediction_warroom_mount_review_entry_rows(packet: dict) -> list[dict]:",
    "def _render_prediction_warroom_ui_mount_review_section() -> None:",
    "build_prediction_warroom_ui_mount_presenter_packet().to_dict()",
    "Prediction WarRoom mount review is display-only",
    "no loader, no approval, no file read, no payload decode, no runtime action",
    "render=false",
    "page_mutation",
)


def _function_source(module_text: str, function_name: str) -> str:
    tree = ast.parse(module_text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(module_text, node) or ""
    raise AssertionError(f"missing function: {function_name}")


def test_ps_q8d_warroom_page_has_folded_review_section_at_q8c_anchor() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    assert "build_prediction_warroom_ui_mount_presenter_packet" in text
    assert "Prediction WarRoom mount review" in text
    assert "_render_prediction_warroom_ui_mount_review_section" in text
    assert "with live_shell.render_folded_section(\"Prediction WarRoom mount review\", expanded=False):" in text
    operator_support_pos = text.index("def _render_warroom_operator_support_review()")
    folded_section_marker = 'with live_shell.render_folded_section("Prediction WarRoom mount review", expanded=False):'
    review_section_pos = text.index(folded_section_marker)
    diagnostics_pos = text.index("get_text(lang, \"ui_slot_diagnostics_title\")")
    assert operator_support_pos < review_section_pos < diagnostics_pos
    assert text.count(folded_section_marker) == 1
    assert text.count("Prediction WarRoom mount review is display-only") == 1
    assert text.count("_render_prediction_warroom_ui_mount_review_section") == 2


def test_ps_q8d_new_helper_is_read_only_and_does_not_runtime_load() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    for marker in REQUIRED_HELPER_MARKERS:
        assert marker in text, marker
    helper_text = "\n".join(
        _function_source(text, function_name)
        for function_name in (
            "_prediction_warroom_mount_review_zone_rows",
            "_prediction_warroom_mount_review_entry_rows",
            "_render_prediction_warroom_ui_mount_review_section",
        )
    )
    for token in FORBIDDEN_NEW_HELPER_TOKENS:
        assert token not in helper_text, token
    assert "st.dataframe" in helper_text
    assert "st.caption" in helper_text
    assert "_render_warroom_reading_caption" in helper_text
    assert "hide_index=True" in helper_text


def test_ps_q8d_q8c_contract_and_q8b_presenter_remain_ready() -> None:
    contract = build_prediction_warroom_page_insertion_contract().to_dict()
    presenter = build_prediction_warroom_ui_mount_presenter_packet().to_dict()
    assert contract["insertion_state"] == "ready_for_future_guarded_warroom_page_insertion"
    assert contract["insertion_metrics"]["future_insertion_allowed_by_contract"] is True
    assert presenter["display_state"] == "ready_for_operator_review_render_disabled"
    assert presenter["mount_entry_row_count"] == 12
    assert presenter["zone_section_count"] == 3
    assert presenter["blocked_entry_row_count"] == 0


def test_ps_q8d_q8c_guard_allows_post_insertion_state() -> None:
    text = Q8C_GUARD.read_text(encoding="utf-8")
    assert "Q8D may insert the folded review section" in text
    assert "render_folded_section(\"Prediction WarRoom mount review\", expanded=False)" in text
    assert "prediction_warroom_page_insertion_contract" in text


def main() -> int:
    test_ps_q8d_warroom_page_has_folded_review_section_at_q8c_anchor()
    test_ps_q8d_new_helper_is_read_only_and_does_not_runtime_load()
    test_ps_q8d_q8c_contract_and_q8b_presenter_remain_ready()
    test_ps_q8d_q8c_guard_allows_post_insertion_state()
    print("[OK] Prediction System PS-Q8D guarded WarRoom page insertion guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
