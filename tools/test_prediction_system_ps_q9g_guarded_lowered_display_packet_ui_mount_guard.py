# path: ./tools/test_prediction_system_ps_q9g_guarded_lowered_display_packet_ui_mount_guard.py
# desc: Focused guard for PS-Q9G guarded lowered display-packet UI mount/review panel.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel import (
    PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION,
    _boundary_rows,
    _metric_rows,
    _widget_candidate_rows,
)
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.processing.l4_consumer_models.shared",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "json",
    "pathlib",
)
FORBIDDEN_PANEL_TOKENS = (
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
    "st.file_uploader",
    "st.text_input",
    "st.number_input",
    "load_prediction",
    "latest_payload",
    "hot_latest",
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
    "persist=True",
)
FORBIDDEN_PAGE_HELPER_TOKENS = FORBIDDEN_PANEL_TOKENS + (
    "build_prediction_warroom_actual_display_packet_lowering_result",
    "build_prediction_warroom_lowered_display_packet_visibility_review_contract(",
)
REQUIRED_PAGE_MARKERS = (
    "render_prediction_warroom_lowered_display_packet_visibility_review_panel",
    "def _render_prediction_warroom_lowered_display_packet_visibility_review_section() -> None:",
    "Prediction WarRoom real payload review",
    "with live_shell.render_folded_section(\"Prediction WarRoom real payload review\", expanded=True):",
    "Prediction WarRoom real payload review is top/default-expanded and read-only",
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


def _function_source(module_text: str, function_name: str) -> str:
    tree = ast.parse(module_text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(module_text, node) or ""
    raise AssertionError(f"missing function: {function_name}")


def test_ps_q9g_panel_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    assert "streamlit" in imports
    for token in FORBIDDEN_PANEL_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_lowered_display_packet_visibility_review_panel.ps_q9g.v1" in text
    assert "render_prediction_warroom_lowered_display_packet_visibility_review_panel" in text
    assert "No lowered display-packet widget candidates are available for review yet." in text
    assert "no loader, no file read, no payload decode" in text


def test_ps_q9g_warroom_page_has_top_default_expanded_review_section_after_q9v() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    for marker in REQUIRED_PAGE_MARKERS:
        assert marker in text, marker
    top_marker = 'with live_shell.render_folded_section("Prediction WarRoom real payload review", expanded=True):'
    old_bottom_marker = 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=False):'
    overview_marker = 'with live_shell.zone_container(\n        label=get_text(lang, "ui_label_overview")'
    assert text.count(top_marker) == 1
    assert old_bottom_marker not in text
    assert text.count("_render_prediction_warroom_lowered_display_packet_visibility_review_section") == 2
    assert text.index(top_marker) < text.index(overview_marker)
    helper_text = _function_source(text, "_render_prediction_warroom_lowered_display_packet_visibility_review_section")
    for token in FORBIDDEN_PAGE_HELPER_TOKENS:
        assert token not in helper_text, token
    assert "render_prediction_warroom_lowered_display_packet_visibility_review_panel()" in helper_text


def test_ps_q9g_rows_are_read_only_and_review_only() -> None:
    packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract().to_dict()
    metric_rows = _metric_rows(packet)
    boundary_rows = _boundary_rows(packet)
    widget_rows = _widget_candidate_rows(packet)
    assert metric_rows[0] == {"name": "contract_state", "value": "blocked_visibility_review_contract"}
    assert widget_rows == []
    boundaries = {item["boundary"]: item["enabled"] for item in boundary_rows}
    assert boundaries["streamlit_review_panel"] is True
    assert boundaries["warroom_card_rendering"] is False
    assert boundaries["ui_triggered_loader_execution"] is False
    assert boundaries["runtime_file_read"] is False
    assert boundaries["payload_decode"] is False
    assert boundaries["autotrade_trigger"] is False
    assert boundaries["broker_private_api"] is False


def test_ps_q9g_panel_version_is_stable() -> None:
    assert PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION == "prediction_warroom_lowered_display_packet_visibility_review_panel.ps_q9g.v1"


def main() -> int:
    test_ps_q9g_panel_static_boundaries_and_markers()
    test_ps_q9g_warroom_page_has_top_default_expanded_review_section_after_q9v()
    test_ps_q9g_rows_are_read_only_and_review_only()
    test_ps_q9g_panel_version_is_stable()
    print("[OK] Prediction System PS-Q9G guarded lowered display-packet UI mount guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
